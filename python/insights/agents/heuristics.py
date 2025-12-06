# agents/insights_agent/heuristics.py

# Thresholds and weights used by the Insights Agent.
# Tweak these to be more/less aggressive.

HEUR = {
    # Brand-level thresholds (fractions)
    "sov_leader": 0.40,         # >40% SoV -> leader
    "sov_gap": 0.25,            # <25% SoV -> needs improvement
    "sev_leader": 0.40,         # >40% SEV -> engagement leader
    "sentiment_good": 0.3,      # avg_sentiment >= 0.3 -> positive sentiment
    "sentiment_bad": 0.0,       # avg_sentiment <= 0.0 -> negative-ish
    "spv_gap": 0.30,            # SPV < 30% -> low positive share
    "sample_size_warning": 5,   # sample size below this -> low confidence
    # Keyword thresholds
    "keyword_opportunity_mentions": 3, # keyword appears in >=3 docs -> worth SEO
    # Prioritization weights
    "weights": {
        "SoV": 0.35,
        "SEV": 0.25,
        "avg_sentiment": 0.25,
        "SPV": 0.15
    }
}
