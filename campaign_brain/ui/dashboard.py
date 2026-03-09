"""
Streamlit Dashboard for Campaign Brain
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.builder import run_campaign_brain
from tools.sql_tool import SQLTool
from tools.analytics import TrendAnalyzer
from config import Config
from agents.rag_agent import get_rag_agent

# Page config
st.set_page_config(
    page_title="PepsiCo Campaign Brain",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── PepsiCo Brand Colors ─────────────────────────────────────────────────────
# Primary Blue : #003087   Red accent : #E31837   Light Blue : #0093D0
# Dark Navy    : #001F5B   White      : #FFFFFF
# ─────────────────────────────────────────────────────────────────────────────

# Custom CSS
st.markdown("""
<style>
    /* ── Global font ── */
    html, body, [class*="css"] {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }

    /* ── Top banner header ── */
    .pep-banner {
        background: linear-gradient(135deg, #003087 0%, #0093D0 100%);
        border-radius: 0.75rem;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
    }
    .pep-banner .logo-circle {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(180deg, #E31837 50%, #003087 50%);
        border: 3px solid #ffffff;
        flex-shrink: 0;
    }
    .pep-banner .title-block h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .pep-banner .title-block p {
        color: #c8d9f0;
        font-size: 0.9rem;
        margin: 0.15rem 0 0 0;
    }

    /* ── Sidebar branding ── */
    .sidebar-brand {
        background: linear-gradient(135deg, #003087, #0093D0);
        color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
        font-weight: 700;
        font-size: 1.1rem;
        letter-spacing: 0.5px;
        margin-bottom: 1rem;
    }
    .sidebar-brand span {
        display: block;
        font-size: 0.75rem;
        font-weight: 400;
        color: #c8d9f0;
        margin-top: 2px;
    }

    /* ── Metric card ── */
    .metric-card {
        background-color: #e8edf5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #003087;
    }

    /* ── Status boxes ── */
    .success-box {
        background-color: #e6f4ea;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #0093D0;
    }
    .warning-box {
        background-color: #fff0f1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #E31837;
    }

    /* ── Accent divider ── */
    .pep-divider {
        height: 3px;
        background: linear-gradient(90deg, #003087, #E31837, #0093D0);
        border: none;
        border-radius: 2px;
        margin: 1rem 0;
    }

    /* ── Primary button override ── */
    div.stButton > button[kind="primary"] {
        background-color: #003087;
        border-color: #003087;
        color: #ffffff;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #0093D0;
        border-color: #0093D0;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'campaign_results' not in st.session_state:
        st.session_state.campaign_results = None
    if 'sql_tool' not in st.session_state:
        st.session_state.sql_tool = SQLTool()
    if 'trend_analyzer' not in st.session_state:
        st.session_state.trend_analyzer = TrendAnalyzer()
    if 'rag_agent' not in st.session_state:
        st.session_state.rag_agent = None
    if 'rag_ready' not in st.session_state:
        st.session_state.rag_ready = False
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []

def main():
    """Main dashboard function"""
    init_session_state()
    
    # ── PepsiCo branded banner ──────────────────────────────────────────────
    st.markdown("""
    <div class="pep-banner">
        <div class="logo-circle"></div>
        <div class="title-block">
            <h1>PepsiCo Campaign Brain</h1>
            <p>AI-Powered Multi-Agent Campaign Planning &nbsp;|&nbsp; PepsiCo Hackathon 2026</p>
        </div>
    </div>
    <hr class="pep-divider">
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        PepsiCo Campaign Brain
        <span>Hackathon 2026</span>
    </div>
    """, unsafe_allow_html=True)
    page = st.sidebar.selectbox(
        "Navigate to",
        ["🚀 Campaign Planner", "📊 Analytics Dashboard", "🔍 Campaign History", "💬 Campaign Analyst", "⚙️ Settings"]
    )
    
    if page == "🚀 Campaign Planner":
        campaign_planner_page()
    elif page == "📊 Analytics Dashboard":
        analytics_dashboard_page()
    elif page == "🔍 Campaign History":
        campaign_history_page()
    elif page == "💬 Campaign Analyst":
        campaign_analyst_page()
    elif page == "⚙️ Settings":
        settings_page()

def campaign_planner_page():
    """Campaign planning interface"""
    st.header("🚀 Create New Campaign")
    
    # Campaign input form
    with st.form("campaign_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Product Launch")
            campaign_objective = st.text_area(
                "Campaign Objective", 
                placeholder="Describe your campaign goals and objectives..."
            )
            target_audience = st.text_area(
                "Target Audience",
                placeholder="Describe your target audience in detail..."
            )
        
        with col2:
            budget = st.number_input(
                "Campaign Budget ($)", 
                min_value=1000, 
                max_value=10000000, 
                value=50000,
                step=1000
            )
            duration = st.number_input(
                "Campaign Duration (days)", 
                min_value=1, 
                max_value=365, 
                value=30
            )
            brand_guidelines = st.text_area(
                "Brand Guidelines (optional)",
                placeholder="Any specific brand guidelines or constraints..."
            )
        
        submitted = st.form_submit_button("🧠 Generate Campaign Plan", type="primary")
    
    if submitted:
        if not campaign_objective or not target_audience:
            st.error("❌ Please fill in Campaign Objective and Target Audience")
            return
        
        # Show processing status
        with st.spinner("🔍 Campaign Brain is analyzing and planning..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            progress_updates = [
                (20, "🔍 Trend Scout analyzing market trends..."),
                (40, "🎯 Strategist developing campaign strategy..."),
                (60, "👥 Persona Simulator creating audience insights..."),
                (80, "🎨 Designer crafting creative concepts..."),
                (100, "⚡ Executor finalizing implementation plan...")
            ]
            
            for progress, message in progress_updates:
                progress_bar.progress(progress)
                status_text.text(message)
                # In a real app, you'd get actual updates from the workflow
            
            try:
                # Run the campaign brain workflow
                results = run_campaign_brain(
                    campaign_objective=campaign_objective,
                    target_audience=target_audience,
                    budget=float(budget),
                    duration_days=int(duration),
                    brand_guidelines=brand_guidelines
                )
                
                # Store results in session state
                st.session_state.campaign_results = {
                    "name": campaign_name,
                    "results": results,
                    "created_at": datetime.now()
                }

                # Auto-build RAG knowledge base in the background
                try:
                    db_path = st.session_state.sql_tool.db_path
                    rag = get_rag_agent()
                    n_chunks = rag.build_knowledge_base(
                        campaign_state=results,
                        db_path=db_path,
                    )
                    st.session_state.rag_agent = rag
                    st.session_state.rag_ready = True
                    st.session_state.chat_messages = []  # reset chat for new campaign
                    st.info(f"💬 Campaign Analyst ready with {n_chunks} knowledge chunks. Navigate to 'Campaign Analyst' to ask questions.")
                except Exception as rag_err:
                    st.warning(f"⚠️ Campaign Analyst could not be initialised: {rag_err}")
                
                # Save to database
                campaign_data = {
                    "name": campaign_name,
                    "objective": campaign_objective,
                    "target_audience": target_audience,
                    "budget": budget,
                    "duration_days": duration,
                    "start_date": datetime.now().strftime("%Y-%m-%d"),
                    "status": "planned"
                }
                
                campaign_id = st.session_state.sql_tool.save_campaign(campaign_data)
                
                progress_bar.progress(100)
                status_text.text("✅ Campaign plan completed!")
                
                st.success("🎉 Campaign Brain has generated your comprehensive campaign plan!")
                
            except Exception as e:
                st.error(f"❌ Error generating campaign plan: {str(e)}")
                return
    
    # Display results if available
    if st.session_state.campaign_results:
        display_campaign_results(st.session_state.campaign_results)

def display_campaign_results(campaign_data):
    """Display the generated campaign plan results"""
    st.header("📋 Campaign Plan Results")
    
    results = campaign_data["results"]
    
    # Campaign overview
    st.subheader("📊 Campaign Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Budget", f"${results.get('budget', 0):,.2f}")
    with col2:
        st.metric("Duration", f"{results.get('duration_days', 0)} days")
    with col3:
        st.metric("Agents Completed", len(results.get('completed_agents', [])))
    with col4:
        st.metric("Status", "✅ Ready" if results.get('presentation_ready') else "⏳ In Progress")
    
    # Tabbed results display
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Market Trends", "🎯 Strategy", "👥 Personas", "🎨 Creative", "⚡ Execution"
    ])
    
    with tab1:
        display_trend_analysis(results)
    
    with tab2:
        display_strategy(results)
    
    with tab3:
        display_personas(results)
    
    with tab4:
        display_creative_concepts(results)
    
    with tab5:
        display_execution_plan(results)
    
    # Download options
    st.subheader("💾 Export Campaign Plan")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download as JSON"):
            json_data = json.dumps(results.get('final_campaign_plan', {}), indent=2, default=str)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{campaign_data['name']}_plan.json",
                mime="application/json"
            )
    
    with col2:
        if st.button("📊 Generate Summary Report"):
            generate_summary_report(campaign_data)

def display_trend_analysis(results):
    """Display trend analysis results"""
    trends = results.get('current_trends', [])
    
    if trends:
        st.write("### 📈 Current Market Trends")
        
        # Trends dataframe
        trends_df = pd.DataFrame([
            {
                "Trend": trend.get('name', 'Unknown'),
                "Relevance": trend.get('relevance', 'medium'),
                "Impact": trend.get('impact', 'medium')
            }
            for trend in trends[:10]
        ])
        
        st.dataframe(trends_df, use_container_width=True)
        
        # Competitor analysis
        competitor_analysis = results.get('competitor_analysis', {})
        if competitor_analysis:
            st.write("### 🏢 Competitive Landscape")
            
            competitors = competitor_analysis.get('top_competitors', [])
            if competitors:
                st.write("**Top Competitors:**")
                for i, competitor in enumerate(competitors[:5], 1):
                    st.write(f"{i}. {competitor}")
            
            strategies = competitor_analysis.get('strategies', [])
            if strategies:
                st.write("**Competitive Strategies:**")
                for strategy in strategies[:3]:
                    st.write(f"• {strategy}")
    else:
        st.info("No trend data available")

def display_strategy(results):
    """Display campaign strategy"""
    strategy = results.get('campaign_strategy', '')
    messaging = results.get('key_messaging', [])
    channels = results.get('channel_recommendations', [])
    metrics = results.get('success_metrics', [])
    
    if strategy:
        st.write("### 🎯 Campaign Strategy")
        st.write(strategy)
    
    if messaging:
        st.write("### 💬 Key Messages")
        for i, message in enumerate(messaging, 1):
            st.write(f"{i}. {message}")
    
    if channels:
        st.write("### 📱 Recommended Channels")
        
        # Create channels dataframe
        channels_df = pd.DataFrame([
            {
                "Channel": channel.get('name', 'Unknown'),
                "Budget": f"${channel.get('budget_allocation', 0):,.0f}",
                "Expected Reach": f"{channel.get('expected_reach', 0):,}"
            }
            for channel in channels
        ])
        
        st.dataframe(channels_df, use_container_width=True)
        
        # Budget allocation pie chart
        if len(channels) > 1:
            fig = px.pie(
                values=[channel.get('budget_allocation', 0) for channel in channels],
                names=[channel.get('name', 'Unknown') for channel in channels],
                title="Budget Allocation by Channel",
                color_discrete_sequence=["#003087", "#E31837", "#0093D0", "#001F5B", "#66A3D2", "#F5A0A0"]
            )
            fig.update_layout(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff")
            st.plotly_chart(fig, use_container_width=True)
    
    if metrics:
        st.write("### 📊 Success Metrics")
        for metric in metrics:
            st.write(f"• {metric}")

def display_personas(results):
    """Display persona analysis"""
    personas = results.get('persona_profiles', [])
    pain_points = results.get('pain_points', [])
    motivations = results.get('motivation_drivers', [])
    
    if personas:
        st.write("### 👥 Target Personas")
        
        for i, persona in enumerate(personas, 1):
            with st.expander(f"Persona {i}: {persona.get('name', 'Unknown')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Demographics:**")
                    st.write(f"Age: {persona.get('age', 'Unknown')}")
                    st.write(f"Occupation: {persona.get('occupation', 'Unknown')}")
                    
                    if persona.get('goals'):
                        st.write("**Goals:**")
                        for goal in persona.get('goals', [])[:3]:
                            st.write(f"• {goal}")
                
                with col2:
                    if persona.get('behaviors'):
                        st.write("**Behaviors:**")
                        for behavior in persona.get('behaviors', [])[:3]:
                            st.write(f"• {behavior}")
                    
                    if persona.get('preferred_channels'):
                        st.write("**Preferred Channels:**")
                        st.write(", ".join(persona.get('preferred_channels', [])))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if pain_points:
            st.write("### 😰 Pain Points")
            for pain in pain_points[:5]:
                st.write(f"• {pain}")
    
    with col2:
        if motivations:
            st.write("### 🎯 Motivations")
            for motivation in motivations[:5]:
                st.write(f"• {motivation}")

def display_creative_concepts(results):
    """Display creative concepts and guidelines"""
    concepts = results.get('creative_concepts', [])
    guidelines = results.get('visual_guidelines', '')
    content_ideas = results.get('content_ideas', [])
    
    if concepts:
        st.write("### 🎨 Creative Concepts")
        
        for i, concept in enumerate(concepts, 1):
            with st.expander(f"Concept {i}: {concept.get('name', 'Creative Concept')}"):
                st.write(f"**Description:** {concept.get('description', 'No description')}")
                
                if concept.get('colors'):
                    st.write(f"**Colors:** {concept.get('colors')}")
                
                if concept.get('typography'):
                    st.write(f"**Typography:** {concept.get('typography')}")
                
                if concept.get('tone'):
                    st.write(f"**Tone:** {concept.get('tone')}")
    
    if guidelines:
        st.write("### 📋 Visual Guidelines")
        st.write(guidelines)
    
    if content_ideas:
        st.write("### 💡 Content Ideas")
        
        content_df = pd.DataFrame([
            {
                "Idea": idea.get('idea', 'Unknown')[:50] + "..." if len(idea.get('idea', '')) > 50 else idea.get('idea', 'Unknown'),
                "Type": idea.get('type', 'unknown'),
                "Effort": idea.get('effort', 'medium'),
                "Impact": idea.get('impact', 'medium')
            }
            for idea in content_ideas[:10]
        ])
        
        st.dataframe(content_df, use_container_width=True)

def display_execution_plan(results):
    """Display execution plan and timeline"""
    timeline = results.get('campaign_timeline', {})
    resources = results.get('resource_allocation', {})
    steps = results.get('implementation_steps', [])
    risks = results.get('risk_mitigation', [])
    
    if timeline:
        st.write("### 📅 Campaign Timeline")
        
        for phase, activities in timeline.items():
            with st.expander(f"{phase.replace('_', ' ').title()}"):
                for activity in activities:
                    st.write(f"• {activity}")
    
    if resources:
        st.write("### 💼 Resource Requirements")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if resources.get('team_requirements'):
                st.write("**Team:**")
                for requirement in resources.get('team_requirements'):
                    st.write(f"• {requirement}")
        
        with col2:
            if resources.get('tools_needed'):
                st.write("**Tools & Platforms:**")
                for tool in resources.get('tools_needed'):
                    st.write(f"• {tool}")
        
        if resources.get('budget_breakdown'):
            st.write("**Budget Breakdown:**")
            for item in resources.get('budget_breakdown'):
                st.write(f"• {item}")
    
    if steps:
        st.write("### ✅ Implementation Steps")
        
        steps_df = pd.DataFrame([
            {
                "Task": step.get('task', 'Unknown')[:50] + "..." if len(step.get('task', '')) > 50 else step.get('task', 'Unknown'),
                "Priority": step.get('priority', 'medium'),
                "Assignee": step.get('assignee', 'Unknown'),
                "Deadline": step.get('deadline', 'TBD')
            }
            for step in steps[:15]
        ])
        
        st.dataframe(steps_df, use_container_width=True)
    
    if risks:
        st.write("### ⚠️ Risk Mitigation")
        for risk in risks:
            st.write(f"• {risk}")


# ---------------------------------------------------------------------------
# 💬 Campaign Analyst – RAG Chatbot Page
# ---------------------------------------------------------------------------

def campaign_analyst_page():
    """RAG-powered chatbot that answers questions about the current campaign analysis."""
    st.header("💬 Campaign Analyst")
    st.markdown(
        "Ask any question about your campaign analysis – trends, personas, strategy, "
        "creative concepts, or execution plan. The analyst has read everything."
    )

    # ── Status banner ────────────────────────────────────────────────────────
    if not st.session_state.get("rag_ready"):
        st.warning(
            "⚠️ No campaign data in memory yet.  \n"
            "Please **run a campaign first** on the 🚀 Campaign Planner page, "
            "then come back here to chat."
        )

        # Still allow manual (re)build from DB if a campaign was run earlier
        st.divider()
        st.subheader("📂 Load from Database")
        if st.button("🔄 Build knowledge base from existing DB records"):
            with st.spinner("Building knowledge base from database …"):
                try:
                    sql = st.session_state.get("sql_tool")
                    db_path = sql.db_path if sql else "campaign_data.db"
                    rag = get_rag_agent()
                    n = rag.build_knowledge_base(db_path=db_path)
                    st.session_state.rag_agent = rag
                    st.session_state.rag_ready = True
                    st.session_state.chat_messages = []
                    st.success(f"✅ Knowledge base ready with {n} chunks from the database.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to build knowledge base: {e}")
        return

    rag: "CampaignRAGAgent" = st.session_state.rag_agent

    # ── Knowledge base info bar ──────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("📄 Knowledge Chunks", len(rag.documents))
    sources = list({m.get("source", "Unknown").split(" –")[0] for m in rag.metadata})
    col2.metric("📚 Sources Indexed", len(sources))
    col3.metric("💬 Messages in Chat", len(st.session_state.chat_messages))

    with st.expander("🗂️ Indexed Sources", expanded=False):
        all_sources = sorted({m.get("source", "Unknown") for m in rag.metadata})
        for src in all_sources:
            st.write(f"• {src}")

    st.divider()

    # ── Chat history ─────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(msg["content"])
            else:
                with st.chat_message("assistant", avatar="🧠"):
                    st.markdown(msg["content"])

    # ── Input box ────────────────────────────────────────────────────────────
    user_question = st.chat_input(
        "Ask anything about your campaign… e.g. 'Which channel has the highest budget allocation?'"
    )

    if user_question:
        # Append user message
        st.session_state.chat_messages.append({"role": "user", "content": user_question})

        # Show user message immediately
        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_question)

        # Generate answer
        with st.spinner("🔍 Retrieving relevant context and generating answer …"):
            answer = rag.ask(user_question)

        # Append and display assistant answer
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
        with chat_container:
            with st.chat_message("assistant", avatar="🧠"):
                st.markdown(answer)

    # ── Utility buttons ──────────────────────────────────────────────────────
    st.divider()
    col_a, col_b, col_c = st.columns(3)

    with col_a:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_messages = []
            st.rerun()

    with col_b:
        if st.button("🔄 Rebuild Knowledge Base"):
            with st.spinner("Rebuilding …"):
                try:
                    sql = st.session_state.get("sql_tool")
                    db_path = sql.db_path if sql else "campaign_data.db"
                    results = (
                        st.session_state.campaign_results["results"]
                        if st.session_state.campaign_results
                        else None
                    )
                    new_rag = get_rag_agent()
                    n = new_rag.build_knowledge_base(
                        campaign_state=results, db_path=db_path
                    )
                    st.session_state.rag_agent = new_rag
                    st.session_state.rag_ready = True
                    st.session_state.chat_messages = []
                    st.success(f"✅ Rebuilt with {n} chunks.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")

    with col_c:
        if st.session_state.chat_messages:
            # Export chat transcript
            transcript = "\n\n".join(
                f"**{m['role'].upper()}:** {m['content']}"
                for m in st.session_state.chat_messages
            )
            st.download_button(
                "📥 Download Transcript",
                data=transcript,
                file_name="campaign_analyst_chat.md",
                mime="text/markdown",
            )

    # ── Suggested questions ──────────────────────────────────────────────────
    st.divider()
    st.subheader("💡 Suggested Questions")
    suggestions = [
        "What are the top 3 market trends identified for this campaign?",
        "Which channel has the highest budget allocation and why?",
        "Summarise all persona profiles and their key pain points.",
        "What is the overall campaign strategy recommended by the Strategist?",
        "What are the main risk mitigation steps in the execution plan?",
        "Which creative concept is best suited for social media?",
        "What are the success metrics defined for this campaign?",
        "Describe the user journey map for the primary persona.",
    ]
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        if cols[idx % 2].button(suggestion, key=f"sugg_{idx}"):
            st.session_state.chat_messages.append({"role": "user", "content": suggestion})
            with st.spinner("Generating answer …"):
                answer = rag.ask(suggestion)
            st.session_state.chat_messages.append({"role": "assistant", "content": answer})
            st.rerun()


def analytics_dashboard_page():
    """Analytics dashboard for campaign performance"""
    st.header("📊 Analytics Dashboard")
    
    # Sample analytics (in a real app, you'd load actual data)
    st.subheader("Campaign Performance Overview")
    
    # Mock performance data
    mock_data = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Impressions': np.random.randint(10000, 50000, 30),
        'Clicks': np.random.randint(500, 2000, 30),
        'Conversions': np.random.randint(20, 100, 30)
    })
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    # PepsiCo-themed Plotly layout defaults
    _pep_layout = dict(
        paper_bgcolor="#ffffff",
        plot_bgcolor="#e8edf5",
        font=dict(color="#001F5B"),
        title_font=dict(color="#003087", size=16),
    )

    with col1:
        fig_impressions = px.line(
            mock_data,
            x='Date',
            y='Impressions',
            title='Daily Impressions',
            color_discrete_sequence=["#003087"]
        )
        fig_impressions.update_layout(**_pep_layout)
        fig_impressions.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig_impressions, use_container_width=True)

    with col2:
        fig_conversions = px.line(
            mock_data,
            x='Date',
            y='Conversions',
            title='Daily Conversions',
            color_discrete_sequence=["#E31837"]
        )
        fig_conversions.update_layout(**_pep_layout)
        fig_conversions.update_traces(line=dict(width=2.5))
        st.plotly_chart(fig_conversions, use_container_width=True)
    
    # Performance metrics
    st.subheader("Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Impressions", "1,250,000", "+15%")
    with col2:
        st.metric("Total Clicks", "45,600", "+8%")
    with col3:
        st.metric("Conversion Rate", "3.2%", "+0.5%")
    with col4:
        st.metric("Cost per Acquisition", "$24.50", "-$2.10")

