import os
import asyncio
from config.rabitmqconfig import rabbitmq_connection
from config.configuration import HITLcompletedqueue, CCAcompletedqueue
from dotenv import load_dotenv
from agents import Runner
from openai import OpenAI
import json
from mail_agent import agent
from rabbitconnect import handling_callback


#  Load environment variables from .env file
load_dotenv()

#  Initialize OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Sample input data to simulate AI reasoning
input_sample = { 
    "property_id": 362,  
    "email_type": "gl_no_bank_entry",
    "message": (
        "The GL entry posted last week has not generated any corresponding "
        "bank entry yet. Please re-run the GL batch to ensure the bank entry is created."
    )
}

async def process_message(body):
    sender = os.getenv("FROM_MAIL")
    receiver = os.getenv("TO_EMAIL")

    decoded_body = body.decode()

    print("\n=== Incoming Message ===")
    print(decoded_body)

    # Run AI agent
    response = await Runner.run(
        agent,
        input=(
            f"Generate a professional HTML email based on this input:\n"
            f"{decoded_body}\n"
            f"Sender: {sender}\nReceiver: {receiver}"
        )
    )

    # Extract final output safely
    agent_output = response["final_output"] if isinstance(response, dict) else response.final_output

    print("\n=== Agent Response ===")
    print(agent_output)


def handl_queue(ch, method, properties, body): 
    ch.basic_ack(delivery_tag=method.delivery_tag)
    asyncio.run(process_message(body))
    

#  Async runner for the Agent
async def main():
    sender = os.getenv("FROM_MAIL")
    receiver = os.getenv("TO_EMAIL")

    channel = rabbitmq_connection()
    if not channel.is_open:
            return

    channel.queue_declare(queue=HITLcompletedqueue,durable=False)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=HITLcompletedqueue,on_message_callback=handl_queue)
    channel.start_consuming()


    response = await Runner.run(
        agent,
        input=(
            f"Generate a professional HTML email based on this input:\n"
            f"{input_sample}\n"
            f"Sender: {sender}\nReceiver: {receiver}"
        )
    )

    print("\n=== Agent Response  ===")
    print(response)


    channel.queue_declare(queue=CCAcompletedqueue,durable=False)
    channel.basic_publish(
        exchange='',
        routing_key=CCAcompletedqueue,
        body=json.dumps({
            "response" : response.final_output,
            "agent":"cca"
        })
    )

#  Entry point
if __name__ == "__main__":
    handling_callback()
    asyncio.run(main())