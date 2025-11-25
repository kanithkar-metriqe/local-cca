from agents import Agent
from email_service import send_email
from agents import function_tool
from teams_tool import send_teams_message


# -----------------------------------------
# 1. Email Sending Tool
# -----------------------------------------
@function_tool
def send_ai_mail(sender: str, receiver: str, subject: str, content: str):
    """Send an AI-generated professional email."""
    send_email(sender, receiver, subject, content)
    return f"Email successfully sent to {receiver}"


# -----------------------------------------
# 2. Mail + Teams Agent
# -----------------------------------------
# 
agent = Agent(
    name="CCA Mail Agent",
    model="gpt-4o-mini",
    instructions=(
        "# 📨 AI Communication Agent\n"
        "\n"
        "## Role\n"
        "You generate **both**:\n"
        "1. Professional HTML email.\n"
        "2. Teams alert message.\n"
        "\n"
        "## Input Format\n"
        "You will receive JSON containing:\n"
        "- property_id\n"
        "- message\n"
        "\n"
        "## Logic\n"
        "1️**Email Logic:**\n"
        "- Generate a professional HTML email.\n"
        "- Keep it concise and focused; do NOT include additional welcomes, repetitive phrases, or irrelevant content.\n"
        "- Include only the essential greeting, issue details, explanation, and clear action points.\n"
        "- Append the static Regards block.\n"
        "- Call `send_ai_mail` with the email content.\n"
        "\n"
        "2️**Teams Logic:**\n"
        "- Create a short, clear Teams alert message from the input.\n"
        "- Call `send_teams_message` with the alert text.\n"
        "\n"
        "## Static Regards Block\n"
        "<table border='0' cellpadding='0' cellspacing='0' style='font-family: Arial, sans-serif; font-size: 14px;'>"
        "<tr>"
        "<td><br>"
        "Regards,<br>"
        "Finance Operations Team<br>"
        "MET Services<br><br>"
        "<img src='https://metriqe.sharepoint.com/sites/productdevelopment/shared%20documents/ux%20-%20files/metriqe/metriqe%20logo%20png%20white%20bg.png?web=1' "
        "alt='MET Logo' "
        "style='width:120px; height:auto; display:block; margin-top:5px;'>"
        "</td>"
        "</tr>"
        "</table>\n"
    ),
    tools=[send_ai_mail, send_teams_message],
)
