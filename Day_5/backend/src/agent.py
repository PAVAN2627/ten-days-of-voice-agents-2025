import logging
import json
import os
import smtplib
from datetime import datetime
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, openai, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class CompleteSDRAssistant(Agent):
    def __init__(self) -> None:
        self.company_data = self._load_company_data()
        self.personas_data = self._load_personas_data()
        self.calendar_data = self._load_calendar_data()
        self.lead_data = {}
        self.conversation_transcript = []
        self.detected_persona = None
        self.conversation_ended = False
        self.is_returning_visitor = False
        self.email_sent = False
        # Email configuration
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
        self.sender_name = os.getenv("SENDER_NAME", "Priya - Razorpay SDR")
        
        super().__init__(
            instructions=f"""You are Priya, SDR for {self.company_data['company']['name']}. Be CONCISE and professional.

MANDATORY OPENING SEQUENCE (ALWAYS DO THIS FIRST):
1. Greet: "Hi! I'm Priya from Razorpay. Before we start, I need a few quick details."
2. Ask for NAME: "What's your name?"
3. Ask for EMAIL: "What's your email address?"
4. Ask for COMPANY: "Which company are you from?"
5. Ask for ROLE: "What's your role there?" (Store as 'role' field)
6. Ask for TEAM SIZE: "How big is your team?" (Store as 'team_size' field)
7. Ask for TIMELINE: "When are you looking to implement this - now, soon, or later?" (Store as 'timeline' field)
8. Ask for NEED: "What brings you to Razorpay today? What are you looking for?"
9. Then say: "Great! Feel free to ask any questions about Razorpay, or I can help you schedule a demo."

INFORMATION COLLECTION RULES:
- ALWAYS ask for Name, Email, Company, Role, Team Size, Timeline, and Need FIRST before anything else
- Ask ONE question at a time, wait for answer
- Use store_lead_info() to save each detail immediately
- After collecting role, use detect_persona() to identify their persona type
- Don't proceed to demos or questions until you have: name, email, company, role, team_size, timeline, need
- If user asks questions before giving details, say: "Happy to help! But first, may I get your name?"

AFTER COLLECTING INFO:
- Answer their questions using search_faq() tool
- Detect their persona (developer/founder/PM/finance/marketer)
- Offer relevant solutions
- Suggest booking a demo

BOOKING PROCESS (FOLLOW THIS ORDER):
1. Ask: "Would you like to schedule a demo?"
2. If yes, ask: "What are the main challenges or pain points you're facing with payments right now?"
3. Store their pain points using store_lead_info(field="pain_points", value="their answer")
4. Ask: "What specific features or solutions are you most interested in seeing?"
5. Store interests using store_lead_info(field="key_interests", value="their answer")
6. Then say: "Perfect! Let me show you available times."
7. ALWAYS call show_available_meetings() to check real slots
8. Present ONLY available options from the tool (never make up times)
9. Use book_meeting() with their choice
10. Confirm with their name and email

CRITICAL RULES:
- NEVER skip the opening sequence
- NEVER book without email
- NEVER suggest times without checking show_available_meetings() first
- ALWAYS store info using store_lead_info() immediately
- Keep responses SHORT (1-2 sentences max)
- Ask one question at a time

EXAMPLE OPENING:
You: "Hi! I'm Priya from Razorpay. Before we start, I need a few quick details. What's your name?"
User: "John"
You: "Nice to meet you, John! What's your email address?"
User: "john@example.com"
You: "Got it. Which company are you from?"
User: "TechCorp"
You: "Great! What's your role there?"
User: "I'm a developer"
You: "Perfect! How big is your team?"
User: "About 10 people"
You: "Got it. When are you looking to implement this - now, soon, or later?"
User: "We need it ASAP"
You: "Understood! What brings you to Razorpay today?"
User: "Need payment gateway"
You: "Excellent! As a developer with an urgent need, I can show you our quick API integration. Feel free to ask questions, or I can help schedule a demo."

AVOID: Long explanations, skipping info collection, making up meeting times
FOCUS: Collect info FIRST → Answer questions → Book demo""",
        )
    
    def _load_company_data(self) -> Dict[str, Any]:
        try:
            with open("company_data/razorpay_faq.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Company FAQ data not found")
            return {"company": {"name": "Razorpay"}, "faq": []}
    
    def _load_personas_data(self) -> Dict[str, Any]:
        try:
            with open("personas.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Personas data not found")
            return {"personas": {}}
    
    def _load_calendar_data(self) -> Dict[str, Any]:
        try:
            with open("mock_calendar.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("Calendar data not found")
            return {"available_slots": [], "booked_meetings": []}
    
    def _has_required_info(self) -> bool:
        """Check if all required information has been collected"""
        required_fields = ["name", "email", "company", "role", "team_size", "timeline", "use_case"]
        return all(self.lead_data.get(field) for field in required_fields)
    
    def _get_missing_info(self) -> list:
        """Get list of missing required information"""
        required_fields = {
            "name": "your name",
            "email": "your email address", 
            "company": "your company name",
            "role": "your role",
            "team_size": "your team size",
            "timeline": "your timeline (now/soon/later)",
            "use_case": "what you're looking for"
        }
        return [label for field, label in required_fields.items() if not self.lead_data.get(field)]
    
    async def _save_lead_data(self) -> str:
        """Save lead data to JSON file immediately"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads/lead_{timestamp}.json"
        
        lead_summary = {
            "timestamp": datetime.now().isoformat(),
            "lead_data": self.lead_data,
            "conversation_transcript": self.conversation_transcript,
            "detected_persona": self.detected_persona,
            "is_returning_visitor": self.is_returning_visitor
        }
        
        os.makedirs("leads", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(lead_summary, f, indent=2)
        
        logger.info(f"💾 Lead data saved to {filename}")
        return filename
    
    def _check_returning_visitor(self, email: str = None, name: str = None, company: str = None) -> Optional[Dict]:
        """Check if this is a returning visitor based on stored lead data"""
        if not any([email, name, company]):
            return None
            
        leads_dir = "leads"
        if not os.path.exists(leads_dir):
            return None
            
        for filename in os.listdir(leads_dir):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(leads_dir, filename), "r") as f:
                        lead = json.load(f)
                        lead_data = lead.get("lead_data", {})
                        
                        if email and lead_data.get("email", "").lower() == email.lower():
                            return lead
                        
                        if (name and company and 
                            lead_data.get("name", "").lower() == name.lower() and
                            lead_data.get("company", "").lower() == company.lower()):
                            return lead
                            
                except Exception as e:
                    logger.error(f"Error reading lead file {filename}: {e}")
                    
        return None

    @function_tool
    async def check_returning_visitor(self, context: RunContext, email: str = None, name: str = None, company: str = None) -> str:
        """Check if this is a returning visitor and load previous conversation data."""
        previous_lead = self._check_returning_visitor(email, name, company)
        
        if previous_lead:
            self.is_returning_visitor = True
            prev_data = previous_lead.get("lead_data", {})
            
            for key, value in prev_data.items():
                if key not in self.lead_data:
                    self.lead_data[key] = value
            
            use_case = prev_data.get("use_case", "payment solutions")
            return f"Welcome back! I remember you were interested in {use_case}. How can I help you today?"
        else:
            return "Nice to meet you! I'm Priya from Razorpay. What brought you here today?"
    
    @function_tool
    async def detect_persona(self, context: RunContext, user_input: str) -> str:
        """Detect user persona based on their language and role."""
        input_lower = user_input.lower()
        
        persona_scores = {}
        for persona_name, persona_data in self.personas_data.get("personas", {}).items():
            score = 0
            for keyword in persona_data.get("keywords", []):
                if keyword in input_lower:
                    score += 1
            persona_scores[persona_name] = score
        
        if persona_scores:
            self.detected_persona = max(persona_scores, key=persona_scores.get)
            if persona_scores[self.detected_persona] > 0:
                self.lead_data["detected_persona"] = self.detected_persona
                return f"Got it! As a {self.detected_persona}, I can share how Razorpay specifically helps people in your role."
        
        return "Thanks for sharing! Let me understand your specific needs better."
    
    @function_tool
    async def get_persona_pitch(self, context: RunContext, pain_point: str = None) -> str:
        """Get persona-specific pitch and benefits."""
        if not self.detected_persona:
            return "Let me share how Razorpay can help your business grow and succeed."
        
        persona_data = self.personas_data["personas"].get(self.detected_persona, {})
        benefits = persona_data.get("key_benefits", [])
        
        if benefits:
            return f"For {self.detected_persona}s: {benefits[0]} Ready to see a demo?"
        
        return "Let's schedule a quick demo."
    
    @function_tool
    async def show_available_meetings(self, context: RunContext, meeting_type: str = "demo") -> str:
        """Show available meeting slots for scheduling."""
        
        available_slots = []
        
        for slot in self.calendar_data.get("available_slots", []):
            if slot.get("available", False) and slot.get("type") == meeting_type:
                available_slots.append(slot)
        
        if not available_slots:
            return "I don't see any available slots for that meeting type right now. Would you like to try a different time?"
        
        options = available_slots[:5]
        name = self.lead_data.get("name", "")
        greeting = f"Great {name}! " if name else ""
        response = f"{greeting}Here are my available times:\n\n"
        
        for i, slot in enumerate(options, 1):
            response += f"{i}. {slot['date']} at {slot['time']} ({slot['duration']})\n"
        
        response += "\nWhich slot works best for you? Just say the number."
        return response
    
    @function_tool
    async def book_meeting(self, context: RunContext, slot_choice: str, meeting_type: str = "demo") -> str:
        """Book a meeting slot. REQUIRES email to be collected first."""
        
        # Check if email is collected
        if not self.lead_data.get("email"):
            return "I need your email address first to send the meeting confirmation. What's your email?"
        
        available_slots = [s for s in self.calendar_data.get("available_slots", []) 
                          if s.get("available", False) and s.get("type") == meeting_type]
        
        if not available_slots:
            return "I don't see any available slots for that meeting type. Let me check other options."
        
        selected_slot = None
        
        try:
            choice_num = int(slot_choice.strip())
            if 1 <= choice_num <= len(available_slots):
                selected_slot = available_slots[choice_num - 1]
        except ValueError:
            for slot in available_slots:
                if slot["time"].lower() in slot_choice.lower() or slot["date"] in slot_choice:
                    selected_slot = slot
                    break
        
        if not selected_slot:
            return "I didn't catch which time you prefer. Could you say the number or specific time again?"
        
        meeting_details = {
            "id": f"meeting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "slot_id": selected_slot["id"],
            "date": selected_slot["date"],
            "time": selected_slot["time"],
            "duration": selected_slot["duration"],
            "type": meeting_type,
            "lead_name": self.lead_data.get("name", "Prospect"),
            "lead_email": self.lead_data.get("email", ""),
            "lead_company": self.lead_data.get("company", ""),
            "booked_at": datetime.now().isoformat()
        }
        
        for slot in self.calendar_data["available_slots"]:
            if slot["id"] == selected_slot["id"]:
                slot["available"] = False
                break
        
        self.calendar_data["booked_meetings"].append(meeting_details)
        
        with open("mock_calendar.json", "w") as f:
            json.dump(self.calendar_data, f, indent=2)
        
        self.lead_data["booked_meeting"] = meeting_details
        
        # Generate and send confirmation email immediately
        await self.generate_follow_up_email(context)
        email_draft = self.lead_data.get("follow_up_email", {})
        
        if email_draft:
            html_body = self._generate_html_email(email_draft)
            email_sent = await self._send_email(
                recipient_email=self.lead_data.get("email", ""),
                subject=email_draft.get("subject", "Demo Confirmation"),
                body=html_body,
                is_html=True
            )
            
            if email_sent:
                logger.info(f"✅ Confirmation email sent to {self.lead_data.get('email', '')}")
            else:
                logger.warning(f"⚠️ Failed to send confirmation email")
        
        # Save lead data immediately after booking
        await self._save_lead_data()
        
        name = self.lead_data.get("name", "")
        email = self.lead_data.get("email", "")
        return f"✅ Perfect! Meeting booked for {selected_slot['date']} at {selected_slot['time']}. Confirmation email sent to {email}. Thanks {name}!"

    @function_tool
    async def check_required_info(self, context: RunContext) -> str:
        """Check if all required information has been collected from the user."""
        if self._has_required_info():
            return "All required information collected: ✅ Name, ✅ Email, ✅ Company, ✅ Role, ✅ Team Size, ✅ Timeline, ✅ Need. You can now answer questions or book meetings."
        else:
            missing = self._get_missing_info()
            return f"Still need to collect: {', '.join(missing)}. Please ask for these details first."
    
    @function_tool
    async def search_faq(self, context: RunContext, query: str) -> str:
        """Search company FAQ for relevant information.
        
        Args:
            query: The user's question or topic to search for
        """
        query_lower = query.lower()
        
        # Simple keyword matching
        for faq_item in self.company_data.get("faq", []):
            question = faq_item["question"].lower()
            answer = faq_item["answer"]
            
            # Check if query keywords match question
            if any(word in question for word in query_lower.split()):
                return answer
        
        # Check products if no FAQ match
        for product in self.company_data.get("products", []):
            if any(word in product["name"].lower() for word in query_lower.split()):
                return f"{product['name']}: {product['description']}"
        
        return "I don't have specific information about that. Let me connect you with our team for detailed information."
    
    @function_tool
    async def store_lead_info(self, context: RunContext, field: str, value: str) -> str:
        """Store lead information as it's collected during conversation.
        
        Args:
            field: The field name (name, company, email, role, use_case, pain_points, key_interests, team_size, timeline)
            value: The value to store
        """
        # Handle list fields (pain_points, key_interests)
        if field in ["pain_points", "key_interests"]:
            if field not in self.lead_data:
                self.lead_data[field] = []
            # Add to list if not already there
            if isinstance(value, str):
                # Split by common separators and add each item
                items = [item.strip() for item in value.replace(" and ", ", ").split(",")]
                for item in items:
                    if item and item not in self.lead_data[field]:
                        self.lead_data[field].append(item)
            logger.info(f"Stored lead info: {field} = {self.lead_data[field]}")
            return f"Got it, I've noted that down."
        else:
            self.lead_data[field] = value
            logger.info(f"Stored lead info: {field} = {value}")
            
            # Auto-detect persona when role is stored
            if field == "role":
                await self.detect_persona(context, value)
            
            return f"Got it, I've noted your {field}."
    
    @function_tool
    async def qualify_prospect(self, context: RunContext, qualification_data: str) -> str:
        """Qualify prospect based on BANT criteria and sales potential."""
        self.lead_data["qualification"] = qualification_data
        
        score = 0
        data_lower = qualification_data.lower()
        
        if any(word in data_lower for word in ["budget", "approved", "funded", "investment"]):
            score += 25
        
        if any(word in data_lower for word in ["cto", "ceo", "founder", "decision", "authorize"]):
            score += 25
            
        if any(word in data_lower for word in ["problem", "issue", "failing", "losing", "need"]):
            score += 25
            
        if any(word in data_lower for word in ["urgent", "asap", "this month", "immediately"]):
            score += 25
        
        self.lead_data["qualification_score"] = score
        
        if score >= 75:
            return "Excellent! You're a perfect fit. Let me get you connected with our solutions engineer immediately."
        elif score >= 50:
            return "Great! I can see real potential here. Let's schedule a quick demo to show you exactly how we can solve this."
        else:
            return "I understand your situation. Let me share some case studies of similar companies we've helped."
    
    @function_tool
    async def generate_crm_notes(self, context: RunContext) -> str:
        """Generate structured CRM notes from the conversation."""
        conversation_text = " ".join(self.conversation_transcript).lower()
        
        # Use stored pain points if available, otherwise detect from conversation
        pain_points = self.lead_data.get("pain_points", [])
        if not pain_points:
            pain_points = []
            pain_keywords = ["problem", "issue", "challenge", "difficult", "failing", "losing", "frustrated"]
            for keyword in pain_keywords:
                if keyword in conversation_text:
                    pain_points.append(f"Mentioned {keyword} with current solution")
        
        budget_mentioned = any(keyword in conversation_text for keyword in ["budget", "cost", "price", "afford", "investment"])
        
        decision_maker_level = "unknown"
        authority_keywords = {
            "high": ["ceo", "cto", "founder", "owner", "president", "vp"],
            "medium": ["manager", "director", "lead", "head"],
            "low": ["developer", "analyst", "coordinator", "associate"]
        }
        
        for level, keywords in authority_keywords.items():
            if any(keyword in conversation_text for keyword in keywords):
                decision_maker_level = level
                break
        
        # Infer timeline if not explicitly collected
        timeline = self.lead_data.get("timeline", "unknown")
        if timeline == "unknown":
            urgency_keywords = {
                "now": ["urgent", "asap", "immediately", "this week", "critical", "now"],
                "soon": ["soon", "this month", "next month", "quarter", "planning"],
                "later": ["eventually", "future", "someday", "later", "exploring"]
            }
            for time_level, keywords in urgency_keywords.items():
                if any(keyword in conversation_text for keyword in keywords):
                    timeline = time_level
                    self.lead_data["timeline"] = timeline
                    break
        
        # Map timeline to urgency level
        urgency_level = "low"
        if timeline == "now":
            urgency_level = "high"
        elif timeline == "soon":
            urgency_level = "medium"
        else:
            urgency_level = "low"
        
        # Calculate fit score
        fit_score = 0
        if pain_points: fit_score += 25
        if budget_mentioned: fit_score += 25
        if decision_maker_level == "high": fit_score += 30
        elif decision_maker_level == "medium": fit_score += 20
        elif decision_maker_level == "low": fit_score += 10
        if urgency_level == "high": fit_score += 20
        elif urgency_level == "medium": fit_score += 10
        
        # Get team size for scoring
        team_size = self.lead_data.get("team_size", "unknown")
        if team_size != "unknown":
            try:
                size_num = int(''.join(filter(str.isdigit, str(team_size))))
                if size_num >= 50:
                    fit_score += 10
                elif size_num >= 10:
                    fit_score += 5
            except:
                pass
        
        # Generate concise CRM-ready notes
        name = self.lead_data.get("name", "Prospect")
        company = self.lead_data.get("company", "Unknown Company")
        role = self.lead_data.get("role", "Unknown Role")
        use_case = self.lead_data.get("use_case", "payment solutions")
        
        notes_text = f"""
LEAD SUMMARY:
{name} from {company} ({role})
Team Size: {team_size}
Timeline: {timeline.upper()}

NEEDS:
- Use Case: {use_case}
- Pain Points: {', '.join(pain_points) if pain_points else 'Not specified'}

QUALIFICATION:
- Decision Authority: {decision_maker_level.upper()}
- Budget Discussed: {'Yes' if budget_mentioned else 'No'}
- Urgency: {urgency_level.upper()}
- Fit Score: {fit_score}/100

NEXT STEPS:
{self.lead_data.get('requested_next_step', 'Follow up with demo')}
""".strip()
        
        crm_notes = {
            "pain_points": pain_points or ["No specific pain points mentioned"],
            "budget_discussed": budget_mentioned,
            "decision_maker_level": decision_maker_level,
            "urgency_level": urgency_level,
            "timeline": timeline,
            "team_size": team_size,
            "fit_score": fit_score,
            "key_interests": self.lead_data.get("key_interests", [self.lead_data.get("use_case", "Payment solutions")]),
            "next_steps": self.lead_data.get("requested_next_step", "Follow up"),
            "notes": notes_text
        }
        
        self.lead_data["crm_notes"] = crm_notes
        return f"CRM notes generated with fit score: {fit_score}/100"
    
    @function_tool
    async def generate_follow_up_email(self, context: RunContext) -> str:
        """Generate a personalized follow-up email draft with conversation insights."""
        name = self.lead_data.get("name", "there")
        company = self.lead_data.get("company", "your company")
        use_case = self.lead_data.get("use_case", "payment solutions")
        persona = self.lead_data.get("detected_persona", "business professional")
        meeting = self.lead_data.get("booked_meeting")
        
        # Get conversation insights - ensure they're lists
        pain_points = self.lead_data.get("pain_points", [])
        if isinstance(pain_points, str):
            pain_points = [pain_points]
        
        key_interests = self.lead_data.get("key_interests", [])
        if isinstance(key_interests, str):
            key_interests = [key_interests]
            
        notes = self.lead_data.get("conversation_notes", "")
        
        if meeting:
            subject = f"Confirmation: {meeting['type'].title()} scheduled for {meeting['date']}"
        else:
            subject = f"Razorpay solutions for {company} - Next steps"
        
        # Persona-specific solutions
        solutions_map = {
            "developer": "Our 15-minute API integration with comprehensive SDKs and sandbox environment will solve your technical challenges. We'll show you webhook support and real-time testing tools.",
            "founder": "We'll demonstrate how to increase your conversion rates by 40% and recover lost revenue with our seamless checkout flow and global payment methods.",
            "product_manager": "Our demo will cover one-click payments, detailed analytics, A/B testing capabilities, and mobile-first design to improve your user experience.",
            "finance": "We'll walk through our transparent pricing with no hidden fees, automated reconciliation, and detailed financial reporting to optimize your costs.",
            "marketer": "We'll show you how to reduce checkout abandonment by 60%, support promotional codes, and access customer payment behavior data for better campaigns."
        }
        solution_text = solutions_map.get(persona, "We'll demonstrate how Razorpay can streamline your payment operations and drive business growth.")
        
        # Build concise email body (2-3 paragraphs)
        meeting_section = ""
        if meeting:
            meeting_section = f"""
✅ DEMO CONFIRMED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: {meeting['date']}
Time: {meeting['time']}
Duration: {meeting['duration']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
        
        # Paragraph 1: Thank you + context
        pain_context = ""
        if pain_points:
            pain_context = f" I understand you're facing challenges with {', '.join(pain_points[:2])}."
        
        # Paragraph 2: Solution
        # Paragraph 3: CTA
        
        email_body = f"""Hi {name},

Thank you for speaking with me today about {company}'s {use_case} needs.{pain_context}

{solution_text}

{meeting_section}{'Looking forward to our demo! ' if meeting else 'Would you like to schedule a quick 30-minute demo? '}Reply to this email or click here to book a time that works for you.

Best regards,
Priya
Sales Development Representative
Razorpay
priya@razorpay.com
"""
        
        email_draft = {
            "subject": subject,
            "body": email_body,
            "recipient": self.lead_data.get("email", ""),
            "generated_at": datetime.now().isoformat(),
            "pain_points": pain_points,
            "key_interests": key_interests,
            "conversation_notes": notes,
            "booked_meeting": meeting
        }
        
        self.lead_data["follow_up_email"] = email_draft
        
        return f"Follow-up email drafted with subject: '{subject}'. Ready to send!"
    
    def _generate_html_email(self, email_draft: dict) -> str:
        """Generate professional HTML email from email draft data."""
        name = self.lead_data.get("name", "there")
        company = self.lead_data.get("company", "your company")
        subject = email_draft.get("subject", "Follow-up from Razorpay")
        body = email_draft.get("body", "")
        
        # Get pain points and interests from lead_data (primary) or email_draft (fallback)
        pain_points = self.lead_data.get("pain_points", email_draft.get("pain_points", []))
        if isinstance(pain_points, str):
            pain_points = [pain_points]
            
        key_interests = self.lead_data.get("key_interests", email_draft.get("key_interests", []))
        if isinstance(key_interests, str):
            key_interests = [key_interests]
            
        booked_meeting = email_draft.get("booked_meeting")
        persona = self.lead_data.get("detected_persona", "business professional")
        use_case = self.lead_data.get("use_case", "payment solutions")
        
        # Get persona-specific solutions
        solutions_map = {
            "developer": "Our 15-minute API integration with comprehensive SDKs and sandbox environment will solve your technical challenges. We'll show you webhook support and real-time testing tools.",
            "founder": "We'll demonstrate how to increase your conversion rates by 40% and recover lost revenue with our seamless checkout flow and global payment methods.",
            "product_manager": "Our demo will cover one-click payments, detailed analytics, A/B testing capabilities, and mobile-first design to improve your user experience.",
            "finance": "We'll walk through our transparent pricing with no hidden fees, automated reconciliation, and detailed financial reporting to optimize your costs.",
            "marketer": "We'll show you how to reduce checkout abandonment by 60%, support promotional codes, and access customer payment behavior data for better campaigns."
        }
        solution_text = solutions_map.get(persona, "We'll demonstrate how Razorpay can streamline your payment operations and drive business growth.")
        
        # Build meeting confirmation section in HTML
        meeting_html = ""
        if booked_meeting:
            meeting_html = f"""
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 25px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <div style="font-size: 24px; font-weight: bold; margin-bottom: 15px;">✅ Demo Confirmed!</div>
                <div style="font-size: 18px; margin: 10px 0;">{booked_meeting['date']}</div>
                <div style="font-size: 20px; font-weight: bold; margin: 10px 0;">{booked_meeting['time']}</div>
                <div style="font-size: 14px; opacity: 0.9; margin-top: 10px;">Duration: {booked_meeting['duration']}</div>
            </div>
            """
        
        html_body = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header img {{
            max-width: 60px;
            margin-bottom: 15px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: bold;
        }}
        .header p {{
            margin: 8px 0 0 0;
            font-size: 14px;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .section {{
            margin: 25px 0;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            color: #667eea;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
            border-left: 3px solid #667eea;
            padding-left: 10px;
        }}
        .highlights {{
            background-color: #f8f9ff;
            border-left: 3px solid #667eea;
            padding: 12px 15px;
            border-radius: 4px;
            margin: 10px 0;
        }}
        .highlight-item {{
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }}
        .highlight-item:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #667eea;
            font-weight: bold;
        }}
        .meeting-box {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        .meeting-date {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        .meeting-time {{
            font-size: 20px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .meeting-duration {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 10px;
        }}
        .footer {{
            background-color: #f5f5f5;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }}
        .footer p {{
            margin: 5px 0;
        }}
        .divider {{
            height: 1px;
            background-color: #e0e0e0;
            margin: 25px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Razorpay</h1>
            <p>Your Personal Sales Development Representative</p>
        </div>
        
        <div class="content">
            {meeting_html}
            
            <div class="greeting">
                Hi {name},<br><br>
                Thank you for speaking with me today! I enjoyed learning about your business and challenges.
            </div>
            
            <div class="divider"></div>
"""
        
        # Add Pain Points section
        if pain_points:
            html_body += f"""
            <div class="section">
                <div class="section-title">🎯 Challenges You Mentioned</div>
                <div class="highlights">
                    {"".join([f'<div class="highlight-item">{point}</div>' for point in pain_points])}
                </div>
            </div>
"""
        
        # Add Solutions section
        html_body += f"""
            <div class="section">
                <div class="section-title">💡 How We'll Help</div>
                <div style="background-color: #f8f9ff; border-left: 3px solid #667eea; padding: 15px; border-radius: 4px; margin: 10px 0; line-height: 1.6;">
                    {solution_text}
                </div>
            </div>
"""
        
        # Add Key Interests section
        if key_interests:
            html_body += f"""
            <div class="section">
                <div class="section-title">📋 What We'll Cover in Demo</div>
                <div class="highlights">
                    {"".join([f'<div class="highlight-item">{interest}</div>' for interest in key_interests])}
                </div>
            </div>
"""
        
        html_body += f"""
            <div class="divider"></div>
            
            <p>I've prepared a customized demo specifically for {use_case}. We'll address each of your challenges and show you exactly how Razorpay can help.</p>
            <p>Looking forward to our conversation!</p>
        </div>
        
        <div class="footer">
            <p><strong>Priya</strong><br>
            Sales Development Representative<br>
            Razorpay</p>
            <p>📧 priya@razorpay.com</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_body
    
    async def _send_email(self, recipient_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send follow-up email to lead (async wrapper for SMTP)."""
        if not recipient_email or not self.sender_email or not self.sender_password:
            logger.warning("Email sending skipped: Missing email configuration")
            logger.warning(f"  - Recipient: {recipient_email}")
            logger.warning(f"  - Sender: {self.sender_email}")
            logger.warning(f"  - Password configured: {bool(self.sender_password)}")
            return False
        
        try:
            logger.info(f"📧 Preparing to send email to {recipient_email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Format: {'HTML' if is_html else 'Plain Text'}")
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg["From"] = formataddr((self.sender_name, self.sender_email))
            msg["To"] = recipient_email
            msg["Subject"] = subject
            
            # Add email body
            if is_html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Send email
            logger.info(f"🔌 Connecting to {self.smtp_server}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30) as server:
                logger.info("🔐 Starting TLS encryption")
                server.starttls()
                logger.info("🔑 Authenticating")
                server.login(self.sender_email, self.sender_password)
                logger.info("📤 Sending email")
                server.send_message(msg)
            
            logger.info(f"✅ Follow-up email sent successfully to {recipient_email}")
            logger.info(f"   Check inbox (or spam folder) at: {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP Authentication failed for {recipient_email}: {str(e)}")
            logger.error("   Check SENDER_EMAIL and SENDER_PASSWORD in .env.local")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error sending to {recipient_email}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending email to {recipient_email}: {str(e)}")
            logger.error(f"   Error type: {type(e).__name__}")
            return False
    
    @function_tool
    async def end_conversation(self, context: RunContext) -> str:
        """End the conversation and save comprehensive lead data."""
        if self.conversation_ended:
            return "Thank you for your time!"
        
        self.conversation_ended = True
        
        await self.generate_crm_notes(context)
        await self.generate_follow_up_email(context)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads/complete_lead_{timestamp}.json"
        
        lead_summary = {
            "timestamp": datetime.now().isoformat(),
            "lead_data": self.lead_data,
            "conversation_transcript": self.conversation_transcript,
            "sales_summary": self._generate_sales_summary(),
            "qualification_score": self.lead_data.get("qualification_score", 0),
            "recommended_action": self._get_recommended_action(),
            "is_returning_visitor": self.is_returning_visitor,
            "detected_persona": self.detected_persona
        }
        
        os.makedirs("leads", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(lead_summary, f, indent=2)
        
        logger.info(f"Complete lead data saved to {filename}")
        
        # Send follow-up email automatically (only if email was collected)
        recipient_email = self.lead_data.get("email", "")
        email_draft = self.lead_data.get("follow_up_email", {})
        
        if not recipient_email:
            logger.warning("No email address collected - skipping email send")
            return self._generate_sales_summary() + "\n\n⚠️ Note: No email address was collected during the conversation."
        
        if recipient_email and email_draft:
            # Generate HTML version of email
            html_body = self._generate_html_email(email_draft)
            
            email_sent = await self._send_email(
                recipient_email=recipient_email,
                subject=email_draft.get("subject", "Follow-up from Razorpay"),
                body=html_body,
                is_html=True
            )
            self.email_sent = email_sent
            lead_summary["email_sent"] = email_sent
            lead_summary["email_sent_at"] = datetime.now().isoformat() if email_sent else None
            
            # Update saved file with email status
            with open(filename, "w") as f:
                json.dump(lead_summary, f, indent=2)
            
            if email_sent:
                summary = self._generate_sales_summary()
                return summary + "\n\n✉️ Follow-up email has been sent to " + recipient_email
        
        return self._generate_sales_summary()
    
    def _generate_sales_summary(self) -> str:
        """Generate a sales-focused summary with next steps."""
        name = self.lead_data.get("name", "")
        company = self.lead_data.get("company", "your company")
        next_step = self.lead_data.get("requested_next_step", "follow up")
        score = self.lead_data.get("qualification_score", 0)
        
        if score >= 75:
            return f"Excellent conversation {name}! Based on {company}'s needs, I'm prioritizing your {next_step} for immediate action. You'll hear from our team within 2 hours. This is exactly the kind of partnership that drives real results!"
        elif score >= 50:
            return f"Great talking with you {name}! {company} has strong potential with Razorpay. I'm scheduling your {next_step} for this week. Our solutions will definitely address your payment challenges."
        else:
            return f"Thanks {name}! I'll make sure {company} gets the right information. Our team will follow up on the {next_step} within 24 hours."
    
    def _get_recommended_action(self) -> str:
        """Determine recommended sales action based on qualification."""
        score = self.lead_data.get("qualification_score", 0)
        
        if score >= 75:
            return "HOT LEAD - Immediate demo/trial setup required"
        elif score >= 50:
            return "WARM LEAD - Schedule demo within 48 hours"
        else:
            return "COLD LEAD - Send nurture content, follow up in 1 week"


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }
    
    # Load environment variables explicitly
    load_dotenv(".env.local", override=True)
    
    # Get Azure credentials
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_version = os.getenv("AZURE_OPENAI_API_VERSION")
    
    logger.info(f"Azure Endpoint: {azure_endpoint}")
    logger.info(f"Azure Deployment: {azure_deployment}")
    logger.info(f"Azure API Key present: {bool(azure_key)}")

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=openai.LLM.with_azure(
                azure_endpoint=azure_endpoint,
                azure_deployment=azure_deployment,
                api_version=azure_version,
                api_key=azure_key,
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-US-alicia", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # To use a realtime model instead of a voice pipeline, use the following session setup instead.
    # (Note: This is for the OpenAI Realtime API. For other providers, see https://docs.livekit.io/agents/models/realtime/))
    # 1. Install livekit-agents[openai]
    # 2. Set OPENAI_API_KEY in .env.local
    # 3. Add `from livekit.plugins import openai` to the top of this file
    # 4. Use the following session setup instead of the version above
    # session = AgentSession(
    #     llm=openai.realtime.RealtimeModel(voice="marin")
    # )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # # Add a virtual avatar to the session, if desired
    # # For other providers, see https://docs.livekit.io/agents/models/avatar/
    # avatar = hedra.AvatarSession(
    #   avatar_id="...",  # See https://docs.livekit.io/agents/models/avatar/plugins/hedra
    # )
    # # Start the avatar and wait for it to join
    # await avatar.start(session, room=ctx.room)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=CompleteSDRAssistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
