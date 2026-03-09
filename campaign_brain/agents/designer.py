"""
Designer Agent - Creates creative concepts and visual guidelines
"""
import json
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class Designer:
    """
    Agent responsible for creating creative concepts,
    visual guidelines, and content ideas.
    """
    
    def __init__(self):
        self.client = Config.get_openai_client()
        self.model = Config.MODEL_NAME
        
    def create_concepts(
        self,
        strategy: str,
        personas: List[Dict[str, Any]],
        brand_guidelines: str,
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create creative concepts and visual guidelines
        
        Args:
            strategy (str): Campaign strategy
            personas (List): User personas
            brand_guidelines (str): Brand guidelines
            channels (List): Recommended channels
            
        Returns:
            Dict containing creative concepts, visual guidelines, and content ideas
        """
        
        # Load designer prompt
        with open("campaign_brain/prompts/designer_prompt.txt", "r") as f:
            prompt_template = f.read()
            
        # Prepare persona insights
        persona_insights = "\n".join([
            f"- {persona.get('name', 'Persona')}: {persona.get('description', 'No description')[:100]}..."
            for persona in personas[:3]
        ])
        
        # Prepare channel requirements
        channel_requirements = "\n".join([
            f"- {channel.get('name', 'Unknown')}: Budget ${channel.get('budget_allocation', 0):,.0f}"
            for channel in channels[:5]
        ])
        
        # Prepare the prompt
        prompt = prompt_template.format(
            strategy=strategy,
            personas=persona_insights,
            brand_guidelines=brand_guidelines or "No specific brand guidelines provided",
            channels=channel_requirements
        )
        
        try:
            # Call the AI model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a senior creative director specializing in FMCG and consumer brand campaigns. "
                            "Generate exactly 3 distinct creative concepts. "
                            "You MUST respond with ONLY a valid JSON object — no markdown, no backticks, no explanatory text before or after. "
                            "The JSON must follow this exact structure: "
                            '{"concepts": [{"name": "string", "description": "3-5 sentence string", "colors": "string", "typography": "string", "imagery": "string", "tone": "string", "channel_adaptations": [{"channel": "string", "format": "string", "specifications": "string"}]}, ...], '
                            '"visual_guidelines": "string", '
                            '"content_ideas": [{"idea": "string", "type": "string", "effort": "low|medium|high", "impact": "low|medium|high"}, ...]}. '
                            "Each concept must have a meaningfully different creative direction. "
                            "Do not include any text outside the JSON object."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=4000
            )
            
            # Parse the response
            creative_text = response.choices[0].message.content
            
            # Extract structured creative output
            creative_output = self._parse_creative_concepts(creative_text, channels)
            with open("campaign_brain/logs/designer_response.txt", "w") as f:
                f.write(creative_text)
            
            return creative_output
            
        except Exception as e:
            print(f"Error in creative concept creation: {str(e)}")
            return self._get_fallback_concepts(channels)
    
    def _parse_creative_concepts(
        self,
        creative_text: str,
        channels: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Parse the AI response into structured creative concepts."""

        import re

        def _finalise(data: Dict) -> Dict:
            """Ensure every required field is present before returning."""
            for concept in data.get("concepts", []):
                if not concept.get("channel_adaptations"):
                    self._enhance_concept(concept, channels)
            if not data.get("content_ideas"):
                data["content_ideas"] = self._get_default_content_ideas(channels)
            if not data.get("visual_guidelines"):
                data["visual_guidelines"] = self._get_default_visual_guidelines()
            return data

        # ── 1. Direct JSON parse (happy path) ────────────────────────────
        try:
            data = json.loads(creative_text.strip())
            if isinstance(data, dict) and "concepts" in data:
                return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 2. Strip markdown fences then parse ──────────────────────────
        try:
            cleaned = re.sub(r"```(?:json)?|```", "", creative_text).strip()
            data = json.loads(cleaned)
            if isinstance(data, dict) and "concepts" in data:
                return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 3. Extract outermost { } block ───────────────────────────────
        try:
            start = creative_text.find("{")
            end = creative_text.rfind("}") + 1
            if start != -1 and end > start:
                data = json.loads(creative_text[start:end])
                if isinstance(data, dict) and "concepts" in data:
                    return _finalise(data)
        except (json.JSONDecodeError, ValueError):
            pass

        # ── 4. Markdown fallback — build minimal concept structs ─────────
        concepts: List[Dict] = []
        blocks = re.split(r"(?m)^#{1,3}\s+(?:Creative\s+)?Concept\s*\d*[:\.]?\s*", creative_text)
        for block in blocks[1:]:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if not lines:
                continue
            concept: Dict[str, Any] = {
                "name": lines[0].strip('*"\'#: '),
                "channel_adaptations": []
            }
            body: List[str] = []
            for line in lines[1:]:
                low = line.lower()
                val = re.sub(r"^[\*\-\(\d\.]+\s*", "", line).strip()
                if "color" in low or "palette" in low:
                    concept.setdefault("colors", val)
                elif "typo" in low or "font" in low or "headline" in low:
                    concept.setdefault("typography", val)
                elif "imager" in low or "photo" in low:
                    concept.setdefault("imagery", val)
                elif "tone" in low or "voice" in low:
                    concept.setdefault("tone", val)
                else:
                    body.append(line.strip("* "))
            concept["description"] = " ".join(body[:6]) if body else concept["name"]
            self._enhance_concept(concept, channels)
            concepts.append(concept)

        return {
            "concepts": concepts or self._get_default_concepts(),
            "visual_guidelines": self._get_default_visual_guidelines(),
            "content_ideas": self._get_default_content_ideas(channels)
        }

    
    def _extract_concept_name(self, line: str) -> str:
        """Extract concept name from header line"""
        line = line.replace("#", "").replace("Concept", "").replace(":", "").strip()
        words = line.split()
        return " ".join(words[:3]) if words else "Creative Concept"
    
    def _add_concept_detail(self, concept: Dict, content: str) -> None:
        """Add detail to concept based on content"""
        content_lower = content.lower()
        
        if "color" in content_lower or "palette" in content_lower:
            concept["colors"] = content
        elif "font" in content_lower or "typography" in content_lower:
            concept["typography"] = content
        elif "image" in content_lower or "visual" in content_lower or "photo" in content_lower:
            concept["imagery"] = content
        elif "tone" in content_lower or "voice" in content_lower:
            concept["tone"] = content
        else:
            if "elements" not in concept:
                concept["elements"] = []
            concept["elements"].append(content)
    
    def _enhance_concept(self, concept: Dict, channels: List[Dict[str, Any]]) -> None:
        """Enhance concept with channel-specific adaptations"""
        concept["channel_adaptations"] = []
        
        for channel in channels:
            channel_name = channel.get("name", "").lower()
            adaptation = {"channel": channel.get("name"), "format": "", "specifications": ""}
            
            if "social" in channel_name or "instagram" in channel_name:
                adaptation["format"] = "Square posts, Stories, Reels"
                adaptation["specifications"] = "1080x1080, 1080x1920, video 15-30s"
            elif "google" in channel_name or "search" in channel_name:
                adaptation["format"] = "Text ads, Display banners"
                adaptation["specifications"] = "Multiple banner sizes, compelling headlines"
            elif "email" in channel_name:
                adaptation["format"] = "Email templates, subject lines"
                adaptation["specifications"] = "Mobile-optimized, clear CTAs"
            elif "video" in channel_name or "tv" in channel_name:
                adaptation["format"] = "Video commercials, bumper ads"
                adaptation["specifications"] = "30s, 15s, 6s formats"
            else:
                adaptation["format"] = "Standard digital format"
                adaptation["specifications"] = "Responsive design"
            
            concept["channel_adaptations"].append(adaptation)
    
    def _create_content_idea(self, content: str) -> Dict[str, Any]:
        """Create structured content idea"""
        return {
            "idea": content,
            "type": self._determine_content_type(content),
            "effort": self._estimate_effort(content),
            "impact": "medium"
        }
    
    def _determine_content_type(self, content: str) -> str:
        """Determine content type based on description"""
        content_lower = content.lower()
        if "video" in content_lower:
            return "video"
        elif "image" in content_lower or "photo" in content_lower:
            return "image"
        elif "blog" in content_lower or "article" in content_lower:
            return "blog_post"
        elif "social" in content_lower or "post" in content_lower:
            return "social_media"
        elif "email" in content_lower:
            return "email"
        else:
            return "mixed_media"
    
    def _estimate_effort(self, content: str) -> str:
        """Estimate effort level for content creation"""
        content_lower = content.lower()
        if "video" in content_lower or "animation" in content_lower:
            return "high"
        elif "design" in content_lower or "graphic" in content_lower:
            return "medium"
        else:
            return "low"
    
    def _get_default_concepts(self) -> List[Dict[str, Any]]:
        """Get default creative concepts"""
        return [
            {
                "name": "Bold & Unapologetic",
                "description": (
                    "A high-energy concept built on loud visuals, oversized typography, and vibrant color clashes. "
                    "It positions the brand as fearless and culturally relevant, speaking directly to a younger audience "
                    "that values authenticity and self-expression. Every touchpoint feels like a statement, not an ad."
                ),
                "colors": "Electric Blue (#003087), Bright Red (#E31837), White (#FFFFFF)",
                "typography": "Extra-bold condensed sans-serif headers; clean minimal body text",
                "imagery": "High-contrast editorial photography, motion blur, street culture aesthetics",
                "tone": "Confident, provocative, energetic",
                "channel_adaptations": []
            },
            {
                "name": "Real Moments, Real People",
                "description": (
                    "An authenticity-first concept anchored in user-generated content and unscripted storytelling. "
                    "The brand steps back and lets real consumers take center stage — sharing genuine experiences "
                    "that build trust and social proof. This approach humanizes the brand and drives organic sharing "
                    "through relatability and emotional resonance."
                ),
                "colors": "Warm Cream (#FFF8F0), Terracotta (#C0633A), Soft Charcoal (#3D3D3D)",
                "typography": "Friendly rounded serif for headers; humanist sans-serif for body",
                "imagery": "User-generated photos, candid lifestyle shots, behind-the-scenes moments",
                "tone": "Warm, genuine, inclusive, conversational",
                "channel_adaptations": []
            },
            {
                "name": "Future Forward",
                "description": (
                    "A sleek, technology-inspired concept that positions the brand at the intersection of innovation "
                    "and lifestyle. Clean lines, gradients, and motion graphics communicate progress and premium quality. "
                    "Ideal for reaching tech-savvy and aspirational audiences who associate modernity with trust."
                ),
                "colors": "Deep Navy (#001F5B), Electric Cyan (#0093D0), Platinum (#E8EDF5)",
                "typography": "Geometric sans-serif throughout; tight tracking for a premium feel",
                "imagery": "Macro product shots, abstract motion graphics, futuristic environments",
                "tone": "Sophisticated, forward-thinking, aspirational",
                "channel_adaptations": []
            },
            {
                "name": "Rooted in Culture",
                "description": (
                    "A culturally immersive concept that taps into the music, art, sports, and food scenes most "
                    "relevant to the target demographic. Partnerships with local creators and influencers make the "
                    "brand feel like a natural part of the community rather than an outsider. "
                    "This concept drives deep engagement through cultural credibility and co-creation."
                ),
                "colors": "Rich Gold (#F5A623), Deep Brown (#3B1F0A), Vivid Green (#2ECC71)",
                "typography": "Expressive display fonts for headlines; clean legible body text",
                "imagery": "Festival scenes, cultural events, creator collaborations, vibrant community moments",
                "tone": "Celebratory, community-driven, culturally aware",
                "channel_adaptations": []
            },
            {
                "name": "Less Is More",
                "description": (
                    "A minimalist concept that lets the product speak for itself through restrained design and precise "
                    "copywriting. White space, muted palettes, and single-focus visuals create a premium, editorial "
                    "look that stands out in a cluttered feed. This approach appeals to discerning consumers who "
                    "appreciate craft, quality, and clarity over noise."
                ),
                "colors": "Pure White (#FFFFFF), Soft Black (#1A1A1A), Accent Sage (#A8B89A)",
                "typography": "Thin serif display font for headlines; minimal body copy",
                "imagery": "Studio product photography, negative space, single hero shots",
                "tone": "Refined, understated, premium, precise",
                "channel_adaptations": []
            }
        ]
    
    def _get_default_visual_guidelines(self) -> str:
        """Get default visual guidelines"""
        return """
        Color Palette: Use consistent brand colors with high contrast for accessibility.
        Typography: Maintain font hierarchy with clear headers and readable body text.
        Imagery: High-quality, on-brand visuals that resonate with target audience.
        Layout: Clean, organized layouts with proper white space and visual balance.
        Consistency: Maintain visual consistency across all channels and touchpoints.
        Accessibility: Ensure designs meet WCAG guidelines for inclusive access.
        """
    
    def _get_default_content_ideas(self, channels: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get default content ideas based on channels"""
        ideas = [
            {"idea": "Behind-the-scenes content showcasing brand authenticity", "type": "video", "effort": "medium", "impact": "high"},
            {"idea": "User-generated content campaigns with branded hashtags", "type": "social_media", "effort": "low", "impact": "high"},
            {"idea": "Educational blog posts addressing customer pain points", "type": "blog_post", "effort": "medium", "impact": "medium"},
            {"idea": "Interactive polls and Q&A sessions", "type": "social_media", "effort": "low", "impact": "medium"},
            {"idea": "Customer success stories and testimonials", "type": "mixed_media", "effort": "medium", "impact": "high"}
        ]
        
        # Add channel-specific ideas
        for channel in channels:
            channel_name = channel.get("name", "").lower()
            if "email" in channel_name:
                ideas.append({"idea": "Weekly newsletter with curated content", "type": "email", "effort": "medium", "impact": "medium"})
            elif "video" in channel_name:
                ideas.append({"idea": "Product demonstration videos", "type": "video", "effort": "high", "impact": "high"})
        
        return ideas[:10]
    
    def _get_fallback_concepts(self, channels: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide fallback creative concepts if AI call fails"""
        return {
            "concepts": self._get_default_concepts(),
            "visual_guidelines": self._get_default_visual_guidelines(),
            "content_ideas": self._get_default_content_ideas(channels)
        }