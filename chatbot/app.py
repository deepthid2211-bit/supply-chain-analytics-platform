"""
Supply Chain Analytics RAG Chatbot
Interactive chatbot for querying supply chain data using natural language
"""

import streamlit as st
import os
from dotenv import load_dotenv
from utils.snowflake_connector import SnowflakeConnector
from utils.rag_engine import RAGEngine
from utils.query_router import QueryRouter
import plotly.express as px
import pandas as pd

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Supply Chain Analytics Chatbot",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "snowflake_connected" not in st.session_state:
    st.session_state.snowflake_connected = False

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Snowflake credentials
    with st.expander("🔐 Snowflake Connection", expanded=False):
        sf_account = st.text_input("Account", value=os.getenv("SNOWFLAKE_ACCOUNT", "VYUVIGG-RVB11850"))
        sf_user = st.text_input("User", value=os.getenv("SNOWFLAKE_USER", "Deepthi"))
        sf_password = st.text_input("Password", type="password", value=os.getenv("SNOWFLAKE_PASSWORD", ""))
        sf_database = st.text_input("Database", value="SUPPLY_CHAIN_ANALYTICS")
        sf_schema = st.text_input("Schema", value="MARTS_MARTS")
        
        if st.button("🔌 Connect to Snowflake"):
            with st.spinner("Connecting..."):
                try:
                    connector = SnowflakeConnector(
                        account=sf_account,
                        user=sf_user,
                        password=sf_password,
                        database=sf_database,
                        schema=sf_schema
                    )
                    st.session_state.sf_connector = connector
                    st.session_state.snowflake_connected = True
                    st.success("✅ Connected!")
                except Exception as e:
                    st.error(f"❌ Connection failed: {str(e)}")
    
    # AI Configuration
    with st.expander("🤖 AI Configuration", expanded=False):
        st.markdown("**LLM Configuration:**")
        
        # Claude (Anthropic) - RECOMMENDED
        anthropic_key = st.text_input("Anthropic API Key (Claude - Best for SQL)", 
                                      type="password", 
                                      value=os.getenv("ANTHROPIC_API_KEY", ""))
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
            st.success("✅ Claude configured")
        
        st.divider()
        
        # Groq (Free alternative)
        groq_key = st.text_input("Groq API Key (Free alternative)", 
                                 type="password", 
                                 value=os.getenv("GROQ_API_KEY", ""))
        if groq_key:
            os.environ["GROQ_API_KEY"] = groq_key
            st.success("✅ Groq configured")
        
        st.divider()
        
        st.info("💡 **Embeddings**: Using FREE HuggingFace (sentence-transformers). No API key needed!")
    
    st.divider()
    
    # Example questions
    st.subheader("💡 Try asking:")
    example_questions = [
        "What were the top 5 products by revenue?",
        "Show sales trends for electronics",
        "Which stores are underperforming?",
        "What's the total revenue by category?",
        "Forecast demand for next quarter"
    ]
    
    for q in example_questions:
        if st.button(q, key=f"example_{q}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": q})
            st.rerun()

# Main content
st.title("📊 Supply Chain Analytics Chatbot")
st.markdown("Ask me anything about your supply chain data! I can analyze sales, inventory, products, and more.")

# Connection status indicator
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.session_state.snowflake_connected:
        st.success("🟢 Snowflake: Connected")
    else:
        st.warning("🟡 Snowflake: Not connected")

with col2:
    # Show active LLM provider
    if os.getenv("ANTHROPIC_API_KEY"):
        st.success("🤖 LLM: Claude 3 Haiku ($0.25/M tokens)")
    elif os.getenv("GROQ_API_KEY"):
        st.info("🤖 LLM: Groq Mixtral (FREE)")
    elif os.getenv("OPENAI_API_KEY"):
        st.info("🤖 LLM: OpenAI GPT-3.5")
    else:
        st.warning("🤖 LLM: Not configured")

with col3:
    st.success("🧠 Embeddings: HuggingFace (Free)")

# Chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display chart if present
            if "chart" in message:
                st.plotly_chart(message["chart"], use_container_width=True)
            
            # Display dataframe if present
            if "dataframe" in message:
                st.dataframe(message["dataframe"], use_container_width=True)

# Chat input
if prompt := st.chat_input("Ask about your supply chain data..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                if not st.session_state.snowflake_connected:
                    response = "⚠️ Please connect to Snowflake first using the sidebar configuration."
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    # Initialize RAG engine if not exists
                    if "rag_engine" not in st.session_state:
                        st.session_state.rag_engine = RAGEngine()
                    
                    # Initialize query router
                    if "query_router" not in st.session_state:
                        st.session_state.query_router = QueryRouter(
                            st.session_state.sf_connector,
                            st.session_state.rag_engine
                        )
                    
                    # Process query
                    result = st.session_state.query_router.process_query(prompt)
                    
                    # Display response
                    st.markdown(result["answer"])
                    
                    # Create message dict
                    message = {
                        "role": "assistant",
                        "content": result["answer"]
                    }
                    
                    # Display and store chart if present
                    if "dataframe" in result and result["dataframe"] is not None:
                        df = result["dataframe"]
                        
                        # Auto-generate chart based on data
                        if len(df.columns) >= 2:
                            # Try to create an appropriate chart
                            if df.select_dtypes(include=['number']).shape[1] > 0:
                                numeric_col = df.select_dtypes(include=['number']).columns[0]
                                categorical_col = df.select_dtypes(exclude=['number']).columns[0] if len(df.select_dtypes(exclude=['number']).columns) > 0 else df.columns[0]
                                
                                fig = px.bar(df.head(10), x=categorical_col, y=numeric_col, 
                                           title=f"{numeric_col} by {categorical_col}")
                                st.plotly_chart(fig, use_container_width=True)
                                message["chart"] = fig
                        
                        # Show data table
                        st.dataframe(df.head(20), use_container_width=True)
                        message["dataframe"] = df
                    
                    st.session_state.messages.append(message)
                    
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    Built with ❤️ using Streamlit, LangChain & Snowflake | 
    <a href='https://github.com/yourusername/supply-chain-analytics' target='_blank'>GitHub</a>
</div>
""", unsafe_allow_html=True)
