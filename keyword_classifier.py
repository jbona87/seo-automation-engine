#!/usr/bin/env python3
"""
Module Name: keyword_intent_pipeline.py
Description: Advanced automated data pipeline for extracting, classifying, 
             and exporting large-scale keyword datasets by search intent.
Author: jbona87
"""

import csv
import json
import logging
import os
from datetime import datetime

# Setup professional system logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class KeywordAutomationEngine:
    def __init__(self):
        # High-value system footprint modifiers
        self.intent_matrix = {
            "Transactional (High Commercial Value)": [
                'buy', 'price', 'cost', 'shop', 'sale', 'cheap', 'purchase', 
                'provider', 'supplier', 'pricing', 'agency', 'service'
            ],
            "Informational (Content Opportunity)": [
                'how', 'what', 'why', 'guide', 'tutorial', 'tips', 'learn', 
                'examples', 'review', 'case study', 'optimization', 'strategy'
            ],
            "Commercial/Navigational (Brand Focus)": [
                'best', 'top', 'vs', 'compare', 'alternative', 'software', 'platform'
            ]
        }

    def classify_intent(self, keyword: str) -> str:
        """Evaluates keyword payloads against the footprint matrix."""
        kw_clean = str(keyword).strip().lower()
        
        for intent, modifiers in self.intent_matrix.items():
            if any(modifier in kw_clean for modifier in modifiers):
                return intent
                
        return "Generic Informational (Unclassified)"

    def execute_pipeline(self, dataset: list, output_csv: str = "classified_keywords.csv"):
        """Executes full extraction, classification, and structured data compilation."""
        logging.info("🤖 INITIALIZING SYSTEM PIPELINE...")
        processed_payloads = []
        
        try:
            # Generate structured datasets
            for index, item in enumerate(dataset, start=1):
                intent = self.classify_intent(item)
                record = {
                    "id": f"KW-{index:04d}",
                    "keyword": item,
                    "intent_classification": intent,
                    "processed_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                    "status": "Verified"
                }
                processed_payloads.append(record)
            
            # Export data payload to structural CSV
            with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["id", "keyword", "intent_classification", "processed_at", "status"])
                writer.writeheader()
                writer.writerows(processed_payloads)
                
            logging.info(f"✅ EXPORT SUCCESSFUL. Data compiled into: {output_csv}")
            return json.dumps(processed_payloads, indent=4)
            
        except Exception as e:
            logging.error(f"❌ PIPELINE ERROR: {str(e)}")
            return None

if __name__ == "__main__":
    # Enterprise-level raw data pool replicating an advanced visibility audit
    raw_seo_dataset = [
        "how to optimize for ai overviews",
        "best igaming supplier link building cost",
        "python data extraction tutorial",
        "buy programmatic seo automation script",
        "advanced technical seo auditing checklist",
        "offsite supplier link velocity analytics"
    ]
    
    # Initialize and run the automation engine
    engine = KeywordAutomationEngine()
    json_output = engine.execute_pipeline(raw_seo_dataset)
    
    print("\n🖥️ TERMINAL JSON DATA STREAM OVERVIEW:\n")
    print(json_output)
