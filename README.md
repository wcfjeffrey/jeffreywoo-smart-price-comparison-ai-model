<div align="center">
  <img src="assets/JeffreyWooSmartPriceComparison.png" alt="JeffreyWooSmartPriceComparisonBanner" width="1200" height="600" />
</div>
 
## JeffreyWoo Smart Price Comparison System

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Next.js](https://img.shields.io/badge/Next.js-14.0.3-black.svg)
![React](https://img.shields.io/badge/React-18.2.0-blue.svg)
![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.4.0-red.svg)
![MLflow](https://img.shields.io/badge/MLflow-2.7.0-yellow.svg)
![Docker](https://img.shields.io/badge/Docker-24.0-blue.svg)
![Kubernetes](https://img.shields.io/badge/Kubernetes-1.28-blue.svg)

## 📊 Overview

> **Not your typical price comparison tool!**

**JeffreyWoo Smart Price Comparison** is an enterprise-grade AI-powered procurement decision-making assistant app through multi-agent AI architecture, hybrid AI+ML predictions, reinforcement learning, and big data analytics with email/calendar integration to help procurement professionals, supply chain managers, and businesses make smarter, faster, and more confident purchasing decisions. It automatically compares prices, predicts future trends, detects anomalies, and optimizes procurement strategies.

## ✨ What It Does

### 📊 Real-Time Price Intelligence
- Compare prices across multiple suppliers instantly using AI agents
- Analyze price trends by day/week/month with predictive models
- Track supplier performance (price, delivery time, rating) in real-time

### 🧠 AI-Powered Strategic Guidance
- **Multi-Agent AI Architecture** — Three specialized AI agents (Data Fetcher, Price Analyst, Report Generator) work together like a team of experts
- **Hybrid AI + ML Predictions** — Combines AI reasoning (why prices change) with ML accuracy (numeric forecasts) for high prediction accuracy
- **Rerank Models** — Cross-encoder rerank models that understand trade-offs between price, delivery speed, and reliability for ranking vendors

### 🔍 Advanced Analytics & Automation
- **Price Predictions** — Short-term (30-day) and long-term (90-day) forecasts with confidence scores
- **Anomaly Detection** — Automatically detects price outliers (statistical anomalies >2.5 standard deviations), and provide anomaly alerts
- **Risk Analysis** — Risk scores (0-100) with detailed risk factors (price volatility, limited supply, long delivery)
- **Reinforcement Learning** — Q-learning agent that learns optimal purchasing strategies through 2,000+ training episodes

### ⏰ Task Automation & Notifications
- **Scheduled Price Checks** — Daily/weekly/monthly automatic price monitoring
- **Email Reports** — Delivery of HTML reports to emails (compatible with Gmail, Outlook, Exchange, and any SMTP-enabled email system)
- **Calendar Integration** — Auto-creates review meetings with attendees and reminders (compatible with any calendar system that supports iCal/ICS format)
- **Windows Desktop Notifications** — Real-time pop-up alerts when prices change

### 🌍 Multi-Market & Multi-Supplier Analysis
- Supports any product category (electronics, office supplies, industrial equipment)
- Unlimited supplier comparison with intelligent ranking
- Historical trend analysis across 10+ years of price data

### 🔒 Enterprise-Grade Architecture
- Built with Docker and Kubernetes for scalable deployment
- PostgreSQL for persistent task and history storage
- Redis for high-performance caching
- Apache Spark (Big Data Processing) for processing millions of price records across thousands of suppliers
- MLflow for model versioning and experiment tracking

## 🚀 Why Choose JeffreyWoo Smart Price Comparison

Most price comparison tools just show you today's prices. This system goes further — embedding AI into your procurement workflow so you can anticipate price changes, identify the best suppliers, optimize purchase timing, and align purchasing strategies with long-term business goals.

|     Feature    | Traditional Tools | Smart Price Comparison |
|----------------|-------------------|------------------------|
|Price Comparison	|✅ Yes	|✅ Yes|
|Supplier Ranking	|❌ Basic	|✅ AI-powered with trade-off analysis|
|Price Predictions	|❌ No	|✅ Hybrid AI+ML (high accuracy)|
|Anomaly Detection	|❌ No	|✅ Statistical & AI detection|
|Task Automation	|❌ No	|✅ Scheduled checks with notifications|
|Reinforcement Learning	|❌ No	|✅ Q-learning for optimal strategies|
|Big Data Processing	|❌ No	|✅ Apache Spark|
|Report Generation	|❌ Manual	|✅ Automatic (HTML/JSON/CSV)|

## 🏗️ Multi-Agent AI System Architecture
<pre lang="markdown">
┌─────────────────────────────────────────────────────────────────────────────┐
│                   JeffreyWoo Smart Price Comparison                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │   Agent A        │    │   Agent B        │    │   Agent C        │       │
│  │   Data Fetcher   │───▶│   Analyst       │───▶│   Reporter       │       │
│  │   (GPT-4o-ca)    │    │   (DeepSeek-V3)  │    │   (GPT-4.1-mini) │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│          │                       │                       │                  │
│          ▼                       ▼                       ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                    Hybrid Prediction Engine                      │       │
│  │  ┌─────────────────────┐    ┌─────────────────────┐              │       │
│  │  │  AI Predictions     │ +  │  ML Predictions     │ = Hybrid     │       │
│  │  │  (LLM Reasoning)    │    │  (Random Forest)    │   Result     │       │
│  │  └─────────────────────┘    └─────────────────────┘              │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                    │                                        │
│                                    ▼                                        │
│  ┌──────────────────────────────────────────────────────────────────┐       │
│  │                    Data & Infrastructure                         │       │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │       │
│  │  │  Spark   │  │  MLflow  │  │  Docker  │  │   K8s    │          │       │
│  │  │  Big Data│  │  Model   │  │  Contain │  │  Orchest │          │       │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘</pre>

## 📦 Data Pipeline
<pre lang="markdown">
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Complete Data Pipeline                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    External Sources                                                         │
│           │                                                                 │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Data Ingestion  │ → Raw price data collected from ChatAnywhere API       │
│  └────────┬────────┘                                                        │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Data Warehouse  │ → Stored as Parquet files for efficient querying       │
│  └────────┬────────┘                                                        │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Spark Processing│ → Distributed processing for large-scale analytics     │
│  └────────┬────────┘                                                        │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ MLflow Training │ → Model training, tracking, and versioning             │
│  └────────┬────────┘                                                        │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ RL Optimization │ → Reinforcement learning for procurement strategies    │
│  └────────┬────────┘                                                        │
│           ▼                                                                 │
│  ┌─────────────────┐                                                        │
│  │ Frontend Display│ → Dashboard, reports, calendar, charts                 │
│  └─────────────────┘                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘</pre>

## 🤖 Tech Stack
| Category| Technologies| 
|---------|-------------|
| Language	| Python, TypeScript| 
| Backend Framework	| FastAPI (async)| 
| Frontend Framework	| Next.js, React| 
| UI	| Tailwind CSS, Recharts, Framer Motion| 
| AI/LLM	| ChatAnywhere API (GPT-4o-ca, DeepSeek-V3, GPT-4.1-mini)| 
| Machine Learning	| scikit-learn (Random Forest, Linear Regression)| 
| Reinforcement Learning	| OpenAI Gym (Q-Learning)| 
| Rerank Models	| Sentence-Transformers (Cross-Encoder)| 
| Big Data	| Apache Spark (PySpark), Parquet| 
| MLOps	| MLflow| 
| Database	| PostgreSQL, Redis| 
| DevOps	| Docker, Kubernetes, GitHub Actions| 
| APIs	| Google Calendar, Gmail, Windows API| 

## 📈 Financial & Procurement Theories Applied
This app leverages procurement, supply chain, and financial principles to automate supplier evaluation, price analysis, and purchase decisions. It transforms raw price data into actionable insights for procurement managers, supply chain directors, and CFOs:

### 📊 Supplier Evaluation Framework
- **Total Cost of Ownership (TCO)** — The app calculates true cost beyond purchase price, incorporating delivery time and quality ratings
- **Supplier Scorecard** — Multi-factor scoring (price 40% + delivery 30% + rating 30%) embedded into dashboards
- **Strategic Sourcing** — Identifies optimal supplier mix based on volume, urgency, and risk tolerance

### 📉 Price Analysis & Forecasting
- **Time Series Analysis** — Moving averages and trend detection for price patterns
- **Seasonal Adjustment** — Identifies recurring price cycles (Black Friday, new product launches)
- **Volatility Measurement** — Standard deviation analysis for price stability assessment

### 🎯 Procurement Optimization
- **Economic Order Quantity (EOQ)** — RL-driven recommendations for optimal order quantities
- **Bulk Purchase Optimization** — Q-learning agent learns when bulk discounts justify larger orders
- **Inventory Timing** — Predicts optimal purchase windows based on price trends

### 🔬 Risk Management
- **Supplier Risk Scoring** — Identifies single-supplier dependencies and concentration risk
- **Price Shock Detection** — Flags sudden price changes >15% within 30 days
- **Supply Chain Resilience** — Recommends supplier diversification strategies

## 💡 Procurement Transformation Impact
This project showcases how AI can reshape procurement and supply chain management by:  
- Digitizing strategic sourcing with predictive modeling and real-time insights  
- Enhancing procurement decisions through scenario simulations and supplier ranking  
- Optimizing purchasing costs with high cost savings across test categories  
- Driving supply chain resilience by identifying alternative suppliers automatically  
- Promoting data-driven procurement with secure handling of pricing intelligence

## ⭐ Technical Skills Strengthened
|Skill Area	| Specific Competencies|
|-----------|----------------------|
|AI/ML Engineering | Multi-agent systems, LLM integration (GPT-4o-ca, DeepSeek-V3, GPT-4.1-mini), hybrid AI+ML predictions, cross-encoder rerank models, reinforcement learning (Q-learning)|
|Big Data	| Apache Spark for distributed processing, Parquet data warehousing, PySpark analytics|
|MLOps	| MLflow model tracking, experiment logging, model versioning|
|Full-Stack Development	| FastAPI async backend, Next.js frontend, Tailwind CSS, real-time dashboards|
|Database Design	| PostgreSQL with SQLAlchemy async, Redis caching, schema design|
|DevOps	| Docker containerization, Kubernetes orchestration, GitHub Actions CI/CD|
|API Integration	| Google Calendar OAuth, Gmail SMTP, Windows API, ChatAnywhere LLM API|

## Automated Scheduling with Windows Integration
Set up a price check once — the system handles everything else:
- ⏰ **Scheduled Checks**	— Daily / Weekly / Monthly automatic price checks
- 📧 **Email Reports**	— Get price reports in HTML
- 📅 **Calendar Events**	— Auto-create Google Calendar meetings to review prices
- 💬 **Desktop Alerts**	— Windows notifications when prices change

<pre lang="markdown">
┌─────────────────────────────────────────────────────────────────┐
│                  What Happens Automatically                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Monday 9:00 AM                                                 │
│       │                                                         │
│       ▼                                                         │
│  📊 System checks prices (takes 5 seconds)                     │
│       │                                                         │
│       ▼                                                         │
│  💬 Windows Desktop Notification: "Price check complete!"      │
│       │                                                         │
│       ▼                                                         │
│  📁 Files automatically organized in your Documents folder     │
│       │                                                         │
│       └── Reports/2026/March/iPhone_17_Pro_report.html          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘</pre>

## Google Calendar & Gmail Integration
Your calendar and email work for you automatically.

Calendar Events:
- 📅 "Weekly iPhone Price Review" appears in your Google Calendar
- 👥 Automatically invites your procurement team
- 🔔 Reminders set for 1 day before and 10 minutes before

Email Reports:
- 📧 Beautiful HTML summary arrives in your inbox
- 📁 HTML attachment for printing or sharing

## 📈 Advanced Analytics
|Feature	|Description|
|---------|-----------|
|Price Trend Analysis	|Statistical analysis of price movements over time|
|Supplier Performance Scoring	|Multi-factor scoring with customizable weights|
|Market Volatility Tracking	|Standard deviation and volatility calculations|
|Seasonal Pattern Detection	|Identification of recurring price patterns|
|Bulk Purchase Optimization	|RL-driven recommendations for optimal order quantities|

## 🔐 Security & Authentication
- JWT Authentication
- OAuth Complete Google OAuth flow for calendar access
- Environment Secrets	All API keys and credentials stored in .env
- CORS Configuration	Proper cross-origin resource sharing for frontend-backend communication
- Rate Limiting on public APIs
- Input Validation with Pydantic models

## 📦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Kubernetes
- OpenAI API Key (via chatanywhere.tech)
- ocker Desktop (optional, for PostgreSQL/Redis)

### Setup

#### 1. Clone and install backend

##### Clone repository
```
git clone https://github.com/jeffreywoo/smart-price-comparison.git
cd SmartPriceComparison
```
##### Backend setup
```
cd ../backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```
##### Frontend setup
```
cd ../frontend
npm install
```
#### 2. Configure Environment
```
cp .env.example .env
Edit .env with your API keys
```
##### Environment Configuration

```
//.env file

OPENAI_API_KEY=your-chatanywhere-api-key
OPENAI_BASE_URL=https://api.chatanywhere.tech/v1
DATABASE_URL=postgresql://admin:password@localhost:5432/price_comparison
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MLFLOW_TRACKING_URI=http://localhost:5000
```
#### 3. Run with Docker Compose
```
docker-compose up -d postgres redis
python init_db.py
```
#### 4. Run both services

##### Terminal 1 - Backend
```
cd backend
uvicorn app.main:app --reload --port 8000
```
##### Terminal 2 - Frontend
```
cd frontend
npm install
npm run dev
```
#### 5. Access Applications
```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Documentation: http://localhost:8000/docs
```
## Project Structure
```text
SmartPriceComparison/
│
├── backend/                                # FastAPI Backend
│   ├── app/
│   │   ├── api/                            # REST API Endpoints
│   │   │   ├── price_compare.py            # Price comparison endpoints
│   │   │   ├── anomaly_detection.py        # Anomaly detection endpoints
│   │   │   ├── reports.py                  # Report generation endpoints
│   │   │   ├── tasks.py                    # Task management endpoints
│   │   │   ├── products.py                 # Product analysis endpoints
│   │   │   └── notifications.py            # Email & calendar endpoints
│   │   │
│   │   ├── services/                       # Business Logic Layer
│   │   │   ├── agent_a.py                  # AI Agent: Data Fetcher
│   │   │   ├── agent_b.py                  # AI Agent: Price Analyst
│   │   │   ├── agent_c.py                  # AI Agent: Report Generator
│   │   │   ├── agent_orchestrator.py       # Multi-Agent Workflow Orchestrator
│   │   │   ├── hybrid_predictor.py         # AI + ML Hybrid Predictions
│   │   │   ├── rerank_service.py           # Supplier Rerank Model (Cross-Encoder)
│   │   │   ├── chatanywhere_integration.py # ChatAnywhere API Client
│   │   │   ├── task_scheduler.py           # APScheduler Task Management
│   │   │   ├── notification_service.py     # Email & Calendar Notifications
│   │   │   ├── google_integration.py       # Google Calendar API
│   │   │   ├── windows_integration.py      # Windows Desktop Notifications
│   │   │   └── redis_cache.py              # Redis Cache Service
│   │   │
│   │   ├── core/                           # Core Configuration
│   │   │   ├── config.py                   # Environment settings
│   │   │   └── database.py                 # PostgreSQL connection
│   │   │
│   │   ├── models/                         # Data Models
│   │   │   └── task.py                     # Task data structure
│   │   │
│   │   └── main.py                         # FastAPI Application Entry Point
│   │
│   ├── data/                               # Persistent Data Storage
│   │   ├── tasks.json                      # Task storage (fallback)
│   │   └── price_comparison.db             # SQLite (fallback)
│   │
│   ├── requirements.txt                    # Python dependencies
│   └── Dockerfile                          # Docker container configuration
│
├── frontend/                               # Next.js Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                    # Main Dashboard
│   │   │   ├── layout.tsx                  # Root layout
│   │   │   └── globals.css                 # Global styles
│   │   │
│   │   ├── components/
│   │   │   └── ui/                         # Reusable UI Components
│   │   │       ├── card.tsx                # Card component
│   │   │       ├── button.tsx              # Button component
│   │   │       ├── badge.tsx               # Badge component
│   │   │       ├── input.tsx               # Input component
│   │   │       ├── select.tsx              # Dropdown select
│   │   │       ├── tabs.tsx                # Tab component
│   │   │       └── alert.tsx               # Alert component
│   │   │
│   │   └── lib/                            # Utility functions
│   │       └── utils.ts                    # Helper functions
│   │
│   ├── public/                             # Static assets
│   ├── package.json                        # NPM dependencies
│   ├── tailwind.config.js                  # Tailwind CSS config
│   ├── next.config.js                      # Next.js config
│   └── Dockerfile                          # Docker container configuration
│
├── ml/                                     # Machine Learning Module
│   ├── inference/
│   │   └── price_predictor.py              # ML price predictions
│   │
│   ├── reinforcement_learning/
│   │   ├── procurement_env.py              # OpenAI Gym environment
│   │   └── train_agent.py                  # RL training script
│   │
│   └── tensorflow/                         # TensorFlow Models (optional)
│       └── price_predictor.py              # TensorFlow neural network
│
├── data/                                   # Data Processing
│   ├── spark/                              # Apache Spark jobs
│   │   └── price_processor.py              # PySpark data processor
│   │
│   ├── ingestion/                          # Data ingestion pipeline
│   │   └── price_ingestion.py              # Data loader
│   │
│   └── warehouse/                          # Data warehouse (Parquet)
│       ├── price_comparison.parquet
│       └── historical_prices.parquet
│
├── kubernetes/                             # Kubernetes Deployment
│   └── deployment.yaml                     # K8s manifests
│
├── reports/                                # Generated Reports
│   └── price_data_*.csv                    # Exported reports
│
├── docker-compose.yml                      # Docker Compose configuration
├── .env.example                            # Environment variables template
├── .gitignore                              # Git ignore file
└── README.md                               # Project documentation
```

## 📚 API Documentation

|Method           | Endpoint Description|
|-----------------|---------------------|
|GET	/api/price/latest	|Get latest price data|
|GET	/api/price/ranked	|Get ranked suppliers|
|GET /api/anomaly/detected	|Get detected anomalies|
|POST /api/reports/generate	|Generate new report|
|POST /api/tasks/	|Schedule price check|
|GET	/api/products/compare/{name}	|Product analysis|
|GET	/api/reports/download/{name}	|Download report|
|GET	/api/notifications/test-email	|Test email notification|

## 🧠 Explanation of JeffreyWoo Smart System

### Three AI Agents

Think of it as hiring three expert employees:

<pre lang="markdown">
┌─────────────────────────────────────────────────────────────────┐
│                     Your AI Team                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  👤 Agent A: The Researcher                                    │
│     • Goes out and finds prices from all suppliers              │
│     • Reads through supplier websites and catalogs              │
│     • Brings back all the raw data                              │
│                                                                 │
│  👤 Agent B: The Analyst                                       │
│     • Looks at all the data and finds patterns                  │
│     • Spots anomalies (prices that don't make sense)            │
│     • Predicts future price movements                           │
│                                                                 │
│  👤 Agent C: The Reporter                                      │
│     • Creates beautiful reports with charts and tables          │
│     • Writes easy-to-understand recommendations                 │
│     • Sends everything to your email and calendar               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘</pre>

### Hybrid AI + Machine Learning

This system uses two prediction engines working together:

|Engine | What It Does | Example|
|-------|--------------|--------|
|AI Engine | Understands why prices change | "iPhone prices drop in September because new models are announced"|
|ML Engine | Learns from historical patterns | "Based on 3 years of data, prices always drop 8% during Black Friday"|

When combined, you get high prediction accuracy — far better than either method alone.

### 🔄 MCP Task Scheduler for Task Management

The system uses MCP (Message Control Protocol) to manage all scheduled tasks:

<pre lang="markdown">
┌─────────────────────────────────────────────────────────────────┐
│                    Task Scheduling Flow                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  You create a task:                                             │
│  "Check iPhone 17 Pro prices every Monday at 9 AM"              │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────┐                │
│  │            MCP Scheduler                    │                │
│  │  • Stores your task                         │                │
│  │  • Waits for Monday 9 AM                    │                │
│  │  • Triggers the price check automatically   │                │
│  └─────────────────────────────────────────────┘                │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────┐                │
│  │         Automatic Actions                   │                │
│  │  • Fetch latest prices                      │                │
│  │  • Compare with previous prices             │                │
│  │  • Generate report                          │                │
│  │  • Send notifications                       │                │
│  └─────────────────────────────────────────────┘                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘</pre>

### 📧 What Happens When a Task Runs?
When the scheduled price check runs, three things happen automatically:

#### 1. Windows Desktop Notification
A pop-up appears on your computer:

```bash
🔔 Price Check Complete!
iPhone 17 Pro prices have been updated.
Best price: $1,049.99 at MegaStore
```

#### 2. Email Report
You receive an email with:
- 📊 **HTML Report** — Beautiful formatted summary
- 📄 **JSON File** — Easily imported into Power BI, Tableau, Power Query, or turned into a spreadsheet by any converters for further analysis
- 📁 **CSV File** — Raw data for your own analysis

#### 3. Google Calendar Event
A meeting is automatically created in your calendar:

```bash
📅 Weekly Price Review: iPhone 17 Pro
📆 Monday at 10:00 AM
👥 Invited: procurement@company.com
📝 Agenda: Review price trends, discuss purchasing strategy
```

#### 4. Files Automatically Organized
Windows automatically saves all reports in organized folders:

```text
Documents/PriceReports/
├── 2024/
│   ├── January/
│   │   ├── iPhone_17_Pro_2024-01-15.html
│   │   ├── iPhone_17_Pro_2024-01-15.json
│   │   └── iPhone_17_Pro_2024-01-22.csv
│   └── February/
│       └── iPhone_17_Pro_2024-02-05.html
```

## 💼 Who Uses This System?

|Role    | How They Benefit|
|--------|-----------------|
|Procurement Managers | Stop overpaying, find the best suppliers instantly|
|Supply Chain Teams | Predict price changes, optimize inventory timing|
|Finance Departments | Accurate budget forecasting, cost reduction|
|Business Owners | Competitive intelligence, margin improvement|

## ⚖️ Disclaimer

Smart Price Comparison provides AI-driven insights for informational purposes only. It does not replace professional procurement advice. Always verify critical purchasing decisions with qualified supply chain professionals.

## 📄 License

MIT License - See LICENSE file for details.

## 🏆 Key Achievements

- **Multi-Agent AI Architecture** - Successfully implemented custom-built orchestration with three specialized AI agents
- **Hybrid Prediction System** - Combined AI reasoning with ML accuracy for high prediction accuracy
- **Enterprise Data Pipeline** - Built Spark-based processing for TB-scale price analysis
- **MLOps Integration** - Implemented MLflow for model versioning and experiment tracking
- **Production Ready** - Docker and Kubernetes deployment with high SLA
- **Real-time Notifications** - Integrated Gmail and Google Calendar APIs
- **Modern UI** - Next.js dashboard with 60 FPS animations and responsive design

## 📋 Sample

  <img src="assets/JeffreyWooSmartPriceComparison1.png" alt="JeffreyWooSmartPriceComparison1" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison2.png" alt="JeffreyWooSmartPriceComparison2" width="1200" height="1000" />
  <img src="assets/JeffreyWooSmartPriceComparison3.png" alt="JeffreyWooSmartPriceComparison3" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison4.png" alt="JeffreyWooSmartPriceComparison4" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison5.png" alt="JeffreyWooSmartPriceComparison5" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison6.png" alt="JeffreyWooSmartPriceComparison6" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison7.png" alt="JeffreyWooSmartPriceComparison7" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison8.png" alt="JeffreyWooSmartPriceComparison8" width="1200" height="800" />
  <img src="assets/JeffreyWooSmartPriceComparison9.png" alt="JeffreyWooSmartPriceComparison9" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison10.png" alt="JeffreyWooSmartPriceComparison10" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison11.png" alt="JeffreyWooSmartPriceComparison11" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison12.png" alt="JeffreyWooSmartPriceComparison12" width="1200" height="600" />
  <img src="assets/JeffreyWooSmartPriceComparison13.png" alt="JeffreyWooSmartPriceComparison13" width="1200" height="1000" />
  <img src="assets/JeffreyWooSmartPriceComparison14.png" alt="JeffreyWooSmartPriceComparison14" width="1200" height="1400" />
  <img src="assets/JeffreyWooSmartPriceComparison15.png" alt="JeffreyWooSmartPriceComparison15" width="1200" height="600" />
  
## 👤 About the Author
Jeffrey Woo — Finance Manager | Strategic FP&A, AI Automation & Cost Optimization | MBA | FCCA | CTA | FTIHK | SAP Financial Accounting (FI) Certified Application Associate | Xero Advisor Certified

📧 **Email:** jeffreywoocf@gmail.com  
💼 **LinkedIn:** https://www.linkedin.com/in/wcfjeffrey/  
🐙 **GitHub:** https://github.com/wcfjeffrey/

Built with ❤️ using AI, ML, and Big Data technologies, designed for procurement excellence.
