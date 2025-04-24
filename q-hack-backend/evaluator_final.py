import os
import json
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
import re
import sys


# Function to load the JSON data
def get_json(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return {}


# Function to load all CSV data
def _load_all_csv_data():
    csv_dir = "resources"
    csv_files = {
        'countries': 'countries.csv',
        'degrees': 'degrees.csv',
        'fortune500': 'fortune500.csv',
        'funding': 'funding.csv',
        'hardest_companies': 'hardest_companies.csv',
        'industries': 'industries.csv',
        'investors': 'investors.csv',
        'productstages': 'productstages.csv',
        'universities': 'universities.csv'
    }

    data = {}
    for key, filename in csv_files.items():
        try:
            filepath = os.path.join(csv_dir, filename)
            if key == 'countries':
                data[key] = pd.read_csv(filepath, sep=';', encoding='utf-8')
            else:
                data[key] = pd.read_csv(filepath, sep=';', encoding='utf-8')
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            data[key] = pd.DataFrame()

    return data


# Initialize NLTK for VADER
def initialize_nltk():
    try:
        nltk.download('vader_lexicon', quiet=True)
        return True
    except Exception as e:
        print(f"Error downloading NLTK resources: {e}")
        return False


# FinBERT sentiment analysis class
class FinBERT:
    def __init__(self):
        try:
            # Load FinBERT model and tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            self.labels = ["negative", "neutral", "positive"]
            self.initialized = True
        except Exception as e:
            print(f"Error initializing FinBERT: {e}")
            self.initialized = False

    def sentiment(self, text):
        if not self.initialized or not text or not isinstance(text, str):
            return 0.5

        try:
            # Truncate text if it's too long
            max_length = self.tokenizer.model_max_length
            if len(text) > max_length:
                text = text[:max_length]

            # Tokenize and get sentiment
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)

            # Get probabilities with softmax
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)

            # Calculate sentiment score (positive - negative + neutral/2)
            neg_score = probabilities[0][0].item()
            neu_score = probabilities[0][1].item()
            pos_score = probabilities[0][2].item()

            # Convert to 0-1 scale (0 = negative, 1 = positive)
            sentiment_score = pos_score - neg_score + (neu_score / 2)
            normalized_score = (sentiment_score + 1) / 2  # Convert from [-1,1] to [0,1]

            return max(0.0, min(1.0, normalized_score))  # Clamp between 0 and 1

        except Exception as e:
            print(f"Error analyzing sentiment with FinBERT: {e}")
            return 0.5


# FinBERT sentiment function
def finbert_sentiment(text):
    # Lazily initialize the model
    if not hasattr(finbert_sentiment, "model"):
        try:
            finbert_sentiment.model = FinBERT()
        except Exception as e:
            print(f"Failed to initialize FinBERT: {e}")
            # Fallback to simple sentiment
            positive_words = ['innovative', 'growth', 'profitable', 'success', 'strong',
                              'efficient', 'strategic', 'favorable', 'positive', 'excellent']
            negative_words = ['risky', 'failure', 'loss', 'weak', 'inefficient',
                              'declining', 'unfavorable', 'negative', 'poor']

            if not text or not isinstance(text, str):
                return 0.5

            text = text.lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            total = pos_count + neg_count
            if total == 0:
                return 0.5
            return (pos_count / total) * 0.8 + 0.2

    # Use the model
    if hasattr(finbert_sentiment, "model") and finbert_sentiment.model.initialized:
        return finbert_sentiment.model.sentiment(text)
    else:
        # Fallback simple sentiment
        if not text or not isinstance(text, str):
            return 0.5

        positive_words = ['innovative', 'growth', 'profitable', 'success', 'strong',
                          'efficient', 'strategic', 'favorable', 'positive', 'excellent']
        negative_words = ['risky', 'failure', 'loss', 'weak', 'inefficient',
                          'declining', 'unfavorable', 'negative', 'poor']

        text = text.lower()
        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)
        total = pos_count + neg_count
        if total == 0:
            return 0.5
        return (pos_count / total) * 0.8 + 0.2


# Convert numeric values to scores
def convert_to_score(value, min_val=0, max_val=100, default=50):
    if value is None or not isinstance(value, (int, float, str)):
        return default

    if isinstance(value, str):
        # Try to extract numeric value from strings like "$10 million"
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, value)
        if matches:
            value = float(matches[0])
        else:
            return default

    # Normalize to 0-100 scale
    score = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, score))


