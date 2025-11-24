import os
from dotenv import load_dotenv

load_dotenv()

CCAincomingqueue = "met-cca-agent-incoming-queue"
HITLcompletedqueue = "met-hitl-agent-completed-queue"
CCAcompletedqueue = "met-cca-agent-completed-queue"
CCAexceptionqueue = "met-cca-agent-exception-queue"

RABBITMQ_HOST = os.getenv("RABITMQHOST")
RABBITMQ_USER = os.getenv("RABITMQUSERNAME")
RABBITMQ_PASSWORD = os.getenv("RABITMQPASSWORD")