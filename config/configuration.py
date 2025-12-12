import os
from dotenv import load_dotenv

load_dotenv()

# CCAincomingqueue = "met-queue-cca-agent"
CCAincomingqueue = "met-queue-cca-agent"
HITLcompletedqueue = "met-hitl-agent-completed-queue"
CCAcompletedqueue = "met-cca-agent-completed-queue"
CCAexceptionqueue = "met-cca-agent-exception-queue"

RABBITMQ_HOST = os.getenv("RABITMQHOST")
RABBITMQ_USER = os.getenv("RABITMQUSERNAME")
RABBITMQ_PASSWORD = os.getenv("RABITMQPASSWORD")