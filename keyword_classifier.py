import csv
import json

def classify_keyword(keyword):
    """
    Automatically classifies a keyword based on search intent modifiers.
    """
    kw_lower = keyword.lower()
    
    # Define footprint modifiers
    transactional_flags = ['buy', 'price', 'cost', 'shop', 'sale', 'cheap', 'purchase', 'provider', 'supplier']
    informational_flags = ['how', 'what', 'why', 'guide', 'tutorial', 'tips', 'learn', 'examples', 'review']
    
    # Logic engine
    for word in transactional_flags:
        if word in kw_lower:
            return "Transactional (High Commercial Value)"
            
    for word in informational_flags:
        if word in kw_lower:
            return "Informational (Content Opportunity)"
            
    return "Commercial/Navigational (Brand Focus)"

def process_keyword_pipeline(input_list):
    """
    Simulates a data pipeline extracting and organizing dataset payloads.
    """
    engineered_output = []
    
    for item in input_list:
        intent = classify_keyword(item)
        payload = {
            "keyword": item,
            "intent_classification": intent,
            "status": "Processed Successfully"
        }
        engineered_output.append(payload)
        
    return json.dumps(engineered_output, indent=4)

if __name__ == "__main__":
    # Sample raw data pool to demonstrate system execution
    raw_dataset = [
        "how to optimize for ai overviews",
        "best igaming supplier link building cost",
        "python data extraction tutorial",
        "buy programmatic seo automation script"
    ]
    
    print("🤖 STARTING AUTOMATED DATA EXTRACTION & CLASSIFICATION...\n")
    pipeline_results = process_keyword_pipeline(raw_dataset)
    print(pipeline_results)
    print("\n✅ PIPELINE COMPLETED SUCCESSFULLY.")
