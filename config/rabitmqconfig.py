import pika
from config.configuration import RABBITMQ_HOST,RABBITMQ_USER,RABBITMQ_PASSWORD

def rabbitmq_connection():
    credentials = pika.PlainCredentials(RABBITMQ_USER,RABBITMQ_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST,credentials=credentials,port=5672))
    channel = connection.channel()
    return channel