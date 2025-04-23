#!/usr/bin/env python3
"""
Test script for the chat module.
Run this from the root directory with: python chat_test.py
"""

import json
import asyncio
import os
import logging
from dotenv import load_dotenv

# Disable file logging completely for testing
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])

# Import query parser directly
from chat_module.services.query_parser import QueryParser

# Override LLMService before importing ChatService
class MockLLMService:
    async def process_complex_query(self, query, company_data, conversation_history=None):
        return {
            "answer": f"This is a mock LLM response for: {query}",
            "model_used": "mock-model",
            "confidence": 0.9
        }

# Now patch the module to inject our mock
import chat_module.services.llm_service
chat_module.services.llm_service.LLMService = MockLLMService

# Now import ChatService which will use our mock
from chat_module.services.chat_service import ChatService

# Load environment variables from .env file
load_dotenv()

# Sample company data
sample_data = {
    "company_name": "TechInnovate",
    "team": {
        "founders": [
            {"name": "Jane Smith", "background": "Ex-Google AI researcher"},
            {"name": "Mike Johnson", "background": "Serial entrepreneur, 2 exits"}
        ],
        "team_strength": "Strong technical expertise in AI and machine learning",
        "network_strength": "Well-connected in Silicon Valley VC community"
    },
    "market": {
        "TAM": "$50B globally",
        "SAM": "$15B in North America and Europe",
        "SOM": "$2.5B in first 3 years",
        "growth_rate": "18% CAGR"
    },
    "product": {
        "stage": "MVP with 5 beta customers",
        "USP": "AI-driven predictive maintenance reducing downtime by 35%",
        "customer_acquisition": "Direct sales to enterprise, 3-month sales cycle"
    },
    "traction": {
        "revenue_growth": {"MRR": "$25K", "ARR": "$300K"},
        "user_growth": "128% QoQ last two quarters",
        "engagement": "Daily active users at 78% of total users",
        "customer_validation": {
            "testimonials": [
                "Reduced our maintenance costs by 40% - CTO, ManufactureCo",
                "Game-changing for our operations - VP Ops, IndustrialTech"
            ],
            "churn": "2.3% monthly",
            "NPS": "72"
        }
    },
    "funding": {
        "stage": "Seed",
        "amount": "$2.1M",
        "cap_table_strength": "Clean, with SAFE notes",
        "investors_on_board": [
            {"name": "TechVentures", "type": "VC"},
            {"name": "AI Angels", "type": "Angel group"}
        ]
    },
    "financial_efficiency": {
        "burn_rate": "$95K monthly",
        "CAC_vs_LTV": "CAC: $12K, LTV: $85K",
        "unit_economics": "85% gross margin on SaaS offering"
    },
    "miscellaneous": {
        "regulatory_risk": "Low - no personal data handling",
        "geographic_focus": "North America initially, Europe in Year 2",
        "timing_fad_risk": "Low - solving persistent industrial problem"
    }
}

async def test_direct_queries():
    """Test queries that should match directly to fields."""
    
    chat_service = ChatService()
    
    test_queries = [
        "Who are the founders?",
        "What's the funding stage?",
        "How much funding have they raised?",
        "What's their burn rate?",
        "Tell me about their team strength",
        "What's their total addressable market?",
        "How do they acquire customers?"
    ]
    
    print("===== DIRECT QUERY TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=sample_data,
            conversation_id="test-123",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print(f"Fields: {response.get('source_fields', [])}")
        print("-" * 50)

async def test_complex_queries():
    """Test queries that require LLM processing."""
    
    chat_service = ChatService()
    
    test_queries = [
        "Is this startup a good investment?",
        "What are the main risks for this company?",
        "Compare their CAC and LTV - is it sustainable?",
        "What's their competitive advantage?",
        "Do they have good unit economics?"
    ]
    
    print("===== COMPLEX QUERY TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=sample_data,
            conversation_id="test-456",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print(f"Model: {response.get('model_used', 'N/A')}")
        print("-" * 50)

async def test_missing_data_queries():
    """Test queries for data that doesn't exist."""
    
    # Create a copy with some data removed
    incomplete_data = json.loads(json.dumps(sample_data))
    del incomplete_data["funding"]["stage"]
    del incomplete_data["financial_efficiency"]["burn_rate"]
    
    chat_service = ChatService()
    
    test_queries = [
        "What's their funding stage?",
        "What's their burn rate?",
    ]
    
    print("===== MISSING DATA TESTS =====")
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await chat_service.process_query(
            query=query,
            company_data=incomplete_data,
            conversation_id="test-789",
            message_history=[]
        )
        print(f"Response: {response['answer']}")
        print("-" * 50)

# This allows the script to be run directly
if __name__ == "__main__":
    print("Starting Chat Module Tests...")
    
    # Run all tests
    asyncio.run(test_direct_queries())
    asyncio.run(test_complex_queries())
    asyncio.run(test_missing_data_queries())
    
    print("All tests completed successfully!")