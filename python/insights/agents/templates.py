# agents/insights_agent/templates.py

SUMMARY_TMPL = """# Atomberg — Share of Voice (SoV) Insights
**Generated:** {generated_time}

## Executive summary
- Top finding: {top_finding}
- Quick recommendation: {quick_recommendation}

"""

FINDING_TMPL = """
### {title}  — Priority: {priority} — Confidence: {confidence:.2f}
{body}
Suggested actions:
{actions}
"""

ACTION_LINE = "- {text} (Impact: {impact}, Effort: {effort})"
