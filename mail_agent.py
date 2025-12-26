from agents import Agent
from agents import function_tool
from email_service import send_email
from teams_tool import send_teams_message
import os
from db.db_master import add_master, get_last_cca_id
from db.db_thread import add_thread
from typing import List, Optional

@function_tool
def send_ai_mail(sender: str, receiver: str, subject: str, content: str):
    """Send an AI-generated professional email."""
    send_email(sender, receiver, subject, content)
    return {"status": "success", "receiver": receiver}

sender = os.getenv("FROM_MAIL")
receiver = os.getenv("TO_EMAIL")

@function_tool
def save_master(
    cca_id: str,
    property_id: int,
    from_mail: str,
    to_mail: List[str],  
    cc_mail: List[str],   
    subject: str,
    body: str,
    source_agent: str = "CCA Mail Agent",
    notify_teams: bool = True,
):
    """Insert a CCA master record."""

    new_id = add_master({
        "cca_id": cca_id,
        "property_id": property_id,
        "from_mail": from_mail,
        "to_mail": to_mail,
        "cc_mail": cc_mail,
        "subject": subject,
        "body": body,
        "source_agent": source_agent,
        "notify_teams": notify_teams
    })

    return {"cca_id": cca_id, "db_id": new_id}


@function_tool
def generate_cca_id(property_id: int):
    """Generate new CCA ID based on last saved entry."""
    last_id = get_last_cca_id(property_id)

    if last_id:
        # Format: CCA-362-0003 → extract 3
        last_num = int(last_id.split("-")[-1])
        new_num = last_num + 1
    else:
        new_num = 1

    # Format with zero padding → 0001
    cca = f"CCA-{property_id}-{new_num:04d}"
    return {"cca_id": cca}

@function_tool
def save_thread(
    cca_id: str,
    direction: str,
    from_mail: List[str],
    to_mail: List[str],
    cc_mail: Optional[List[str]] = None,
    subject: str = "",
    body: str = "",
    send_date: Optional[str] = None,
    receive_date: Optional[str] = None,
    attachments: Optional[List[str]] = None,
    status: str = "SENT"
):
    """Insert a CCA thread entry."""

    new_id = add_thread({
        "cca_id": cca_id,
        "direction": direction,
        "from_mail": from_mail,
        "to_mail": to_mail,
        "cc_mail": cc_mail or [],
        "subject": subject,
        "body": body,
        "send_date": send_date,
        "receive_date": receive_date,
        "attachments": attachments or [],
        "status": status
    })


    return {"thread_id": new_id}


INSTRUCTIONS_FILE = os.path.join("prompts", "cca_instruction.adf")

try:
    with open(INSTRUCTIONS_FILE, "r", encoding="utf-8") as f:
        CCA_INSTRUCTIONS = f.read()
except FileNotFoundError as error:
    print("file not found")

agent = Agent(
    name="CCA Mail Agent",
    model="gpt-5.2",
    instructions=CCA_INSTRUCTIONS,
    tools=[send_ai_mail, send_teams_message, save_master, save_thread, generate_cca_id],
)
