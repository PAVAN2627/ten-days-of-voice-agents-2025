# 🛍️ Day 9: ACP-Enhanced E-Commerce Voice Agent

## 🎯 Project Overview

A production-ready **E-Commerce Voice Shopping Assistant** built with **ACP (Agentic Commerce Protocol)** patterns, featuring type-safe commerce operations, real-time cart synchronization, and intelligent voice interactions powered by Murf AI's Anusha voice.

This is Day 9 of the **Murf AI Voice Agent Challenge** - taking voice commerce to the next level with enterprise-grade architecture and seamless user experience.

---

## ✨ Key Features

### 🎤 Voice-First Shopping Experience
- **Natural Conversations** - Shop entirely through voice commands
- **Smart Product Discovery** - Browse 50+ products across multiple categories
- **Intelligent Cart Management** - Add, update, remove items by voice
- **Size Selection** - Supports S, M, L, XL, XXL for clothing items
- **Order Placement** - Complete checkout hands-free

### 🏗️ ACP Architecture (Agentic Commerce Protocol)
- **Type-Safe Models** - Pydantic-based validation for all commerce operations
- **Structured Commerce Layer** - Clean separation of concerns
- **Error Handling** - Comprehensive validation and error messages
- **API Layer** - FastAPI endpoints with automatic validation

### 🔄 Real-Time Synchronization
- **Bidirectional Cart Sync** - Voice ↔ UI cart stays perfectly synchronized
- **Live Updates** - Changes reflect instantly across all interfaces
- **Session Management** - Persistent cart state during shopping session
- **Order Notifications** - Real-time order confirmation display

### � Modern UI/UX
- **3-Column Layout** - Products | Voice Chat | Shopping Cart
- **Product Gallery** - Beautiful product cards with images
- **Interactive Cart** - Quantity controls, remove items, live totals
- **Order Success** - Animated confirmation with order details
- **Category Filters** - Easy product browsing by category

### 📧 Email Integration
- **HTML Order Confirmations** - Professional email templates
- **Order Details** - Complete breakdown with items, sizes, prices
- **Delivery Information** - Customer details and shipping address
- **SMTP Support** - Gmail and custom SMTP servers

### 🛡️ User Authentication
- **Voice Login** - Authenticate using voice commands
- **Account Creation** - Register new users by voice
- **Session Persistence** - Maintain user state throughout shopping

---

## 🚀 What's New in Day 9?

### ✅ ACP Implementation
- Type-safe Pydantic models for Product, Order, LineItem, Buyer
- Structured commerce functions with comprehensive validation
- FastAPI endpoints with automatic request/response validation
- Clean architecture following ACP patterns

### ✅ Cart Synchronization Fixes
- Voice quantity updates now sync to UI instantly
- UI cart removals sync back to voice agent
- Size information preserved throughout the flow
- No more duplicate items with different sizes

### ✅ Enhanced Size Handling
- Added XXL size support
- Smart size normalization (handles "medium" → "M", "2XL" → "XXL")
- Size validation only for clothing items
- Size displayed in cart and order confirmations

### ✅ Voice Improvements
- Changed to Murf AI Anusha (Indian English female voice)
- Clear instructions for size-only-on-clothing
- Better error messages and confirmations

### ✅ UI Enhancements
- Fixed "Size: NA" display issue
- Unique cart item keys for same product with different sizes
- Order success message stays visible until new item added
- Smooth scrolling chat interface

---

## �️H Tech Stack

| Component | Technology |
|-----------|-----------|
| **Voice Platform** | LiveKit Agents |
| **Speech-to-Text** | Deepgram Nova-3 |
| **LLM** | Google Gemini 2.5 Flash |
| **Text-to-Speech** | Murf AI Anusha (Indian English) |
| **Frontend** | Next.js 15, React, TypeScript |
| **Backend** | Python, FastAPI |
| **Validation** | Pydantic v2 |
| **Styling** | Tailwind CSS, Framer Motion |
| **Email** | SMTP (Gmail/Custom) |
| **Storage** | JSON (users, orders, catalog) |

---

## 📦 Project Structure

```
Day_9/
├── backend/
│   ├── src/
│   │   └── agent.py              # Main voice agent with 20+ function tools
│   ├── acp_models.py             # Type-safe Pydantic models
│   ├── acp_commerce.py           # ACP commerce layer
│   ├── acp_api.py                # FastAPI endpoints
│   ├── commerce.py               # Core commerce functions
│   ├── auth.py                   # User authentication
│   ├── email_service.py          # Order confirmation emails
│   ├── catalog.json              # Product catalog
│   ├── users.json                # User database
│   ├── orders.json               # Order history
│   └── pyproject.toml            # Python dependencies
│
├── frontend/
│   ├── app/
│   │   ├── api/                  # API routes
│   │   │   ├── cart/route.ts    # Cart sync endpoint
│   │   │   ├── auth/route.ts    # Auth endpoint
│   │   │   └── order-placed/route.ts
│   │   └── page.tsx              # Main app page
│   ├── components/
│   │   └── app/
│   │       └── unified-shopping-view.tsx  # Main UI component
│   └── package.json              # Node dependencies
│
└── README.md                     # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm (or npm)
- Gmail account (for email notifications)

### 1. Backend Setup

```bash
cd Day_9/backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env.local
# Edit .env.local with your API keys:
# - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET
# - GOOGLE_API_KEY (for Gemini)
# - DEEPGRAM_API_KEY
# - MURF_API_KEY
# - SENDER_EMAIL, SENDER_PASSWORD (Gmail)

