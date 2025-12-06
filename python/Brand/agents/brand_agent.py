import json
import re
from brand_keywords import brand_keywords
from nlp_classifier import SemanticBrandClassifier


class BrandDetectionAgent:
    
    def __init__(self):
        self.semantic_classifier = SemanticBrandClassifier()

    def detect_from_keywords(self, text):
        text_lower = text.lower()
        
        detected = []
        for brand, keywords in brand_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    detected.append(brand)
                    break

        if not detected:
            return None   # No match
        
        if len(detected) == 1:
            return detected[0]

        # Multiple brands detected → ambiguous
        return detected[0]    # choose first
        

    def classify(self, entry):
        text = (entry["title"] + " " + entry["snippet"]).strip()
        
        # 1. Try exact keyword match
        brand = self.detect_from_keywords(text)
        if brand:
            return brand, 1.0  # full confidence

        # 2. If not found → use semantic AI fallback
        brand_sem, conf = self.semantic_classifier.predict(text)

        if conf > 0.40:   # threshold
            return brand_sem, conf
        
        return "Unknown", conf


    def run(self, input_file="../../Search_retrieval/search_agents/data/raw_results.json", output_file="data/classified_results.json"):
        import os
        from pathlib import Path
        
        # Ensure output directory exists
        Path("data").mkdir(exist_ok=True)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file not found: {input_file}")
            print(f"💡 Please run the search agent first to generate raw_results.json")
            return []
        
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        output = []

        for entry in data:
            brand, conf = self.classify(entry)
            entry["brand"] = brand
            entry["confidence"] = round(conf, 3)
            output.append(entry)

        # save
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ Brand Detection Completed → {len(output)} classified entries")
        print(f"📁 Saved to: {output_file}")
        return output


if __name__ == "__main__":
    agent = BrandDetectionAgent()
    output = agent.run()
