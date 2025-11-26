# Day 6 Backend - Fraud Alert Voice Agent

**Part of 10 Days of Voice Agents Challenge**

A complete fraud alert voice agent implementation for a fictional bank (SecureBank) that detects suspicious transactions, verifies customer identity, and handles fraud cases.

## 🎯 MVP Features

✅ **Sample Fraud Cases Database** - 4 realistic fake fraud cases in `fraud_cases.json`  
✅ **Voice Agent Persona** - Professional fraud department representative  
✅ **Identity Verification** - Security question-based verification (non-sensitive)  
✅ **Transaction Review** - Agent reads suspicious transaction details  
✅ **Fraud Classification** - Mark as legitimate or fraudulent  
✅ **Database Persistence** - Update case status and outcomes  
✅ **Voice AI Pipeline** - Deepgram STT, Google Gemini LLM, Murf TTS  

## 📋 Quick Start

### 1. Setup Environment
```bash
cd Day_6/backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

### 2. Configure API Keys
```bash
cp .env.example .env.local
# Edit .env.local with your API keys:
#   GOOGLE_API_KEY
#   DEEPGRAM_API_KEY
#   MURF_API_KEY
#   LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
```

### 3. Run the Agent
```bash
python -m livekit.agents dev
# Or: python src/agent.py dev
```

### 4. Test with Frontend
- Go to https://meet.livekit.io
- Enter your LiveKit URL and room name
- The fraud agent will automatically engage

## 📁 Project Structure

```
Day_6/backend/
├── src/
│   ├── agent.py              # Main fraud detection agent
│   └── __init__.py
├── fraud_cases.json          # Sample fraud case database
├── pyproject.toml            # Python dependencies
├── .env.example              # Environment template
├── .env.local                # Local secrets (not in repo)
├── README.md                 # This file
└── tests/
    └── test_agent.py         # Agent tests
```

## 🛠️ How It Works

### Database Structure

`fraud_cases.json` contains 4 sample fraud cases with fields:
- **id** - Case identifier (FC001, FC002, etc.)
- **userName** - Customer name (fake)
- **cardEnding** - Masked card number (****4242)
- **transactionName** - Merchant name
- **transactionAmount** - Transaction amount
- **transactionTime** - When the transaction occurred
- **transactionLocation** - Fraudulent location
- **securityQuestion** - Non-sensitive verification question
- **securityAnswer** - Answer to security question
- **status** - Current case status
- **outcome** - Case result (legitimate/fraudulent)
- **outcomeNote** - Detailed outcome summary

### Agent Flow

```
1. GREETING
   Agent: "Hello, SecureBank Fraud Department..."
   
2. VERIFICATION
   Agent: "To verify, answer this security question..."
   Customer: [Provides answer]
   
   ✅ Correct → Continue
   ❌ Wrong → End call
   
3. TRANSACTION REVIEW
   Agent: "We detected a transaction at [Merchant]..."
   Agent: "Amount: [Amount], Location: [Location]"
   Agent: "Did you make this transaction?"
   
4. CLASSIFICATION
   Customer: "Yes" → Mark as SAFE
   Customer: "No" → Mark as FRAUDULENT
   
5. CLOSURE
   Agent: "Your [action] has been processed..."
   Call ends, database updated
