"""Third-party integrations — Slack, Jira, Notion."""

import httpx

from app.core.config import settings


# ─── Slack ────────────────────────────────────────────────────────────────────

async def post_to_slack(channel: str, text: str) -> str:
    """Post a message to a Slack channel. Returns the message timestamp."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {settings.SLACK_BOT_TOKEN}"},
            json={"channel": channel, "text": text, "mrkdwn": True},
        )
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(f"Slack error: {data.get('error')}")
        return data["ts"]


async def push_action_items_to_slack(meeting_title: str, action_items: list, channel: str):
    """Format and push action items summary to Slack."""
    lines = [f"*Action items from: {meeting_title}*\n"]
    for i, item in enumerate(action_items, 1):
        assignee = f" → {item['assignee_name']}" if item.get("assignee_name") else ""
        due = f" (due {item['due_date']})" if item.get("due_date") else ""
        lines.append(f"{i}. {item['title']}{assignee}{due}")
    await post_to_slack(channel, "\n".join(lines))


# ─── Jira ─────────────────────────────────────────────────────────────────────

async def push_to_jira(action_item) -> str:
    """Create a Jira issue for an action item. Returns the Jira issue ID."""
    auth = (settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
    payload = {
        "fields": {
            "summary": action_item.title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": action_item.description or action_item.title}],
                    }
                ],
            },
            "issuetype": {"name": "Task"},
            "priority": {"name": action_item.priority.capitalize()},
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.JIRA_BASE_URL}/rest/api/3/issue",
            auth=auth,
            json=payload,
        )
        response.raise_for_status()
        return response.json()["id"]


# ─── Notion ───────────────────────────────────────────────────────────────────

async def push_to_notion(database_id: str, action_item) -> str:
    """Create a Notion page in the given database. Returns the page ID."""
    headers = {
        "Authorization": f"Bearer {settings.NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {"title": [{"text": {"content": action_item.title}}]},
            "Status": {"select": {"name": action_item.status.value}},
            "Priority": {"select": {"name": action_item.priority.value}},
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        return response.json()["id"]
