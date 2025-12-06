class EngagementCalculator:

    def compute(self, entry):
        # Google results => no engagement
        if entry["platform"] == "google":
            return 0
        
        views = entry.get("views", 0) or 0
        likes = entry.get("likes", 0) or 0
        comments = entry.get("comments", 0) or 0

        engagement = likes + comments + (views * 0.001)

        return round(engagement, 3)
