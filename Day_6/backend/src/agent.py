import logging
import os
import asyncio
import random
from datetime import datetime
from typing import Annotated, Literal, Optional
from dataclasses import dataclass, field

print("\n========== FRAUD ALERT AGENT LOADED ==========\n")

from dotenv import load_dotenv
from pydantic import Field
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
    RunContext,
    function_tool,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from database import FraudDatabase, FraudCase as DBFraudCase

logger = logging.getLogger("agent")

load_dotenv(".env.local")

# Initialize database
db = FraudDatabase()

# ======================================================
# FRAUD CASE STATE
# ======================================================
@dataclass
class FraudCase:
    """Fraud case data structure"""
    id: str
    userName: str
    securityIdentifier: str
    cardEnding: str
    cardType: str
    transactionName: str
    transactionAmount: str
    transactionTime: str
    transactionLocation: str
    transactionCategory: str
    transactionSource: str
    status: str
    securityQuestion: str
    securityAnswer: str
    createdAt: str
    outcome: str | None = None
    outcomeNote: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "userName": self.userName,
            "securityIdentifier": self.securityIdentifier,
            "cardEnding": self.cardEnding,
            "cardType": self.cardType,
            "transactionName": self.transactionName,
            "transactionAmount": self.transactionAmount,
            "transactionTime": self.transactionTime,
            "transactionLocation": self.transactionLocation,
            "transactionCategory": self.transactionCategory,
            "transactionSource": self.transactionSource,
            "status": self.status,
            "securityQuestion": self.securityQuestion,
            "securityAnswer": self.securityAnswer,
            "createdAt": self.createdAt,
            "outcome": self.outcome,
            "outcomeNote": self.outcomeNote,
        }

@dataclass
class SessionData:
    """Session state for fraud detection"""
    fraud_case: FraudCase | None = None
    user_verified: bool = False
    call_phase: str = "initial"  # initial, verification, transaction_review, resolution, completed

# ======================================================
# DATABASE OPERATIONS
# ======================================================
def save_fraud_case(fraud_case: FraudCase) -> bool:
    """Save updated fraud case back to database"""
    try:
        success = db.update_fraud_case_status(
            fraud_case.id,
            fraud_case.status,
            fraud_case.outcome or "pending",
            fraud_case.outcomeNote or ""
        )
        
        if success:
            logger.info(f"✅ Fraud case {fraud_case.id} saved successfully")
            logger.info(f"   Status: {fraud_case.status}")
            logger.info(f"   Outcome: {fraud_case.outcome}")
            logger.info(f"   Note: {fraud_case.outcomeNote}")
        
        return success
    except Exception as e:
        logger.error(f"Error saving fraud case: {e}")
        return False

# ======================================================
# FUNCTION TOOLS FOR FRAUD AGENT
# ======================================================

@function_tool
async def verify_customer_card(
    ctx: RunContext[SessionData],
    card_ending_digits: Annotated[str, Field(description="Last 4 digits of customer's card")],
) -> str:
    """First step: Identify customer by card ending digits"""
    provided_digits = card_ending_digits.strip().replace(" ", "")
    
    try:
        print(f"\n🔍 DEBUG: Looking for card ending: {repr(provided_digits)}")
        print(f"🔍 DEBUG: All cards in database:")
        all_cases = db.get_all_fraud_cases()
        for case in all_cases:
            print(f"   - {case.userName}: {repr(case.cardEnding)}")
        
        # Query database for matching card ending
        matching_case = db.get_fraud_case_by_card(provided_digits)
        print(f"🔍 DEBUG: Query result: {matching_case}")
        
        if not matching_case:
            print(f"❌ NO MATCHING CARD FOUND for digits: {provided_digits}")
            return "I'm sorry, I cannot find an account matching those card digits. For security reasons, I cannot proceed. This call will be ended."
        
        # Found matching card - convert to agent FraudCase and update session
        fraud_case = FraudCase(
            id=matching_case.id,
            userName=matching_case.userName,
            securityIdentifier=matching_case.securityIdentifier,
            cardEnding=matching_case.cardEnding,
            cardType=matching_case.cardType,
            transactionName=matching_case.transactionName,
            transactionAmount=matching_case.transactionAmount,
            transactionTime=matching_case.transactionTime,
            transactionLocation=matching_case.transactionLocation,
            transactionCategory=matching_case.transactionCategory,
            transactionSource=matching_case.transactionSource,
            status=matching_case.status,
            securityQuestion=matching_case.securityQuestion,
            securityAnswer=matching_case.securityAnswer,
            createdAt=matching_case.createdAt,
            outcome=matching_case.outcome,
            outcomeNote=matching_case.outcomeNote
        )
        
        ctx.userdata.fraud_case = fraud_case
        security_question = matching_case.securityQuestion
        print(f"✅ CARD VERIFIED: {matching_case.userName} (Card: {provided_digits})")
        print(f"   Now asking security question: {security_question}")
        
        return f"Great! I found your account for {matching_case.userName}. Now, to complete the verification, please answer this security question: {security_question}"
    
    except Exception as e:
        logger.error(f"Error verifying card: {e}")
        return "There was an error verifying your identity. Please try again later."

