import json
import os
import time
from dotenv import load_dotenv
import requests
from openai import OpenAI

# -----------------------------
# 0. Load Environment Variables
# -----------------------------
load_dotenv("Keys.env")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY")
if not OPENAI_API_KEY or not BRIGHTDATA_API_KEY:
    raise RuntimeError("OPENAI_API_KEY or BRIGHTDATA_API_KEY missing in Keys.env")

client = OpenAI(api_key=OPENAI_API_KEY)
MODEL_NAME = "gpt-4o"  # vision + file support model

# -----------------------------
# 1. Structuring PDF via Assistants (correct attachment usage)
# -----------------------------
JSON_SCHEMA_PROMPT = """
Produce JSON matching this schema exactly (omit nulls):
{
  "team": {
    "founders": [{"name": string, "background": string}],
    "team_strength": string,
    "network_strength": string
  },
  "market": {
    "TAM": string,
    "SAM": string,
    "SOM": string,
    "growth_rate": string
  },
  "product": {
    "stage": string,
    "USP": string,
    "customer_acquisition": string,
    "launch date": string
  },
  "traction": {
    "revenue_growth": {"MRR": string, "ARR": string},
    "user_growth": string,
    "engagement": string,
    "customer_validation": {"testimonials": [string], "churn": string, "NPS": string},
    "active_users": string
  },
  "funding": {
    "stage": string,
    "amount": string,
    "cap_table_strength": string,
    "investors_on_board": [{"name": string, "type": string}]
  },
  "financial_efficiency": {
    "burn_rate": string,
    "CAC_vs_LTV": string,
    "unit_economics": string
  },
  "miscellaneous": {
    "regulatory_risk": string,
    "geographic_focus": string,
    "timing_fad_risk": string
  }
}
"""


def structure_pdf_with_assistant(pdf_path: str) -> dict:
    """Uses Assistants API to process a PDF file and return structured JSON."""
    # 1. Upload PDF file to OpenAI
    with open(pdf_path, "rb") as f:
        file_obj = client.files.create(file=f, purpose="assistants")
    file_id = file_obj.id

    # 2. Create assistant (with file_search tool)
    assistant = client.beta.assistants.create(
        name="PitchDeck Extractor",
        model=MODEL_NAME,
        tools=[{"type": "file_search"}],
        instructions=(
            "You are an expert at analysing startup pitch decks. "
            "Return ONLY valid JSON conforming to the schema provided by the user. "
            "Make sure your response is valid JSON without any markdown formatting or backticks."
        ),
    )

    # 3. Create thread and upload file via a message
    thread = client.beta.threads.create()
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=JSON_SCHEMA_PROMPT + "\n\nExtract from the attached pitch deck.",
        attachments=[{"file_id": file_id, "tools": [{"type": "file_search"}]}]
    )

    # 4. Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    # 5. Poll for run completion
    while run.status not in ("completed", "failed"):
        time.sleep(1.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    if run.status == "failed":
        raise RuntimeError(f"Assistant run failed: {run.last_error}")

    # 6. Get response from assistant
    msgs = client.beta.threads.messages.list(thread.id, order="desc")
    assistant_msg = next((m for m in msgs.data if m.role == "assistant"), None)
    if not assistant_msg:
        raise RuntimeError("No assistant response found")

    content_text = assistant_msg.content[0].text.value.strip()

    # Debug: Print the raw content to see what's being returned
    print("Raw content from assistant:")
    print(content_text)

    # Try to extract JSON from the content (in case it's wrapped in markdown code blocks)
    import re
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content_text)
    if json_match:
        content_text = json_match.group(1).strip()
        print("Extracted JSON from markdown code block")

    # Try to parse JSON with error handling
    try:
        return json.loads(content_text)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Content length: {len(content_text)}")
        if content_text:
            print(f"First 500 chars: {content_text[:500]}")

        # Try a different approach - use another API call to fix the JSON
        corrected_json = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system",
                 "content": "You're a JSON repair expert. Convert the following text to valid JSON matching the schema, fixing any formatting issues:"},
                {"role": "user",
                 "content": f"{JSON_SCHEMA_PROMPT}\n\nHere's the text to convert to JSON:\n{content_text}"}
            ]
        )

        corrected_text = corrected_json.choices[0].message.content.strip()

        # Try to extract JSON again if needed
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', corrected_text)
        if json_match:
            corrected_text = json_match.group(1).strip()

        return json.loads(corrected_text)

# -----------------------------
# 2. Enrich with LinkedIn Data via BrightData API
# -----------------------------

def enrich_with_linkedin(data: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    for founder in data.get("team", {}).get("founders", []):
        resp = requests.post(
            "https://api.brightdata.com/linkedin/profile",
            headers=headers,
            json={"name": founder["name"]},
            timeout=30,
        )
        founder["linkedin_profile_data"] = resp.json()
    return data

# -----------------------------
# 3. Main Pipeline
# -----------------------------

def main():
    pdf_path = "./airbnb.pdf"  # TODO: parameterize

    structured = structure_pdf_with_assistant(pdf_path)
    enriched = enrich_with_linkedin(structured)

    # TODO: metric calculations
    enriched["metrics"] = {}

    out = "./output.json"
    with open(out, "w") as f:
        json.dump(enriched, f, indent=2)
    print(f"Pipeline complete. Output written to {out}")

if __name__ == "__main__":
    main()


