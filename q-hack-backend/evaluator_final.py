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

try:
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    print("Vader not available")

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


# 7. Modify the age evaluation function to better value founders in their 30s-40s
def eval_founder_age(founder_age):
    if founder_age is None:
        return 60  # Increased default from 50

    try:
        age = int(founder_age)
        if 25 <= age <= 35:  # Broader prime range
            return 100
        elif 35 < age <= 45:  # Value experience more
            return 90  # Increased from 80
        elif 45 < age <= 55:  # Value experience more
            return 80  # Increased from 60
        elif 20 <= age < 25:  # Very young founders
            return 70  # New category
        else:
            return 60  # Increased from 40
    except:
        return 60  # Increased default from 50


# Evaluate founder network strength
def eval_founder_network_strength(founder_network_strength):
    if founder_network_strength is None:
        return 50

    try:
        strength = int(founder_network_strength)
        return convert_to_score(strength, 0, 1000)
    except:
        return 50


# 2. Improve the Team evaluation for known unicorns
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
        founder_count_score = 65  # Increased from 60
    elif 2 <= founder_count <= 3:
        founder_count_score = 100
    else:
        founder_count_score = 80  # Increased from 70
    team_score += founder_count_score
    factors += 1

    # Process each founder
    for founder in founders:
        # Background check - give higher score by default
        background = founder.get('background', '')
        background_score = 60  # Increased default from 50
        if background:
            found_industry = False
            for industry in input_csvs['industries']['keyword']:
                if str(industry).lower() in background.lower():
                    found_industry = True
                    break
            background_score = 95 if found_industry else 60  # Increased both values
        team_score += background_score
        factors += 1

        # University check - improved scoring
        university = founder.get('university', '')
        university_score = 60  # Increased default from 50
        if university:
            for uni in input_csvs['universities']['institution']:
                if str(uni).lower() in university.lower():
                    university_score = 95  # Increased from 90
                    break
        team_score += university_score
        factors += 1

        # Degree check - improved scoring
        degree = founder.get('degree', '')
        degree_score = 60  # Increased default from 50
        if degree:
            for deg in input_csvs['degrees']['full_name']:
                if str(deg).lower() in degree.lower():
                    degree_score = 95  # Increased from 90
                    break
        team_score += degree_score
        factors += 1

        # Network strength - keep as is
        network_strength = founder.get('network_strength')
        network_score = eval_founder_network_strength(network_strength)
        team_score += network_score
        factors += 1

        # Age check - adjusted to value experience more
        age = founder.get('age')
        age_score = eval_founder_age(age)
        team_score += age_score
        factors += 1

        # Previous employments - improved scoring
        employments = founder.get('previous_employments', [])
        employment_score = 60  # Increased default from 50
        if employments:
            hardest_companies = set(input_csvs['hardest_companies']['company'].str.lower())
            emp_years = 0
            premium_company = False

            for emp in employments:
                company = emp.get('company', '').lower()

                # Check if in hard companies list
                if company in hardest_companies:
                    premium_company = True
                    emp_years += 3  # Give extra weight to premium companies

                # Estimate years (simplified)
                start = emp.get('start', '')
                end = emp.get('end', '')
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
                employment_score = 100 if premium_company else 95
            elif emp_years >= 5:
                employment_score = 90 if premium_company else 80
            else:
                employment_score = 75 if premium_company else 65

        team_score += employment_score
        factors += 1

        # LinkedIn posts
        linkedin_posts = founder.get('linkedin_posts_last_30d', 0)
        posts_score = convert_to_score(linkedin_posts, 0, 20)
        team_score += posts_score
        factors += 1

    # Avoid division by zero
    if factors == 0:
        return 60  # Increased default from 50

    final_score = round(team_score / factors)

    # Apply a slight boost for complete team data
    if len(founders) >= 2 and factors > 5:
        final_score = min(100, final_score + 5)

    return final_score


# 3. Adjust market evaluation to better reflect market potential
def evaluate_market(input_json, input_csvs):
    market_data = input_json.get('market', {})
    market_score = 0
    factors = 0

    # TAM (Total Addressable Market) - adjusted scaling
    tam = market_data.get('TAM', '')
    tam_score = 60  # Increased default from 50
    if tam:
        # Extract numeric value from string like "$27 billion"
        number_pattern = r"[+-]?\d*\.?\d+"
        matches = re.findall(number_pattern, tam)
        if matches:
            value = float(matches[0])
            tam_score = convert_to_score(value, 0, 100)

            # Adjust for billion/million - increased multipliers
            if 'billion' in tam.lower():
                tam_score = min(100, tam_score * 1.8)  # Increased from 1.5
            elif 'million' in tam.lower():
                tam_score = tam_score * 0.9  # Increased from 0.8
    market_score += tam_score
    factors += 1

    # Growth rate - give higher importance
    growth_rate = market_data.get('growth_rate', '')
    growth_score = 60  # Increased default from 50
    if growth_rate:
        try:
            value = float(growth_rate)
            growth_score = convert_to_score(value, 0, 20)
            # Apply exponential scaling for high growth markets
            if value > 10:
                growth_score = min(100, growth_score * 1.5)
        except:
            pass
    # Add higher weight to growth rate
    market_score += growth_score * 1.5
    factors += 1.5  # Adjusted factor weight

    if factors == 0:
        return 60  # Increased default from 50

    return round(market_score / factors)


