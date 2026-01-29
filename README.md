# 🏨 Hotel Complaint Management System

**AI-Powered Multi-Agent System for Automated Guest Complaint Handling**

Built by **Siddhi Pandya** | Interview Task for **Doozy Robotics** | January 28, 2026

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Agent Details](#agent-details)
- [RAG Integration](#rag-integration)
- [Database Schema](#database-schema)
- [Sample Output](#sample-output)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

A **production-grade, multi-agent AI system** for automating hotel guest complaint processing using:
- **LangGraph** for workflow orchestration
- **Ollama** (llama3.2:3b) for local LLM inference
- **RAG** (Chroma vector store) for policy-based recommendations
- **SQLite** for persistent storage

### **What It Does:**

1. ✅ **Analyzes** complaints → severity, sentiment, category
2. ✅ **Plans** actions → retrieves policies via RAG
3. ✅ **Drafts** responses → professional, empathetic communications
4. ✅ **Stores** data → SQLite + JSON history

### **Special Features:**

- 😊 **Positive Feedback Detection** - No apologies for compliments!
- 💰 **Policy-Based Compensation** - RAG-informed recommendations
- 🎨 **Tone Adaptation** - Adjusts based on severity & sentiment
- 📊 **Full Audit Trail** - Complete logging & history

---

## 🏗️ System Architecture

```
┌────────────────────────────────────────────┐
│        INPUT: Guest Complaint              │
└──────────────────┬─────────────────────────┘
                   ↓
    ┌──────────────────────────────┐
    │   Agent 1: Analysis          │
    │   • Severity (4 levels)      │
    │   • Sentiment (-1 to 1)      │
    │   • Category (13 types)      │
    │   • Escalation decision      │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────┐
    │   Agent 2: Action Planning   │
    │   • RAG policy retrieval 🔍  │
    │   • Action items             │
    │   • Compensation             │
    │   • Response guidance        │
    └──────────────┬───────────────┘
                   ↓
    ┌──────────────────────────────┐
    │   Agent 3: Response          │
    │   • Professional response    │
    │   • Tone adaptation          │
    │   • Includes timeline        │
    └──────────────┬───────────────┘
                   ↓
┌────────────────────────────────────────────┐
│  OUTPUT: Complete Analysis + Response      │
│  STORAGE: SQLite DB + JSON Files           │
└────────────────────────────────────────────┘
```

### **State Management:**

Uses **LangGraph's `shared_memory`** pattern:

```python
shared_memory = {
    "analysis": {...},    # From Agent 1
    "actions": {...},     # From Agent 2  
    "response": {...}     # From Agent 3
}
```

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| **4-Level Severity** | Low, Medium, High, Critical |
| **Sentiment Analysis** | -1.0 (negative) to 1.0 (positive) |
| **13 Categories** | Maintenance, cleanliness, service, etc. |
| **RAG Integration** | Retrieves hotel policies for actions |
| **Positive Feedback** | Detects compliments, responds warmly |
| **Auto-Escalation** | High/Critical → management alerts |
| **Dual Storage** | SQLite database + JSON history |
| **Compensation Logic** | Policy-based recommendations |

---

## 🛠️ Technology Stack

- **Workflow:** LangGraph (agent orchestration)
- **LLM:** Ollama (llama3.2:3b, local inference)
- **RAG:** Chroma + OllamaEmbeddings
- **Database:** SQLite
- **Validation:** Pydantic
- **Language:** Python 3.10+

---

## 🚀 Installation

### **Step 1: Install Ollama**

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download
```

### **Step 2: Pull LLM Model**

```bash
ollama pull llama3.2:3b
```

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

### **Step 4: Verify Setup**

```bash
ollama list  # Should show llama3.2:3b
```

---

## 📖 Usage

### **Interactive Mode:**

```bash
python main.py
```

**Example Session:**

```
📝 PLEASE ENTER COMPLAINT DETAILS
📢 Complaint: AC not working in room 312
👤 Guest: John Doe
🏨 Room: 312
📧 Contact: john@email.com

🚀 Processing...

📋 ANALYSIS: HIGH severity, maintenance category
⚙️ ACTIONS: 3 urgent actions, Engineering dept
📧 RESPONSE: Professional apology with timeline
📁 Saved to: output/complaint_John_Doe_TIMESTAMP.json
```

### **Programmatic Usage:**

```python
from app.graph.workflow import process_complaint

result = process_complaint(
    complaint_text="Room was dirty",
    guest_name="Jane Smith",
    room_number="205",
    contact_info="jane@email.com"
)

print(result['severity_level'])      # 'medium'
print(result['guest_response'])      # Full response
print(result['compensation_recommended'])  # Offer
```

---

## 📁 Project Structure

```
hotel-complaint-system/
│
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── README.md                  # This file
│
├── app/
│   ├── agents/
│   │   ├── analysis_agent.py       # Agent 1
│   │   ├── action_planning_agent.py # Agent 2 (RAG)
│   │   └── response_agent.py       # Agent 3
│   │
│   ├── graph/
│   │   └── workflow.py             # LangGraph workflow
│   │
│   ├── tools/
│   │   ├── rag_tool.py            # RAG (Chroma)
│   │   └── database.py            # SQLite ops
│   │
│   └── schema.py                   # Models & state
│
├── config/
│   └── settings.py                 # Configuration
│
├── data/
│   ├── hotel_policies.json         # RAG policies
│   ├── hotel_complaints.db         # SQLite (auto)
│   └── complaints_history.json     # History (auto)
│
└── output/                          # Results (auto)
    └── complaint_*.json
```

---

## 🤖 Agent Details

### **Agent 1: Analysis**

**Classifies:** Severity, sentiment, category, escalation

**Severity Levels:**
- **Critical:** Health/safety hazards, legal threats
- **High:** Essential amenities down, major failures
- **Medium:** Single issues, service delays
- **Low:** Minor requests, positive feedback

**Categories:** maintenance, cleanliness, amenities, service, billing, noise, privacy, safety, food_beverage, parking, check_in_out, general, positive_feedback

**Output:**
```json
{
  "severity_level": "high",
  "category": "maintenance",
  "sentiment_score": -0.8,
  "escalation_required": true,
  "key_issues": ["AC not working"]
}
```

---

### **Agent 2: Action Planning (RAG)**

**Uses RAG to retrieve:** Relevant hotel policies

**Creates:** 
- Internal action items (with priorities)
- Department assignments
- Timelines
- Compensation recommendations
- Response tone guidance

**RAG Process:**
1. Query: `"{category} {severity} complaint resolution"`
2. Retrieve: Top-3 relevant policies from Chroma
3. Generate: Policy-compliant action plan

**Output:**
```json
{
  "internal_actions": [
    {
      "action": "Fix AC within 1 hour",
      "responsible": "Engineering",
      "priority": "urgent",
      "timeline": "30 minutes"
    }
  ],
  "assigned_department": "Engineering",
  "estimated_resolution_time": "1 hour",
  "compensation_recommended": "25% discount",
  "guest_response_tone": "apologetic and urgent"
}
```

---

### **Agent 3: Response**

**Drafts:** Professional, empathetic guest responses

**Tone Adaptation:**
- Critical → Very apologetic, urgent
- High → Apologetic, action-focused
- Medium → Professional, solution-oriented
- Positive feedback → Warm, grateful (NO apologies!)

**Output:**
```json
{
  "guest_response": "Dear Mr. Doe,\n\nI sincerely apologize...",
  "response_type": "complaint"
}
```

---

## 🔍 RAG Integration

### **Technology:**
- **Vector Store:** Chroma
- **Embeddings:** OllamaEmbeddings (llama3.2:3b)
- **Policies:** 6 hotel policies in `data/hotel_policies.json`

### **How It Works:**

1. **Load policies** → Create embeddings → Store in Chroma
2. **Query time** → Build semantic query → Retrieve top-K policies
3. **Use in prompt** → Inform action planning decisions

### **Benefits:**
- ✅ Policy-compliant recommendations
- ✅ Consistent compensation offers
- ✅ Reduces hallucinations

---

## 💾 Database Schema

**SQLite Table:** `complaints`

| Column | Type | Description |
|--------|------|-------------|
| complaint_id | TEXT | UUID |
| guest_name | TEXT | Guest name |
| room_number | TEXT | Room number |
| severity_level | TEXT | Severity |
| category | TEXT | Category |
| sentiment_score | REAL | Sentiment |
| escalation_required | INTEGER | 0/1 |
| compensation_recommended | TEXT | Offer |
| guest_response | TEXT | Response |
| created_at | TEXT | Timestamp |

**Query Examples:**

```sql
-- High/critical complaints
SELECT * FROM complaints 
WHERE severity_level IN ('high', 'critical');

-- Count by category
SELECT category, COUNT(*) 
FROM complaints 
GROUP BY category;
```

---

## 📊 Sample Output

### **Input:**
```
Complaint: "AC not working, room too hot"
Guest: John Doe
Room: 312
```

### **Output:**

```
📋 COMPLAINT ANALYSIS
Severity        : HIGH
Category        : maintenance
Sentiment Score : -0.75
Escalation      : YES

⚙️ ACTION PLAN
Department      : Engineering
ETA             : Within 1 hour
Compensation    : 25% room discount

📧 GUEST RESPONSE
Dear Mr. Doe,

I sincerely apologize for the AC issue. Our engineering 
team will fix it within 1 hour. As compensation, we're 
offering a 25% discount on your stay.

Sincerely,
Guest Relations Manager
```

**JSON:** `output/complaint_John_Doe_TIMESTAMP.json`

---

## 🐛 Troubleshooting

### **"Ollama connection failed"**
```bash
ollama serve
ollama pull llama3.2:3b
```

### **"RAG initialization failed"**
System will use mock policies as fallback. No action needed.

### **"No response generated"**
Check `shared_memory` is in `schema.py`:
```python
shared_memory: Dict[str, Any]
```

### **"Slow processing"**
Reduce tokens in `config/settings.py`:
```python
LLM_MAX_TOKENS = 256
```

---

## 📞 Contact

**Siddhi Pandya**  
Email: siddhip568@gmail.com  
Phone: +91 9484454737

---

## 🎉 Quick Start

```bash
# 1. Install Ollama + model
ollama pull llama3.2:3b

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

---

**System ready to process complaints! 🚀**