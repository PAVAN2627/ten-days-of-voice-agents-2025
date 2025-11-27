# Day 7: DailyMart Voice Grocery Assistant 🛒🎙️

## Overview

Day 7 implements a **fully functional voice-based grocery ordering system** using LiveKit's agent framework. This is a production-ready voice AI agent that allows customers to order groceries, manage their cart, and complete purchases entirely through voice commands.

## 🎯 What This Agent Does

The DailyMart Voice Agent is an intelligent grocery shopping assistant that handles:

### Core Features
- **User Authentication**: Register new customers or login existing users via voice
- **Voice Shopping**: Browse catalog, add items to cart using natural language
- **Recipe-Based Shopping**: Add all ingredients for Indian recipes (e.g., "add ingredients for biryani")
- **Cart Management**: View cart, update quantities, remove items
- **Order Processing**: Review order details, confirm, and receive email confirmation
- **Order Tracking**: Check order status, view order history
- **Smart Features**: 
  - Budget limits (e.g., "keep it under ₹1000")
  - Dietary filters (vegan, vegetarian, gluten-free)
  - Personalized recommendations based on order history
  - Reorder previous orders
  - **Delivery Charges**: ₹50 flat rate, FREE on orders above ₹1000
  - **Discounts**: 10% off on orders above ₹5000 (festival seasons only)

## 🏗️ Architecture Analysis

### Backend Agent (`agent.py`)

The agent is built with **802 lines** of sophisticated Python code using LiveKit's agent framework.

#### Key Components:

**1. DailyMartAgent Class** (Lines 1-300)
- Manages user sessions, cart state, and order processing
- Handles data persistence (users.json, orders.json, catalog.json)
- Implements password normalization for voice input (e.g., "two two three" → "223")
- Smart item search with fuzzy matching
- Recipe ingredient lookup system
- Email confirmation with HTML templates

**2. Function Tools** (Lines 301-700)
The agent exposes 22 function tools that the LLM can call:

| Tool | Purpose | Key Logic |
|------|---------|-----------|
| `register_new_customer` | Create new account | Collects name, email, password, address, mobile |
| `login_customer` | Authenticate user | Password normalization for voice input |
| `add_item_to_cart` | Add products | Fuzzy search, budget/dietary checks |
| `add_recipe_ingredients` | Recipe shopping | Adds all ingredients for Indian dishes |
| `show_catalog` | Browse products | Category-based browsing |
| `remove_item_from_cart` | Remove products | Fuzzy name matching |
| `update_item_quantity` | Change quantities | Supports voice commands like "make it 3" |
| `view_cart` | Show cart summary | Itemized list with totals |
| `review_order_details` | Pre-checkout review | Creates pending order |
| `confirm_order` | Place order | Saves order, sends email, clears cart |
| `show_order_history` | Past orders | Shows last 5 orders with details |
| `show_last_order` | Last order details | Shows complete details of most recent order |
| `check_order_status` | Track order | Real-time status updates |
| `reorder_last_order` | Quick reorder | Reorders most recent order (no ID needed) |
| `reorder_previous_order` | Specific reorder | Reorders by Order ID |
| `get_recommendations` | Personalized suggestions | Based on order frequency |
| `set_budget_limit` | Budget control | Prevents overspending |
| `set_dietary_filter` | Dietary preferences | Filters items by tags |
| `reset_password` | Password recovery | Updates user password |
| `check_delivery_charges` | Check delivery fees | Shows ₹50 fee, FREE above ₹1000 |
| `check_discount_eligibility` | Check discount status | 10% off above ₹5000 (festival only) |
| `advance_order_status` | Status simulation | For testing order progression |

**3. Voice Pipeline Integration** (Lines 701-802)
```python
session = AgentSession(
    stt=deepgram.STT(model="nova-3"),           # Speech-to-Text
    llm=google.LLM(model="gemini-2.5-flash"),   # Language Model
    tts=murf.TTS(voice="en-IN-anusha"),         # Text-to-Speech (Indian voice)
    vad=silero.VAD.load(),                       # Voice Activity Detection
)
```

#### Smart Features Implementation:

**Password Normalization** (Lines 90-100)
```python
def normalize_password(self, password: str) -> str:
    # Converts "two two three" → "223"
    replacements = {"zero": "0", "one": "1", ...}
    for word, digit in replacements.items():
        password = password.replace(word, digit)
    return password.replace(" ", "")
```

**Budget Enforcement** (Lines 400-410)
```python
if agent.budget_limit:
    current_total = sum(item["quantity"] * item["price"] for item in agent.cart)
    new_total = current_total + (quantity * item["price"])
    if new_total > agent.budget_limit:
        return f"Adding {item['name']} would exceed your budget..."
```

