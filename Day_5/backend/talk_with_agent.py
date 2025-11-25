#!/usr/bin/env python3
"""
Simple CLI script to talk with the Razorpay SDR Agent
Tests core functionality without needing LiveKit setup
"""

import json
import os
from datetime import datetime

def load_company_data():
    """Load company FAQ data"""
    try:
        with open("company_data/razorpay_faq.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ company_data/razorpay_faq.json not found")
        return None

def search_faq(company_data, query):
    """Search FAQ for answer"""
    query_lower = query.lower()
    
    for faq_item in company_data.get("faq", []):
        question = faq_item["question"].lower()
        if any(word in question for word in query_lower.split()):
            return faq_item["answer"]
    
    for product in company_data.get("products", []):
        if any(word in product["name"].lower() for word in query_lower.split()):
            return f"{product['name']}: {product['description']}"
    
    return "I don't have specific information about that. Let me connect you with our team for detailed information."

def detect_persona(user_input, personas_data):
    """Detect user persona"""
    input_lower = user_input.lower()
    
    persona_scores = {}
    for persona_name, persona_data in personas_data.get("personas", {}).items():
        score = 0
        for keyword in persona_data.get("keywords", []):
            if keyword in input_lower:
                score += 1
        persona_scores[persona_name] = score
    
    if persona_scores:
        detected = max(persona_scores, key=persona_scores.get)
        if persona_scores[detected] > 0:
            return detected
    
    return None

def calculate_qualification_score(conversation):
    """Calculate BANT score from conversation"""
    score = 0
    text = " ".join(conversation).lower()
    
    if any(word in text for word in ["budget", "approved", "funded", "investment"]):
        score += 25
    
    if any(word in text for word in ["cto", "ceo", "founder", "decision", "authorize"]):
        score += 25
    
    if any(word in text for word in ["problem", "issue", "failing", "losing", "need"]):
        score += 25
    
    if any(word in text for word in ["urgent", "asap", "this month", "immediately"]):
        score += 25
    
    return score

def get_lead_temperature(score):
    """Get lead temperature based on score"""
    if score >= 75:
        return "🔥 HOT"
    elif score >= 50:
        return "🌡️ WARM"
    else:
        return "❄️ COLD"

def save_lead(lead_data):
    """Save lead to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"leads/cli_lead_{timestamp}.json"
    
    os.makedirs("leads", exist_ok=True)
    
    with open(filename, "w") as f:
        json.dump(lead_data, f, indent=2)
    
    return filename

def main():
    """Main conversation loop"""
    print("=" * 70)
    print("🎤 Razorpay SDR Agent - Interactive Chat")
    print("=" * 70)
    print()
    print("Hi! I'm Priya from Razorpay 👋")
    print("Type 'quit' to end conversation")
    print("Type 'summary' to see lead summary")
    print()
    print("-" * 70)
    print()
    
    # Load data
    company_data = load_company_data()
    if not company_data:
        return
    
    try:
        with open("personas.json", "r") as f:
            personas_data = json.load(f)
    except FileNotFoundError:
        personas_data = {"personas": {}}
    
    # Initialize conversation
    lead_data = {}
    conversation = []
    persona = None
    
    # Initial greeting
    greeting = "What brought you here today?"
    print(f"Priya: {greeting}\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
        except EOFError:
            break
        
        if not user_input:
            continue
        
        if user_input.lower() == "quit":
            print("\nPriya: Thank you for chatting with me! Our team will follow up soon. 👋\n")
            break
        
        if user_input.lower() == "summary":
            print("\n" + "=" * 70)
            print("📊 LEAD SUMMARY")
            print("=" * 70)
            print(json.dumps(lead_data, indent=2))
            print("=" * 70 + "\n")
            continue
        
        conversation.append(user_input)
        
        # Detect persona if not already detected
        if not persona:
            persona = detect_persona(user_input, personas_data)
            if persona:
                print(f"\n[System: Detected persona - {persona}]\n")
        
        # Store specific lead info
        if "name" in user_input.lower() and "i'm" in user_input.lower():
            # Try to extract name
            parts = user_input.split("i'm")[-1].strip().split("from")[0].strip()
            if parts:
                lead_data["name"] = parts
                print(f"[System: Stored name - {parts}]\n")
        
        if "company" in user_input.lower() or "from" in user_input.lower():
            words = user_input.split()
            for i, word in enumerate(words):
                if word.lower() in ["from", "company"]:
                    if i + 1 < len(words):
                        company = " ".join(words[i+1:i+3])
                        if company and len(company) > 2:
                            lead_data["company"] = company
                            print(f"[System: Stored company - {company}]\n")
                            break
        
        if "@" in user_input and "." in user_input:
            email = user_input.split()
            for word in email:
                if "@" in word and "." in word:
                    lead_data["email"] = word
                    print(f"[System: Stored email - {word}]\n")
                    break
        
        # Generate response using FAQ
        response = search_faq(company_data, user_input)
        
        # Persona-specific response
        if persona and persona in personas_data.get("personas", {}):
            persona_info = personas_data["personas"][persona]
            if any(word in user_input.lower() for word in ["benefit", "what", "how", "why"]):
                benefits = persona_info.get("key_benefits", [])
                if benefits:
                    response = f"Great question! For {persona}s like you, here are key benefits:\n"
                    for i, benefit in enumerate(benefits[:2], 1):
                        response += f"{i}. {benefit}\n"
        
        print(f"\nPriya: {response}\n")
        
        # Check for end-of-conversation signals
        if any(word in user_input.lower() for word in ["that's all", "done", "thanks", "bye", "goodbye"]):
            print("=" * 70)
            print("📋 CALL SUMMARY")
            print("=" * 70)
            
            # Calculate score
            score = calculate_qualification_score(conversation)
            temp = get_lead_temperature(score)
            
            print(f"\nLead Quality: {temp} ({score}/100)")
            
            if persona:
                print(f"Persona: {persona}")
                lead_data["detected_persona"] = persona
            
            if lead_data:
                print(f"\nCaptured Lead Info:")
                for key, value in lead_data.items():
                    print(f"  • {key}: {value}")
            
            # Save lead
            lead_data["score"] = score
            lead_data["temperature"] = temp
            lead_data["conversation"] = conversation
            lead_data["timestamp"] = datetime.now().isoformat()
            
            filename = save_lead(lead_data)
            print(f"\n✅ Lead data saved to: {filename}")
            print("=" * 70)
            break
    
    print("\n✉️ Follow-up email will be sent automatically when using LiveKit agent!")
    print("📚 For full feature demo with voice, run: uv run python src/agent.py dev\n")

if __name__ == "__main__":
    main()