# 5. Improve evaluation of Product to better weight tangible features
def evaluate_product(input_json, input_csvs):
    product_data = input_json.get('product', {})
    product_score = 0
    factors = 0

    # Product stage - give higher weight
    stage = product_data.get('stage', '')
    stage_score = 60  # Increased default from 50
    if stage:
        for index, row in input_csvs['productstages'].iterrows():
            if str(row['stage']).lower() in stage.lower():
                try:
                    stage_score = float(row['score'])
                    # Give bonus for later stage products
                    if stage_score > 70:
                        stage_score = min(100, stage_score + 5)
                except:
                    pass
                break
    product_score += stage_score * 1.2  # Higher weight for product stage
    factors += 1.2

    # USP (Unique Selling Proposition)
    usp = product_data.get('USP', '')
    usp_score = 60  # Increased default from 50
    if usp:
        usp_score = finbert_sentiment(usp) * 100
    product_score += usp_score
    factors += 1

    # Customer acquisition
    acquisition = product_data.get('customer_acquisition', '')
    acquisition_score = 60  # Increased default from 50
    if acquisition:
        acquisition_score = finbert_sentiment(acquisition) * 100
    product_score += acquisition_score
    factors += 1

    if factors == 0:
        return 60  # Increased default from 50

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


# 6. Modify traction metrics evaluation to better recognize early signs of success
def evaluate_traction(input_json, input_csvs):
    traction_data = input_json.get('traction', {})
    traction_score = 0
    factors = 0

    # Get VADER analyzer
    vader = get_vader_analyzer()

    # User growth - give higher weight
    user_growth = traction_data.get('user_growth', '')
    growth_score = 60  # Increased default from 50
    if user_growth:
        growth_score = finbert_sentiment(user_growth) * 100
        # Give extra weight to positive user growth signals
        if growth_score > 70:
            growth_score = min(100, growth_score + 10)
    traction_score += growth_score * 1.3  # Higher weight for user growth
    factors += 1.3

    # User engagement
    engagement = traction_data.get('engagement', '')
    engagement_score = 60  # Increased default from 50
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
        # Give bonus for notable trend scores
        if trend_score > 50:
            trend_quality = min(100, trend_quality + 10)
    traction_score += trend_quality * 1.2  # Higher weight
    factors += 1.2

    if factors == 0:
        return 60  # Increased default from 50

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


# 4. Adjust financial efficiency to be less generous
def evaluate_financial_efficiency(input_json, input_csvs):
    financial_data = input_json.get('financial_efficiency', {})
    financial_score = 0
    factors = 0

    # Burn rate
    burn_rate = financial_data.get('burn_rate', '')
    burn_score = 50
    if burn_rate:
        raw_score = finbert_sentiment(burn_rate) * 100
        # Apply a more realistic curve - scale down high scores
        burn_score = min(90, raw_score * 0.9)
    financial_score += burn_score
    factors += 1

    # CAC vs LTV
    cac_ltv = financial_data.get('CAC_vs_LTV', '')
    cac_score = 50
    if cac_ltv:
        raw_score = finbert_sentiment(cac_ltv) * 100
        # Apply a more realistic curve - scale down high scores
        cac_score = min(90, raw_score * 0.9)
    financial_score += cac_score
    factors += 1

    # Unit economics
    unit_econ = financial_data.get('unit_economics', '')
    unit_score = 50
    if unit_econ:
        raw_score = finbert_sentiment(unit_econ) * 100
        # Apply a more realistic curve - scale down high scores
        unit_score = min(90, raw_score * 0.9)
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
# Modifications to improve evaluation metrics

# 1. Adjust the weights in calculate_unicorn_score to better reflect the importance of each factor
def calculate_unicorn_score(scores):
    weights = {
        'Team': 0.30,  # Increased from 0.25
        'Market': 0.20,  # Kept the same
        'Product': 0.18,  # Increased from 0.15
        'Traction': 0.15,  # Kept the same
        'Funding': 0.08,  # Decreased from 0.10
        'Financial Efficiency': 0.07,  # Decreased from 0.10
        'Miscellaneous': 0.02  # Decreased from 0.05
    }

    weighted_sum = sum(scores[key] * weights[key] for key in weights)

    # Apply a slight curve to push strong startups higher
    if weighted_sum > 60:
        weighted_sum = weighted_sum + (weighted_sum - 60) * 0.15

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
        #output_file = filename.replace(".json", "_evaluated.json")

        # Load original JSON to update with metrics
        with open(filename, 'r') as f:
            original_data = json.load(f)

        # Update metrics and save
        #original_data["metrics"] = result
        #with open(output_file, 'w') as f:
        #    json.dump(original_data, f, indent=2)

        #print(f"Results saved to {output_file}")

    except Exception as e:
        print(f"Error during evaluation: {e}")