import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Atomberg SOV Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #FF6B35;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all data files with statistics"""
    data = {}
    stats = {}
    
    # Load raw search results
    raw_path = Path("Search_retrieval/search_agents/data/raw_results.json")
    if raw_path.exists():
        with open(raw_path, 'r', encoding='utf-8') as f:
            data['raw'] = json.load(f)
            stats['raw_count'] = len(data['raw'])
    
    # Load classified results
    classified_path = Path("Brand/agents/data/classified_results.json")
    if classified_path.exists():
        with open(classified_path, 'r', encoding='utf-8') as f:
            data['classified'] = json.load(f)
            stats['classified_count'] = len(data['classified'])
    
    # Load sentiment results
    sentiment_path = Path("sentiment/agents/data/scored_results.json")
    if sentiment_path.exists():
        with open(sentiment_path, 'r', encoding='utf-8') as f:
            data['sentiment'] = json.load(f)
            stats['sentiment_count'] = len(data['sentiment'])
    
    # Load SOV metrics
    metrics_path = Path("SOV/data/metrics.json")
    if metrics_path.exists():
        with open(metrics_path, 'r', encoding='utf-8') as f:
            data['metrics'] = json.load(f)
    
    # Load insights
    insights_path = Path("insights/agents/data/insights.json")
    if insights_path.exists():
        with open(insights_path, 'r', encoding='utf-8') as f:
            data['insights'] = json.load(f)
    
    data['stats'] = stats
    return data

def main():
    # Header
    st.markdown('<h1 class="main-header">🎯 Atomberg Share of Voice Analytics</h1>', unsafe_allow_html=True)
    
    # Load data
    try:
        data = load_data()
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        st.info("💡 Please run the complete pipeline first:\n1. Search Agent\n2. Brand Agent\n3. Sentiment Agent\n4. SOV Metrics Agent\n5. Insights Agent")
        return
    
    # Sidebar
    with st.sidebar:
        st.image("https://www.atomberg.com/cdn/shop/files/Logo.png?v=1697709685&width=200", width=200)
        st.markdown("---")
        
        # Show data statistics
        if 'stats' in data:
            st.markdown("### 📊 Data Statistics")
            if 'raw_count' in data['stats']:
                st.metric("Raw Results", f"{data['stats']['raw_count']:,}")
            if 'classified_count' in data['stats']:
                st.metric("Classified", f"{data['stats']['classified_count']:,}")
            if 'sentiment_count' in data['stats']:
                st.metric("Analyzed", f"{data['stats']['sentiment_count']:,}")
            st.markdown("---")
        
        st.markdown("### 📊 Dashboard Navigation")
        page = st.radio("Select View:", [
            "🏠 Overview",
            "📈 Share of Voice",
            "😊 Sentiment Analysis",
            "🔍 Brand Comparison",
            "💡 Insights & Recommendations",
            "📋 Raw Data Explorer"
        ])
        
        st.markdown("---")
        st.markdown("### ⚙️ Settings")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Main content based on selection
    if page == "🏠 Overview":
        show_overview(data)
    elif page == "📈 Share of Voice":
        show_sov(data)
    elif page == "😊 Sentiment Analysis":
        show_sentiment(data)
    elif page == "🔍 Brand Comparison":
        show_brand_comparison(data)
    elif page == "💡 Insights & Recommendations":
        show_insights(data)
    elif page == "📋 Raw Data Explorer":
        show_raw_data(data)