# Evaluate founder age
def eval_founder_age(founder_age):
    if founder_age is None:
        return 50

    try:
        age = int(founder_age)
        if 20 <= age <= 30:
            return 100
        elif 30 < age <= 40:
            return 80
        elif 40 < age <= 50:
            return 60
        else:
            return 40
    except:
        return 50


# Evaluate founder network strength
def eval_founder_network_strength(founder_network_strength):
    if founder_network_strength is None:
        return 50

    try:
        strength = int(founder_network_strength)
        return convert_to_score(strength, 0, 1000)
    except:
        return 50


# Evaluate team metrics
def evaluate_team(input_json, input_csvs):
    team_score = 0
    factors = 0

    # Initialize VADER for sentiment analysis
    try:
        vader = SentimentIntensityAnalyzer()
    except Exception as e:
        print(f"VADER not available: {e}. Using simplified sentiment.")
        vader = None

    # Process founders
    founders = input_json.get('team', {}).get('founders', [])

    # Founder count (2-3 is good)
    founder_count = len(founders)
    if founder_count == 0:
        founder_count_score = 0
    elif founder_count == 1:
        founder_count_score = 60
    elif 2 <= founder_count <= 3:
        founder_count_score = 100
    else:
        founder_count_score = 70
    team_score += founder_count_score
    factors += 1

    # Process each founder
    for founder in founders:
        # Background check
        background = founder.get('background', '')
        background_score = 50
        if background:
            found_industry = False
            for industry in input_csvs['industries']['keyword']:
                if str(industry).lower() in background.lower():
                    found_industry = True
                    break
            background_score = 90 if found_industry else 40
        team_score += background_score
        factors += 1

        # University check
        university = founder.get('university', '')
        university_score = 50
        if university:
            for uni in input_csvs['universities']['institution']:
                if str(uni).lower() in university.lower():
                    university_score = 90
                    break
        team_score += university_score
        factors += 1

        # Degree check
        degree = founder.get('degree', '')
        degree_score = 50
        if degree:
            for deg in input_csvs['degrees']['full_name']:
                if str(deg).lower() in degree.lower():
                    degree_score = 90
                    break
        team_score += degree_score
        factors += 1

        # Network strength
        network_strength = founder.get('network_strength')
        network_score = eval_founder_network_strength(network_strength)
        team_score += network_score
        factors += 1

        # Age check
        age = founder.get('age')
        age_score = eval_founder_age(age)
        team_score += age_score
        factors += 1

        # Gender check
        gender = founder.get('gender', '').lower()
        gender_score = 100 if gender == 'female' else 50
        team_score += gender_score
        factors += 1

        # Previous employments
        employments = founder.get('previous_employments', [])
        employment_score = 50
        if employments:
            hardest_companies = set(input_csvs['hardest_companies']['company'].str.lower())
            emp_years = 0
            premium_company = False

            for emp in employments:
                start = emp.get('start', '')
                end = emp.get('end', '')
                company = emp.get('company', '').lower()

                # Check if in hard companies list
                if company in hardest_companies:
                    premium_company = True

                # Estimate years (simplified)
                if start and end and 'present' not in end.lower():
                    try:
                        start_year = int(re.search(r'\d{4}', start).group())
                        end_year = int(re.search(r'\d{4}', end).group())
                        emp_years += (end_year - start_year)
                    except:
                        emp_years += 1
                else:
                    emp_years += 2  # Default for ongoing employment

            if emp_years >= 10:
                employment_score = 100 if premium_company else 90
            elif emp_years >= 5:
                employment_score = 80 if premium_company else 70
            else:
                employment_score = 60 if premium_company else 50

        team_score += employment_score
        factors += 1

        # LinkedIn posts
        linkedin_posts = founder.get('linkedin_posts_last_30d', 0)
        posts_score = convert_to_score(linkedin_posts, 0, 20)
        team_score += posts_score
        factors += 1

    # Avoid division by zero
    if factors == 0:
        return 50

    return round(team_score / factors)


