from agents import Agent
from agents import function_tool
from email_service import send_email
from teams_tool import send_teams_message
import os
from db.db_master import add_master, get_last_cca_id
from db.db_thread import add_thread
from datetime import datetime
from typing import List, Optional





# -----------------------------------------
# 1. Email Sending Tool
# -----------------------------------------
@function_tool
def send_ai_mail(sender: str, receiver: str, subject: str, content: str):
    """Send an AI-generated professional email."""
    send_email(sender, receiver, subject, content)
    return {"status": "success", "receiver": receiver}


# -----------------------------------------
# 2. DB Tools — FIXED (NO dict, strict params)
# -----------------------------------------
sender = os.getenv("FROM_MAIL")
receiver = os.getenv("TO_EMAIL")

@function_tool
def save_master(
    cca_id: str,
    property_id: int,
    from_mail: str,
    to_mail: List[str],   # FIXED
    cc_mail: List[str],   # FIXED
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
    attachments: Optional[List[str]] = None,  # FIXED: Explicit List[str] type
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

    print("-------------------------------------------", new_id)

    return {"thread_id": new_id}


# -----------------------------------------
# 3. Mail + Teams Agent
# -----------------------------------------
agent = Agent(
    name="CCA Mail Agent",
    model="gpt-4o-mini",
    instructions=(
        """
        # 📨 AI CCA Communication Agent

        ## ROLE
        You must perform 4 responsibilities in this order:
        1. Generate a professional HTML email.
        2. Generate a short Microsoft Teams alert message.
        3. Automatically generate a CCA ID (if not provided).
        4. Save database records using the DB tools.

        ## INPUT JSON
        - property_id (number)
        - message (string)
        - subject (string)
        - cca_id (optional)
        - event_type (optional)
        - from_mail (string)
        - to_mail (array of strings)
        - cc_mail (array of strings)
        - db_save_master (true/false)
        - db_save_thread (true/false)
        - direction (string: "inbound" or "outbound")  ← REQUIRED for thread
        - attachments (array of strings, optional)

        ## CCA ID RULES
        - If `cca_id` is missing, call `generate_cca_id(property_id)` and use the returned value.
        - Use this CCA ID for email subject, Teams message, and DB records.

        ## EMAIL RULES
        - Generate a concise professional HTML email with:
          Greeting → Issue → Required Actions → Regards block
        - Do NOT add extra greetings or repeated text.
        - Call `send_ai_mail(sender, receiver, subject, content)` with the same subject and body.

        ## TEAMS RULES
        - Generate a short alert for Teams.
        - Call `send_teams_message(text)`.

        ## DATABASE RULES
        - If `db_save_master` is true:
          → Call `save_master()` with all required fields:
            cca_id, property_id, from_mail, to_mail, cc_mail, subject, body, source_agent, notify_teams
        - If `db_save_thread` is true:
          → Call `save_thread()` with all required fields:
            cca_id, direction, from_mail, to_mail, cc_mail, subject, body, send_date (optional), receive_date (optional), attachments (optional), status
        - Never save to DB unless the corresponding flag is explicitly true.
        - Always include the returned result of the DB tool in your final response so we know if it succeeded.

        ## IMPORTANT
        - Always perform: CCA ID → Email → Teams → DB.
        - Never modify input fields.
        - Never generate random data.
        - Ensure all array fields (`to_mail`, `cc_mail`, `attachments`) are proper JSON arrays.
        - All tool calls must match their schema exactly.
        """
    ),
    tools=[send_ai_mail, send_teams_message, save_master, save_thread, generate_cca_id],
)
