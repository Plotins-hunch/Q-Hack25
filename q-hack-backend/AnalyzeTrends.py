import os
import json
import time
import random
from pytrends.request import TrendReq


PROXIES = [
    'http://34.123.12.43:3128',
    'http://51.158.123.35:8811',
    'http://103.216.82.50:6666',
    # Add more if available
]

def safe_trend_request(pytrends, keyword, retries=1):
    for attempt in range(retries):
        try:
            pytrends.build_payload([keyword], timeframe='today 12-m')
            interest_df = pytrends.interest_over_time()
            return interest_df
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = random.randint(15, 45)
                print(f"⚠️ [429 Retry] Too many requests. Retrying in {wait}s... (Attempt {attempt+2}/{retries})")
                time.sleep(wait)
            else:
                raise e

def get_pytrends_with_proxies():
    for proxy in PROXIES:
        try:
            print(f"🧭 [Proxy] Attempting proxy: {proxy}")
            pytrends = TrendReq(proxies=[proxy], timeout=(2, 5))
            # Test request
            pytrends.build_payload(['test'], timeframe='now 1-d')
            pytrends.interest_over_time()
            print("✅ [Proxy] Proxy is functional.")
            return pytrends
        except Exception as e:
            print(f"❌ [Proxy Error] Proxy failed: {proxy} — {e}")
            continue
    print("⚠️ [Proxy Fallback] All proxies failed. Proceeding without proxy.")
    return TrendReq(timeout=(2, 5))

def add_google_trend_score(data: dict, filename: str) -> dict:
    print("\n📊 [Trend Analysis] Starting Google Trends enrichment...")

    # Step 1: Extract company name
    company_name = os.path.splitext(os.path.basename(filename))[0].capitalize()
    print(f"🔍 [Debug] Extracted company name from filename: {company_name}")

    # Step 2: Initialize Pytrends (with fallback proxy logic)
    try:
        pytrends = get_pytrends_with_proxies()
    except Exception as e:
        print(f"❌ [Error] Could not initialize Pytrends session: {e}")
        return data

    # Step 3: Fetch trend data
    try:
        interest_df = safe_trend_request(pytrends, company_name)
        if interest_df.empty:
            print(f"⚠️ [Warning] No trend data found for {company_name}.")
            avg_score = 0
        else:
            avg_score = int(interest_df[company_name].mean())
            print(f"📊 [Success] Average trend score for {company_name}: {avg_score}")
    except Exception as e:
        print(f"❌ [Error] Failed to retrieve trend data: {e}")
        avg_score = 0

    # Step 4: Insert into JSON
    data.setdefault("traction", {})["google_trend_score"] = avg_score
    print("✅ [Debug] Trend score added to JSON data.")

    return data

