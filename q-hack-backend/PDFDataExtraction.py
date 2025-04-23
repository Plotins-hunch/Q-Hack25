import json
import os
import time
from dotenv import load_dotenv
import requests
from openai import OpenAI
import datetime

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
{{
  "company_name": "string",
  "team": {
    "founders": [{"name": "string", "background": "string"}],
    "team_strength": "string",
    "network_strength": "string"
  },
  "market": {
    "TAM": "string",
    "SAM": "string",
    "SOM": "string",
    "growth_rate": "string"
  },
  "product": {
    "stage": "string",
    "USP": "string",
    "customer_acquisition": "string"
  },
  "traction": {
    "revenue_growth": {"MRR": "string", "ARR": "string"},
    "user_growth": "string",
    "engagement": "string",
    "customer_validation": {
      "testimonials": ["string"],
      "churn": "string",
      "NPS": "string"
    }
  },
  "funding": {
    "stage": "string",
    "amount": "string",
    "cap_table_strength": "string",
    "investors_on_board": [{"name": "string", "type": "string"}]
  },
  "financial_efficiency": {
    "burn_rate": "string",
    "CAC_vs_LTV": "string",
    "unit_economics": "string"
  },
  "miscellaneous": {
    "regulatory_risk": "string",
    "geographic_focus": "string",
    "timing_fad_risk": "string"
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
def safe_json(resp, label: str) -> dict | list:
    """
    Return resp.json() if the body is non-empty and valid JSON;
    otherwise log & return {}.
    """
    text = resp.text.strip()
    if not text:
        print(f"[WARN] {label}: empty response (HTTP {resp.status_code})")
        return {}
    try:
        return resp.json()
    except json.JSONDecodeError:
        print(f"[ERROR] {label}: invalid JSON\n{text[:500]}")
        return {}

def fetch_snapshot(snapshot_id: str, max_wait_sec: int = 300) -> list[dict]:
    """
    Download an existing Bright Data snapshot; if it is not ready yet,
    poll the /progress/ endpoint (up to `max_wait_sec`) until 'success'.
    """
    headers = {"Authorization": f"Bearer {BRIGHTDATA_API_KEY}"}
    data_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json"

    # 1) first try direct download
    resp = requests.get(data_url, headers=headers, timeout=30)
    if resp.ok and resp.text.strip():
        recs = safe_json(resp, f"snapshot {snapshot_id}")
        if isinstance(recs, list) and recs:
            return recs

    # 2) if empty → poll /progress/
    prog_url = f"https://api.brightdata.com/datasets/v3/progress/{snapshot_id}"
    deadline = time.time() + max_wait_sec
    while time.time() < deadline:
        prog = requests.get(prog_url, headers=headers, timeout=15)
        status = safe_json(prog, f"progress {snapshot_id}").get("status")
        print(f"[INFO] Snapshot {snapshot_id} status={status!r}")
        if status == "ready":
            break
        if status in ("failed", "error"):
            raise RuntimeError(f"Snapshot {snapshot_id} failed: {prog.text}")
        time.sleep(5)
    else:
        raise RuntimeError(f"Timeout waiting for snapshot {snapshot_id}")

    # 3) final download
    recs = safe_json(requests.get(data_url, headers=headers, timeout=30),
                     f"snapshot {snapshot_id}")
    if not isinstance(recs, list):
        raise ValueError(f"Unexpected data from snapshot {snapshot_id}: {recs}")
    return recs

# ── enrichment main ───────────────────────────────────────────────────────────
def enrich_with_linkedin(data: dict) -> dict:
    """
    For each founder:
      • trigger Bright Data discover-by-name dataset
      • wait (up to 5 min) for the snapshot
      • pick the profile whose current_company.name matches our company
      • extract:
          university, connections, age, gender, previous employments,
          linkedin_posts_last_30d
    Also adds `company_followers` at root level.
    """
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type":  "application/json",
    }
    DATASET_ID = "gd_l1viktl72bvl7bjuj0"

    # try to find the company name in the structured payload
    company_name = (
        data.get("company_name")
        or data.get("team", {}).get("company_overview", {}).get("name")
        or ""
    ).lower()

    for founder in data.get("team", {}).get("founders", []):
        first, *rest = founder["name"].split()
        if not rest:
            print(f"[WARN] skipping founder with single name: {founder['name']}")
            continue
        last = " ".join(rest)

        # — 1) trigger discover job
        trigger_url = (
            "https://api.brightdata.com/datasets/v3/trigger"
            f"?dataset_id={DATASET_ID}"
            "&include_errors=true&type=discover_new&discover_by=name"
        )
        trig = requests.post(trigger_url,
                             headers=headers,
                             json=[{"first_name": first, "last_name": last}],
                             timeout=60)
        if not trig.ok:
            print(f"[ERROR] trigger failed for {founder['name']}: {trig.text}")
            continue

        snapshot_id = safe_json(trig, f"trigger {founder['name']}").get("snapshot_id")
        if not snapshot_id:
            print(f"[WARN] no snapshot_id for {founder['name']}")
            continue
        print(f"[INFO] Snapshot {snapshot_id} queued for {founder['name']}")

        # — 2) download / wait (up to 5 min)
        try:
            profiles = fetch_snapshot(snapshot_id, max_wait_sec=300)
        except Exception as e:
            print(f"[ERROR] snapshot fetch failed for {founder['name']}: {e}")
            continue

        # choose profile matching company_name
        prof = next(
            (p for p in profiles
             if p.get("current_company", {}).get("name", "").lower() == company_name),
            profiles[0]
        )
        print(f"[INFO] Using profile {prof.get('url')}")

        # — 3) extract fields
        founder["university"] = (
            prof.get("educations_details")
            or (prof.get("education") or [{}])[0].get("title")
        )
        founder["network_strength"] = prof.get("connections")
        founder["age"] = prof.get("age")
        founder["gender"] = prof.get("gender")

        # previous employments
        exp = prof.get("experience") or []
        founder["previous_employments"] = [
            {
                "company": e.get("company"),
                "title":   e.get("title"),
                "start":   e.get("start_date"),
                "end":     e.get("end_date"),
            }
            for e in exp
        ]

        # posts in last 30 days
        activity = prof.get("activity") or prof.get("posts") or []
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
        recent = [
            p for p in activity
            if p.get("created_at") and
               datetime.datetime.fromisoformat(
                   p["created_at"].replace("Z", "+00:00")
               ) >= cutoff
        ]
        founder["linkedin_posts_last_30d"] = len(recent)

    # — 4) company follower count (if we have a LinkedIn company URL)
    comp_url = (
        data.get("team", {})
            .get("company_overview", {})
            .get("url")
        or None
    )
    if comp_url:
        comp_resp = requests.post(
            "https://api.brightdata.com/linkedin/company",
            headers=headers,
            json={"url": comp_url},
            timeout=30
        )
        data["company_followers"] = safe_json(comp_resp, "company").get("numFollowers")

    return data



# -----------------------------
# 3. Main Pipeline
# -----------------------------

def main():
    pdf_path = "./airbnb.pdf"  # TODO: parameterize

    #structured = structure_pdf_with_assistant(pdf_path)
    structured = {
        "company_name": "Airbnb",
        "team": {
            "founders": [
                {"name": "Brian Chesky", "background": "Industrial Design"},
                {"name": "Joe Gebbia", "background": "Product Design"},
                {"name": "Nathan Blecharczyk", "background": "Computer Science"}
            ],
            "team_strength": "Strong multidisciplinary team with design and technical expertise",
            "network_strength": "Leverage existing networks for rapid expansion"
        },
        "market": {
            "TAM": "150 million short-term stays annually",
            "SAM": "15 million potential customers in major cities",
            "SOM": "2 million target customers acquired",
            "growth_rate": "Growing at a significant rate as the market matures"
        },
        "product": {
            "stage": "Launched and operating",
            "USP": "Affordable, personal accommodations; enabling people to monetize extra space",
            "customer_acquisition": "Online marketing, partnerships with local events, and word-of-mouth"
        },
        "traction": {
            "revenue_growth": {"MRR": "$200,000", "ARR": "$2.4 million"},
            "user_growth": "Increasing user growth month over month",
            "engagement": "High engagement with returning users",
            "customer_validation": {
                "testimonials": [
                    "'AirBed&Breakfast freaking rocks!' - User Review",
                    "‘A complete success. It is easy to use and it made me money.’ - User Review"
                ],
                "churn": "Low churn rate due to customer satisfaction",
                "NPS": "Net Promoter Score above industry average"
            }
        },
        "funding": {
            "stage": "Series A",
            "amount": "$500,000",
            "cap_table_strength": "Diverse with strong lead investors",
            "investors_on_board": [
                {"name": "Sequoia Capital", "type": "Venture Capital"},
                {"name": "Y Combinator", "type": "Accelerator"}
            ]
        },
        "financial_efficiency": {
            "burn_rate": "$100,000 monthly",
            "CAC_vs_LTV": "Sustainable with a growing LTV/CAC ratio",
            "unit_economics": "High margin per booking"
        },
        "miscellaneous": {
            "regulatory_risk": "Moderate risk due to evolving local laws",
            "geographic_focus": "Global with focus on major urban centers",
            "timing_fad_risk": "Low risk as platform adoption grows"
        }
    }

    enriched = enrich_with_linkedin(structured)

    # TODO: metric calculations
    enriched["metrics"] = {}

    out = "./output.json"
    with open(out, "w") as f:
        json.dump(enriched, f, indent=2)
    print(f"Pipeline complete. Output written to {out}")

if __name__ == "__main__":
    main()


