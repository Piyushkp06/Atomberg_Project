from googleapiclient.discovery import build

class YouTubeSearchClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)

    def search(self, query, max_results=15):
        search_results = self.youtube.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_results["items"]]

        # fetch statistics
        stats = self.youtube.videos().list(
            part="statistics",
            id=",".join(video_ids)
        ).execute()

        stats_map = {item["id"]: item for item in stats["items"]}

        formatted = []
        for item in search_results["items"]:
            vid = item["id"]["videoId"]
            snippet = item["snippet"]
            stat = stats_map.get(vid, {}).get("statistics", {})

            formatted.append({
                "platform": "youtube",
                "keyword": query,
                "title": snippet.get("title"),
                "snippet": snippet.get("description"),
                "url": f"https://www.youtube.com/watch?v={vid}",
                "views": int(stat.get("viewCount", 0)),
                "likes": int(stat.get("likeCount", 0)),
                "comments": int(stat.get("commentCount", 0))
            })

        return formatted