**Email Confirmation** (Lines 120-200)
- HTML email template with DailyMart branding
- Itemized order details
- Delivery address
- Order tracking information

### Frontend Architecture

**Tech Stack:**
- Next.js 15.5.2 (React 19)
- LiveKit Components React
- TypeScript
- Tailwind CSS
- Motion (Framer Motion)

**Key Files:**
- `app/(app)/page.tsx` - Main entry point
- `components/app/app.tsx` - App wrapper with LiveKit providers
- `components/app/session-view.tsx` - Active call UI
- `components/app/welcome-view.tsx` - Landing page
- `app-config.ts` - DailyMart branding configuration

## 🎨 UI Features

### Enhanced Welcome Screen
- **Animated Logo**: Rotating entrance with shadow effects
- **Gradient Background**: Blue to purple to green animated circles
- **Feature Cards**: Voice ordering, smart cart, fast delivery
- **Popular Items**: Quick view of available categories
- **Responsive Design**: Mobile and desktop optimized

### Dual Message View (Session)
- **Side-by-Side Layout**: Agent messages (blue) | Center logo | User messages (green)
- **Centered Logo**: Animated DailyMart logo with pulsing indicators
- **Auto-Scrolling**: Both columns scroll independently
- **Status Indicators**: Real-time speaking/listening status
- **Message Bubbles**: Color-coded with timestamps

### Enhanced Email Confirmation
- **Professional Design**: Gradient header with DailyMart branding
- **Complete Pricing**: Subtotal, delivery, discount breakdown
- **Order Tracking**: Order ID and status badge
- **Customer Info**: Name, email, mobile, delivery address
- **What's Next**: Clear next steps and tracking info
- **Contact Support**: Help links and contact information

### Logo Assets
- `dailymartlogowithname.png` - Full logo with company name
- `dailymartjustlogo.png` - Icon-only logo

## 🚀 How to Run

### Prerequisites
```bash
# Install uv (Python package manager)
pip install uv

# Install LiveKit CLI
brew install livekit  # macOS
# or download from https://github.com/livekit/livekit-cli
```

### Backend Setup
```bash
cd Day_7/backend

# Create virtual environment
uv venv

# Install dependencies
uv pip install -e .

# Configure environment variables
cp .env.example .env.local
# Edit .env.local with your API keys:
# - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# - GOOGLE_API_KEY (for Gemini)
# - SMTP credentials for email

# Start the agent
python -m livekit.agents dev
```

### Frontend Setup
```bash
cd Day_7/frontend

# Install dependencies
pnpm install

# Configure environment
cp .env.example .env.local
# Edit .env.local:
# LIVEKIT_URL=ws://localhost:7880

# Start development server
pnpm dev
```

### Access
- Frontend: http://localhost:3001
- LiveKit Server: http://localhost:7880

## 📊 Data Files

### catalog.json
Product catalog with categories:
- Groceries (rice, flour, oil, etc.)
- Spices & Masalas
- Snacks & Namkeen
- Ready to Eat
- Beverages
- Sweets & Desserts

### users.json
User database:
```json
{
  "user@example.com": {
    "name": "John Doe",
    "email": "user@example.com",
    "password": "hashed_password",
    "address": "123 Main St",
    "mobile": "9876543210",
    "created_at": "2025-11-28T10:00:00"
  }
}
```

### orders.json
Order history:
```json
{
  "ORD_20251128_100000": {
    "order_id": "ORD_20251128_100000",
    "customer_email": "user@example.com",
    "items": [...],
    "total": 500,
    "status": "delivered",
    "timestamp": "2025-11-28T10:00:00",
    "delivery_address": "123 Main St"
  }
}
```

## 🎤 Voice Interaction Examples

### Registration
```
User: "I'm a new customer"
Agent: "Great! Let me help you register. What's your full name?"
User: "John Doe"
Agent: "What's your email address?"
User: "john@example.com"
Agent: "Please choose a password"
User: "two two three three"
Agent: "What's your delivery address?"
User: "123 Main Street, Mumbai"
Agent: "What's your mobile number?"
User: "nine eight seven six five four three two one zero"
Agent: "Welcome John! Your account has been created."
```

### Shopping
```
User: "Show me groceries"
Agent: "Here are our groceries: Rice, Flour, Oil..."
User: "Add basmati rice"
Agent: "Added 1 Basmati Rice to your cart (₹150)"
User: "Add ingredients for biryani"
Agent: "Added ingredients for Biryani: Basmati Rice, Biryani Masala, Ghee... Total: ₹450"
User: "Show my cart"
Agent: "Your cart contains: 1x Basmati Rice (₹150), 1x Biryani Masala (₹80)... Total: ₹450"
```

