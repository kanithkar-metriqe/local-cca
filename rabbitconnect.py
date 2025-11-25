from config.rabitmqconfig import rabbitmq_connection
from config.configuration import HITLcompletedqueue
import json


def handling_callback():
    try:
        SAMPLE_DATA = { 
                "property_id": 362,
                "event_type": "Missing Bank Entry",
                "message": (
                    "GL entry posted last week does not have a corresponding bank entry. "
                    "Please review and take necessary action."
                )
            }
        channel = rabbitmq_connection()
        channel.queue_declare(queue=HITLcompletedqueue,durable=False)
        channel.basic_publish(
        exchange='',
        routing_key=HITLcompletedqueue,
        body=json.dumps({
            "response" : SAMPLE_DATA,
            "agent":"cca"
        })
    )
    except Exception as e:
        print(e)
        channel = rabbitmq_connection()
        channel.queue_declare(queue=HITLcompletedqueue,durable=False)
        channel.basic_publish(
            exchange='',  
            routing_key=HITLcompletedqueue,
            body=json.dumps({
                "response" : e,
                "agent":"exception"
            })
        )

 