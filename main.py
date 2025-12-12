import os
import json
import asyncio
from dotenv import load_dotenv

from config.rabitmqconfig import rabbitmq_connection
from config.configuration import CCAincomingqueue, CCAcompletedqueue
from mail_agent import agent
from rabbitconnect import handling_callback
from openai import OpenAI
from agents import Runner

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

def on_rabbitmq_message(ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print("\n Message received from HITL queue")
    
    # Run async function in the event loop
    asyncio.run(process_message(body))


def start_consumer():
    channel = rabbitmq_connection()
    if not channel or not channel.is_open:
        print("RabbitMQ connection failed")
        return

    channel.queue_declare(queue=CCAincomingqueue, durable=False)
    channel.basic_qos(prefetch_count=1)

    channel.basic_consume(
        queue=CCAincomingqueue,
        on_message_callback=on_rabbitmq_message
    )

    print("\n Waiting for HITL queue messages...\n")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\n Stopping consumer...")
        channel.stop_consuming()
    except Exception as e:
        print(f"Consuming error: {e}")

if __name__ == "__main__":
    handling_callback()
    
    print("\n CCA Agent Listener Started Successfully")
    # start_consumer()
    print("\n Python shutdown complete")