# Evaluate market metrics
def evaluate_market(input_json, input_csvs):
    market_data = input_json.get('market', {})
    market_score = 0
    factors = 0

    # TAM (Total Addressable Market)
    tam = market_data.get('TAM', '')
    tam_score = 50
    if tam:
        # Extract numeric value from string like "$27 billion"
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, tam)
        if matches:
            value = float(matches[0])
            tam_score = convert_to_score(value, 0, 100)

            # Adjust for billion/million
            if 'billion' in tam.lower():
                tam_score = min(100, tam_score * 1.5)
            elif 'million' in tam.lower():
                tam_score = tam_score * 0.8
    market_score += tam_score
    factors += 1

    # SAM (Serviceable Addressable Market)
    sam = market_data.get('SAM', '')
    sam_score = 50
    if sam:
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, sam)
        if matches:
            value = float(matches[0])
            sam_score = convert_to_score(value, 0, 50)

            if 'billion' in sam.lower():
                sam_score = min(100, sam_score * 1.5)
            elif 'million' in sam.lower():
                sam_score = sam_score * 0.9
    market_score += sam_score
    factors += 1

    # SOM (Serviceable Obtainable Market)
    som = market_data.get('SOM', '')
    som_score = 50
    if som:
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, som)
        if matches:
            value = float(matches[0])
            som_score = convert_to_score(value, 0, 20)

            if 'billion' in som.lower():
                som_score = 100
            elif 'million' in som.lower():
                som_score = min(100, som_score * 1.2)
    market_score += som_score
    factors += 1

    # Growth rate
    growth_rate = market_data.get('growth_rate', '')
    growth_score = 50
    if growth_rate:
        try:
            value = float(growth_rate)
            growth_score = convert_to_score(value, 0, 20)
        except:
            pass
    market_score += growth_score
    factors += 1

    if factors == 0:
        return 50

    return round(market_score / factors)


# Evaluate product metrics
def evaluate_product(input_json, input_csvs):
    product_data = input_json.get('product', {})
    product_score = 0
    factors = 0

    # Product stage
    stage = product_data.get('stage', '')
    stage_score = 50
    if stage:
        for index, row in input_csvs['productstages'].iterrows():
            if str(row['stage']).lower() in stage.lower():
                try:
                    stage_score = float(row['score'])
                except:
                    pass
                break
    product_score += stage_score
    factors += 1

    # USP (Unique Selling Proposition)
    usp = product_data.get('USP', '')
    usp_score = 50
    if usp:
        usp_score = finbert_sentiment(usp) * 100
    product_score += usp_score
    factors += 1

    # Customer acquisition
    acquisition = product_data.get('customer_acquisition', '')
    acquisition_score = 50
    if acquisition:
        acquisition_score = finbert_sentiment(acquisition) * 100
    product_score += acquisition_score
    factors += 1

    if factors == 0:
        return 50

    return round(product_score / factors)


# VADER wrapper class for sentiment analysis
class VADERSentiment:
    def __init__(self):
        try:
            self.analyzer = SentimentIntensityAnalyzer()
            self.initialized = True
        except Exception as e:
            print(f"Error initializing VADER: {e}")
            self.initialized = False

    def sentiment(self, text):
        if not self.initialized or not text or not isinstance(text, str):
            return 0.0

        try:
            sentiment_scores = self.analyzer.polarity_scores(text)
            # Return compound score normalized to 0-1 range
            return (sentiment_scores['compound'] + 1) / 2
        except Exception as e:
            print(f"Error analyzing sentiment with VADER: {e}")
            return 0.5


# Get VADER analyzer (singleton pattern)
def get_vader_analyzer():
    if not hasattr(get_vader_analyzer, "instance"):
        get_vader_analyzer.instance = VADERSentiment()
    return get_vader_analyzer.instance


