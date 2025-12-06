# agents/insights_agent/insights_agent.py

import json
import os
import datetime
from pathlib import Path
from collections import defaultdict
from heuristics import HEUR
from templates import SUMMARY_TMPL, FINDING_TMPL, ACTION_LINE

def load_metrics(path="../../SOV/data/metrics.json"):
    if not os.path.exists(path):
        print(f"❌ Error: Input file not found: {path}")
        print(f"💡 Please run the SOV metrics agent first to generate metrics.json")
        return None
    
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def score_brand(brand_vals):
    # Weighted score combining SoV, SEV, avg_sentiment, SPV
    w = HEUR["weights"]
    return (
        w["SoV"] * brand_vals.get("SoV", 0) +
        w["SEV"] * brand_vals.get("SEV", 0) +
        w["avg_sentiment"] * brand_vals.get("avg_sentiment", 0) +
        w["SPV"] * brand_vals.get("SPV", 0)
    )

def priority_from_score(score):
    if score >= 0.35:
        return "High"
    if score >= 0.18:
        return "Medium"
    return "Low"

def confidence_from_sample(size):
    if size >= HEUR["sample_size_warning"]:
        return 0.9
    return max(0.4, size / HEUR["sample_size_warning"])

def generate_brand_findings(metrics):
    if not metrics:
        return []
    
    brand_metrics = metrics.get("brand_metrics", {})
    totals = metrics.get("totals", {})
    findings = []
    scores = {}
    
    if not brand_metrics:
        return []
    
    for brand, vals in brand_metrics.items():
        sc = score_brand(vals)
        scores[brand] = sc

    # rank brands by score
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    # top brand insight
    top_brand, top_score = ranked[0]
    top_vals = brand_metrics[top_brand]
    top_conf = confidence_from_sample(top_vals.get("sample_size", 0))

    # Construct leader/lagger insights for Atomberg specifically
    atomberg = brand_metrics.get("Atomberg")
    if not atomberg:
        # No data for Atomberg
        findings.append({
            "title": "No Atomberg mentions found",
            "priority": "High",
            "confidence": 0.85,
            "body": "Agent did not find measurable Atomberg mentions in the dataset. Confirm keywords and data sources.",
            "actions": [
                {"text": "Re-run Search Agent with additional brand and product keywords", "impact": "High", "effort": "Low"},
                {"text": "Increase top_n per keyword to 50 to capture more docs", "impact": "Medium", "effort": "Low"}
            ]
        })
        return findings

    # Leader / gap checks
    a_sov = atomberg.get("SoV", 0)
    a_sev = atomberg.get("SEV", 0)
    a_spv = atomberg.get("SPV", 0)
    a_sent = atomberg.get("avg_sentiment", 0)
    sample = atomberg.get("sample_size", 0)
    conf = confidence_from_sample(sample)

    # Strength: high sentiment
    if a_sent >= HEUR["sentiment_good"]:
        findings.append({
            "title": "Atomberg has strong positive sentiment",
            "priority": priority_from_score(a_sent),
            "confidence": conf,
            "body": f"Avg sentiment = {a_sent:.2f}; positive share (SPV) = {a_spv:.2f}. This is a strong brand perception signal.",
            "actions": [
                {"text": "Promote positive testimonials and extract quotes for ad copy", "impact": "Medium", "effort": "Low"},
                {"text": "Create short testimonial videos for YouTube/Instagram", "impact": "High", "effort": "Medium"}
            ]
        })

    # Weakness: low SoV in brand-agnostic keywords
    if a_sov < HEUR["sov_gap"]:
        findings.append({
            "title": "Atomberg under-indexed in organic brand-agnostic searches",
            "priority": "High" if a_sov < 0.15 else "Medium",
            "confidence": conf,
            "body": f"SoV = {a_sov:.2f} which is below the target threshold ({HEUR['sov_gap']}). Competitors capture more brand-agnostic attention.",
            "actions": [
                {"text": "Produce SEO-focused long-form articles for target keywords (e.g., 'best smart fan India')", "impact": "High", "effort": "Medium"},
                {"text": "Add structured comparison pages 'Atomberg vs Havells' with schema markup", "impact": "High", "effort": "Medium"}
            ]
        })

    # Engagement leader suggestion
    if a_sev >= HEUR["sev_leader"]:
        findings.append({
            "title": "Atomberg content drives strong engagement",
            "priority": "High",
            "confidence": conf,
            "body": f"Share of Engagement Voice = {a_sev:.2f} — Atomberg content is resonating (views/likes/comments).",
            "actions": [
                {"text": "Scale influencer partnerships and paid boosts on high-engagement videos", "impact": "High", "effort": "Medium"},
                {"text": "Repurpose high-engagement video clips into short-form ads", "impact": "High", "effort": "Low"}
            ]
        })

    # Low positive share (SPV) issue
    if a_spv < HEUR["spv_gap"]:
        findings.append({
            "title": "Proportion of positive mentions is low",
            "priority": "Medium",
            "confidence": conf,
            "body": f"SPV = {a_spv:.2f}. Consider improving product messaging and addressing common negative points.",
            "actions": [
                {"text": "Run root-cause analysis on negative snippets to find recurring complaints", "impact": "High", "effort": "Medium"},
                {"text": "Publish FAQ / troubleshooting content to reduce negative mentions", "impact": "Medium", "effort": "Low"}
            ]
        })

    # Competitor-specific insights: who outranks Atomberg by SoV
    # find top competitor by SoV
    comp_sorted = sorted(
        [(b, vals.get("SoV", 0)) for b, vals in brand_metrics.items() if b != "Atomberg"],
        key=lambda x: x[1], reverse=True
    )
    if comp_sorted:
        top_comp, top_comp_sov = comp_sorted[0]
        if top_comp_sov > a_sov + 0.05:  # meaningful gap
            findings.append({
                "title": f"{top_comp} leads Atomberg in visibility",
                "priority": "High",
                "confidence": 0.85,
                "body": f"{top_comp} SoV = {top_comp_sov:.2f}, Atomberg SoV = {a_sov:.2f}. Consider targeted counter-content and ad placements.",
                "actions": [
                    {"text": f"Run targeted content comparing Atomberg with {top_comp}", "impact": "High", "effort": "Medium"},
                    {"text": f"Place paid search ads on queries where {top_comp} ranks highly", "impact": "High", "effort": "Low"}
                ]
            })

    return findings

