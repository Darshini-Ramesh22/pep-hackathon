# PepsiCo Campaign Brain

**AI-Powered Multi-Agent Campaign Planning System**  
*Built for PepsiCo Hackathon 2026*

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

Multiple AI agents collaborate through LangGraph to deliver end-to-end campaign strategies — trend analysis, audience personas, creative concepts, and execution timelines.

## Agents

| Agent | Role |
|-------|------|
| Trend Scout | Market trends & competitive landscape |
| Strategist | Campaign strategy & channel mix |
| Persona Simulator | Audience personas & journey maps |
| Designer | Creative concepts & visual guidelines |
| Executor | Timelines, budgets & implementation plans |

## Setup

```bash
pip install -r requirements.txt
```

Add your key to `.env`:

```bash
AI_GATEWAY_API_KEY=sk-your-key-here
DATABASE_URL=sqlite:///campaign_data.db
```

## Run Locally

```bash
streamlit run streamlit_app.py
```

Opens at `http://localhost:8501`. The terminal also prints a **Network URL** (LAN) and **External URL**.

## Deploy to Streamlit Cloud

1. Push to GitHub (`.gitignore` already excludes `.env` and secrets):
   ```bash
   git init && git add . && git commit -m "PepsiCo Campaign Brain"
   git remote add origin https://github.com/<user>/campaign_brain.git
   git push -u origin main
   ```

2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**  
   Set **Main file path** to `streamlit_app.py` and click **Deploy**.

3. Under **Settings → Secrets**, add:
   ```toml
   AI_GATEWAY_API_KEY = "sk-your-key-here"
   DATABASE_URL       = "sqlite:///campaign_data.db"
   ```

Your app goes live at `https://<app-name>.streamlit.app`.
