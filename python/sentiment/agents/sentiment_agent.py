import json
from sentiment_model import SentimentModel
from engagement import EngagementCalculator

class SentimentEngagementAgent:

    def __init__(self, use_transformer=False):
        """
        Initialize agent
        Args:
            use_transformer: Set to True for better accuracy (heavy CPU usage)
                           Set to False for fast processing (recommended for low-spec laptops)
        """
        self.sentiment_model = SentimentModel(use_transformer=use_transformer)
        self.eng_calc = EngagementCalculator()

    def run(self, input_file="../../Brand/agents/data/classified_results.json", output_file="data/scored_results.json"):
        import os
        from pathlib import Path
        
        # Ensure output directory exists
        Path("data").mkdir(exist_ok=True)
        
        if not os.path.exists(input_file):
            print(f"❌ Error: Input file not found: {input_file}")
            print(f"💡 Please run the brand detection agent first to generate classified_results.json")
            return []
        
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        output = []

        for entry in data:
            text = (entry.get("title", "") + " " + entry.get("snippet", "")).strip()
            
            # 1. Sentiment
            polarity, label, conf = self.sentiment_model.analyze(text)
            
            entry["sentiment_score"] = round(polarity, 3)
            entry["sentiment_label"] = label
            entry["sentiment_confidence"] = round(conf, 3)

            # 2. Engagement
            entry["engagement_score"] = self.eng_calc.compute(entry)

            output.append(entry)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"✅ Sentiment + Engagement scoring complete → {len(output)} entries.")
        print(f"📁 Saved to: {output_file}")
        return output
 
 
if __name__ == "__main__":
    agent = SentimentEngagementAgent()
    agent.run()