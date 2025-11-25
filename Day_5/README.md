# Day 5: Complete SDR Voice Agent with Email Automation

## 🎯 Project Overview

A fully-featured AI-powered Sales Development Representative (SDR) voice agent for Razorpay that handles lead qualification, demo scheduling, and automated email follow-ups. The agent collects customer information, answers questions about Razorpay's payment solutions, books meetings, and sends professional confirmation emails.

## ✨ Key Features

### 🤖 Voice Agent Capabilities
- **Mandatory Information Collection**: Systematically collects name, email, company, and use case
- **Intelligent Persona Detection**: Identifies user role (developer, founder, PM, finance, marketer)
- **FAQ Search**: Answers questions about Razorpay products and services
- **Demo Scheduling**: Books meetings from real calendar availability
- **Pain Points Discovery**: Collects customer challenges before booking demos
- **Lead Qualification**: BANT-based scoring system
- **CRM Notes Generation**: Automatic structured notes with fit scores

### 📧 Email Automation
- **Instant Confirmation Emails**: Sent immediately after booking
- **Professional HTML Templates**: Branded Razorpay design
- **Personalized Content**: Includes pain points, interests, and meeting details
- **SMTP Integration**: Gmail-based email delivery
- **Lead Data Persistence**: JSON-based storage with full conversation history

### 🎨 UI Features
- **Razorpay Branding**: Blue/indigo gradient theme with payment icons
- **Animated Welcome Page**: Smooth transitions and hover effects
- **Equal Width Message Boxes**: Fixed-width layout for balanced appearance
- **Responsive Design**: Works on desktop and mobile
- **Real-time Voice Visualization**: Audio bars during conversation

## 🏗️ Architecture

### Backend Stack
- **Framework**: LiveKit Agents (Python)
- **LLM**: Azure OpenAI (GPT-4)
- **STT**: Deepgram Nova-3
- **TTS**: Murf AI (Falcon voice)
- **Email**: SMTP (Gmail)
- **Data Storage**: JSON files

### Frontend Stack
- **Framework**: Next.js 15 + React 19
- **UI Library**: LiveKit Components React
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **TypeScript**: Full type safety

## 📋 Agent Workflow

### 1. Opening Sequence (Mandatory)
```
1. Greet user
2. Ask for NAME
3. Ask for EMAIL
4. Ask for COMPANY
5. Ask for USE CASE/NEED
6. Proceed to questions or demo booking
```

### 2. Demo Booking Flow
```
1. User expresses interest in demo
2. Agent asks: "What are your main payment challenges?"
3. Store pain points
4. Agent asks: "What features interest you most?"
5. Store key interests
6. Show available meeting slots
7. Book selected slot
8. Generate and send confirmation email immediately
```

### 3. Email Generation
- Personalized greeting with user's name
- Meeting confirmation details
- Pain points mentioned
- Solutions overview (persona-specific)
- Key interests to cover
- Professional signature

## 🚀 Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- LiveKit server running locally
- Azure OpenAI account
- Gmail account with App Password

### Backend Setup

1. **Navigate to backend directory**:
```bash
cd Day_5/backend
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
# or
uv sync
```

3. **Configure environment variables** (`.env.local`):
```env
# LiveKit
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret

# AI Services
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_OPENAI_API_VERSION=2024-12-01-preview
DEEPGRAM_API_KEY=your_key
MURF_API_KEY=your_key

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=Priya - Razorpay SDR
```

4. **Generate Gmail App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Enable 2-Factor Authentication
   - Create new App Password
   - Use it in `SENDER_PASSWORD`

5. **Test email configuration**:
```bash
python test_email.py
```

6. **Run the agent**:
```bash
python src/agent.py dev
```

### Frontend Setup

