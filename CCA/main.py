import os
import json
import asyncio
import threading
import time
from dotenv import load_dotenv

from config.rabitmqconfig import rabbitmq_connection
from config.configuration import HITLcompletedqueue, CCAcompletedqueue
from mail_agent import agent
from rabbitconnect import handling_callback
from openai import OpenAI
from agents import Runner

# ==========================================
# CONFIG
# ==========================================
QUEUE_IDLE_TIMEOUT = 15  # Auto-shutdown if idle for 15 seconds

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ==========================================
# ASYNC PROCESS HANDLER
# ==========================================
async def process_message(body):
    print("\n process_message TRIGGERED")

    sender = os.getenv("FROM_MAIL")
    receiver = os.getenv("TO_EMAIL")

    decoded_body = body.decode()

    print("\n=== Incoming Message ===")
    print(decoded_body)

    # Run agent
    response = await Runner.run(
        agent,
        input=(
            f"Generate a professional HTML email based on this input:\n"
            f"{decoded_body}\n"
            f"Sender: {sender}\nReceiver: {receiver}"
        )
    )

    agent_output = (
        response["final_output"]
        if isinstance(response, dict)
        else getattr(response, "final_output", None)
    )

    print("\n=== Agent Response ===")
    print(agent_output)

    # Publish to next queue
    channel = rabbitmq_connection()
    channel.queue_declare(queue=CCAcompletedqueue, durable=False)

    channel.basic_publish(
        exchange="",
        routing_key=CCAcompletedqueue,
        body=json.dumps({
            "response": agent_output,
            "agent": "cca"
        })
    )

    print("Result pushed to CCA queue")


# ==========================================
# RabbitMQ callback
# ==========================================
def on_rabbitmq_message(ch, method, properties, body, loop):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("\n Message received from HITL queue")

    loop.call_soon_threadsafe(asyncio.create_task, process_message(body))


# ==========================================
# RABBITMQ CONSUMER + AUTO SHUTDOWN
# ==========================================
def start_consumer():
    # Create event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    print("\n Event loop started in RabbitMQ consumer thread")

    channel = rabbitmq_connection()
    if not channel or not channel.is_open:
        print("RabbitMQ connection failed")
        return

    channel.queue_declare(queue=HITLcompletedqueue, durable=False)
    channel.basic_qos(prefetch_count=1)

    last_message_time = time.time()

    def on_msg(ch, method, props, body):
        nonlocal last_message_time
        last_message_time = time.time()
        on_rabbitmq_message(ch, method, props, body, loop)

    channel.basic_consume(
        queue=HITLcompletedqueue,
        on_message_callback=on_msg
    )

    print("\n Waiting for HITL queue messages...\n")

    # Blocking consumer executed inside another thread
    def consume():
        try:
            channel.start_consuming()
        except Exception as e:
            print("Consuming stopped:", e)

    consume_thread = threading.Thread(target=consume, daemon=True)
    consume_thread.start()

    # Monitor idle queue to auto-shutdown
    async def monitor_idle_timeout():
        while True:
            await asyncio.sleep(2)
            idle_for = time.time() - last_message_time

            if idle_for >= QUEUE_IDLE_TIMEOUT:
                print(f"\n No messages for {QUEUE_IDLE_TIMEOUT}s → Auto-Shutdown")
                try:
                    channel.stop_consuming()
                except:
                    pass
                loop.stop()
                break

    loop.create_task(monitor_idle_timeout())

    loop.run_forever()

    print("\n Event loop ended — consumer thread shutting down")


# ==========================================
# MAIN ENTRY POINT
# ==========================================
if __name__ == "__main__":
    handling_callback()

    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

    print("\n CCA Agent Listener Started Successfully")

    # Clean shutdown
    consumer_thread.join()
    print("\n Python shutdown complete")
