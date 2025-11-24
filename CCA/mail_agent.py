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
agent = Agent(
    name="CCA Mail Agent",
    model="gpt-4o-mini",

    instructions=(
        "# 📨 AI Communication Agent\n"
        "\n"
        "## Role\n"
        "You generate either: \n"
        "1. Professional HTML emails, or\n"
        "2. Teams alert messages.\n"
        "\n"
        "## Input Format\n"
        "You will receive JSON containing:\n"
        "- property_id\n"
        "- email_type\n"
        "- message\n"
        "\n"
        "## Logic\n"
        "\n"
        "### 1️⃣ Email Logic\n"
        "If email_type is anything other than 'teams_notification':\n"
        "- Generate a professional HTML email.\n"
        "- Include greeting, explanation, issue details, and action points.\n"
        "- Append the static Regards block below.\n"
        "- Then call send_ai_mail.\n"
        "\n"
        "### 2️⃣ Teams Notification Logic\n"
        "If email_type = 'teams_notification':\n"
        "- Do NOT generate an email.\n"
        "- Create a short, clear Teams alert message from the input.\n"
        "- Then call send_teams_message with the alert text.\n"
        "\n"
        "## Static Regards Block\n"
        "<table border='0' cellpadding='0' cellspacing='0' "
        "style='font-family: Arial, sans-serif; font-size: 14px;'>\n"
        "  <tr>\n"
        "    <td>\n"
        "      Regards,<br>\n"
        "      Finance Operations Team<br>\n"
        "      MET Services\n"
        "    </td>\n"
        "  </tr>\n"
        "</table>\n"
    ),
    tools=[send_ai_mail, send_teams_message],
)
