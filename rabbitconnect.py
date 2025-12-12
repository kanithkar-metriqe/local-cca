from config.rabitmqconfig import rabbitmq_connection
from config.configuration import HITLcompletedqueue, CCAincomingqueue
import json


def handling_callback():
    try:
        # SAMPLE_DATA = {
        #     "trackingId": "",
        #     "propertyCode": "362",
        #     "propertyId": "",
        #     "dashboard_info": [
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "HITL Agent process initiated and waiting for human intervention."
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Starting HITL Agent for property code "
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "HITL Agent completed for property code "
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Preparing adaptive card message for human review."
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Error in HITL Agent: 'NoneType' object has no attribute 'get'"
        #         }
        #     ],
        #     "response": {
        #         "summary": "The bank statement amount matches the merchant settlement amount, but there is a variance in the associated GL amount.",
        #         "classification": "Unmatched - High GL Amount Variance",
        #         "merchant_amount": "800.00",
        #         "bank_amount": "800.00",
        #         "merchant_settlement_date": "2025-08-11",
        #         "bank_statement_date": "2025-08-11",
        #         "reason": "The bank statement amount of 800.00 matches the merchant settlement amount of 800.00 on the settlement date of 2025-08-11. However, the GL amount of 1000.00 shows a high variance of 200.00 from the expected amount.",
        #         "analysis_steps": "1. Verified the bank statement amount (800.00) against the merchant amount (800.00) - they match. 2. Checked for merchant fees or charges; identified fees totaling 20.00. 3. Analyzed GL amount of 1000.00, which shows a significant variance from the bank statement. 4. Since the GL variance is significant, classified as unmatched.",
        #         "recommended_action": "Send to HITL queue for investigation.",
        #         "is_hitl_required": "true"
        #     },
        #     "databaseCreds": {
        #         "host": "metriqe-db-new.cf8ac60ou0zv.ap-south-1.rds.amazonaws.com",
        #         "username": "postgres",
        #         "password": "Metriqe123#",
        #         "database": "met_ai_agents_dev",
        #         "port": "5432"
        #     },
        #     "agent": "cra",
        #     "module": "HITL Agent",
        #     "trackingId": "",
        #     "error": "Unknown error",
        #     "dashboard_info": [
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "HITL Agent process initiated and waiting for human intervention."
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Starting HITL Agent for property code "
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "HITL Agent completed for property code "
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Preparing adaptive card message for human review."
        #         },
        #         {
        #             "trackingId": "",
        #             "agent": "HITL Agent",
        #             "agentProcessId": "null",
        #             "source": "HITL Agent",
        #             "status": "Error in HITL Agent: 'NoneType' object has no attribute 'get'"
        #         }
        #     ]
        # }

 
        SAMPLE_DATA = { 
                "property_id": 362,
                "mail_type":"escalation",
                "message": 
                    "During the BR review for Candlewood Suites Bismarck (Property Code 362), a bank entry dated 29-Aug-2025 for $1,476.30 with the description “AMERICAN EXPRESS SETTLEMENT XXXXXX2463” remains unmatched. The corresponding GL entry dated 21-Aug-2025 shows $1,475.00, resulting in a variance that prevents reconciliation. The transaction is associated with Fiserv, and the posting sequence suggests a possible settlement or rounding difference. Kindly review this variance and take the necessary action to resolve the mismatch.",
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
                    "database": "met_ai_agents_dev",
                    "username":"postgres",
                    "password":"Metriqe123#",
                    "host":"metriqe-db-new.cf8ac60ou0zv.ap-south-1.rds.amazonaws.com",
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

 