### Checkout
```
User: "I want to place my order"
Agent: "Please review your order details: Name: John Doe, Address: 123 Main St... Total: ₹450. Are all these details correct?"
User: "Yes"
Agent: "Order confirmed! Order ID: ORD_20251128_100000. We'll deliver to 123 Main St. A confirmation email has been sent."
```

### Reordering (Smart - No Order ID Needed!)
```
User: "Show my previous orders"
Agent: "You have 3 orders. Here are your recent orders:

1. Order ID: ORD_20251128_100000
   Date: November 28, 2025
   Status: Delivered
   Total: ₹450
   Items: 1x Basmati Rice, 1x Biryani Masala, 1x Ghee

2. Order ID: ORD_20251127_150000
   Date: November 27, 2025
   Status: Delivered
   Total: ₹300
   Items: 2x Milk, 1x Bread

To reorder any of these, just say 'reorder my last order' or provide the Order ID."

User: "Reorder my last order"
Agent: "Great! I've added items from your last order (ORD_20251128_100000 placed on November 28, 2025) to your cart: 1x Basmati Rice, 1x Biryani Masala, 1x Ghee. Total added: ₹450. Say 'show cart' to review."
```

### Show Last Order (No ID Needed!)
```
User: "Show my last order"
Agent: "Here's your last order:

Order ID: ORD_20251128_100000
Date: November 28, 2025 at 10:00 AM
Status: Delivered
Delivery Address: 123 Main Street, Mumbai

Items:
- 1x Basmati Rice (₹150 each) = ₹150
- 1x Biryani Masala (₹80 each) = ₹80
- 1x Ghee (₹220 each) = ₹220

Subtotal: ₹450
Delivery Charge: FREE
Total: ₹450

Would you like to reorder this? Just say 'reorder my last order'."
```

## 🔧 Technical Highlights

### Voice Processing Pipeline
1. **User speaks** → Microphone captures audio
2. **WebRTC** → Audio streamed to LiveKit server
3. **Deepgram STT** → Converts speech to text (Nova-3 model)
4. **Gemini LLM** → Understands intent, calls appropriate function tools
5. **Function Execution** → Agent processes request (add to cart, etc.)
6. **Response Generation** → LLM creates natural response
7. **Murf TTS** → Converts text to speech (Indian English voice)
8. **Audio Playback** → User hears response

### State Management
- **Session State**: Current user, cart, pending order
- **Persistent State**: Users, orders, catalog (JSON files)
- **Temporary State**: Budget limits, dietary filters (session-only)

### Error Handling
- Graceful fallbacks for missing items
- Password normalization for voice input
- Budget and dietary constraint validation
- Email failure handling (continues without email)

## 🎓 Key Learnings

1. **Voice-First Design**: Password normalization, fuzzy matching for voice input
2. **Function Tool Architecture**: 18 tools for comprehensive functionality
3. **State Persistence**: JSON-based storage for users and orders
4. **Email Integration**: HTML templates for professional confirmations
5. **Smart Features**: Budget limits, dietary filters, recommendations
6. **Indian Context**: Indian voice (en-IN-anusha), Indian recipes, Rupee pricing

## 🚧 Future Enhancements

- [ ] Payment gateway integration
- [ ] Real-time order tracking with delivery partner
- [ ] Multi-language support (Hindi, Tamil, etc.)
- [ ] Voice-based OTP verification
- [ ] Product images in catalog
- [ ] Inventory management
- [ ] Promotional offers and coupons
- [ ] Subscription-based ordering
- [ ] Voice-based product search with filters
- [ ] Integration with actual grocery suppliers

## 📝 Environment Variables

### Backend (.env.local)
```env
LIVEKIT_URL=http://localhost:7880
LIVEKIT_API_KEY=your_api_key
LIVEKIT_API_SECRET=your_api_secret
GOOGLE_API_KEY=your_gemini_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
SENDER_NAME=DailyMart
```

### Frontend (.env.local)
```env
LIVEKIT_URL=ws://localhost:7880
```

## 🎯 Success Metrics

- ✅ 22 function tools implemented
- ✅ 950+ lines of production-ready code
- ✅ Voice-optimized password handling
- ✅ Email confirmation system
- ✅ Budget and dietary constraints
- ✅ Order history and reordering
- ✅ Personalized recommendations
- ✅ Smart pricing (delivery charges + discounts)
- ✅ Indian voice and context

---

**Status**: Production Ready ✅  
**Last Updated**: November 28, 2025  
**Voice Pipeline**: LiveKit + Deepgram + Gemini + Murf
