# agents/metrics_agent/metrics_engine.py

import json
import csv
import os
import statistics
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Any


class MetricsEngine:
    def __init__(self, input_path="../sentiment/agents/data/scored_results.json"):
        self.input_path = input_path
        self.data = self._load_input()

    def _load_input(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.input_path):
            print(f"❌ Error: Input file not found: {self.input_path}")
            print(f"💡 Please run the sentiment agent first to generate scored_results.json")
            return []
        
        with open(self.input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def _safe_get_num(self, item, key):
        v = item.get(key, 0)
        try:
            return float(v) if v is not None else 0.0
        except:
            return 0.0

    def compute(self) -> Dict[str, Any]:
        # Check if data is empty
        if not self.data:
            print("⚠️  No data to compute metrics. Returning empty result.")
            return {
                "totals": {},
                "brand_metrics": {},
                "platform_metrics": {},
                "keyword_metrics": {}
            }
        
        # aggregate containers
        brands = set()
        brand_entries = defaultdict(list)
        platform_entries = defaultdict(list)
        keyword_entries = defaultdict(list)

        total_mentions = 0
        total_engagement = 0.0
        total_positive_mentions = 0

        # Normalize and bucket entries
        for entry in self.data:
            brand = entry.get("brand", "Unknown") or "Unknown"
            platform = entry.get("platform", "unknown")
            keyword = entry.get("keyword", "unknown")

            brands.add(brand)
            brand_entries[brand].append(entry)
            platform_entries[platform].append(entry)
            keyword_entries[keyword].append(entry)

            # count mention if brand is not Unknown
            if brand != "Unknown":
                total_mentions += 1

            # engagement
            total_engagement += self._safe_get_num(entry, "engagement_score")

            # positive mentions
            if entry.get("sentiment_label") == "positive":
                total_positive_mentions += 1

        # build brand metrics
        brand_metrics = {}
        for brand in sorted(list(brands)):
            entries = brand_entries[brand]
            mentions = len([e for e in entries if e.get("brand", "Unknown") != "Unknown"])
            engagement_sum = sum(self._safe_get_num(e, "engagement_score") for e in entries)
            positive_mentions = len([e for e in entries if e.get("sentiment_label") == "positive"])
            sentiment_scores = [self._safe_get_num(e, "sentiment_score") for e in entries if e.get("sentiment_score") is not None]

            avg_sentiment = round(statistics.mean(sentiment_scores), 4) if sentiment_scores else 0.0

            # Use safe arithmetic:
            sov = round(mentions / total_mentions, 4) if total_mentions > 0 else 0.0
            sev = round(engagement_sum / total_engagement, 4) if total_engagement > 0 else 0.0
            spv = round(positive_mentions / total_positive_mentions, 4) if total_positive_mentions > 0 else 0.0
            sw_sov = round(sov * avg_sentiment, 6)

            brand_metrics[brand] = {
                "mentions": mentions,
                "SoV": sov,
                "engagement_sum": round(engagement_sum, 3),
                "SEV": sev,
                "positive_mentions": positive_mentions,
                "SPV": spv,
                "avg_sentiment": round(avg_sentiment, 4),
                "SW_SoV": sw_sov,
                "sample_size": len(entries)
            }

        # platform and keyword level metrics (same logic)
        def summarize_buckets(bucket):
            out = {}
            for key, entries in bucket.items():
                mentions = len([e for e in entries if e.get("brand", "Unknown") != "Unknown"])
                engagement_sum = sum(self._safe_get_num(e, "engagement_score") for e in entries)
                positive_mentions = len([e for e in entries if e.get("sentiment_label") == "positive"])
                sentiment_scores = [self._safe_get_num(e, "sentiment_score") for e in entries if e.get("sentiment_score") is not None]
                avg_sentiment = round(statistics.mean(sentiment_scores), 4) if sentiment_scores else 0.0

                sov = round(mentions / total_mentions, 4) if total_mentions > 0 else 0.0
                sev = round(engagement_sum / total_engagement, 4) if total_engagement > 0 else 0.0
                spv = round(positive_mentions / total_positive_mentions, 4) if total_positive_mentions > 0 else 0.0
                sw_sov = round(sov * avg_sentiment, 6)

                out[key] = {
                    "mentions": mentions,
                    "SoV": sov,
                    "engagement_sum": round(engagement_sum, 3),
                    "SEV": sev,
                    "positive_mentions": positive_mentions,
                    "SPV": spv,
                    "avg_sentiment": avg_sentiment,
                    "SW_SoV": sw_sov,
                    "sample_size": len(entries)
                }
            return out

        platform_metrics = summarize_buckets(platform_entries)
        keyword_metrics = summarize_buckets(keyword_entries)

        # totals
        totals = {
            "total_documents": len(self.data),
            "total_mentions": total_mentions,
            "total_engagement": round(total_engagement, 3),
            "total_positive_mentions": total_positive_mentions,
            "brands_evaluated": sorted(list(brands))
        }

        result = {
            "totals": totals,
            "brand_metrics": brand_metrics,
            "platform_metrics": platform_metrics,
            "keyword_metrics": keyword_metrics
        }

        return result

    def save(self, metrics: Dict[str, Any], out_json="data/metrics.json", out_csv="data/metrics.csv"):
        # Ensure output directory exists
        Path("data").mkdir(exist_ok=True)
        
        # save json
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4, ensure_ascii=False)

        # flatten a CSV for quick dashboard/table viewing (brand-level rows)
        header = [
            "level", "key",
            "mentions", "SoV", "engagement_sum", "SEV",
            "positive_mentions", "SPV", "avg_sentiment", "SW_SoV", "sample_size"
        ]
        rows = []
        for brand, vals in metrics["brand_metrics"].items():
            rows.append(["brand", brand] + [vals.get(h) for h in ["mentions", "SoV", "engagement_sum", "SEV", "positive_mentions", "SPV", "avg_sentiment", "SW_SoV", "sample_size"]])

        for platform, vals in metrics["platform_metrics"].items():
            rows.append(["platform", platform] + [vals.get(h) for h in ["mentions", "SoV", "engagement_sum", "SEV", "positive_mentions", "SPV", "avg_sentiment", "SW_SoV", "sample_size"]])

        for keyword, vals in metrics["keyword_metrics"].items():
            rows.append(["keyword", keyword] + [vals.get(h) for h in ["mentions", "SoV", "engagement_sum", "SEV", "positive_mentions", "SPV", "avg_sentiment", "SW_SoV", "sample_size"]])

        with open(out_csv, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for r in rows:
                writer.writerow(r)

        print(f"✅ Saved metrics -> {out_json} and {out_csv}")
        print(f"📊 Total brands evaluated: {len(metrics.get('brand_metrics', {}))}")
        print(f"📁 Files saved in: data/")

if __name__ == "__main__":
    engine = MetricsEngine(input_path="../sentiment/agents/data/scored_results.json")
    metrics = engine.compute()
    
    if metrics["totals"]:
        engine.save(metrics)
        # pretty print summary
        print("\n" + "="*60)
        print("📊 SHARE OF VOICE (SOV) METRICS SUMMARY")
        print("="*60)
        import pprint
        print("\n🎯 TOTALS:")
        pprint.pprint(metrics["totals"])
        print("\n🏢 BRAND METRICS:")
        pprint.pprint(metrics["brand_metrics"])
    else:
        print("\n❌ No metrics to display. Please ensure the data pipeline is complete.")