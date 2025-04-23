import json
import requests
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")  # TODO: set your OpenAI API key securely

# -----------------------------
# 1. Structuring PDF via ChatGPT
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
    "customer_acquisition": string
  },
  "traction": {
    "revenue_growth": {"MRR": string, "ARR": string},
    "user_growth": string,
    "engagement": string,
    "customer_validation": {
      "testimonials": [string],
      "churn": string,
      "NPS": string
    }
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

def structure_pdf_with_chatgpt(pdf_path: str) -> dict:
    system_msg = {"role": "system", "content": "You extract structured data from pitch-deck PDFs into a precise JSON schema."}

    with open(pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    user_msg = {"role": "user", "content": f"{JSON_SCHEMA_PROMPT}\n\nExtract structured data directly from the provided pitchdeck PDF."}

    resp = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[system_msg, user_msg],
        temperature=0,
        files=[("pitchdeck.pdf", pdf_bytes)]
    )

    content = resp.choices[0].message.content.strip()
    return json.loads(content)

# -----------------------------
# 2. Enrich with LinkedIn Data via BrightData API
# -----------------------------
def enrich_with_linkedin(data: dict, api_key: str) -> dict:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Company enrichment by founder names
    enriched_founders = []
    for founder in data["team"]["founders"]:
        resp = requests.post(
            "https://api.brightdata.com/linkedin/profile",
            headers=headers,
            json={"name": founder["name"]}
        )
        founder["linkedin_profile_data"] = resp.json()
        enriched_founders.append(founder)
    data["team"]["founders"] = enriched_founders

    return data

# -----------------------------
# 3. Main Pipeline
# -----------------------------
def main():
    pdf_path = "./pitchdeck.pdf"  # TODO: Replace with actual file path or input mechanism
    brightdata_api_key = "YOUR_BRIGHTDATA_API_KEY"  # TODO: Securely load from env or config

    structured_data = structure_pdf_with_chatgpt(pdf_path)
    enriched_data = enrich_with_linkedin(structured_data, brightdata_api_key)

    # TODO: Define and implement scoring logic and data enrichment using proposed tools
    enriched_data["metrics"] = {}

    output_path = "./output.json"
    with open(output_path, "w") as f:
        json.dump(enriched_data, f, indent=2)

    print(f"Pipeline complete. Output written to {output_path}")

if __name__ == "__main__":
    main()


