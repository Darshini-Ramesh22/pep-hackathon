"""
Persona Simulator Agent - Creates detailed user personas and journey maps
"""
import json
import sys
import os
from typing import Dict, List, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config


class PersonaSimulator:
    """
    Agent responsible for creating detailed user personas,
    journey maps, and understanding user psychology.
    """
    
    def __init__(self):
        self.client = Config.get_openai_client()
        self.model = Config.MODEL_NAME
        
    def create_personas(
        self,
        target_audience: str,
        strategy: str,
        trends: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create detailed user personas and journey maps
        
        Args:
            target_audience (str): Target audience description
            strategy (str): Campaign strategy
            trends (List): Current market trends
            
        Returns:
            Dict containing personas, journey maps, pain points, and motivations
        """
        
        # Load persona prompt
        with open("campaign_brain/prompts/persona_prompt.txt", "r") as f:
            prompt_template = f.read()
            
        # Prepare trend influences
        trend_influences = "\n".join([
            f"- {trend.get('name', 'Unknown')}" 
            for trend in trends[:5]
        ])
        
        # Prepare the prompt
        prompt = prompt_template.format(
            target_audience=target_audience,
            strategy=strategy,
            trends=trend_influences
        )
        
        try:
            # Call the AI model
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": '''You are a UX researcher and behavioral psychologist expert in creating detailed user personas and mapping customer journeys. Focus on psychological insights and actionable persona details.
                        JSON Format:
                        {
                        "name": <persona name>,
                        "age_range": <age range>,
                        "pain_points": [<pain_points>],
                        "media_habits": [<media_habits>],
                        "shopping_and_decision_making_behavior": <shopping_and_decision_making_behavior>,
                        "snacking_preferences": [<snacking_preferences>],
                        "decision_driver": <decision_driver>,
                        "preferred_offer_type": <preferred_offer_type>
                        }                        
                        '''
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            # Parse the response
            persona_text = response.choices[0].message.content
            print(f"Persona Simulator raw response:\n{persona_text}\n")
            
            # Extract structured personas
            personas = self._parse_personas(persona_text)
            with open("campaign_brain/logs/persona_simulator_response.txt", "w") as f:
                f.write(persona_text)
            
            return personas
            
        except Exception as e:
            print(f"Error in persona creation: {str(e)}")
            return self._get_fallback_personas()
    
    def _parse_personas(self, persona_text: str) -> Dict[str, Any]:
        """Parse the AI response into structured persona data"""
        
        try:
            # Try to extract JSON if present
            start = persona_text.find("{")
            end = persona_text.rfind("}") + 1
            if start != -1 and end != 0:
                json_str = persona_text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: extract structure from text
        lines = persona_text.split("\n")
        
        personas = []
        journey_maps = []
        pain_points = []
        motivations = []
        
        current_persona = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Identify persona sections
            if "persona" in line.lower() and (":" in line or "#" in line):
                if current_persona:
                    personas.append(current_persona)
                current_persona = {"name": self._extract_persona_name(line)}
                current_section = "persona"
                continue
            
            # Identify other sections
            if "journey" in line.lower():
                current_section = "journey"
                continue
            elif "pain" in line.lower():
                current_section = "pain"
                continue
            elif "motivation" in line.lower():
                current_section = "motivation"
                continue
            
            # Extract content
            if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                content = line[1:].strip()
                if current_section == "pain" and content:
                    pain_points.append(content)
                elif current_section == "motivation" and content:
                    motivations.append(content)
                elif current_section == "journey" and content:
                    journey_maps.append({"step": content, "emotion": "neutral"})
                elif current_section == "persona" and content:
                    self._add_persona_detail(current_persona, content)
        
        # Add the last persona
        if current_persona:
            personas.append(current_persona)
        
        # Enhance personas with default structure
        for persona in personas:
            self._enhance_persona(persona)
        
        return {
            "personas": personas,
            "journey_maps": journey_maps or self._get_default_journey(),
            "pain_points": pain_points[:10] or self._get_default_pain_points(),
            "motivations": motivations[:10] or self._get_default_motivations()
        }
    
    def _extract_persona_name(self, line: str) -> str:
        """Extract persona name from header line"""
        # Remove common prefixes and get the core name
        line = line.replace("#", "").replace("Persona", "").replace(":", "").strip()
        words = line.split()
        return words[0] if words else "Persona"
    
    def _add_persona_detail(self, persona: Dict, content: str) -> None:
        """Add detail to persona based on content"""
        content_lower = content.lower()
        
        if "age" in content_lower or "year" in content_lower:
            persona["age"] = content
        elif "job" in content_lower or "work" in content_lower or "manager" in content_lower:
            persona["occupation"] = content
        elif "goal" in content_lower or "want" in content_lower:
            if "goals" not in persona:
                persona["goals"] = []
            persona["goals"].append(content)
        elif "behavior" in content_lower or "habit" in content_lower:
            if "behaviors" not in persona:
                persona["behaviors"] = []
            persona["behaviors"].append(content)
        else:
            if "description" not in persona:
                persona["description"] = content
            else:
                persona["description"] += f" {content}"
    
    def _enhance_persona(self, persona: Dict) -> None:
        """Enhance persona with default structure"""
        defaults = {
            "age": "25-35 years old",
            "occupation": "Professional",
            "goals": ["Achieve success", "Save time", "Get value"],
            "behaviors": ["Uses social media daily", "Researches before buying"],
            "pain_points": ["Limited time", "Too many options"],
            "preferred_channels": ["Social media", "Email", "Mobile"],
            "decision_factors": ["Price", "Quality", "Reviews"]
        }
        
        for key, default_value in defaults.items():
            if key not in persona:
                persona[key] = default_value
    
    def _get_default_journey(self) -> List[Dict[str, Any]]:
        """Get default customer journey map"""
        return [
            {"step": "Awareness - Discovers need or problem", "emotion": "curious", "touchpoint": "Social media"},
            {"step": "Interest - Researches solutions", "emotion": "excited", "touchpoint": "Search engines"},
            {"step": "Consideration - Compares options", "emotion": "analytical", "touchpoint": "Website"},
            {"step": "Purchase - Makes decision", "emotion": "confident", "touchpoint": "Online store"},
            {"step": "Post-purchase - Uses product", "emotion": "satisfied", "touchpoint": "Product experience"},
            {"step": "Advocacy - Shares experience", "emotion": "happy", "touchpoint": "Reviews/referrals"}
        ]
    
    def _get_default_pain_points(self) -> List[str]:
        """Get default pain points - snack/children focused"""
        return [
            "Finding snacks kids actually like and eat",
            "Balancing taste with nutritional value",
            "Managing allergies and dietary restrictions",
            "Avoiding artificial colors and sugars",
            "Cost vs. quality trade-off",
            "Difficulty finding trending/cool snacks",
            "Limited availability in local stores",
            "Too many confusing options and claims",
            "Environmental impact of packaging",
            "Time to research and plan snacking",
            "Kids rejecting 'healthy' options",
            "Building good eating habits",
            "Portion control and overeating",
            "Snack fatigue - same options every day",
            "Trust in brand and ingredient claims"
        ]
    
    def _get_default_motivations(self) -> List[str]:
        """Get default motivations - snack/children focused"""
        return [
            "Keep kids healthy and well-nourished",
            "Find snacks that kids love and ask for again",
            "Save time on snacking decisions",
            "Feel like a good parent making smart choices",
            "Get good value and save money",
            "Support eco-friendly and sustainable brands",
            "Keep up with trending snack brands",
            "Gain social approval from peers and family",
            "Ensure reliable, trustworthy nutrition",
            "Discover new flavors and varieties",
            "Build loyalty through rewards programs",
            "Enable active, healthy lifestyles",
            "Create positive food associations for kids",
            "Reduce decision fatigue and stress",
            "Support child's growth and development"
        ]
    
    def _get_fallback_personas(self) -> Dict[str, Any]:
        """Provide fallback personas if AI call fails - with snack/children focus"""
        return {
            "personas": [
                {
                    "name": "Snack Seeker Samantha",
                    "age_range": "7-10 years",
                    "occupation": "Student (Grade 2-4)",
                    "demographics": "Urban/Suburban, middle-income family",
                    "values": ["Fun", "Taste", "Health-conscious (somewhat)", "Peer approval"],
                    "interests": ["YouTube gaming channels", "TikTok trends", "Friends' recommendations", "Collectible packaging"],
                    "goals": ["Have cool snacks like friends", "Discover new flavors", "Earn rewards from loyalty app"],
                    "pain_points": ["Parents say 'no' to sugary snacks", "Limited pocket money", "Snacks not as cool as friends'"],
                    "media_habits": ["YouTube Kids", "Instagram Reels", "TikTok", "Streaming shows"],
                    "snacking_preferences": ["Fun flavors", "Crunchy texture", "Colorful packaging", "Limited edition items"],
                    "decision_driver": "Peer recommendations and visual appeal",
                    "trusted_sources": ["YouTube reviewers", "TikTok influencers", "Friends", "Parents"]
                },
                {
                    "name": "Health-Conscious Mom Monica",
                    "age_range": "35-45 years",
                    "occupation": "Working Parent",
                    "demographics": "Urban, educated, health-conscious",
                    "values": ["Child's health", "Natural ingredients", "Convenience", "Sustainability"],
                    "interests": ["Parenting blogs", "Nutrition articles", "Eco-friendly products", "Instagram lifestyle"],
                    "goals": ["Find nutritious snacks kids love", "Support sustainable brands", "Save time on snacking decisions"],
                    "pain_points": ["Time to research healthy options", "Cost premium for organic", "Kids rejecting healthy snacks", "Allergies and dietary restrictions"],
                    "media_habits": ["Instagram", "Pinterest", "Parenting newsletters", "Google search"],
                    "snacking_preferences": ["No artificial colors/flavors", "Whole grain", "Low sugar", "Transparent ingredient list"],
                    "decision_driver": "Nutrition facts, brand reputation, and peer reviews",
                    "trusted_sources": ["Nutritionist recommendations", "Parent blogs", "Product reviews", "Certification labels"]
                },
                {
                    "name": "Trendy Teen Tyler",
                    "age_range": "13-16 years",
                    "occupation": "Student (Middle/High School)",
                    "demographics": "Urban, digital native, style-conscious",
                    "values": ["Trends", "Social status", "Authenticity", "Sustainability"],
                    "interests": ["TikTok trends", "Instagram influencers", "Gaming", "Sustainability movements"],
                    "goals": ["Have viral snack brands", "Participate in trends", "Feel eco-conscious", "Social media worthy"],
                    "pain_points": ["Peer pressure on snack choices", "Want healthy but trendy", "Limited budget", "Sustainability concerns"],
                    "media_habits": ["TikTok", "Instagram", "YouTube", "Discord/Twitch"],
                    "snacking_preferences": ["Instagram-worthy packaging", "Trending brands", "Plant-based options", "Unique flavors"],
                    "decision_driver": "Social media influence and trend participation",
                    "trusted_sources": ["TikTok influencers", "Peer recommendations", "Instagram trends", "YouTube reviews"]
                },
                {
                    "name": "Budget-Savvy Dad Dev",
                    "age_range": "38-48 years",
                    "occupation": "Working Parent",
                    "demographics": "Suburban, value-conscious, pragmatic",
                    "values": ["Value for money", "Convenience", "Family time", "Quality"],
                    "interests": ["Bulk purchasing", "Deal hunting", "Family activities", "Practical solutions"],
                    "goals": ["Find affordable quality snacks", "Stock pantry efficiently", "Keep kids satisfied", "Save money"],
                    "pain_points": ["Prices rising", "Hard to find good deals", "Kids want premium brands", "Quality vs. price trade-off"],
                    "media_habits": ["WhatsApp groups", "Email newsletters", "Retail apps", "Reddit"],
                    "snacking_preferences": ["Good value packs", "Bulk options", "No unnecessary packaging", "Price-conscious"],
                    "decision_driver": "Price, value, and practical convenience",
                    "trusted_sources": ["Price comparison apps", "Friend recommendations", "Retailer loyalty programs", "Deal websites"]
                },
                {
                    "name": "Active Adventure Amy",
                    "age_range": "8-12 years",
                    "occupation": "Student (Sports enthusiast)",
                    "demographics": "Any location, fitness-oriented family",
                    "values": ["Energy", "Health", "Performance", "Teamwork"],
                    "interests": ["Sports", "Outdoor activities", "Fitness challenges", "Sports heroes"],
                    "goals": ["Get energy for sports", "Perform better", "Be strong like athletes", "Fuel adventures"],
                    "pain_points": ["Need quick energy", "Heavy snacks slow them down", "Want healthy not boring", "Performance pressure"],
                    "media_habits": ["YouTube sports channels", "TikTok fitness creators", "Instagram sports accounts"],
                    "snacking_preferences": ["Protein-rich", "Energy bars", "Light and portable", "Endorsed by athletes"],
                    "decision_driver": "Performance benefits and athlete endorsements",
                    "trusted_sources": ["Sports influencers", "Coach recommendations", "Athletic brands", "Performance reviews"]
                }
            ],
            "journey_maps": self._get_default_journey(),
            "pain_points": self._get_default_pain_points(),
            "motivations": self._get_default_motivations()
        }