@function_tool
async def verify_customer_security(
    ctx: RunContext[SessionData],
    security_answer: Annotated[str, Field(description="Answer to the customer's security question")],
) -> str:
    """Second step: Verify security question answer"""
    if ctx.userdata.fraud_case is None:
        return "No customer card verified yet. Please provide your card number first."
    
    fraud_case = ctx.userdata.fraud_case
    provided_answer = security_answer.strip().lower()
    correct_answer = fraud_case.securityAnswer.lower().strip()
    
    if provided_answer == correct_answer:
        ctx.userdata.user_verified = True
        print(f"✅ SECURITY QUESTION VERIFIED for {fraud_case.userName}")
        return f"Perfect! Your identity has been fully verified. Now let me tell you about the suspicious transaction we detected on your {fraud_case.cardType} card ending in {fraud_case.cardEnding}."
    else:
        print(f"❌ SECURITY ANSWER FAILED for {fraud_case.userName}")
        return "I'm sorry, that answer is incorrect. For security reasons, I cannot proceed without proper verification. This call will be ended."

@function_tool
async def get_current_fraud_case_details(
    ctx: RunContext[SessionData],
) -> str:
    """Get the current verified fraud case details for the conversation"""
    if ctx.userdata.fraud_case is None:
        return "No active fraud case at this time."
    
    case = ctx.userdata.fraud_case
    return f"Current fraud case - Customer: {case.userName}, Card: {case.cardType} ending in {case.cardEnding}, Transaction: {case.transactionName}, Amount: {case.transactionAmount}, Date/Time: {case.transactionTime}, Location: {case.transactionLocation}, Category: {case.transactionCategory}"

@function_tool
async def confirm_transaction_legitimate(
    ctx: RunContext[SessionData],
) -> str:
    """Mark transaction as confirmed legitimate by customer"""
    if ctx.userdata.fraud_case is None:
        return "No active fraud case."
    
    fraud_case = ctx.userdata.fraud_case
    fraud_case.status = "confirmed_safe"
    fraud_case.outcome = "legitimate"
    fraud_case.outcomeNote = f"Customer confirmed transaction as legitimate on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"✅ TRANSACTION CONFIRMED SAFE: {fraud_case.id}")
    print(f"   Customer: {fraud_case.userName}")
    print(f"   Transaction: {fraud_case.transactionName} - {fraud_case.transactionAmount}")
    
    save_fraud_case(fraud_case)
    
    return f"Excellent! We have confirmed that the transaction of {fraud_case.transactionAmount} at {fraud_case.transactionName} was authorized by you. Your account remains secure and the case is now closed."

@function_tool
async def report_transaction_fraudulent(
    ctx: RunContext[SessionData],
) -> str:
    """Mark transaction as fraudulent and take protective action"""
    if ctx.userdata.fraud_case is None:
        return "No active fraud case."
    
    fraud_case = ctx.userdata.fraud_case
    fraud_case.status = "confirmed_fraud"
    fraud_case.outcome = "fraudulent"
    fraud_case.outcomeNote = f"Customer reported as fraudulent. Card blocked and dispute initiated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    print(f"⚠️ TRANSACTION MARKED FRAUDULENT: {fraud_case.id}")
    print(f"   Customer: {fraud_case.userName}")
    print(f"   Transaction: {fraud_case.transactionName} - {fraud_case.transactionAmount}")
    print(f"   Protective Actions: Card blocked, dispute raised")
    
    save_fraud_case(fraud_case)
    
    return f"We understand. This transaction has been flagged as fraudulent. We are immediately blocking your card ending in {fraud_case.cardEnding} to prevent further unauthorized transactions. A dispute has been raised for the {fraud_case.transactionAmount} charge. You will receive a replacement card within 3 to 5 business days. Is there anything else we can help you with?"