def generate_keyword_opportunities(metrics):
    km = metrics.get("keyword_metrics", {})
    ops = []
    for kw, vals in km.items():
        if vals.get("mentions", 0) >= HEUR["keyword_opportunity_mentions"]:
            ops.append({
                "keyword": kw,
                "mentions": vals.get("mentions"),
                "SoV": vals.get("SoV"),
                "avg_sentiment": vals.get("avg_sentiment"),
                "suggestions": [
                    {"text": f"Create long-form SEO blog for '{kw}'", "impact": "High", "effort": "Medium"},
                    {"text": f"Produce comparison video targeting '{kw}'", "impact": "Medium", "effort": "Medium"}
                ]
            })
    return ops

def generate_platform_insights(metrics):
    pm = metrics.get("platform_metrics", {})
    insights = []
    # Example: if YouTube SEV >> Google SEV, recommend video focus
    yt = pm.get("youtube", {})
    gg = pm.get("google", {})
    if yt and gg:
        if yt.get("SEV", 0) > gg.get("SEV", 0) + 0.10:
            insights.append({
                "title": "YouTube is a higher engagement channel than Google",
                "priority": "Medium",
                "confidence": 0.8,
                "body": f"YouTube SEV = {yt.get('SEV'):.2f} vs Google SEV = {gg.get('SEV'):.2f}. Invest more in creators and video content.",
                "actions": [
                    {"text": "Identify top-performing creators and pitch collaborations", "impact": "High", "effort": "Medium"},
                    {"text": "Create short-form assets for shorts/reels", "impact": "High", "effort": "Low"}
                ]
            })
    return insights

def assemble_insights(metrics):
    if not metrics:
        return {
            "summary": {},
            "findings": [],
            "keyword_opportunities": []
        }
    
    findings = []
    findings.extend(generate_brand_findings(metrics))
    findings.extend(generate_platform_insights(metrics))
    keyword_ops = generate_keyword_opportunities(metrics)

    # Pack result
    generated_time = datetime.datetime.utcnow().isoformat() + "Z"
    exec_summary = {
        "generated_at": generated_time,
        "total_documents": metrics.get("totals", {}).get("total_documents", 0),
        "top_findings_count": len(findings),
        "keyword_opportunities_count": len(keyword_ops)
    }

    payload = {
        "summary": exec_summary,
        "findings": findings,
        "keyword_opportunities": keyword_ops
    }
    return payload

def save_outputs(payload, out_json="data/insights.json", out_md="data/insights.md"):
    # Ensure output directory exists
    Path("data").mkdir(exist_ok=True)
    
    # save JSON
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)

    # produce markdown
    now = payload["summary"]["generated_at"]
    top = payload["findings"][0] if payload["findings"] else {}
    top_finding = top.get("title", "No major findings")
    quick_reco = top.get("actions", [{"text":"No actions"}])[0]["text"]
    md = SUMMARY_TMPL.format(generated_time=now, top_finding=top_finding, quick_recommendation=quick_reco)

    for f in payload["findings"]:
        actions_md = "\n".join([ACTION_LINE.format(text=a["text"], impact=a["impact"], effort=a["effort"]) for a in f["actions"]])
        md += FINDING_TMPL.format(title=f["title"], priority=f["priority"], confidence=f["confidence"], body=f["body"], actions=actions_md)

    if payload.get("keyword_opportunities"):
        md += "\n## Keyword opportunities\n"
        for k in payload["keyword_opportunities"]:
            md += f"- **{k['keyword']}** — mentions: {k['mentions']}, SoV: {k['SoV']}\n"
            for s in k["suggestions"]:
                md += f"  - {s['text']} (Impact: {s['impact']}, Effort: {s['effort']})\n"

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(md)
    
    print(f"✅ Insights generated successfully")
    print(f"📁 JSON: {out_json}")
    print(f"📄 Markdown: {out_md}")

def run(input_path="../../SOV/data/metrics.json"):
    metrics = load_metrics(input_path)
    if not metrics:
        return None
    payload = assemble_insights(metrics)
    save_outputs(payload)
    return payload


if __name__ == "__main__":
    payload = run("../../SOV/data/metrics.json")
    if payload:
        print("\n" + "="*60)
        print("🎯 INSIGHTS GENERATION COMPLETE")
        print("="*60)
        print("\n📊 Summary:")
        import pprint
        pprint.pprint(payload["summary"])
        print(f"\n💡 Top Findings: {len(payload['findings'])}")
        print(f"🔑 Keyword Opportunities: {len(payload['keyword_opportunities'])}")
    else:
        print("\n❌ Could not generate insights. Please run the complete pipeline first.")
