import json
import os
import time
from dotenv import load_dotenv
import requests
from openai import OpenAI
import datetime
import copy
import re
from AnalyzeTrends import add_google_trend_score
from evaluator_final import evaluate as evaluate_metrics

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
            "Make sure your response is valid JSON without any markdown formatting or backticks. "
            "Ensure the following rules are respected: "
            "1. 'growth_rate' must be a real number formatted as a string (e.g., '3.75'). "
            "2. 'geographic_focus' must explicitly mention the country where the startup is based. "
            "3. The structure of the response must exactly match the schema provided by the user. "
            "4. Do not add additional fields not present in the schema. "
            "5. The Pitchdeck you are receiving is biased towards the company that created it. Please try to be objective when filling the JSON"
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
def is_company_match(profile, target_name):
    company = profile.get("current_company", {})
    return company and company.get("name", "").strip().lower() == target_name

def profile_match_score(profile, company_name, first, last):
    score = 0
    if is_company_match(profile, company_name):
        score += 3
    if profile.get("full_name", "").lower() == f"{first} {last}".lower():
        score += 2

    experience = profile.get("experience")
    if isinstance(experience, list):
        if any(exp.get("company", "").lower() == company_name for exp in experience):
            score += 1

    return score


# ── enrichment main ───────────────────────────────────────────────────────────
def is_company_match(profile, target_name):
    company = profile.get("current_company", {})
    return company and company.get("name", "").strip().lower() == target_name

def profile_match_score(profile, company_name, first, last):
    score = 0
    if is_company_match(profile, company_name):
        score += 3
    if profile.get("full_name", "").lower() == f"{first} {last}".lower():
        score += 2
    experience = profile.get("experience")
    if isinstance(experience, list):
        if any(exp.get("company", "").lower() == company_name for exp in experience):
            score += 1
    return score

def enrich_with_linkedin(data: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    DATASET_ID = "gd_l1viktl72bvl7bjuj0"
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

        # Trigger Bright Data job
        trigger_url = (
            "https://api.brightdata.com/datasets/v3/trigger"
            f"?dataset_id={DATASET_ID}&include_errors=true&type=discover_new&discover_by=name"
        )
        trig = requests.post(trigger_url, headers=headers,
                             json=[{"first_name": first, "last_name": last}],
                             timeout=60)
        if not trig.ok:
            print(f"[ERROR] trigger failed for {founder['name']}: {trig.text}")
            continue

        snapshot_id = safe_json(trig, f"trigger {founder['name']}").get("snapshot_id")
        if not snapshot_id:
            print(f"[WARN] no snapshot_id for {founder['name']}")
            continue

        try:
            profiles = fetch_snapshot(snapshot_id, max_wait_sec=300)
        except Exception as e:
            print(f"[ERROR] snapshot fetch failed for {founder['name']}: {e}")
            continue

        # Score profiles
        # Score all profiles
        scored_profiles = [
            (profile_match_score(p, company_name, first, last), p)
            for p in profiles
        ]

        if scored_profiles:
            # Always select the best scoring profile — even if score is low
            best_score, prof = max(scored_profiles, key=lambda sp: sp[0])
            if best_score <= 0:
                print(f"[WARN] No confident match found for {founder['name']}, falling back to highest followers")
            else:
                print(f"[INFO] Selected profile {prof.get('url')} with score {best_score}")

            founder["university"] = (
                    prof.get("educations_details")
                    or (prof.get("education") or [{}])[0].get("title")
            )
            founder["network_strength"] = prof.get("connections")
            founder["Followers"] = prof.get("followers")
            founder["degree"] = prof.get("degree")
            founder["age"] = prof.get("age")
            founder["gender"] = prof.get("gender")
            experience = prof.get("experience") or []
            founder["previous_employments"] = [
                {
                    "company": e.get("company"),
                    "title": e.get("title"),
                    "start": e.get("start_date"),
                    "end": e.get("end_date"),
                }
                for e in experience if e.get("company") and e.get("title")
            ]
            activity = prof.get("activity") or prof.get("posts") or []
            cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30)
            recent = [
                p for p in activity
                if p.get("created_at") and
                   datetime.datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) >= cutoff
            ]
            founder["linkedin_posts_last_30d"] = len(recent)
        else:
            # No profiles at all
            print(f"[WARN] No profiles found for {founder['name']}")
            founder["university"] = None
            founder["degree"] = None
            founder["network_strength"] = None
            founder["age"] = None
            founder["gender"] = None
            founder["previous_employments"] = []
            founder["linkedin_posts_last_30d"] = None

    comp_url = data.get("team", {}).get("company_overview", {}).get("url")
    if comp_url:
        comp_resp = requests.post(
            "https://api.brightdata.com/linkedin/company",
            headers=headers,
            json={"url": comp_url},
            timeout=30
        )
        data["company_followers"] = safe_json(comp_resp, "company").get("numFollowers")

    return data