class FraudDetectionAgent(Agent):
    def __init__(self, fraud_case: Optional[FraudCase] = None):
        # Build dynamic instructions - use the fraud case details if available
        # But also emphasize that agent should use function tools to access current fraud case
        if fraud_case:
            instructions = f"""
            You are a professional fraud detection specialist for SecureBank, a fictional banking institution.
            
            Your role is to investigate suspicious transactions and protect customer accounts.
            
            CRITICAL RULES:
            1. NEVER ask for full card numbers, PINs, passwords, or sensitive credentials
            2. NEVER ask for full account numbers or full security identifiers
            3. Only ask the customer to confirm the LAST 4 DIGITS of their card ending number
            4. Be calm, professional, and reassuring
            5. Explain that this is a routine security check
            6. IMPORTANT: After verification, always use the ACTUAL fraud case data that was verified (the customer may provide a different card number than initially expected)
            
            CONVERSATION FLOW:
            1. Greet and introduce yourself as SecureBank Fraud Department
            2. Explain you're calling about a suspicious transaction
            3. STEP 1: Ask for the last 4 digits of their card ending number
            4. STEP 2: Once you know which customer it is, ask THEIR specific security question (you will know their question after step 1)
            5. After BOTH verifications pass, read out the transaction details
            6. Ask if customer made the transaction (simple yes/no)
            7. Use the appropriate tool to mark as safe or fraudulent
            8. Close with protective action summary
            
            Keep responses concise, no complex punctuation, no emojis, professional and reassuring tone.
            """
        else:
            instructions = """
            You are a professional fraud detection specialist for SecureBank, a fictional banking institution.
            
            Your role is to investigate suspicious transactions and protect customer accounts.
            
            CRITICAL RULES:
            1. NEVER ask for full card numbers, PINs, passwords, or sensitive credentials
            2. NEVER ask for full account numbers or full security identifiers
            3. Only ask the customer to confirm the LAST 4 DIGITS of their card ending number
            4. Be calm, professional, and reassuring
            5. Explain that this is a routine security check
            
            CONVERSATION FLOW:
            1. Greet and introduce yourself as SecureBank Fraud Department
            2. Explain you're calling about a suspicious transaction
            3. Ask the customer to confirm the last 4 digits of their card ending number
            4. After verification, read out the transaction details to the customer
            5. Ask if customer made the transaction (simple yes/no)
            6. Use the appropriate tool to mark as safe or fraudulent
            7. Close with protective action summary
            
            Keep responses concise, no complex punctuation, no emojis, professional and reassuring tone.
            """
        
        super().__init__(
            instructions=instructions,
            tools=[
                verify_customer_card,
                verify_customer_security,
                get_current_fraud_case_details,
                confirm_transaction_legitimate,
                report_transaction_fraudulent,
            ],
        )

# ======================================================
# PREWARM
# ======================================================
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

# ======================================================
# MAIN ENTRYPOINT
# ======================================================
async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "="*60)
    print("🏦 FRAUD ALERT AGENT - SECUREBANK FRAUD DEPARTMENT")
    print("📁 Database: SQLite (fraud_cases.db)")
    print("="*60 + "\n")

    # Create session data
    session_data = SessionData()
    
    # Load a random fraud case from the database
    # In production, this would be triggered by an actual incoming call with customer ID
    try:
        all_cases = db.get_all_fraud_cases()
        
        if all_cases:
            # Randomly select a fraud case
            selected_case_data = random.choice(all_cases)
            fraud_case = FraudCase(
                id=selected_case_data.id,
                userName=selected_case_data.userName,
                securityIdentifier=selected_case_data.securityIdentifier,
                cardEnding=selected_case_data.cardEnding,
                cardType=selected_case_data.cardType,
                transactionName=selected_case_data.transactionName,
                transactionAmount=selected_case_data.transactionAmount,
                transactionTime=selected_case_data.transactionTime,
                transactionLocation=selected_case_data.transactionLocation,
                transactionCategory=selected_case_data.transactionCategory,
                transactionSource=selected_case_data.transactionSource,
                status=selected_case_data.status,
                securityQuestion=selected_case_data.securityQuestion,
                securityAnswer=selected_case_data.securityAnswer,
                createdAt=selected_case_data.createdAt,
                outcome=selected_case_data.outcome,
                outcomeNote=selected_case_data.outcomeNote
            )
            session_data.fraud_case = fraud_case
            
            print(f"📞 INCOMING FRAUD ALERT CALL")
            print(f"👤 Customer: {session_data.fraud_case.userName}")
            print(f"🆔 Fraud Case ID: {session_data.fraud_case.id}")
            print(f"💳 Card: {session_data.fraud_case.cardType} ending in {session_data.fraud_case.cardEnding}")
            print(f"🛍️  Transaction: {session_data.fraud_case.transactionName}")
            print(f"💰 Amount: {session_data.fraud_case.transactionAmount}")
            print(f"🌍 Location: {session_data.fraud_case.transactionLocation}")
            print(f"⏰ Time: {session_data.fraud_case.transactionTime}")
            print(f"❓ Security Q: {session_data.fraud_case.securityQuestion}")
            print(f"   (Answer: {session_data.fraud_case.securityAnswer})")
            print("-"*60 + "\n")
    except Exception as e:
        logger.error(f"Error loading fraud case from database: {e}")
    
    # Create session
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-IN-anusha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=session_data,
    )

    usage_collector = metrics.UsageCollector()
    
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=FraudDetectionAgent(fraud_case=session_data.fraud_case),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))

