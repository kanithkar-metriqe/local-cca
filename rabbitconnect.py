from config.rabitmqconfig import rabbitmq_connection
from config.configuration import HITLcompletedqueue, CCAincomingqueue
import json


def handling_callback():
    try:
        SAMPLE_DATA = { 
                "property_id": '362',
                "mail_type":"escalation",
                "message": 
                    "During the BR review for Candlewood Suites Bismarck (Property Code 362), a bank entry dated 29-Aug-2025 for $1,400.00 with the description “AMERICAN EXPRESS SETTLEMENT XXXXXX2463” remains unmatched. The corresponding GL entry dated 21-Aug-2025 shows $1,475.00, resulting in a variance that prevents reconciliation. The transaction is associated with Fiserv, and the posting sequence suggests a possible settlement or rounding difference. Kindly review this variance and take the necessary action to resolve the mismatch.",
                "trackingId":"",
                "dashboard_info":[
                    {
                        "success": False,
                        "error": "",
                        "trackingId": "",
                        "dashboard_info": "Test From CCA",
                        "property_id": "362",
                    }   
                ],
            #     "database_creds":{
            #         "database": "learning",
            #         "username":"postgres",
            #         "password":"Kanith@14",
            #         "host":"localhost",
            #         "port":"5432"
            #    },
                "database_creds":{
                    "database": "learning",
                    "username":"postgres",
                    "password":"Kanith@14",
                    "host":"localhost",
                    "port":"5432"
               },
            }
        channel = rabbitmq_connection()
        channel.queue_declare(queue=CCAincomingqueue,durable=False)
        channel.basic_publish(
        exchange='',
        routing_key=CCAincomingqueue,
        body=json.dumps(SAMPLE_DATA)
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

 