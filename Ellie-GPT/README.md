# ✨ Ellie-GPT  
### A Multi-Persona AI Assistant with Tool-Calling + Live Web Search

Ellie-GPT is a command-line AI assistant built with **Python**, **LangChain**, **LangGraph**, and **OpenAI**.  
It includes multiple personality modes (“Ellies”) and supports real-time internet search using the **ddgs** (DuckDuckGo) search tool.

This project demonstrates tool-calling, agent reasoning, persona switching, and structured prompting — perfect for AI engineering portfolios.

---

## 🚀 Features

### 🎭 Multi-Persona Modes
Ellie can switch between four distinct personalities:

- **✈️ Travel Ellie** — trip planning, flights, itineraries, activities  
- **🧘‍♀️ Fitness Ellie** — workouts, nutrition, wellness routines  
- **📚 Study Ellie** — study planning, assignment breakdowns, explanations  
- **💬 Chat Ellie** — emotional support and conversation  

Switch anytime using: /mode 

---

### 🧠 Tool-Calling Agent (LangGraph)
Ellie is powered by a LangGraph REACT agent that autonomously decides when to call tools.

Current tools include:

- **calculator** — performs basic arithmetic  
- **web_search** — live internet search using DuckDuckGo through `ddgs`  

Ellie automatically uses `web_search` when the user asks for:
- news  
- current events  
- live information  
- travel details  
- celebrity updates  
- factual lookups  

---

### 🌍 Live Internet Search  
Web search is powered by **ddgs**, a DuckDuckGo search wrapper.  
It requires **no API key** and returns structured search results for Ellie to summarize.

Example: 
"You: what’s the latest news on Carlos Alcaraz?"

Ellie will call: web_search(“latest news on Carlos Alcaraz”)

and summarize real search results.

---

## 📦 Installation

Clone the project:

```bash
git clone <your-repository-url>
cd Ellie-GPT

Create a uv virtual environment (optional but recommended):
uv venv
source .venv/bin/activate

uv add langchain langgraph langchain-openai python-dotenv ddgs requests

🔑 Environment Variables
Create a .env file:
OPENAI_API_KEY=your_openai_key_here

No search API key is needed — DuckDuckGo search works without one.

▶️ Running Ellie-GPT

Run the program:
uv run main.py

Choose your persona:
1. Travel Ellie
2. Fitness Ellie
3. Study Ellie
4. Chat Ellie

Chat naturally:

Exit:
quit 

Ellie-GPT/
│
├── main.py           # main program (agent, tools, personas)
├── README.md         # documentation
├── .env              # environment variables (OpenAI key)
└── .venv/            # uv virtual environment (optional)

🛠 Tech Stack
	•	Python
	•	LangChain
	•	LangGraph
	•	OpenAI API
	•	uv package manager
	•	ddgs (DuckDuckGo search)