1. **Navigate to frontend directory**:
```bash
cd Day_5/frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure environment** (`.env.local`):
```env
LIVEKIT_URL=ws://127.0.0.1:7880
LIVEKIT_API_KEY=devkey
LIVEKIT_API_SECRET=secret
NEXT_PUBLIC_LIVEKIT_URL=ws://127.0.0.1:7880
```

4. **Run development server**:
```bash
npm run dev
```

5. **Open browser**:
```
http://localhost:3000
```

## 📁 Project Structure

```
Day_5/
├── backend/
│   ├── src/
│   │   └── agent.py              # Main agent logic
│   ├── company_data/
│   │   └── razorpay_faq.json     # FAQ database
│   ├── leads/                     # Stored lead data
│   ├── mock_calendar.json         # Calendar availability
│   ├── personas.json              # Persona definitions
│   ├── test_email.py              # Email testing utility
│   └── .env.local                 # Environment config
├── frontend/
│   ├── components/
│   │   └── app/
│   │       ├── welcome-view.tsx   # Landing page
│   │       ├── session-view.tsx   # Chat interface
│   │       ├── tile-layout.tsx    # Video tiles
│   │       └── dual-message-view.tsx  # Message display
│   └── app/
│       └── page.tsx               # Main page
└── README.md                      # This file
```

## 🔧 Key Functions

### Agent Functions

| Function | Purpose |
|----------|---------|
| `store_lead_info()` | Store customer information |
| `search_faq()` | Search Razorpay FAQ database |
| `detect_persona()` | Identify user role/persona |
| `show_available_meetings()` | Display calendar slots |
| `book_meeting()` | Book demo and send email |
| `generate_follow_up_email()` | Create personalized email |
| `generate_crm_notes()` | Create structured CRM data |
| `end_conversation()` | Save lead and send final email |

### Email Functions

| Function | Purpose |
|----------|---------|
| `_generate_html_email()` | Create HTML email template |
| `_send_email()` | Send via SMTP with logging |

## 📊 Data Models

### Lead Data Structure
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "company": "TechCorp",
  "use_case": "payment gateway",
  "pain_points": ["high transaction fees", "slow settlements"],
  "key_interests": ["API integration", "webhook support"],
  "detected_persona": "developer",
  "booked_meeting": {
    "date": "2024-11-26",
    "time": "2:00 PM",
    "duration": "30 minutes"
  },
  "qualification_score": 75,
  "crm_notes": { ... }
}
```

## 🎨 UI Components

### Welcome View
- Razorpay logo with animations
- Gradient background
- "Start Conversation" button
- Footer with branding

### Session View
- Equal-width message boxes (calc(50% - 80px))
- Centered Razorpay logo
- Agent video tile with animations
- User camera/screen share tile

### Tile Layout
- Animated agent visualization
- Blue/indigo gradient theme
- Payment icon overlay
- Smooth transitions

## 📧 Email System

### Features
- ✅ Instant delivery after booking
- ✅ Professional HTML templates
- ✅ Personalized content
- ✅ Meeting confirmation details
- ✅ Pain points and interests included
- ✅ Branded Razorpay design

### Troubleshooting
If emails aren't received:
1. Check spam/junk folder
2. Verify Gmail App Password
3. Whitelist sender email
4. Run `python test_email.py`
5. Check agent logs for errors

## 🧪 Testing

### Test Email System
```bash
cd Day_5/backend
python test_email.py
```

### Test Agent Locally
1. Start LiveKit server
2. Run backend agent
3. Run frontend
4. Open browser and start conversation

### Test Scenarios
- ✅ Information collection flow
- ✅ FAQ search functionality
- ✅ Demo booking with pain points
- ✅ Email delivery
- ✅ Lead data persistence
- ✅ Returning visitor detection

## 📈 Metrics & Logging

The agent logs:
- STT/TTS metrics
- LLM token usage
- Email send status
- Lead qualification scores
- Conversation transcripts

## 🔐 Security Notes

- Never commit `.env.local` files
- Use App Passwords, not account passwords
- Store sensitive data securely
- Validate all user inputs
- Sanitize email content

## 🐛 Known Issues & Solutions

### Issue: Emails not received
**Solution**: Check spam folder, whitelist sender

### Issue: Agent not collecting info
**Solution**: Restart agent, check instructions

### Issue: Calendar slots not showing
**Solution**: Verify `mock_calendar.json` has available slots

### Issue: Azure OpenAI errors
**Solution**: Check API key and deployment name

## 🎯 Success Criteria

- ✅ Collects all required information (name, email, company, use case)
- ✅ Asks for pain points before booking
- ✅ Books meetings from real calendar
- ✅ Sends confirmation emails immediately
- ✅ Stores complete lead data
- ✅ Professional UI with Razorpay branding
- ✅ Smooth animations and transitions
- ✅ Equal-width message layout

## 📝 Future Enhancements

- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Multi-language support
- [ ] Voice cloning for Priya
- [ ] Advanced analytics dashboard
- [ ] A/B testing for email templates
- [ ] SMS notifications
- [ ] Meeting reminders

## 🤝 Contributing

This is a learning project. Feel free to:
- Report bugs
- Suggest features
- Improve documentation
- Optimize code

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- **Agent Name**: Priya
- **Company**: Razorpay
- **Role**: AI-powered SDR
- **Specialty**: Payment solutions

## 📞 Support

For issues or questions:
1. Check this README
2. Review agent logs
3. Test email system
4. Check environment variables

---

**Built with ❤️ using LiveKit, Azure OpenAI, and Next.js**