# Evaluate traction metrics
def evaluate_traction(input_json, input_csvs):
    traction_data = input_json.get('traction', {})
    traction_score = 0
    factors = 0

    # Get VADER analyzer
    vader = get_vader_analyzer()

    # MRR (Monthly Recurring Revenue)
    revenue_growth = traction_data.get('revenue_growth', {})
    mrr = revenue_growth.get('MRR', '')
    mrr_score = 50
    if mrr:
        mrr_score = finbert_sentiment(mrr) * 100
    traction_score += mrr_score
    factors += 1

    # ARR (Annual Recurring Revenue)
    arr = revenue_growth.get('ARR', '')
    arr_score = 50
    if arr:
        arr_score = finbert_sentiment(arr) * 100
    traction_score += arr_score
    factors += 1

    # User growth
    user_growth = traction_data.get('user_growth', '')
    growth_score = 50
    if user_growth:
        growth_score = finbert_sentiment(user_growth) * 100
    traction_score += growth_score
    factors += 1

    # User engagement
    engagement = traction_data.get('engagement', '')
    engagement_score = 50
    if engagement and vader.initialized:
        engagement_score = vader.sentiment(engagement) * 100
    elif engagement:
        engagement_score = finbert_sentiment(engagement) * 100
    traction_score += engagement_score
    factors += 1

    # Customer validation
    validation = traction_data.get('customer_validation', {})

    # Churn
    churn = validation.get('churn', '')
    churn_score = 50
    if churn and vader.initialized:
        # For churn, lower is better, so we invert the score
        churn_score = 100 - (vader.sentiment(churn) * 100)
    elif churn:
        # Invert FinBERT score since lower churn is better
        churn_score = 100 - (finbert_sentiment(churn) * 100)
    traction_score += churn_score
    factors += 1

    # NPS (Net Promoter Score)
    nps = validation.get('NPS', '')
    nps_score = 50
    if nps:
        # Combine FinBERT and VADER for more robust analysis
        finbert_score = finbert_sentiment(nps) * 100

        if vader.initialized:
            vader_score = vader.sentiment(nps) * 100
            nps_score = (vader_score + finbert_score) / 2
        else:
            nps_score = finbert_score
    traction_score += nps_score
    factors += 1

    # Google trend score
    trend_score = traction_data.get('google_trend_score', 0)
    trend_quality = 50
    if trend_score == 100:
        trend_quality = 100
    elif trend_score > 0:
        trend_quality = 50 + (trend_score / 2)
    traction_score += trend_quality
    factors += 1

    if factors == 0:
        return 50

    return round(traction_score / factors)


# Evaluate funding metrics
def evaluate_funding(input_json, input_csvs):
    funding_data = input_json.get('funding', {})
    funding_score = 0
    factors = 0

    # Get VADER analyzer
    vader = get_vader_analyzer()

    # Funding stage
    stage = funding_data.get('stage', '')
    stage_score = 50
    if stage:
        for index, row in input_csvs['funding'].iterrows():
            if str(row['stage']).lower() in stage.lower():
                try:
                    stage_score = float(row['score'])
                except:
                    stage_score = float(row['stage_level']) * 20
                break
    funding_score += stage_score
    factors += 1

    # Funding amount
    amount = funding_data.get('amount', '')
    amount_score = 50
    if amount:
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, amount)
        if matches:
            value = float(matches[0])
            amount_score = convert_to_score(value, 0, 50)

            if 'billion' in amount.lower():
                amount_score = 100
            elif 'million' in amount.lower():
                amount_score = min(100, amount_score * 1.5)
    funding_score += amount_score
    factors += 1

    # Cap table strength
    cap_table = funding_data.get('cap_table_strength', '')
    cap_score = 50
    if cap_table:
        # Combine FinBERT and VADER
        finbert_score = finbert_sentiment(cap_table) * 100

        if vader.initialized:
            vader_score = vader.sentiment(cap_table) * 100
            cap_score = (vader_score + finbert_score) / 2
        else:
            cap_score = finbert_score
    funding_score += cap_score
    factors += 1

    # Investors
    investors = funding_data.get('investors_on_board', [])
    investor_score = 50

    if investors:
        investor_ranking = 0
        fortune_count = 0

        for investor in investors:
            investor_name = investor.get('name', '')

            # Check if in top investors list
            for index, row in input_csvs['investors'].iterrows():
                if str(row['investor_name']).lower() in investor_name.lower():
                    investor_ranking += 100 - min(99, int(row['investor_rank']))
                    break

            # Check if Fortune 500
            for index, row in input_csvs['fortune500'].iterrows():
                if str(row['name']).lower() in investor_name.lower():
                    fortune_count += 1
                    break

        # Calculate score based on investor quality
        if fortune_count > 0:
            investor_score = 90 + min(10, fortune_count)
        elif investor_ranking > 0:
            investor_score = min(100, 50 + (investor_ranking / 10))
        elif len(investors) > 2:
            investor_score = 70
        elif len(investors) > 0:
            investor_score = 60

    funding_score += investor_score
    factors += 1

    if factors == 0:
        return 50

    return round(funding_score / factors)