def campaign_history_page():
    """Campaign history and management"""
    st.header("🔍 Campaign History")
    
    # In a real app, you'd load actual campaign history from the database
    st.info("Campaign history functionality would display previously created campaigns here.")
    
    # Mock campaign list
    campaigns = [
        {"name": "Summer Launch", "status": "Completed", "budget": 50000, "roi": "185%"},
        {"name": "Holiday Sales", "status": "Active", "budget": 75000, "roi": "145%"},
        {"name": "Brand Awareness", "status": "Planned", "budget": 30000, "roi": "TBD"}
    ]
    
    campaigns_df = pd.DataFrame(campaigns)
    st.dataframe(campaigns_df, use_container_width=True)

def settings_page():
    """Settings and configuration"""
    st.header("⚙️ Settings")
    
    st.subheader("🔑 API Configuration")
    
    # Display current configuration (without showing sensitive keys)
    st.write("**Current Model Configuration:**")
    st.write(f"Model: {Config.MODEL_NAME}")
    st.write(f"Base URL: {Config.BASE_URL}")
    st.write(f"API Key: {'*' * 20}{Config.API_KEY[-4:] if len(Config.API_KEY) > 4 else '****'}")
    
    st.subheader("🎛️ Campaign Defaults")
    default_budget = st.number_input("Default Budget", value=50000)
    default_duration = st.number_input("Default Duration (days)", value=30)
    
    if st.button("Save Settings"):
        st.success("Settings saved successfully!")

