# 🚀 Deployment Guide - RAG Chatbot

Complete guide to deploy your Supply Chain Analytics Chatbot to Streamlit Cloud.

## 📋 Prerequisites

- [x] Chatbot code complete (app.py + utils/)
- [x] GitHub account
- [x] Snowflake credentials
- [ ] OpenAI API key (get from https://platform.openai.com/api-keys)
- [ ] Groq API key - OPTIONAL but recommended (FREE at https://console.groq.com)

## 🔑 Step 1: Get API Keys

### OpenAI API Key (Required)
1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-...`)
5. **Billing**: Add $5-10 for testing (embeddings are cheap: ~$0.0001 per 1K tokens)

### Groq API Key (Optional - Recommended)
1. Go to: https://console.groq.com
2. Sign up with GitHub/Google
3. Navigate to API Keys
4. Create new key
5. Copy the key (starts with `gsk_...`)
6. **FREE tier**: 30 requests/min, 6000/day - plenty for portfolio demos!

## 📦 Step 2: Test Locally

Before deploying, test everything works:

```bash
# Navigate to chatbot directory
cd /Users/deepthi/.openclaw/workspace/supply-chain-analytics-platform/chatbot

# Create .env file
cp .env.template .env

# Edit .env with your credentials
nano .env  # or use any text editor

# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py
```

Test queries:
- "What are the top 5 products by revenue?"
- "Show sales by category"
- "Explain what a fact table is"

If everything works → proceed to deployment!

## 🐙 Step 3: Push to GitHub

```bash
# Navigate to project root
cd /Users/deepthi/.openclaw/workspace/supply-chain-analytics-platform

# Add chatbot files
git add chatbot/
git status  # Verify files are staged

# Commit
git commit -m "Add RAG chatbot with Streamlit UI

- Natural language query interface
- RAG-powered context retrieval
- Automatic SQL generation
- Snowflake integration
- Groq/OpenAI LLM support"

# Push to GitHub
git push origin main
```

**⚠️ IMPORTANT**: Make sure `.env` is in `.gitignore` - never commit API keys!

```bash
# Add to .gitignore if not present
echo "chatbot/.env" >> .gitignore
git add .gitignore
git commit -m "Update .gitignore for chatbot secrets"
git push origin main
```

## ☁️ Step 4: Deploy to Streamlit Cloud

### 4.1 Create Streamlit Cloud Account
1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. Authorize Streamlit to access your repositories

### 4.2 Deploy App
1. Click **"New app"** button
2. Select your repository: `supply-chain-analytics-platform`
3. Set branch: `main`
4. Set main file path: `chatbot/app.py`
5. (Optional) Customize URL: `yourname-supply-chain-chatbot`
6. Click **"Deploy!"**

### 4.3 Configure Secrets
1. While deployment is running, click **"⚙️ Settings"** (top right)
2. Go to **"Secrets"** tab
3. Paste your secrets in TOML format:

```toml
# Snowflake Connection
SNOWFLAKE_ACCOUNT = "VYUVIGG-RVB11850"
SNOWFLAKE_USER = "Deepthi"
SNOWFLAKE_PASSWORD = "DeepthiD2211@7893190472"
SNOWFLAKE_DATABASE = "SUPPLY_CHAIN_ANALYTICS"
SNOWFLAKE_SCHEMA = "MARTS_MARTS"
SNOWFLAKE_WAREHOUSE = "COMPUTE_WH"

# OpenAI (required for embeddings)
OPENAI_API_KEY = "sk-proj-..."

# Groq (optional, but recommended for faster inference)
GROQ_API_KEY = "gsk_..."
```

4. Click **"Save"**
5. App will auto-restart with secrets loaded

### 4.4 Wait for Deployment
- Initial deployment: 2-5 minutes
- Streamlit will install dependencies from `requirements.txt`
- Watch logs for any errors

## ✅ Step 5: Test Deployed App

Once deployed, you'll get a URL like:
```
https://yourname-supply-chain-chatbot.streamlit.app
```

**Test Checklist**:
- [ ] App loads without errors
- [ ] Can connect to Snowflake (click "Connect to Snowflake" in sidebar)
- [ ] Ask: "What are the top products by revenue?"
- [ ] Verify chart renders
- [ ] Check data table displays
- [ ] Try an explanation query: "What is a fact table?"

## 📱 Step 6: Share Your App

### Add to Resume
```
PROJECTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Supply Chain Analytics Platform with RAG Chatbot
├─ Interactive chatbot for natural language data queries
├─ RAG architecture: LangChain + FAISS + OpenAI embeddings
├─ Automatic SQL generation from user questions
├─ Real-time Snowflake integration (18K+ transactions)
├─ Deployed on Streamlit Cloud for public access
└─ Tech: Python, Streamlit, LangChain, Snowflake, FAISS
   
🔗 Live Demo: https://yourname-supply-chain-chatbot.streamlit.app
📂 GitHub: https://github.com/yourusername/supply-chain-analytics
```

### Update LinkedIn
Create a post:

```
🚀 Excited to share my latest project!

Built an AI-powered Supply Chain Analytics Chatbot that lets users query 
complex data using plain English. 

Key features:
✅ RAG (Retrieval Augmented Generation) for context-aware responses
✅ Automatic SQL generation from natural language
✅ Real-time Snowflake data warehouse integration
✅ Interactive visualizations

Try asking:
• "What are the top products by revenue?"
• "Show sales trends for electronics"
• "Which stores are underperforming?"

Tech Stack: Python • Streamlit • LangChain • OpenAI • Snowflake • FAISS

🔗 Live Demo: https://yourname-supply-chain-chatbot.streamlit.app

#DataEngineering #MachineLearning #RAG #LLM #Python #Snowflake
```

### Add to Portfolio Website
```html
<div class="project">
  <h3>Supply Chain Analytics RAG Chatbot</h3>
  <p>Intelligent chatbot powered by RAG architecture enabling natural language 
  queries on supply chain data.</p>
  
  <div class="tech-stack">
    <span>Python</span>
    <span>Streamlit</span>
    <span>LangChain</span>
    <span>OpenAI</span>
    <span>Snowflake</span>
    <span>FAISS</span>
  </div>
  
  <div class="links">
    <a href="https://yourname-supply-chain-chatbot.streamlit.app">Live Demo</a>
    <a href="https://github.com/yourusername/supply-chain-analytics">GitHub</a>
  </div>
</div>
```

## 🔧 Step 7: Maintenance

### Monitor Usage
- Streamlit Cloud dashboard shows app usage
- Monitor OpenAI API usage: https://platform.openai.com/usage
- Groq is free, no monitoring needed

### Update App
```bash
# Make changes locally
cd chatbot/
# Edit files...

# Test locally
streamlit run app.py

# Push to GitHub
git add .
git commit -m "Update chatbot: <description>"
git push origin main

# Streamlit auto-deploys on push!
```

### Cost Estimates
**Per 1000 queries**:
- OpenAI embeddings (ada-002): ~$0.10
- OpenAI GPT-3.5-turbo: ~$0.50
- Groq (Mixtral): **FREE**
- Snowflake compute: ~$0.20

**Monthly (100 queries/day)**:
- Total: ~$2-5/month (practically free for portfolio)

### Troubleshooting

**App won't start**:
- Check logs in Streamlit Cloud dashboard
- Verify all secrets are set correctly
- Ensure requirements.txt is complete

**Snowflake connection fails**:
- Verify credentials in secrets
- Check if warehouse is running
- Test connection with provided credentials

**Slow responses**:
- Use Groq instead of OpenAI (3-5x faster)
- Reduce retrieval documents (k=2 instead of k=3)
- Optimize SQL queries

**Out of API credits**:
- OpenAI: Add more credits
- Or switch to Groq (FREE)

## 🎯 Success Metrics

Track these to show impact on resume:
- [ ] Number of queries processed
- [ ] Types of questions users ask
- [ ] Response accuracy
- [ ] Average response time
- [ ] User engagement (return visits)

You can add a simple analytics counter in the app:

```python
# In app.py
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

st.session_state.query_count += 1
st.sidebar.metric("Total Queries", st.session_state.query_count)
```

## 🏆 What Recruiters See

When you share this on your resume:

✅ **Modern AI skills**: RAG, LLM, embeddings  
✅ **Full-stack deployment**: Backend + frontend + cloud  
✅ **Production-ready**: Live URL they can test immediately  
✅ **Real data engineering**: Snowflake integration  
✅ **Initiative**: Built beyond basic requirements  

This project shows you can:
- Work with cutting-edge AI/ML technologies
- Deploy production applications
- Integrate multiple systems (DB + LLM + UI)
- Build user-friendly interfaces

## 📞 Questions?

If you run into issues:
1. Check Streamlit Cloud logs
2. Review error messages
3. Test locally first
4. Verify all secrets are correct

---

**🎉 Congratulations!** You've deployed a production RAG chatbot!

This is a **major differentiator** on your resume. Most candidates show static dashboards - you have an **interactive AI-powered application** that recruiters can actually use.

**Next Steps**:
1. Test thoroughly
2. Add URL to resume
3. Post on LinkedIn
4. Start applying to H1B-friendly companies!

Good luck! 🚀