def show_overview(data):
    """Overview page with key metrics"""
    st.markdown("## 📊 Executive Summary")
    
    if 'metrics' not in data:
        st.warning("⚠️ No metrics data available. Please run the SOV metrics agent.")
        return
    
    metrics = data['metrics']
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    totals = metrics.get('totals', {})
    brand_metrics = metrics.get('brand_metrics', {})
    atomberg_data = brand_metrics.get('Atomberg', {})
    
    with col1:
        sov = atomberg_data.get('SoV', 0) * 100  # Convert to percentage
        st.metric(
            label="🎯 Atomberg SOV",
            value=f"{sov:.1f}%",
            delta=f"{sov - 25:.1f}% vs avg" if sov > 0 else None
        )
    
    with col2:
        total = totals.get('total_mentions', 0)
        st.metric(
            label="📢 Total Mentions",
            value=f"{total:,}",
        )
    
    with col3:
        atomberg_mentions = atomberg_data.get('mentions', 0)
        st.metric(
            label="⭐ Atomberg Mentions",
            value=f"{atomberg_mentions:,}",
        )
    
    with col4:
        avg_sentiment = atomberg_data.get('avg_sentiment', 0)
        st.metric(
            label="😊 Atomberg Sentiment",
            value=f"{avg_sentiment:.2f}",
            delta="Positive" if avg_sentiment > 0 else "Negative"
        )
    
    st.markdown("---")
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Brand Distribution")
        brand_metrics = metrics.get('brand_metrics', {})
        if brand_metrics:
            brand_data = []
            for brand, vals in brand_metrics.items():
                if brand != 'Unknown':
                    brand_data.append({'Brand': brand, 'Mentions': vals.get('mentions', 0)})
            
            brand_df = pd.DataFrame(brand_data)
            brand_df = brand_df.sort_values('Mentions', ascending=False)
            
            fig = px.pie(brand_df, values='Mentions', names='Brand',
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 SOV Comparison")
        brand_metrics = metrics.get('brand_metrics', {})
        if brand_metrics:
            sov_data = []
            for brand, vals in brand_metrics.items():
                if brand != 'Unknown':
                    sov_data.append({'Brand': brand, 'SOV %': vals.get('SoV', 0) * 100})
            
            sov_df = pd.DataFrame(sov_data)
            sov_df = sov_df.sort_values('SOV %', ascending=True)
            
            fig = px.bar(sov_df, x='SOV %', y='Brand', orientation='h',
                        color='SOV %',
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Platform breakdown
    st.markdown("### 🌐 Platform Breakdown")
    col1, col2 = st.columns(2)
    
    with col1:
        platform_metrics = metrics.get('platform_metrics', {})
        if platform_metrics:
            platform_data = []
            for platform, vals in platform_metrics.items():
                platform_data.append({'Platform': platform.title(), 'Count': vals.get('mentions', 0)})
            
            platform_df = pd.DataFrame(platform_data)
            fig = px.bar(platform_df, x='Platform', y='Count',
                        color='Platform',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'classified' in data:
            platforms = {}
            for item in data['classified']:
                platform = item.get('source', 'Unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
            
            st.markdown("**Platform Stats:**")
            for platform, count in platforms.items():
                st.markdown(f"- **{platform}:** {count} results")

def show_sov(data):
    """Share of Voice detailed analysis"""
    st.markdown("## 📈 Share of Voice Analysis")
    
    if 'metrics' not in data:
        st.warning("⚠️ No metrics data available.")
        return
    
    metrics = data['metrics']
    
    # SOV Gauge Chart
    col1, col2 = st.columns([2, 1])
    
    with col1:
        brand_metrics = metrics.get('brand_metrics', {})
        atomberg_data = brand_metrics.get('Atomberg', {})
        sov = atomberg_data.get('SoV', 0) * 100  # Convert to percentage
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=sov,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Atomberg Share of Voice (%)"},
            delta={'reference': 25},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#FF6B35"},
                'steps': [
                    {'range': [0, 20], 'color': "#FFE5E0"},
                    {'range': [20, 40], 'color': "#FFB8A8"},
                    {'range': [40, 100], 'color': "#FF8A70"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 50
                }
            }
        ))
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Key Metrics")
        totals = metrics.get('totals', {})
        st.metric("Total Market Share", f"{sov:.1f}%")
        st.metric("Total Mentions", f"{totals.get('total_mentions', 0):,}")
        st.metric("Atomberg Mentions", f"{atomberg_data.get('mentions', 0):,}")
        
        # Market position
        if brand_metrics:
            sov_list = [(brand, vals.get('SoV', 0)) for brand, vals in brand_metrics.items() if brand != 'Unknown']
            sov_brands = sorted(sov_list, key=lambda x: x[1], reverse=True)
            atomberg_rank = next((i+1 for i, (brand, _) in enumerate(sov_brands) if brand == 'Atomberg'), None)
            if atomberg_rank:
                st.metric("Market Position", f"#{atomberg_rank}")
    
    st.markdown("---")
    
    # Brand comparison table
    st.markdown("### 🏆 Brand Rankings")
    brand_metrics = metrics.get('brand_metrics', {})
    if brand_metrics:
        comparison_data = []
        for brand, vals in brand_metrics.items():
            if brand != 'Unknown':
                comparison_data.append({
                    'Brand': brand,
                    'SOV %': round(vals.get('SoV', 0) * 100, 2),
                    'Mentions': vals.get('mentions', 0)
                })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('SOV %', ascending=False)
        comparison_df['Rank'] = range(1, len(comparison_df) + 1)
        comparison_df = comparison_df[['Rank', 'Brand', 'SOV %', 'Mentions']]
        
        # Highlight Atomberg row
        def highlight_atomberg(row):
            return ['background-color: #FFE5E0' if row['Brand'] == 'Atomberg' else '' for _ in row]
        
        st.dataframe(
            comparison_df.style.apply(highlight_atomberg, axis=1),
            use_container_width=True,
            hide_index=True
        )
    
    # Trend analysis (if available)
    st.markdown("### 📊 Distribution Visualization")
    col1, col2 = st.columns(2)
    
    with col1:
        brand_metrics = metrics.get('brand_metrics', {})
        if brand_metrics:
            brand_data = []
            for brand, vals in brand_metrics.items():
                if brand != 'Unknown':
                    brand_data.append({'Brand': brand, 'Mentions': vals.get('mentions', 0)})
            
            brand_df = pd.DataFrame(brand_data)
            brand_df = brand_df.sort_values('Mentions', ascending=False)
            
            fig = px.treemap(brand_df, path=['Brand'], values='Mentions',
                           color='Mentions',
                           color_continuous_scale='RdYlGn')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if brand_metrics:
            sov_data = []
            for brand, vals in brand_metrics.items():
                if brand != 'Unknown':
                    sov_data.append({'Brand': brand, 'SOV': vals.get('SoV', 0)})
            
            sov_df = pd.DataFrame(sov_data)
            sov_df = sov_df.sort_values('SOV', ascending=False)
            
            fig = px.funnel(sov_df, x='SOV', y='Brand',
                          color='SOV')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def show_sentiment(data):
    """Sentiment analysis page"""
    st.markdown("## 😊 Sentiment Analysis")
    
    if 'sentiment' not in data or not data['sentiment']:
        st.warning("⚠️ No sentiment data available.")
        return
    
    sentiment_data = data['sentiment']
    
    # Overall sentiment metrics
    col1, col2, col3, col4 = st.columns(4)
    
    positive = sum(1 for item in sentiment_data if item.get('sentiment_label', '').lower() == 'positive')
    negative = sum(1 for item in sentiment_data if item.get('sentiment_label', '').lower() == 'negative')
    neutral = sum(1 for item in sentiment_data if item.get('sentiment_label', '').lower() == 'neutral')
    total = len(sentiment_data)
    
    with col1:
        st.metric("😊 Positive", f"{positive} ({positive/total*100:.1f}%)")
    with col2:
        st.metric("😐 Neutral", f"{neutral} ({neutral/total*100:.1f}%)")
    with col3:
        st.metric("😞 Negative", f"{negative} ({negative/total*100:.1f}%)")
    with col4:
        avg_score = sum(item.get('sentiment_score', 0) for item in sentiment_data) / total
        st.metric("📊 Avg Score", f"{avg_score:.2f}")
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Sentiment Distribution")
        sentiment_counts = {
            'Positive': positive,
            'Neutral': neutral,
            'Negative': negative
        }
        
        fig = px.pie(
            values=list(sentiment_counts.values()),
            names=list(sentiment_counts.keys()),
            color=list(sentiment_counts.keys()),
            color_discrete_map={'Positive': '#00D45A', 'Neutral': '#FFB800', 'Negative': '#FF4B4B'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📈 Sentiment Score Distribution")
        scores = [item.get('sentiment_score', 0) for item in sentiment_data]
        
        fig = px.histogram(x=scores, nbins=20, 
                         color_discrete_sequence=['#667eea'])
        fig.update_layout(
            xaxis_title="Sentiment Score",
            yaxis_title="Count",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Brand-wise sentiment
    st.markdown("### 🏷️ Brand-wise Sentiment Breakdown")
    
    brand_sentiment = {}
    for item in sentiment_data:
        brand = item.get('brand', 'Unknown')
        sentiment = item.get('sentiment_label', 'neutral').lower().capitalize()
        
        if brand not in brand_sentiment:
            brand_sentiment[brand] = {'Positive': 0, 'Neutral': 0, 'Negative': 0}
        
        if sentiment in brand_sentiment[brand]:
            brand_sentiment[brand][sentiment] += 1
    
    # Create stacked bar chart
    brand_df = pd.DataFrame(brand_sentiment).T.reset_index()
    brand_df.columns = ['Brand', 'Positive', 'Neutral', 'Negative']
    
    fig = go.Figure(data=[
        go.Bar(name='Positive', x=brand_df['Brand'], y=brand_df['Positive'], marker_color='#00D45A'),
        go.Bar(name='Neutral', x=brand_df['Brand'], y=brand_df['Neutral'], marker_color='#FFB800'),
        go.Bar(name='Negative', x=brand_df['Brand'], y=brand_df['Negative'], marker_color='#FF4B4B')
    ])
    fig.update_layout(barmode='stack', height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Top positive and negative mentions
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⭐ Most Positive Mentions")
        positive_items = sorted(
            [item for item in sentiment_data if item.get('sentiment_label', '').lower() == 'positive'],
            key=lambda x: x.get('sentiment_score', 0),
            reverse=True
        )[:5]
        
        for item in positive_items:
            with st.expander(f"Score: {item.get('sentiment_score', 0):.2f} - {item.get('brand', 'Unknown')}"):
                st.write(f"**Platform:** {item.get('platform', 'Unknown')}")
                st.write(f"**Title:** {item.get('title', 'N/A')[:100]}...")
                st.write(f"**Link:** {item.get('url', 'N/A')}")
    
    with col2:
        st.markdown("### ⚠️ Most Negative Mentions")
        negative_items = sorted(
            [item for item in sentiment_data if item.get('sentiment_label', '').lower() == 'negative'],
            key=lambda x: x.get('sentiment_score', 0)
        )[:5]
        
        for item in negative_items:
            with st.expander(f"Score: {item.get('sentiment_score', 0):.2f} - {item.get('brand', 'Unknown')}"):
                st.write(f"**Platform:** {item.get('platform', 'Unknown')}")
                st.write(f"**Title:** {item.get('title', 'N/A')[:100]}...")
                st.write(f"**Link:** {item.get('url', 'N/A')}")

def show_brand_comparison(data):
    """Brand comparison analysis"""
    st.markdown("## 🔍 Brand Comparison Analysis")
    
    if 'classified' not in data:
        st.warning("⚠️ No classification data available.")
        return
    
    # Get all brands
    brands = {}
    for item in data['classified']:
        brand = item.get('brand', 'Unknown')
        if brand not in brands:
            brands[brand] = []
        brands[brand].append(item)
    
    # Brand selector
    col1, col2 = st.columns([1, 3])
    with col1:
        selected_brands = st.multiselect(
            "Select brands to compare:",
            options=list(brands.keys()),
            default=['Atomberg'] + [b for b in list(brands.keys())[:2] if b != 'Atomberg']
        )
    
    if not selected_brands:
        st.info("Please select at least one brand to compare.")
        return
    
    # Comparison metrics
    st.markdown("### 📊 Key Metrics Comparison")
    
    comparison_data = []
    for brand in selected_brands:
        # Get all items for this brand from classified data
        brand_items = brands[brand]
        total_mentions = len(brand_items)
        
        # Get sentiment data for this brand (from scored_results via sentiment key)
        brand_sentiment_items = []
        if 'sentiment' in data:
            brand_sentiment_items = [s for s in data['sentiment'] if s.get('brand') == brand]
        
        # Calculate sentiment metrics
        if brand_sentiment_items:
            avg_sentiment = sum(s.get('sentiment_score', 0) for s in brand_sentiment_items) / len(brand_sentiment_items)
            positive_count = sum(1 for s in brand_sentiment_items if s.get('sentiment_label', '').lower() == 'positive')
            positive_pct = (positive_count / len(brand_sentiment_items)) * 100
            
            # Calculate engagement (only for items with actual engagement)
            engagement_scores = [s.get('engagement_score', 0) for s in brand_sentiment_items if s.get('engagement_score', 0) > 0]
            avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        else:
            avg_sentiment = 0
            positive_pct = 0
            avg_engagement = 0
        
        comparison_data.append({
            'Brand': brand,
            'Mentions': total_mentions,
            'Avg Sentiment': round(avg_sentiment, 2),
            'Positive %': round(positive_pct, 1),
            'Avg Engagement': round(avg_engagement, 0)
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Display as styled table
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Mentions Comparison")
        fig = px.bar(comparison_df, x='Brand', y='Mentions',
                    color='Brand',
                    color_discrete_sequence=px.colors.qualitative.Set3)
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 😊 Sentiment Comparison")
        fig = px.bar(comparison_df, x='Brand', y='Avg Sentiment',
                    color='Avg Sentiment',
                    color_continuous_scale='RdYlGn')
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Radar chart comparison
    st.markdown("### 🎯 Multi-dimensional Comparison")
    
    # Normalize metrics for radar chart
    metrics_for_radar = ['Mentions', 'Avg Sentiment', 'Positive %', 'Avg Engagement']
    
    fig = go.Figure()
    
    for _, row in comparison_df.iterrows():
        values = [
            row['Mentions'] / comparison_df['Mentions'].max() * 100,
            (row['Avg Sentiment'] + 1) * 50,  # Normalize from -1,1 to 0,100
            row['Positive %'],
            row['Avg Engagement'] / comparison_df['Avg Engagement'].max() * 100 if comparison_df['Avg Engagement'].max() > 0 else 0
        ]
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics_for_radar,
            fill='toself',
            name=row['Brand']
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

def show_insights(data):
    """Insights and recommendations page"""
    st.markdown("## 💡 Insights & Recommendations")
    
    if 'insights' not in data:
        st.warning("⚠️ No insights data available.")
        return
    
    insights = data['insights']
    
    # Summary metrics
    if 'summary' in insights:
        summary = insights['summary']
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Documents Analyzed", summary.get('total_documents', 0))
        with col2:
            st.metric("Key Findings", summary.get('top_findings_count', 0))
        with col3:
            st.metric("Keyword Opportunities", summary.get('keyword_opportunities_count', 0))
        
        st.markdown(f"**Generated:** {summary.get('generated_at', 'N/A')}")
    
    st.markdown("---")
    
    # Key Findings
    st.markdown("### 🎯 Key Findings")
    
    if 'findings' in insights and insights['findings']:
        for i, finding in enumerate(insights['findings'], 1):
            priority_color = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(finding.get('priority', 'Medium'), '⚪')
            
            with st.expander(f"{priority_color} {finding.get('title', 'Insight')} - Priority: {finding.get('priority', 'Medium')}"):
                st.markdown(f"**Confidence:** {finding.get('confidence', 0):.0%}")
                st.markdown(f"**Analysis:** {finding.get('body', 'No details')}")
                
                if 'actions' in finding and finding['actions']:
                    st.markdown("**Recommended Actions:**")
                    for action in finding['actions']:
                        impact = action.get('impact', 'Medium')
                        effort = action.get('effort', 'Medium')
                        st.markdown(f"- {action.get('text', '')} (Impact: **{impact}**, Effort: **{effort}**)")
    else:
        st.info("No findings generated yet. Please run the insights agent.")
    
    st.markdown("---")
    
    # Keyword opportunities
    st.markdown("### 🔑 Keyword Opportunities")
    
    if 'keyword_opportunities' in insights and insights['keyword_opportunities']:
        for opp in insights['keyword_opportunities']:
            with st.expander(f"🔍 {opp.get('keyword', 'Unknown')} - {opp.get('mentions', 0)} mentions"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Share of Voice", f"{opp.get('SoV', 0):.1%}")
                with col2:
                    st.metric("Avg Sentiment", f"{opp.get('avg_sentiment', 0):.2f}")
                
                if 'suggestions' in opp and opp['suggestions']:
                    st.markdown("**Content Suggestions:**")
                    for sug in opp['suggestions']:
                        st.markdown(f"- {sug.get('text', '')} (Impact: **{sug.get('impact', 'Medium')}**, Effort: **{sug.get('effort', 'Medium')}**)")
    else:
        st.info("No keyword opportunities identified.")
    
    st.markdown("---")
    
    # Action Summary
    st.markdown("### 📋 Action Summary")
    
    if 'findings' in insights and insights['findings']:
        all_actions = []
        for finding in insights['findings']:
            if 'actions' in finding:
                for action in finding['actions']:
                    all_actions.append({
                        'Finding': finding.get('title', 'Unknown'),
                        'Action': action.get('text', ''),
                        'Impact': action.get('impact', 'Medium'),
                        'Effort': action.get('effort', 'Medium'),
                        'Priority': finding.get('priority', 'Medium')
                    })
        
        if all_actions:
            actions_df = pd.DataFrame(all_actions)
            
            # Color code by priority with better contrast
            def highlight_priority(row):
                colors = {
                    'High': 'background-color: #ff4444; color: white; font-weight: bold',
                    'Medium': 'background-color: #ffa500; color: black; font-weight: bold',
                    'Low': 'background-color: #44aa44; color: white; font-weight: bold'
                }
                return [colors.get(row['Priority'], '')] * len(row)
            
            st.dataframe(
                actions_df.style.apply(highlight_priority, axis=1),
                use_container_width=True,
                hide_index=True
            )
    
    # Download report
    st.markdown("---")
    st.markdown("### 📄 Export Report")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Download Full Report (JSON)"):
            st.download_button(
                label="Download JSON",
                data=json.dumps(insights, indent=4),
                file_name=f"atomberg_insights_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📈 Download Metrics (CSV)"):
            if 'metrics' in data:
                metrics_df = pd.DataFrame([data['metrics']])
                csv = metrics_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"atomberg_metrics_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

def show_raw_data(data):
    """Raw data explorer"""
    st.markdown("## 📋 Raw Data Explorer")
    
    tabs = st.tabs(["🔍 Search Results", "🏷️ Brand Classification", "😊 Sentiment Data", "📊 Metrics"])
    
    with tabs[0]:
        if 'raw' in data:
            st.markdown(f"**Total Results:** {len(data['raw'])}")
            
            # Filters
            col1, col2 = st.columns(2)
            with col1:
                search_term = st.text_input("Search in titles/snippets:")
            with col2:
                source_filter = st.multiselect(
                    "Filter by platform:",
                    options=list(set(item.get('platform', 'Unknown') for item in data['raw']))
                )
            
            # Filter data
            filtered_data = data['raw']
            if search_term:
                filtered_data = [item for item in filtered_data 
                               if search_term.lower() in item.get('title', '').lower() 
                               or search_term.lower() in item.get('snippet', '').lower()]
            if source_filter:
                filtered_data = [item for item in filtered_data 
                               if item.get('platform') in source_filter]
            
            # Display
            st.markdown(f"**Showing {len(filtered_data)} results**")
            
            for i, item in enumerate(filtered_data[:50], 1):  # Limit to 50
                with st.expander(f"{i}. {item.get('title', 'No title')[:80]}..."):
                    st.write(f"**Platform:** {item.get('platform', 'Unknown')}")
                    st.write(f"**Keyword:** {item.get('keyword', 'N/A')}")
                    st.write(f"**Link:** {item.get('url', 'N/A')}")
                    st.write(f"**Snippet:** {item.get('snippet', 'N/A')[:200]}...")
            
            # Download
            if st.button("Download Raw Data"):
                st.download_button(
                    label="Download JSON",
                    data=json.dumps(filtered_data, indent=4),
                    file_name="raw_search_results.json",
                    mime="application/json"
                )
        else:
            st.info("No raw search data available.")
    
    with tabs[1]:
        if 'classified' in data:
            st.markdown(f"**Total Classified:** {len(data['classified'])}")
            
            # Brand distribution
            brands = {}
            for item in data['classified']:
                brand = item.get('brand', 'Unknown')
                brands[brand] = brands.get(brand, 0) + 1
            
            brand_df = pd.DataFrame(list(brands.items()), columns=['Brand', 'Count'])
            brand_df = brand_df.sort_values('Count', ascending=False)
            
            st.dataframe(brand_df, use_container_width=True, hide_index=True)
            
            # Sample data
            st.markdown("**Sample Classified Results:**")
            for i, item in enumerate(data['classified'][:20], 1):
                with st.expander(f"{i}. {item.get('brand', 'Unknown')} - {item.get('title', 'No title')[:60]}..."):
                    st.json(item)
        else:
            st.info("No classification data available.")
    
    with tabs[2]:
        if 'sentiment' in data:
            st.markdown(f"**Total Analyzed:** {len(data['sentiment'])}")
            
            sentiment_df = pd.DataFrame(data['sentiment'])
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Avg Sentiment Score", 
                         f"{sentiment_df['sentiment_score'].mean():.2f}")
            with col2:
                st.metric("Avg Engagement Score", 
                         f"{sentiment_df['engagement_score'].mean():.2f}")
            with col3:
                st.metric("Avg Compound Score", 
                         f"{sentiment_df['compound_score'].mean():.2f}")
            
            # Show dataframe with selected columns
            display_cols = ['brand', 'platform', 'title', 'sentiment_label', 'sentiment_score', 'engagement_score']
            available_cols = [col for col in display_cols if col in sentiment_df.columns]
            
            st.dataframe(sentiment_df[available_cols].head(100), use_container_width=True)
            
            # Download
            csv = sentiment_df.to_csv(index=False)
            st.download_button(
                label="Download Sentiment Data (CSV)",
                data=csv,
                file_name="sentiment_analysis.csv",
                mime="text/csv"
            )
        else:
            st.info("No sentiment data available.")
    
    with tabs[3]:
        if 'metrics' in data:
            st.markdown("**SOV Metrics:**")
            st.json(data['metrics'])
            
            # Download
            st.download_button(
                label="Download Metrics (JSON)",
                data=json.dumps(data['metrics'], indent=4),
                file_name="sov_metrics.json",
                mime="application/json"
            )
        else:
            st.info("No metrics data available.")

if __name__ == "__main__":
    main()