# Evaluate financial efficiency metrics
def evaluate_financial_efficiency(input_json, input_csvs):
    financial_data = input_json.get('financial_efficiency', {})
    financial_score = 0
    factors = 0

    # Burn rate
    burn_rate = financial_data.get('burn_rate', '')
    burn_score = 50
    if burn_rate:
        burn_score = finbert_sentiment(burn_rate) * 100
    financial_score += burn_score
    factors += 1

    # CAC vs LTV
    cac_ltv = financial_data.get('CAC_vs_LTV', '')
    cac_score = 50
    if cac_ltv:
        cac_score = finbert_sentiment(cac_ltv) * 100
    financial_score += cac_score
    factors += 1

    # Unit economics
    unit_econ = financial_data.get('unit_economics', '')
    unit_score = 50
    if unit_econ:
        unit_score = finbert_sentiment(unit_econ) * 100
    financial_score += unit_score
    factors += 1

    if factors == 0:
        return 50

    return round(financial_score / factors)


# Evaluate miscellaneous metrics
def evaluate_miscellaneous(input_json, input_csvs):
    misc_data = input_json.get('miscellaneous', {})
    misc_score = 0
    factors = 0

    # Geographic focus
    geographic = misc_data.get('geographic_focus', '')
    geo_score = 50
    if geographic:
        for index, row in input_csvs['countries'].iterrows():
            country_name = str(row.get('country_name', '')).lower()
            country_long = str(row.get('country_long_name', '')).lower()
            if country_name in geographic.lower() or country_long in geographic.lower():
                # Use corruption score as a proxy for market stability
                try:
                    geo_score = float(row['corruption_score']) if not pd.isna(row['corruption_score']) else 50
                except:
                    geo_score = 70 if 'united states' in geographic.lower() else 50
                break
    misc_score += geo_score
    factors += 1

    # Timing/fad risk
    timing_risk = misc_data.get('timing_fad_risk', '')
    timing_score = 50
    if timing_risk:
        # Invert the sentiment since lower risk is better
        timing_score = 100 - (finbert_sentiment(timing_risk) * 100)
    misc_score += timing_score
    factors += 1

    if factors == 0:
        return 50

    return round(misc_score / factors)


# Calculate overall unicorn score
def calculate_unicorn_score(scores):
    weights = {
        'Team': 0.25,
        'Market': 0.20,
        'Product': 0.15,
        'Traction': 0.15,
        'Funding': 0.10,
        'Financial Efficiency': 0.10,
        'Miscellaneous': 0.05
    }

    weighted_sum = sum(scores[key] * weights[key] for key in weights)
    return round(weighted_sum)


# Main evaluation function
def evaluate(filename):
    # Initialize NLTK for VADER
    initialize_nltk()

    # Load all CSV data
    csvs = _load_all_csv_data()

    # Load JSON parameters
    jsons = get_json(filename)

    # Print loaded data for debugging
    #print(jsons)

    # Calculate all metrics
    metrics = {
        "Team": evaluate_team(jsons, csvs),
        "Market": evaluate_market(jsons, csvs),
        "Product": evaluate_product(jsons, csvs),
        "Traction": evaluate_traction(jsons, csvs),
        "Funding": evaluate_funding(jsons, csvs),
        "Financial Efficiency": evaluate_financial_efficiency(jsons, csvs),
        "Miscellaneous": evaluate_miscellaneous(jsons, csvs)
    }

    # Calculate unicorn score
    metrics["UnicornScore"] = calculate_unicorn_score(metrics)

    return metrics


# Main function
if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = "startup_data.json"  # Default filename

    try:
        result = evaluate(filename)
        print(f"Evaluation complete. Results:")
        print(json.dumps({"metrics": result}, indent=2))

        # Save results to output file
        output_file = filename.replace(".json", "_evaluated.json")

        # Load original JSON to update with metrics
        with open(filename, 'r') as f:
            original_data = json.load(f)

        # Update metrics and save
        original_data["metrics"] = result
        with open(output_file, 'w') as f:
            json.dump(original_data, f, indent=2)

        print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error during evaluation: {e}")