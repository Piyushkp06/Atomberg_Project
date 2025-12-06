import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google_search import GoogleSearchClient
from yt_search import YouTubeSearchClient

# Load environment variables
load_dotenv(dotenv_path="../../.env")

class SearchAgent:
    def __init__(self, google_api_key=None, youtube_api_key=None, google_cse_id=None):
        # Load from env if not provided
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        self.youtube_api_key = youtube_api_key or os.getenv("YOUTUBE_API_KEY")
        self.google_cse_id = google_cse_id or os.getenv("GOOGLE_CSE_ID", "f4ba61aa656954076")
        
        if not self.google_api_key or not self.youtube_api_key:
            raise ValueError("❌ API keys not found! Please set GOOGLE_API_KEY and YOUTUBE_API_KEY in .env file")
        
        self.google_client = GoogleSearchClient(self.google_api_key, self.google_cse_id)
        self.youtube_client = YouTubeSearchClient(self.youtube_api_key)
        
        # Ensure data directory exists
        Path("data").mkdir(exist_ok=True)

    def run(self, keywords, top_n=20):
        all_results = []

        for kw in keywords:
            print(f"\n🔍 Searching for keyword: {kw}")

            # Google search
            google_data = self.google_client.search(kw, num_results=top_n)
            print(f"  → Google results: {len(google_data)}")
            all_results.extend(google_data)

            # YouTube search
            youtube_data = self.youtube_client.search(kw, max_results=top_n)
            print(f"  → YouTube results: {len(youtube_data)}")
            all_results.extend(youtube_data)

        # Save results
        with open("data/raw_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Results saved to data/raw_results.json")
        return all_results


if __name__ == "__main__":
    # Example usage
    keywords = [
        "smart fan",
        "Atomberg fan",
        "best smart fan India"
    ]
    
    print("🔑 Loading API keys from .env file...\n")
    
    try:
        agent = SearchAgent()
        results = agent.run(keywords, top_n=10)
        print(f"\n📊 Total results collected: {len(results)}")
    except ValueError as e:
        print(e)
        print("\n💡 Create a .env file with:")
        print("   GOOGLE_API_KEY=your_google_api_key")
        print("   YOUTUBE_API_KEY=your_youtube_api_key")
        print("   GOOGLE_CSE_ID=your_cse_id")
