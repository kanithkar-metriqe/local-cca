import requests
from agents import function_tool

import requests
import os
from typing import Dict, Any

WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

@function_tool
# def send_teams_message(text: str):
def send_teams_message(agent_text: str) -> str:
    """
    Create and send an Adaptive Card that includes agent text.
    """

    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "Metriqe",
                            "size": "Large",
                            "weight": "Bolder",
                            "color": "Accent"
                        },
                         {
                            "type": "TextBlock",
                            "text": "CCA Notification Bot",
                            "size": "small",
                            "weight": "Bolder",
                            "color": "Accent"
                        },
                        {
                            "type": "TextBlock",
                            "text": agent_text,      # 👈 AGENT TEXT IS INSERTED HERE
                            "wrap": True,
                            "spacing": "Medium"
                        }
                    ],
                    "actions": [
                        {
                            "type": "Action.OpenUrl",
                            "title": "Approved",
                            "url": "https://example.com"
                        },
                        {
                            "type": "Action.OpenUrl",
                            "title": "Resubmit",
                            "url": "https://example.com"
                        }
                    ]
                }
            }
        ]
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(WEBHOOK_URL, json=card_payload, headers=headers)

    if response.status_code == 200:
        return "Adaptive Card sent successfully ✔️"
    else:
        return f"❌ Failed: {response.status_code} - {response.text}"