def generate_summary_report(campaign_data):
    """Generate and display a summary report"""
    st.subheader("📋 Campaign Summary Report")
    
    results = campaign_data["results"]
    
    # Create a comprehensive summary
    summary = f"""
# Campaign Brain Summary Report

**Campaign Name:** {campaign_data['name']}
**Generated:** {campaign_data['created_at'].strftime('%Y-%m-%d %H:%M')}

## Campaign Overview
- **Objective:** {results.get('campaign_objective', 'N/A')}
- **Budget:** ${results.get('budget', 0):,.2f}
- **Duration:** {results.get('duration_days', 0)} days
- **Target Audience:** {results.get('target_audience', 'N/A')}

## Strategy
{results.get('campaign_strategy', 'No strategy available')}

## Key Insights
- **Trends Identified:** {len(results.get('current_trends', []))}
- **Personas Created:** {len(results.get('persona_profiles', []))}
- **Creative Concepts:** {len(results.get('creative_concepts', []))}
- **Implementation Steps:** {len(results.get('implementation_steps', []))}

## Success Metrics
{chr(10).join(f"- {metric}" for metric in results.get('success_metrics', []))}

## Next Steps
1. Review and approve campaign plan
2. Begin creative asset production
3. Set up tracking and analytics
4. Launch campaign according to timeline
5. Monitor performance and optimize

---
*Generated by Campaign Brain AI*
"""
    
    st.text_area("Summary Report", summary, height=400)
    
    st.download_button(
        label="📄 Download Report",
        data=summary,
        file_name=f"{campaign_data['name']}_summary.md",
        mime="text/markdown"
    )

if __name__ == "__main__":
    # Import numpy for mock data
    import numpy as np
    main()