# Run the agent
python src/agent.py dev
```

### 2. Frontend Setup

```bash
cd Day_9/frontend

# Install dependencies
pnpm install

# Configure environment
cp .env.example .env.local
# Edit .env.local with:
# - LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET

# Run development server
pnpm dev
```

### 3. Access the App

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 🎮 How to Use

### Voice Commands Examples

**Authentication:**
- "I want to login with email john@example.com and password mypassword"
- "Create account for John Doe with email john@example.com"

**Browsing:**
- "Show me all products"
- "Browse mugs"
- "Show me electronics under 2000 rupees"

**Shopping:**
- "Add coffee mug to cart"
- "Add premium t-shirt size M to cart"
- "Add 2 wireless mouse to cart"
- "Show my cart"

**Cart Management:**
- "Increase quantity of coffee mug to 3"
- "Change t-shirt size to L"
- "Remove wireless mouse from cart"

**Checkout:**
- "Place order"
- "Show my last order"
- "Show my order history"

---

## 🏗️ ACP Architecture

### Type-Safe Models (acp_models.py)

```python
class Product(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "INR"
    category: str
    description: Optional[str] = None

class LineItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)
    size: Optional[str] = None

class Order(BaseModel):
    id: str
    buyer: Buyer
    line_items: List[LineItemWithDetails]
    total_amount: float
    status: OrderStatus
```

### Commerce Layer (acp_commerce.py)

- `list_products()` - Get product catalog with filters
- `create_order()` - Create order with validation
- `get_order()` - Retrieve order by ID
- `calculate_totals()` - Compute order totals

### API Layer (acp_api.py)

FastAPI endpoints with automatic validation:
- `GET /acp/catalog` - Product listing
- `POST /acp/orders` - Create order
- `GET /acp/orders/{order_id}` - Get order details

---

## 📧 Email Configuration

### Gmail Setup

1. Enable 2-Factor Authentication in your Google Account
2. Generate an App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Create password for "Mail"
3. Add to `.env.local`:

```env
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
SENDER_NAME=Your Store Name
```

### Custom SMTP

```env
SMTP_SERVER=smtp.yourserver.com
SMTP_PORT=587
SENDER_EMAIL=noreply@yourstore.com
SENDER_PASSWORD=your-password
```

---

## 🔄 Cart Synchronization Flow

```
Voice Command → Backend Agent → Update Cart → Sync to Frontend
                                                      ↓
UI Interaction → Frontend Cart → API Call → Backend Agent
```

**Key Features:**
- All voice operations read from frontend cart first
- All cart updates sync to frontend immediately
- Size information preserved throughout
- No duplicate items with different sizes

---

## 🎨 UI Features

### Product Gallery
- Beautiful product cards with images
- Category filtering
- Price display in Indian Rupees
- One-click add to cart

### Voice Chat
- Real-time message display
- User/Agent message differentiation
- Auto-scrolling to latest message
- Voice controls (mic, camera, screen share)

### Shopping Cart
- Live item count and total
- Quantity controls (+/-)
- Remove item button
- Size display for clothing
- Order success animation

---

## 🧪 Testing

### Test ACP Models
```bash
cd backend
python test_acp_models.py
```

### Test Commerce Functions
```bash
python test_acp_commerce.py
```

### Test Email Service
```bash
python -c "from email_service import test_email_configuration; test_email_configuration()"
```

---

## 📊 Function Tools (20+)

1. `browse_catalog` - Browse products with filters
2. `add_to_cart` - Add items with size selection
3. `show_cart` - Display cart contents
4. `remove_from_cart` - Remove items
5. `update_cart_quantity` - Change quantities
6. `update_item_size` - Change clothing sizes
7. `place_order` - Complete checkout
8. `show_last_order` - View recent order
9. `get_order_history` - View all orders
10. `get_spending_info` - Spending analytics
11. `login_user` - Authenticate user
12. `create_account` - Register new user
13. `save_cart_for_later` - Save cart
14. `load_saved_cart` - Restore cart
15. `track_order` - Order status
16. `get_categories` - List categories
17. `list_order_statuses` - Available statuses

---

## 🌟 Highlights

- ✅ **Production-Ready** - Type-safe, validated, error-handled
- ✅ **Real-Time Sync** - Voice and UI stay perfectly synchronized
- ✅ **Beautiful UI** - Modern, responsive, intuitive
- ✅ **Smart Voice** - Natural conversations with Anusha
- ✅ **Email Notifications** - Professional order confirmations
- ✅ **Size Support** - S, M, L, XL, XXL with smart normalization
- ✅ **ACP Patterns** - Enterprise-grade architecture

---

## 🎯 Industry Applications

This technology can power voice shopping for:
- 🛒 E-commerce platforms (Amazon, Flipkart)
- 🏪 Grocery delivery (BigBasket, Blinkit, Zepto)
- 👕 Fashion retail (Myntra, Ajio)
- 📱 Electronics stores
- 🍕 Food delivery apps

---

## 🙏 Acknowledgments

Built as part of the **Murf AI Voice Agent Challenge**

- **Murf AI** - Amazing TTS voices
- **LiveKit** - Powerful voice platform
- **Deepgram** - Accurate STT
- **Google** - Gemini LLM

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🔗 Links

- [Murf AI](https://murf.ai/)
- [LiveKit](https://livekit.io/)
- [Deepgram](https://deepgram.com/)
- [Google Gemini](https://ai.google.dev/)

---

**Built with ❤️ for the Murf AI Voice Agent Challenge**

*Day 9 of 10 - Building the future of voice commerce!* 🚀
