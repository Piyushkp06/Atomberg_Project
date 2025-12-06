from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentModel:
    def __init__(self, use_transformer=False):
        """
        Initialize sentiment model
        Args:
            use_transformer: If True, loads heavy transformer model (268MB, CPU-intensive)
                           If False, uses only VADER (lightweight, fast)
        """
        self.vader = SentimentIntensityAnalyzer()
        self.transformer = None
        
        if use_transformer:
            try:
                from transformers import pipeline  # type: ignore
                print("⚠️  Loading transformer model (268MB, CPU-intensive)...")
                self.transformer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")  # type: ignore
                print("✅ Transformer model loaded")
            except Exception as e:
                print(f"⚠️  Could not load transformer model: {e}")
                print("📌 Using VADER only (lightweight mode)")
        else:
            print("📌 Using VADER only (lightweight mode - recommended for low-spec laptops)")

    def vader_score(self, text):
        return self.vader.polarity_scores(text)["compound"]

    def transformer_label(self, text):
        if self.transformer is None:
            return "neutral", 0.0
        try:
            result = self.transformer(text[:200])[0]  # limit tokens
            label = result["label"].lower()
            score = result["score"]

            if "pos" in label:
                return "positive", score
            elif "neg" in label:
                return "negative", score
            else:
                return "neutral", score
        except:
            return "neutral", 0.0

    def analyze(self, text):
        if not text or text.strip() == "":
            return 0.0, "neutral", 0.0

        vader = self.vader_score(text)

        if vader >= 0.4:
            return vader, "positive", abs(vader)
        if vader <= -0.4:
            return vader, "negative", abs(vader)

        # If transformer available and ambiguous → use it as fallback
        if self.transformer is not None:
            label, conf = self.transformer_label(text)
            return vader, label, conf
        
        # Otherwise, classify based on VADER threshold
        if vader > 0.05:
            return vader, "positive", abs(vader)
        elif vader < -0.05:
            return vader, "negative", abs(vader)
        else:
            return vader, "neutral", abs(vader)