```

### Function Tools

The agent can call these tools:

**`verify_customer(answer: str)`**
- Compares answer to stored security answer
- Enables proceeding if correct
- Ends call if incorrect

**`confirm_transaction_legitimate()`**
- Marks case as confirmed_safe
- Saves to database
- Provides confirmation message

**`report_transaction_fraudulent()`**
- Marks case as confirmed_fraud
- Updates database with protective actions
- Describes card blocking and dispute process

## 💾 Database Format

### Example Case Entry

```json
{
  "id": "FC001",
  "userName": "John Smith",
  "securityIdentifier": "12345",
  "cardEnding": "4242",
  "cardType": "Visa",
  "transactionName": "ABC Industry Limited",
  "transactionAmount": "$1,250.00",
  "transactionTime": "2025-01-15 03:45 AM",
  "transactionLocation": "Shanghai, China",
  "transactionCategory": "e-commerce",
  "transactionSource": "alibaba.com",
  "status": "pending_review",
  "securityQuestion": "What is the last 4 digits of your phone number?",
  "securityAnswer": "5678",
  "createdAt": "2025-01-15T03:45:00Z",
  "outcome": null,
  "outcomeNote": null
}
```

### After Call (Updated)

```json
{
  "status": "confirmed_safe",
  "outcome": "legitimate",
  "outcomeNote": "Customer confirmed transaction as legitimate on 2025-01-15 14:32:45"
}
```

## 🎭 Sample Fraud Cases

### Case 1: John Smith
- Card: Visa ****4242
- Transaction: ABC Industry Limited - $1,250 (alibaba.com)
- Location: Shanghai, China
- Time: 2025-01-15 03:45 AM
- Security Q: "Last 4 digits of your phone number?"
- Answer: "5678"

### Case 2: Sarah Johnson
- Card: Mastercard ****8765
- Transaction: Premium Electronics - $3,500
- Location: Los Angeles, CA
- Time: 2025-01-14 11:22 PM
- Security Q: "What is your favorite city?"
- Answer: "Boston"

### Case 3: Michael Brown
- Card: Visa ****5555
- Transaction: International Travel Agency - $8,900
- Location: Dubai, UAE
- Time: 2025-01-15 06:15 AM
- Security Q: "What is your mother's maiden name?"
- Answer: "Williams"

### Case 4: Emily Davis
- Card: Amex ****3333
- Transaction: Luxury Fashion House - $5,600
- Location: Paris, France
- Time: 2025-01-14 02:30 PM
- Security Q: "In what city were you born?"
- Answer: "Seattle"

## 🔧 Configuration

### Environment Variables

Edit `.env.local`:
```bash
# LiveKit Configuration
LIVEKIT_URL=ws://127.0.0.1:7880          # Local or cloud URL
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# API Keys
GOOGLE_API_KEY=your_key_here             # Gemini LLM
DEEPGRAM_API_KEY=your_key_here           # Speech-to-Text
MURF_API_KEY=your_key_here               # Text-to-Speech
```

### Voice Configuration

In `src/agent.py`, modify these for different voices:
```python
tts=murf.TTS(
    voice="en-US-matthew",      # Change voice here
    style="Conversation",        # Or "Professional", etc.
    text_pacing=True,
)
```

## 📊 Technologies

| Component | Service | Model |
|-----------|---------|-------|
| **Speech-to-Text** | Deepgram | Nova-3 |
| **Language Model** | Google Cloud | Gemini 2.5 Flash |
| **Text-to-Speech** | Murf AI | Matthew (Conversation) |
| **Turn Detection** | LiveKit | Multilingual |
| **Voice Activity** | Silero | VAD |
| **Noise Cancellation** | LiveKit | BVC |

## 🧪 Testing

### Manual Test

1. Start the agent: `python -m livekit.agents dev`
2. Go to https://meet.livekit.io
3. Enter LiveKit URL and join room
4. When asked for security answer, provide correct answer (e.g., "5678")
5. Agent reads transaction
6. Say "Yes" or "No" to confirm/deny
7. Check console for logs and verify database update

### Console Output

```
========== FRAUD ALERT AGENT - SECUREBANK FRAUD DEPARTMENT
📁 Fraud Cases Database: /path/to/fraud_cases.json