def refine_with_chatgpt_holes(data: dict) -> dict:
    """
    Calls ChatGPT to fill any nulls or empty previous_employments in our JSON,
    preserving the existing structure exactly—and then tags each filled field
    with a "<field>_source": "chatgpt" marker for manual review.
    """
    # 1) Keep a copy of the original
    original = copy.deepcopy(data)

    # 2) Build and send the ChatGPT prompt (unchanged)
    schema = """
You will be given a JSON object describing a startup. Whenever a field is null
or previous_employments is an empty list, you must fill in a plausible value
that matches the existing format. Do not add new keys or remove existing ones. For `previous_employments`, use this format: {
    "company": "All Star Flooring",
    "title": "Co-Owner",
    "start": "Aug 2014",
    "end": "Present"
  },
Return ONLY the completed JSON.
"""
    messages = [
        {"role": "system", "content": "You are a JSON-refinement assistant."},
        {"role": "user", "content": f"{schema}\n\nHere is the JSON to fix:\n```json\n{json.dumps(data, indent=2)}\n```"}
    ]
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.strip("```json").strip("```").strip()
    refined = json.loads(text)

    # 3) Recursively compare and tag any filled fields
    def annotate(ref_node, orig_node, parent_key=None):
        # Dict case
        if isinstance(ref_node, dict) and isinstance(orig_node, dict):
            # iterate over a static list of keys
            for key in list(ref_node.keys()):
                val = ref_node[key]
                orig_val = orig_node.get(key)

                # Recurse first
                if isinstance(val, dict):
                    annotate(val, orig_val or {}, key)
                elif isinstance(val, list):
                    # tag empty→filled previous_employments
                    if key == "previous_employments" and not orig_val and val:
                        ref_node[f"{key}_source"] = "chatgpt"
                    # recurse into list items
                    for idx, item in enumerate(val):
                        orig_item = {}
                        if isinstance(orig_val, list) and idx < len(orig_val):
                            orig_item = orig_val[idx] or {}
                        if isinstance(item, dict):
                            annotate(item, orig_item, key)
                else:
                    # tag scalar fields that were null/empty but now have content
                    if orig_val in (None, [], "") and val not in (None, [], ""):
                        ref_node[f"{key}_source"] = "chatgpt"

        # List at root or nested under a non-dict key
        elif isinstance(ref_node, list) and isinstance(orig_node, list):
            for idx, item in enumerate(ref_node):
                orig_item = orig_node[idx] if idx < len(orig_node) else {}
                if isinstance(item, dict):
                    annotate(item, orig_item, parent_key)

    annotate(refined, original)
    return refined


# -----------------------------
# 3. Main Pipeline
# -----------------------------

def main(pdf_path=None):
    # pdf_path = os.path.join(os.path.dirname(__file__), "Tinder.pdf")

    # Define cache directory and output path
    os.makedirs("./PreviouslyCalculatedSlidedecks", exist_ok=True)
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    cached_path = os.path.join("PreviouslyCalculatedSlidedecks", f"{filename}.json")

    # 🔁 Return cached version if available
    if os.path.exists(cached_path):
        print(f"📂 Cached JSON found for {filename}, loading from {cached_path}")
        with open(cached_path, "r") as f:
            return json.load(f)

    # 🧠 Run full pipeline
    print(f"🔄 Processing new pitch deck: {pdf_path}")
    structured = structure_pdf_with_assistant(pdf_path)
    enriched = enrich_with_linkedin(structured)
    refined = refine_with_chatgpt_holes(enriched)

    company_name = refined.get("company_name", "Unknown")
    refined = add_google_trend_score(refined, company_name)

    refined["metrics"] = evaluate_metrics(refined)

    # 💾 Save result to cache directory
    with open(cached_path, "w") as f:
        json.dump(refined, f, indent=2)
    print(f"✅ Output written to {cached_path}")

    return refined


if __name__ == "__main__":
    main()


