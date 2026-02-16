# 📊 Supply Chain Analytics RAG Chatbot

An intelligent chatbot powered by RAG (Retrieval Augmented Generation) that lets users query supply chain data using natural language. Built with Streamlit, LangChain, and Snowflake.

![Chatbot Demo](https://img.shields.io/badge/Status-Live-success)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)

## 🚀 Features

- **Natural Language Queries**: Ask questions in plain English
- **Intelligent Query Routing**: Automatically determines if you need data or explanations
- **SQL Generation**: Converts natural language to optimized SQL queries
- **RAG-Powered Context**: Retrieves relevant business context for accurate responses
- **Interactive Visualizations**: Automatic chart generation from query results
- **Real-Time Snowflake Connection**: Live data from your data warehouse
- **Multiple LLM Support**: Works with OpenAI or Groq (free, faster)

## 💬 Example Questions

Try asking:
- "What were the top 5 products by revenue last quarter?"
- "Show me sales trends for electronics category"
- "Which stores are underperforming?"
- "What's the total revenue by region?"
- "Explain how stock turnover is calculated"
- "Forecast demand for Product X"

## 🏗️ Architecture

```
User Question → Query Classifier
                ↓
        ┌───────┴────────┐
        ↓                ↓
    Data Query      Explanation Query
        ↓                ↓
    RAG Context     RAG Retrieval
        ↓                ↓
    SQL Generator   LLM Response
        ↓
    Snowflake Query
        ↓
    Results + Visualization
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM Framework**: LangChain
- **Embeddings**: OpenAI ada-002
- **Vector Store**: FAISS
- **Data Warehouse**: Snowflake
- **LLM**: OpenAI GPT-3.5 or Groq Mixtral-8x7b
- **Visualization**: Plotly

## 📦 Installation

### 1. Clone Repository

```bash
cd supply-chain-analytics-platform/chatbot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.template .env
# Edit .env with your credentials:
# - Snowflake account details
# - OpenAI API key OR Groq API key (free)
```

### 5. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## 🔑 API Keys

### OpenAI (Required for embeddings)
Get your key: https://platform.openai.com/api-keys
- Used for: Text embeddings (ada-002) and optional LLM

### Groq (Optional - Recommended)
Get FREE key: https://console.groq.com
- Faster inference than OpenAI
- Free tier: 30 requests/minute
- Uses Mixtral-8x7b model

## ☁️ Deployment to Streamlit Cloud

### Prerequisites
1. GitHub account
2. API keys configured
3. Snowflake credentials

### Steps

1. **Push to GitHub**
```bash
cd /Users/deepthi/.openclaw/workspace/supply-chain-analytics-platform
git add chatbot/
git commit -m "Add RAG chatbot"
git push origin main
```

2. **Deploy to Streamlit Cloud**
- Go to: https://share.streamlit.io
- Click "New app"
- Connect your GitHub repository
- Set main file: `chatbot/app.py`
- Click "Deploy"

3. **Configure Secrets**
In Streamlit Cloud dashboard → Settings → Secrets:

```toml
SNOWFLAKE_ACCOUNT = "VYUVIGG-RVB11850"
SNOWFLAKE_USER = "Deepthi"
SNOWFLAKE_PASSWORD = "your_password"
SNOWFLAKE_DATABASE = "SUPPLY_CHAIN_ANALYTICS"
SNOWFLAKE_SCHEMA = "MARTS_MARTS"
OPENAI_API_KEY = "sk-..."
GROQ_API_KEY = "gsk_..."  # Optional
```

4. **Share Your App**
Your app will be live at: `https://your-app-name.streamlit.app`

Add this link to your resume! 🎉

## 🧪 Testing Locally

Test with sample questions:

```python
# In Python shell
from utils.snowflake_connector import SnowflakeConnector
from utils.rag_engine import RAGEngine
from utils.query_router import QueryRouter

# Initialize
sf = SnowflakeConnector(account="...", user="...", password="...")
rag = RAGEngine()
router = QueryRouter(sf, rag)

# Test query
result = router.process_query("What are the top 5 products by revenue?")
print(result["answer"])
print(result["dataframe"])
```

## 📊 Database Schema

The chatbot queries these tables:

- **FACT_SALES**: Transaction-level sales data
- **DIM_PRODUCTS**: Product catalog with categories and brands
- **DIM_STORES**: Store locations and details
- **DIM_DATE**: Date dimension for time intelligence

See parent `README.md` for full schema documentation.

## 🎨 Customization

### Add Custom Knowledge
Edit `utils/rag_engine.py` to add domain-specific documents:

```python
custom_docs = [
    Document(
        page_content="Your custom business rules here...",
        metadata={"source": "custom", "type": "business_rules"}
    )
]
rag_engine.add_documents(custom_docs)
```

### Change LLM Model
In `utils/query_router.py`, modify the model:

```python
self.llm = ChatOpenAI(
    model="gpt-4",  # Use GPT-4 for better accuracy
    temperature=0
)
```

### Customize UI Theme
Edit `.streamlit/config.toml` for colors and styling.

## 🐛 Troubleshooting

### Connection Issues
- Verify Snowflake credentials in `.env`
- Check network connectivity
- Ensure warehouse is running

### No Results Returned
- Check table names (should be MARTS_MARTS schema)
- Verify data exists in Snowflake
- Review generated SQL in app output

### Slow Response
- Switch to Groq API for faster inference
- Reduce `k` parameter in RAG retrieval
- Optimize SQL queries

## 📈 Performance

Typical response times:
- Simple queries: 2-3 seconds
- Complex aggregations: 4-6 seconds
- With Groq: ~50% faster than OpenAI

## 🔒 Security

- Never commit `.env` file
- Use Streamlit secrets in production
- Rotate API keys regularly
- Use read-only Snowflake credentials

## 📝 Resume Impact

Add to your resume:

> **Supply Chain Analytics RAG Chatbot**
> - Built intelligent chatbot with RAG architecture (LangChain + FAISS) enabling natural language queries on 18K+ transactions
> - Implemented automatic SQL generation from user questions using LLM-powered query routing
> - Deployed production app on Streamlit Cloud with real-time Snowflake integration
> - Tech: Python, Streamlit, LangChain, OpenAI, Snowflake, FAISS
> - **Live Demo**: https://your-app.streamlit.app

## 🤝 Contributing

This is a portfolio project, but feel free to:
- Report bugs
- Suggest features
- Share improvements

## 📄 License

MIT License - See parent project LICENSE

## 👤 Author

**Deepthi**
- LinkedIn: [Your LinkedIn]
- GitHub: [Your GitHub]
- Portfolio: [Your Portfolio Site]

---

Built with ❤️ using Streamlit, LangChain & Snowflake
