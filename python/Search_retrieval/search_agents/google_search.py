import time
from googleapiclient.discovery import build

class GoogleSearchClient:
    def __init__(self, api_key, cse_id="f4ba61aa656954076"):
        self.api_key = api_key
        self.cse_id = cse_id
        self.service = build("customsearch", "v1", developerKey=api_key)

    def search(self, query, num_results=50, retries=3):
        formatted_results = []
        
        # Google Custom Search API returns max 10 results per request
        # So we need to paginate if num_results > 10
        results_to_fetch = min(num_results, 100)  # API limit is 100
        
        for attempt in range(retries):
            try:
                start_index = 1
                while len(formatted_results) < results_to_fetch:
                    # Fetch up to 10 results per request
                    num = min(10, results_to_fetch - len(formatted_results))
                    
                    result = self.service.cse().list(
                        q=query,
                        cx=self.cse_id,
                        num=num,
                        start=start_index
                    ).execute()
                    
                    items = result.get("items", [])
                    if not items:
                        break
                    
                    for item in items:
                        formatted_results.append({
                            "platform": "google",
                            "keyword": query,
                            "title": item.get("title", ""),
                            "snippet": item.get("snippet", ""),
                            "url": item.get("link", ""),
                            "views": None,
                            "likes": None,
                            "comments": None
                        })
                    
                    start_index += 10
                    
                    # Rate limiting - be nice to the API
                    time.sleep(0.5)
                    
                    # Break if we've fetched enough or reached the end
                    if len(items) < num or len(formatted_results) >= results_to_fetch:
                        break
                
                return formatted_results
            
            except Exception as e:
                print(f"[Google Search] Error: {e}")
                if "API key" in str(e) or "invalid" in str(e).lower():
                    print(f"[Google Search] ❌ Invalid API key or CSE ID. Check your credentials.")
                    return []
                if attempt < retries - 1:
                    print(f"[Google Search] Retrying... (attempt {attempt + 2}/{retries})")
                    time.sleep(2)
        
        print(f"[Google Search] ❌ Failed after {retries} attempts")
        return formatted_results
