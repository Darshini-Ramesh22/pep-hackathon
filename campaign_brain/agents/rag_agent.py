"""
RAG Agent for Campaign Brain
Collates all analysis outputs (DB, Trends, Personas, Strategy, Design)
into an in-memory knowledge base using text-embedding-3-small embeddings,
then answers human questions via retrieval + LLM generation.
"""
import sys
import os
import json
import math
import sqlite3
import warnings
import requests
import urllib3
from typing import List, Dict, Any, Optional, Tuple

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _json_to_text(data: Any, indent: int = 0) -> str:
    """Recursively convert a JSON-serialisable object to readable text."""
    prefix = "  " * indent
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            key_str = str(k).replace("_", " ").title()
            val_str = _json_to_text(v, indent + 1)
            lines.append(f"{prefix}{key_str}:\n{val_str}")
        return "\n".join(lines)
    elif isinstance(data, list):
        lines = []
        for item in data:
            lines.append(f"{prefix}- {_json_to_text(item, indent + 1)}")
        return "\n".join(lines)
    else:
        return f"{prefix}{data}"


# ---------------------------------------------------------------------------
# Core RAG Agent
# ---------------------------------------------------------------------------

class CampaignRAGAgent:
    """
    In-memory Retrieval-Augmented Generation agent for Campaign Brain.

    Workflow:
      1. build_knowledge_base(campaign_state) – chunks & embeds all analysis
      2. ask(question) – retrieves top-k chunks, generates answer via LLM
    """

    EMBEDDING_URL = "https://api.ai-gateway.tigeranalytics.com/v1/embeddings"
    EMBEDDING_MODEL = "text-embedding-3-small"
    TOP_K = 5

    def __init__(self):
        self.api_key: str = Config.API_KEY
        self.documents: List[str] = []          # raw text chunks
        self.metadata: List[Dict] = []           # source metadata per chunk
        self.embeddings: List[List[float]] = []  # parallel list of vectors
        self.is_ready: bool = False
        self._openai_client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_knowledge_base(
        self,
        campaign_state: Optional[Dict[str, Any]] = None,
        db_path: Optional[str] = None,
    ) -> int:
        """
        Collect documents from all sources and embed them into memory.

        Parameters
        ----------
        campaign_state : dict
            The final CampaignState dict returned by run_campaign_brain().
        db_path : str, optional
            Path to the SQLite database file.

        Returns
        -------
        int  Number of chunks indexed.
        """
        self.documents = []
        self.metadata = []
        self.embeddings = []

        chunks = self._collect_all_chunks(campaign_state, db_path)

        print(f"📚 RAG: Embedding {len(chunks)} document chunks …")
        for text, meta in chunks:
            emb = self._embed(text)
            if emb:
                self.documents.append(text)
                self.metadata.append(meta)
                self.embeddings.append(emb)

        self.is_ready = len(self.documents) > 0
        print(f"✅ RAG knowledge base ready with {len(self.documents)} chunks.")
        return len(self.documents)

    def ask(self, question: str) -> str:
        """
        Answer a question using retrieval + LLM generation.

        Parameters
        ----------
        question : str

        Returns
        -------
        str  The LLM-generated answer grounded in retrieved context.
        """
        if not self.is_ready:
            return (
                "⚠️ The knowledge base is not yet built. "
                "Please run a campaign first so I have data to analyse."
            )

        # 1. Embed the question
        q_emb = self._embed(question)
        if not q_emb:
            return "⚠️ Could not generate embedding for your question. Please try again."

        # 2. Retrieve top-k chunks
        retrieved = self._retrieve(q_emb, k=self.TOP_K)

        # 3. Build context string
        context_parts = []
        for chunk_text, meta, score in retrieved:
            source_label = meta.get("source", "Unknown")
            context_parts.append(f"[Source: {source_label}]\n{chunk_text}")
        context = "\n\n---\n\n".join(context_parts)

        # 4. Generate answer
        return self._generate(question, context)

    # ------------------------------------------------------------------
    # Document Collection
    # ------------------------------------------------------------------

    def _collect_all_chunks(
        self,
        campaign_state: Optional[Dict[str, Any]],
        db_path: Optional[str],
    ) -> List[Tuple[str, Dict]]:
        """Collect and chunk text from every analysis source."""
        chunks: List[Tuple[str, Dict]] = []

        # ── 1. Database records ──────────────────────────────────────────
        chunks.extend(self._chunks_from_database(db_path))

        if campaign_state:
            cs = campaign_state if isinstance(campaign_state, dict) else {}

            # ── 2. Trend Analysis ─────────────────────────────────────────
            chunks.extend(self._chunks_from_trends(cs))

            # ── 3. Persona Analysis ───────────────────────────────────────
            chunks.extend(self._chunks_from_personas(cs))

            # ── 4. Strategist Output ──────────────────────────────────────
            chunks.extend(self._chunks_from_strategy(cs))

            # ── 5. Designer Output ────────────────────────────────────────
            chunks.extend(self._chunks_from_design(cs))

        return chunks

    # ── Source-specific chunkers ─────────────────────────────────────────

    def _chunks_from_database(self, db_path: Optional[str]) -> List[Tuple[str, Dict]]:
        """Pull campaigns, trends, personas rows from SQLite."""
        chunks = []
        resolved = db_path or Config.DATABASE_URL.replace("sqlite:///", "")
        if not os.path.exists(resolved):
            return chunks
        try:
            con = sqlite3.connect(resolved)
            con.row_factory = sqlite3.Row
            cur = con.cursor()

            # Campaigns table
            try:
                rows = cur.execute("SELECT * FROM campaigns").fetchall()
                for row in rows:
                    d = dict(row)
                    text = (
                        f"Campaign Record\n"
                        f"Name: {d.get('name', 'N/A')}\n"
                        f"Objective: {d.get('objective', 'N/A')}\n"
                        f"Target Audience: {d.get('target_audience', 'N/A')}\n"
                        f"Budget: ${d.get('budget', 0):,.2f}\n"
                        f"Duration: {d.get('duration_days', 0)} days\n"
                        f"Status: {d.get('status', 'planned')}\n"
                        f"Created At: {d.get('created_at', 'N/A')}"
                    )
                    chunks.append((text, {"source": "Database – Campaigns", "id": d.get("id")}))
            except Exception:
                pass

            # Trends table
            try:
                rows = cur.execute("SELECT * FROM trends").fetchall()
                for row in rows:
                    d = dict(row)
                    text = (
                        f"Stored Trend\n"
                        f"Name: {d.get('trend_name', 'N/A')}\n"
                        f"Category: {d.get('category', 'N/A')}\n"
                        f"Description: {d.get('description', 'N/A')}\n"
                        f"Relevance Score: {d.get('relevance_score', 'N/A')}\n"
                        f"Impact Score: {d.get('impact_score', 'N/A')}\n"
                        f"Source: {d.get('source', 'N/A')}"
                    )
                    chunks.append((text, {"source": "Database – Trends", "id": d.get("id")}))
            except Exception:
                pass

            # Personas table
            try:
                rows = cur.execute("SELECT * FROM personas").fetchall()
                for row in rows:
                    d = dict(row)
                    text = (
                        f"Stored Persona\n"
                        f"Name: {d.get('persona_name', 'N/A')}\n"
                        f"Demographics: {d.get('demographics', 'N/A')}\n"
                        f"Goals: {d.get('goals', 'N/A')}\n"
                        f"Pain Points: {d.get('pain_points', 'N/A')}\n"
                        f"Behaviors: {d.get('behaviors', 'N/A')}"
                    )
                    chunks.append((text, {"source": "Database – Personas", "id": d.get("id")}))
            except Exception:
                pass

            con.close()
        except Exception as e:
            print(f"⚠️  RAG: DB read error – {e}")
        return chunks

    def _chunks_from_trends(self, cs: Dict) -> List[Tuple[str, Dict]]:
        """Chunk trend scout analysis."""
        chunks = []

        # Current trends list
        trends = cs.get("current_trends", [])
        if trends:
            for i, t in enumerate(trends):
                text = (
                    f"Market Trend #{i + 1}\n"
                    f"Name: {t.get('name', t.get('trend', 'Unknown'))}\n"
                    f"Description: {t.get('description', t.get('detail', 'N/A'))}\n"
                    f"Relevance: {t.get('relevance', 'medium')}\n"
                    f"Impact: {t.get('impact', 'medium')}\n"
                    f"Opportunities: {t.get('opportunities', 'N/A')}\n"
                    f"Recommendation: {t.get('recommendation', 'N/A')}"
                )
                chunks.append((text, {"source": "Trend Analysis", "index": i}))

        # Market insights
        insights = cs.get("market_insights", [])
        if insights:
            text = "Market Insights Summary\n" + "\n".join(f"- {i}" for i in insights)
            chunks.append((text, {"source": "Trend Analysis – Insights"}))

        # Competitor analysis
        comp = cs.get("competitor_analysis", {})
        if comp:
            text = f"Competitive Landscape\n{_json_to_text(comp)}"
            chunks.append((text, {"source": "Trend Analysis – Competition"}))

        return chunks

    def _chunks_from_personas(self, cs: Dict) -> List[Tuple[str, Dict]]:
        """Chunk persona simulator analysis."""
        chunks = []

        personas = cs.get("persona_profiles", [])
        for i, p in enumerate(personas):
            lines = [f"Persona Profile #{i + 1}"]
            for key, val in p.items():
                label = str(key).replace("_", " ").title()
                if isinstance(val, list):
                    lines.append(f"{label}: {', '.join(str(x) for x in val)}")
                else:
                    lines.append(f"{label}: {val}")
            chunks.append(("\n".join(lines), {"source": "Persona Analysis", "index": i}))

        pain_points = cs.get("pain_points", [])
        if pain_points:
            text = "Audience Pain Points\n" + "\n".join(f"- {p}" for p in pain_points)
            chunks.append((text, {"source": "Persona Analysis – Pain Points"}))

        motivations = cs.get("motivation_drivers", [])
        if motivations:
            text = "Motivation Drivers\n" + "\n".join(f"- {m}" for m in motivations)
            chunks.append((text, {"source": "Persona Analysis – Motivations"}))

        journeys = cs.get("user_journey_maps", [])
        for i, journey in enumerate(journeys):
            text = f"User Journey Map #{i + 1}\n{_json_to_text(journey)}"
            chunks.append((text, {"source": "Persona Analysis – Journey", "index": i}))

        return chunks

    def _chunks_from_strategy(self, cs: Dict) -> List[Tuple[str, Dict]]:
        """Chunk strategist output."""
        chunks = []

        strategy = cs.get("campaign_strategy", "")
        if strategy:
            chunks.append((f"Campaign Strategy\n{strategy}", {"source": "Strategist"}))

        messaging = cs.get("key_messaging", [])
        if messaging:
            text = "Key Messages\n" + "\n".join(f"{i + 1}. {m}" for i, m in enumerate(messaging))
            chunks.append((text, {"source": "Strategist – Key Messaging"}))

        channels = cs.get("channel_recommendations", [])
        if channels:
            lines = ["Channel Recommendations"]
            for ch in channels:
                lines.append(
                    f"- {ch.get('name', 'Unknown')}: "
                    f"Budget ${ch.get('budget_allocation', 0):,.0f}, "
                    f"Reach {ch.get('expected_reach', 0):,}, "
                    f"Platform: {ch.get('platform', 'N/A')}"
                )
            chunks.append(("\n".join(lines), {"source": "Strategist – Channels"}))

        metrics = cs.get("success_metrics", [])
        if metrics:
            text = "Success Metrics\n" + "\n".join(f"- {m}" for m in metrics)
            chunks.append((text, {"source": "Strategist – Metrics"}))

        return chunks

    def _chunks_from_design(self, cs: Dict) -> List[Tuple[str, Dict]]:
        """Chunk designer output."""
        chunks = []

        concepts = cs.get("creative_concepts", [])
        for i, c in enumerate(concepts):
            text = (
                f"Creative Concept #{i + 1}\n"
                f"Name: {c.get('name', 'Unnamed')}\n"
                f"Description: {c.get('description', 'N/A')}\n"
                f"Colors: {c.get('colors', 'N/A')}\n"
                f"Typography: {c.get('typography', 'N/A')}\n"
                f"Tone: {c.get('tone', 'N/A')}\n"
                f"Key Visual: {c.get('key_visual', 'N/A')}"
            )
            chunks.append((text, {"source": "Designer – Creative Concepts", "index": i}))

        guidelines = cs.get("visual_guidelines", "")
        if guidelines:
            chunks.append((f"Visual Guidelines\n{guidelines}", {"source": "Designer – Guidelines"}))

        content_ideas = cs.get("content_ideas", [])
        if content_ideas:
            lines = ["Content Ideas"]
            for idea in content_ideas:
                lines.append(
                    f"- [{idea.get('type', 'N/A')}] {idea.get('idea', 'N/A')} "
                    f"(Effort: {idea.get('effort', 'N/A')}, Impact: {idea.get('impact', 'N/A')})"
                )
            chunks.append(("\n".join(lines), {"source": "Designer – Content Ideas"}))

        # Timeline & Execution
        timeline = cs.get("campaign_timeline", {})
        if timeline:
            text = f"Campaign Timeline\n{_json_to_text(timeline)}"
            chunks.append((text, {"source": "Executor – Timeline"}))

        steps = cs.get("implementation_steps", [])
        if steps:
            lines = ["Implementation Steps"]
            for s in steps:
                lines.append(
                    f"- {s.get('task', 'N/A')} | Priority: {s.get('priority', 'N/A')} "
                    f"| Assignee: {s.get('assignee', 'N/A')} | By: {s.get('deadline', 'N/A')}"
                )
            chunks.append(("\n".join(lines), {"source": "Executor – Implementation"}))

        risks = cs.get("risk_mitigation", [])
        if risks:
            text = "Risk Mitigation\n" + "\n".join(f"- {r}" for r in risks)
            chunks.append((text, {"source": "Executor – Risk Mitigation"}))

        return chunks

    # ------------------------------------------------------------------
    # Embedding & Retrieval
    # ------------------------------------------------------------------

    def _embed(self, text: str) -> Optional[List[float]]:
        """
        Call the Tiger Analytics gateway embeddings endpoint.
        Matches the usage pattern provided by the user.
        """
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {"model": self.EMBEDDING_MODEL, "input": text}
            response = requests.post(
                self.EMBEDDING_URL,
                json=payload,
                headers=headers,
                verify=False,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            print(f"⚠️  RAG embed error: {e}")
            return None

    def _retrieve(
        self, query_embedding: List[float], k: int = 5
    ) -> List[Tuple[str, Dict, float]]:
        """Return top-k chunks by cosine similarity."""
        scored = []
        for text, meta, emb in zip(self.documents, self.metadata, self.embeddings):
            score = _cosine_similarity(query_embedding, emb)
            scored.append((text, meta, score))
        scored.sort(key=lambda x: x[2], reverse=True)
        return scored[:k]

    # ------------------------------------------------------------------
    # LLM Generation
    # ------------------------------------------------------------------

    def _get_openai_client(self):
        """Lazy-initialize the OpenAI client via Config."""
        if self._openai_client is None:
            self._openai_client = Config.get_openai_client()
        return self._openai_client

    def _generate(self, question: str, context: str) -> str:
        """
        Generate an answer using the Gemini model with retrieved context.
        """
        system_prompt = (
            "You are Campaign Brain's intelligent analyst. "
            "Your job is to answer marketing and campaign-related questions "
            "based ONLY on the provided context from the campaign analysis.\n\n"
            "Rules:\n"
            "- Be concise, specific, and actionable.\n"
            "- Reference the source (e.g., 'According to the Trend Analysis…').\n"
            "- If the context does not contain enough information, say so honestly.\n"
            "- Format responses clearly using bullet points or short paragraphs.\n"
            "- Do NOT hallucinate or add information not present in the context."
        )

        user_message = (
            f"Context from campaign analysis:\n\n"
            f"{context}\n\n"
            f"---\n\n"
            f"Question: {question}"
        )

        try:
            client = self._get_openai_client()
            response = client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=1024,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ Error generating answer: {str(e)}"


# ---------------------------------------------------------------------------
# Module-level singleton (shared across Streamlit re-runs via session_state)
# ---------------------------------------------------------------------------

def get_rag_agent() -> CampaignRAGAgent:
    """Return a new CampaignRAGAgent instance."""
    return CampaignRAGAgent()
