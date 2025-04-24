# Q-Hack25

Q-Hack25 is a prototype platform designed to automate the evaluation of startup pitch decks. It extracts key metrics from PDF presentations, enriches them with external data sources, and computes scores across various dimensions to assist in investment decision-making.

## 🚀 Features

- **Automated PDF Parsing**: Extracts structured information from startup pitch decks.
- **Data Enrichment**: Integrates data from APIs such as Crunchbase, LinkedIn, and PitchBook.
- **Metric Computation**: Calculates scores for:
  - **Team**: Founders' backgrounds, team composition, network strength.
  - **Market**: TAM, SAM, SOM, growth rates.
  - **Product**: Development stage, unique selling proposition, customer acquisition strategies.
  - **Traction**: Revenue growth (MRR, ARR), user engagement, customer validation (testimonials, churn, NPS).
  - **Funding**: Funding stage and amount, cap table strength, investors involved.
  - **Financial Efficiency**: Burn rate, CAC vs. LTV, unit economics.
  - **Miscellaneous**: Regulatory risks, geographic focus, timing/fad risks.
- **Scoring Framework**: Utilizes machine learning models (e.g., scikit-learn, XGBoost) and Bayesian methods for evaluation.
- **User Interface**: Frontend dashboard for visualizing scores and insights.
- **Automated Notifications**: Sends emails when specific data points are unavailable or require attention.

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI
- **Frontend**: React.js
- **Data Processing**: pandas, numpy
- **API Calls**: requests, aiohttp
- **Web Scraping**: BeautifulSoup, Scrapy
- **Machine Learning**: scikit-learn, XGBoost

## 📂 Repository Structure

- `q-hack-backend/`: Backend services and API endpoints.
- `qhack-frontend/`: Frontend React application.
- `email_module/`: Handles automated email notifications.
- `logs/`: Logging and monitoring data.
- `requirements.txt`: Python dependencies.
- `README`: Project overview and documentation.

## 📈 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Plotins-hunch/Q-Hack25.git
   cd Q-Hack25
   ```

2. **Set up the backend**:
   ```bash
   cd q-hack-backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

3. **Set up the frontend**:
   ```bash
   cd ../qhack-frontend
   npm install
   npm run serve
   ```

4. **Access the application**:
   - Frontend: `http://localhost:8080`
   - Backend API: `http://localhost:8000`

## 📬 Contact

For questions or collaboration inquiries, please contact the repository maintainer through GitHub.


# Advanced Startup Evaluation: Our Technical Approach and Metrics

Our startup evaluation tool employs sophisticated natural language processing, sentiment analysis, and data processing techniques to deliver objective assessments of early-stage companies. By combining multiple data sources with advanced analytical methods, we provide comprehensive insights that go beyond traditional evaluation approaches.

## Technical Framework and Tools

### Metrics
## Natural Language Processing & Sentiment Analysis

Our system uses two complementary sentiment analysis engines to evaluate unstructured text data:

1. **FinBERT Model**: We leverage the ProsusAI/finbert model, a specialized BERT variant fine-tuned on financial text. This transformer-based architecture allows us to accurately assess sentiment in domain-specific language common in startup descriptions, business plans, and market analyses.

2. **VADER (Valence Aware Dictionary and sEntiment Reasoner)**: As a complementary approach, we employ NLTK's VADER sentiment analyzer, which is particularly effective at social media content and informal communications, helping evaluate founder messaging and public perception.

3. **Fallback Sentiment Analysis**: Our system includes a rule-based fallback mechanism that analyzes the presence of positive and negative keywords when advanced NLP models are unavailable.

### Data Processing Framework

Our evaluation pipeline processes multiple data types:

- **JSON Data**: Startup profiles structured as nested JSON objects containing qualitative and quantitative data
- **CSV Databases**: Reference datasets for benchmarking and classification including:
  - Fortune 500 companies
  - Top universities worldwide
  - Industry taxonomies
  - Country economic indicators
  - Investor rankings
  - Hard-to-get-into companies
  - Product stage classifications
  - Educational degree taxonomies

### Numeric Normalization and Scoring

We employ sophisticated normalization techniques to ensure consistent scoring across metrics:

