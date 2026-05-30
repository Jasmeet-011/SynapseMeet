"""AI summarization + structured extraction service using GPT-4o."""

import json

import openai

from app.core.config import settings

openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# ─── Prompts ──────────────────────────────────────────────────────────────────

SUMMARY_SYSTEM_PROMPT = """You are an expert meeting analyst. Given a meeting transcript,
produce a concise, structured summary. Be factual and specific. Do not add information
not present in the transcript."""

EXTRACTION_SYSTEM_PROMPT = """You are an expert at extracting structured information from
meeting transcripts. Extract action items, decisions, and key topics with precision.
Always respond with valid JSON matching the provided schema."""


async def generate_summary(transcript: str, language: str = "en") -> str:
    """Generate a concise meeting summary from transcript text."""
    lang_instruction = f" Respond in {language}." if language != "en" else ""

    response = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT + lang_instruction},
            {
                "role": "user",
                "content": f"Summarize this meeting transcript in 3-5 bullet points:\n\n{transcript}",
            },
        ],
        max_tokens=500,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


async def extract_action_items(transcript: str) -> list[dict]:
    """
    Extract action items from transcript using GPT-4o function calling.

    Returns list of:
    {
        "title": str,
        "assignee_name": str | None,
        "due_date": str | None,   # ISO date string
        "priority": "low" | "medium" | "high" | "critical",
        "transcript_excerpt": str
    }
    """
    tools = [
        {
            "type": "function",
            "function": {
                "name": "save_action_items",
                "description": "Save extracted action items from the meeting",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action_items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "assignee_name": {"type": ["string", "null"]},
                                    "due_date": {"type": ["string", "null"], "format": "date"},
                                    "priority": {
                                        "type": "string",
                                        "enum": ["low", "medium", "high", "critical"],
                                    },
                                    "transcript_excerpt": {"type": "string"},
                                },
                                "required": ["title", "priority", "transcript_excerpt"],
                            },
                        }
                    },
                    "required": ["action_items"],
                },
            },
        }
    ]

    response = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Extract all action items from this meeting transcript:\n\n{transcript}",
            },
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "save_action_items"}},
        temperature=0.1,
    )

    tool_call = response.choices[0].message.tool_calls
    if not tool_call:
        return []

    data = json.loads(tool_call[0].function.arguments)
    return data.get("action_items", [])


async def extract_topics_and_keywords(transcript: str) -> dict:
    """Extract main topics and keywords from a transcript."""
    response = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Extract topics and keywords from this transcript. "
                    "Return JSON: {\"topics\": [str], \"keywords\": [str]}\n\n"
                    f"{transcript}"
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)


async def analyze_sentiment(transcript: str, speakers: dict) -> dict:
    """
    Analyze per-speaker sentiment from transcript.
    speakers: {speaker_label: speaker_name}
    Returns: {speaker_name: {"positive": float, "neutral": float, "negative": float}}
    """
    if not speakers:
        return {}

    response = await openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Analyze the sentiment of each speaker in this transcript. "
                    f"Speakers: {list(speakers.values())}. "
                    f"Return JSON with speaker names as keys and sentiment scores "
                    f"(positive/neutral/negative summing to 1.0) as values.\n\n{transcript}"
                ),
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = response.choices[0].message.content or "{}"
    return json.loads(content)