📞 INCOMING FRAUD ALERT CALL
👤 Customer: John Smith
🆔 Fraud Case ID: FC001
💳 Card: Visa ending in 4242
💰 Amount: $1,250.00
🌍 Location: Shanghai, China
```

### Verify Database Update

After call completes, check `fraud_cases.json`:
```bash
cat fraud_cases.json | grep -A 5 "FC001"
```

Should show:
- `"status": "confirmed_safe"` or `"status": "confirmed_fraud"`
- `"outcome": "legitimate"` or `"outcome": "fraudulent"`
- `"outcomeNote"` with timestamp

## 🚀 Running Commands

### Download Models
```bash
python src/agent.py download-files
```

### Interactive Console
```bash
python src/agent.py console
```

### Dev Server
```bash
python src/agent.py dev
```

### Production
```bash
python src/agent.py start
```

## 🐳 Docker Deployment

```bash
docker build -t fraud-agent .
docker run -p 8081:8081 \
  -e GOOGLE_API_KEY=your_key \
  -e DEEPGRAM_API_KEY=your_key \
  -e MURF_API_KEY=your_key \
  -e LIVEKIT_URL=your_url \
  fraud-agent
```

## 🐛 Troubleshooting

### Issue: "Cannot import livekit"
**Solution:** Install dependencies
```bash
pip install -e .
```

### Issue: "API key is invalid"
**Solution:** Check `.env.local` has correct keys from:
- Google Cloud Console
- Deepgram Dashboard
- Murf AI Console
- LiveKit Dashboard

### Issue: "Connection refused"
**Solution:** Ensure LiveKit server is running
```bash
livekit-server --dev
```

### Issue: "No audio input/output"
**Solution:**
- Check browser microphone permissions
- Test microphone on another website
- Verify input/output devices in browser settings

### Issue: "fraud_cases.json not found"
**Solution:**
- File should be in `Day_6/backend/fraud_cases.json`
- Check console output for actual path
- Ensure running from correct directory

### Issue: "Database not updating"
**Solution:**
- Check file permissions (needs write access)
- Verify JSON format is valid
- Check console for error messages
- Ensure agent completes full conversation

## 📚 Code Overview

### Main Classes

**FraudCase** - Data model for fraud cases
- Stores all case information
- Methods: `to_dict()` for serialization

**SessionData** - Per-call session state
- `fraud_case` - Current case being investigated
- `user_verified` - Whether customer passed verification
- `call_phase` - Current conversation phase

**FraudDetectionAgent** - The agent personality
- Inherits from LiveKit Agent
- Instructions for fraud department behavior
- Configured with 3 function tools

### Main Functions

**`load_fraud_case_by_name(username)`** - Load case from database  
**`save_fraud_case(case)`** - Update case in database  
**`verify_customer(answer)`** - Tool: Verify customer identity  
**`confirm_transaction_legitimate()`** - Tool: Mark as safe  
**`report_transaction_fraudulent()`** - Tool: Mark as fraud  

## 🎯 MVP Checklist

- [x] Created fraud_cases.json with 4 sample cases
- [x] Agent loads case at call start
- [x] Agent introduces as fraud department
- [x] Agent asks security verification question
- [x] Agent reads transaction details
- [x] Agent asks if customer made transaction
- [x] Function tools mark as safe or fraudulent
- [x] Database updated with status and outcome
- [x] Console logs show all actions
- [x] Call completes gracefully

## 🚀 Advanced Goals (Future)

- [ ] LiveKit Telephony integration (real phone calls)
- [ ] Dynamic case loading by username
- [ ] DTMF input support (phone keypad)
- [ ] Multiple case handling in single call
- [ ] Case management UI/dashboard
- [ ] Real database (SQLite/MongoDB)
- [ ] Escalation to human agents
- [ ] Call recording and transcription
- [ ] Fraud scoring/risk assessment
- [ ] Integration with real bank systems

## 📖 Resources

- [LiveKit Agents Docs](https://docs.livekit.io/agents/)
- [LiveKit Function Tools](https://docs.livekit.io/agents/build/tools/)
- [Google Gemini API](https://ai.google.dev)
- [Deepgram STT](https://developers.deepgram.com)
- [Murf AI TTS](https://murf.ai)
- [Python SQLite](https://www.geeksforgeeks.org/python/python-sqlite/)

## 📄 License

MIT License - See LICENSE file

---

**Created for:** 10 Days of Voice Agents Challenge 2025