- **Range Normalization**: Converting diverse metrics to standardized 0-100 scores
- **Contextual Scaling**: Applying domain-specific multipliers (e.g., recognizing billion-dollar markets)
- **Score Clamping**: Ensuring all values fall within appropriate bounds
- **Weighted Aggregation**: Combining multiple sub-metrics with calibrated importance factors

## Core Evaluation Metrics

### Team Metrics
- **Founder Count Analysis**: Optimal team composition assessment
- **Background Industry Matching**: NLP-based matching of founder experience with target industry
- **University Prestige Verification**: Cross-referencing with top university database
- **Degree Relevance Assessment**: Analysis of educational background appropriateness
- **Network Strength Quantification**: Numerical evaluation of professional network reach
- **Age Optimality Analysis**: Age pattern matching against success patterns
- **Gender Diversity Measurement**: Team composition diversity scoring
- **Employment History Analysis**:
  - Duration calculation using regex pattern matching for date extraction
  - Premium company identification through database cross-referencing
- **LinkedIn Activity Measurement**: Social media presence and thought leadership evaluation

### Market Metrics
- **TAM/SAM/SOM Analysis**: Market size extraction using regex pattern matching
- **Market Size Classification**: Identification of billion/million-dollar markets with corresponding multipliers
- **Growth Rate Quantification**: Conversion of percentage text to normalized scores

### Product Metrics
- **Development Stage Classification**: Matching product maturity against reference database
- **USP Sentiment Analysis**: Using FinBERT to evaluate unique selling proposition strength
- **Customer Acquisition Sentiment Analysis**: Deep analysis of go-to-market strategy viability

### Traction Metrics
- **Revenue Growth Sentiment Analysis**: NLP evaluation of MRR/ARR descriptions
- **User Growth Analysis**: Combined VADER and FinBERT sentiment scoring
- **Engagement Metric Processing**: Multi-model sentiment analysis of user engagement descriptions
- **Churn Rate Sentiment Analysis**: Inverted sentiment scoring (lower is better)
- **NPS Sentiment Evaluation**: Combined model approach to Net Promoter Score assessment
- **Google Trend Score Processing**: Quantitative analysis of public interest metrics

### Funding Metrics
- **Funding Stage Classification**: Database matching of funding rounds against reference models
- **Amount Extraction and Normalization**: Regex-based monetary value extraction
- **Cap Table Sentiment Analysis**: Multi-model evaluation of ownership structure
- **Investor Quality Assessment**:
  - Top investor database cross-referencing
  - Fortune 500 investor identification
  - Investor quantity and diversity evaluation

### Financial Efficiency Metrics
- **Burn Rate Sentiment Analysis**: FinBERT evaluation of capital efficiency
- **CAC vs LTV Analysis**: Customer acquisition cost relative to lifetime value scoring
- **Unit Economics Sentiment Analysis**: Business model viability assessment

### Miscellaneous Metrics
- **Geographic Focus Analysis**: Country database matching with corruption score extraction
- **Timing/Fad Risk Assessment**: Inverted sentiment analysis of trend sustainability

## Weighted Score Aggregation

Our UnicornScore employs a carefully calibrated weighting system:
- Team (30%)
- Market (20%)
- Product (18%)
- Traction (15%)
- Funding (8%)
- Financial Efficiency (7%)
- Miscellaneous (2%)

Additionally, we apply a non-linear scoring curve that better differentiates high-potential startups, applying a 15% bonus to base scores above 60.

## Implementation Technologies

Built using Python's data science ecosystem:
- **pandas**: For database management and data manipulation
- **NumPy**: For numerical operations and array processing
- **NLTK**: For basic NLP functionality and VADER sentiment analysis
- **PyTorch**: For deep learning-based text analysis via the FinBERT model
- **Hugging Face Transformers**: For accessing and implementing state-of-the-art NLP models
- **Regular Expressions**: For sophisticated pattern matching and text extraction

This comprehensive technical approach combines multiple data sources, advanced NLP techniques, and carefully calibrated scoring systems to produce nuanced startup evaluations that can identify potential unicorns with greater accuracy than traditional methods.

