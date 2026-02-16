"""
RAG (Retrieval Augmented Generation) engine for document retrieval
"""

import os
from typing import List, Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class RAGEngine:
    """Handle document embedding, storage, and retrieval"""
    
    def __init__(self, knowledge_base_path: str = "data/knowledge_base"):
        """Initialize RAG engine with knowledge base"""
        self.knowledge_base_path = knowledge_base_path
        
        # Use HuggingFace embeddings (FREE, no API key needed!)
        # This model is small, fast, and good quality
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.vector_store = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Initialize with default knowledge
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self) -> None:
        """Initialize vector store with default supply chain knowledge"""
        
        # Default knowledge documents
        documents = [
            Document(
                page_content="""
                Supply Chain Analytics Database Schema:
                
                FACT_SALES: Contains all sales transactions
                - TRANSACTION_ID: Unique transaction identifier
                - SALE_DATE: Date of sale
                - PRODUCT_ID: Product identifier (FK to DIM_PRODUCTS)
                - STORE_ID: Store identifier (FK to DIM_STORES)
                - QUANTITY: Number of units sold
                - UNIT_PRICE: Price per unit
                - TOTAL_AMOUNT: Total sale amount (quantity * unit_price)
                - DISCOUNT_AMOUNT: Discount applied
                - PAYMENT_METHOD: Method of payment (Credit Card, Cash, etc.)
                
                DIM_PRODUCTS: Product dimension table
                - PRODUCT_ID: Unique product identifier
                - PRODUCT_NAME: Name of the product
                - CATEGORY: Product category (Electronics, Clothing, etc.)
                - BRAND: Product brand
                - UNIT_COST: Cost to acquire the product
                - CURRENT_STOCK: Current inventory level
                
                DIM_STORES: Store dimension table
                - STORE_ID: Unique store identifier
                - STORE_NAME: Name of the store
                - CITY: Store location city
                - STATE: Store location state
                - REGION: Geographic region (West, East, etc.)
                - STORE_SIZE_SQFT: Store size in square feet
                - OPENING_DATE: Date store opened
                
                DIM_DATE: Date dimension table for time intelligence
                - DATE_KEY: Date in YYYYMMDD format
                - FULL_DATE: Actual date
                - YEAR, QUARTER, MONTH, DAY: Time components
                - DAY_OF_WEEK: Day name (Monday, etc.)
                - IS_WEEKEND: Boolean flag for weekends
                """,
                metadata={"source": "schema", "type": "database_schema"}
            ),
            Document(
                page_content="""
                Common Business Questions and SQL Patterns:
                
                Top Products by Revenue:
                SELECT p.PRODUCT_NAME, SUM(s.TOTAL_AMOUNT) as total_revenue
                FROM FACT_SALES s
                JOIN DIM_PRODUCTS p ON s.PRODUCT_ID = p.PRODUCT_ID
                GROUP BY p.PRODUCT_NAME
                ORDER BY total_revenue DESC
                LIMIT 10
                
                Sales Trends Over Time:
                SELECT d.YEAR, d.MONTH, SUM(s.TOTAL_AMOUNT) as monthly_revenue
                FROM FACT_SALES s
                JOIN DIM_DATE d ON s.SALE_DATE = d.FULL_DATE
                GROUP BY d.YEAR, d.MONTH
                ORDER BY d.YEAR, d.MONTH
                
                Store Performance:
                SELECT st.STORE_NAME, st.REGION, SUM(s.TOTAL_AMOUNT) as revenue
                FROM FACT_SALES s
                JOIN DIM_STORES st ON s.STORE_ID = st.STORE_ID
                GROUP BY st.STORE_NAME, st.REGION
                ORDER BY revenue DESC
                
                Category Analysis:
                SELECT p.CATEGORY, 
                       COUNT(DISTINCT s.TRANSACTION_ID) as num_transactions,
                       SUM(s.QUANTITY) as units_sold,
                       SUM(s.TOTAL_AMOUNT) as revenue
                FROM FACT_SALES s
                JOIN DIM_PRODUCTS p ON s.PRODUCT_ID = p.PRODUCT_ID
                GROUP BY p.CATEGORY
                ORDER BY revenue DESC
                """,
                metadata={"source": "sql_patterns", "type": "query_examples"}
            ),
            Document(
                page_content="""
                Key Metrics and KPIs:
                
                Revenue Metrics:
                - Total Revenue: Sum of all TOTAL_AMOUNT in FACT_SALES
                - Average Order Value (AOV): Average of TOTAL_AMOUNT
                - Revenue Per Store: Total revenue divided by store count
                - Revenue Growth: Period-over-period revenue change
                
                Product Metrics:
                - Best Sellers: Products with highest sales volume
                - Stock Turnover: How quickly inventory sells
                - Average Discount Rate: DISCOUNT_AMOUNT / TOTAL_AMOUNT
                
                Store Metrics:
                - Store Efficiency: Revenue per square foot
                - Regional Performance: Revenue by region
                - Store Productivity: Sales per store employee
                
                Customer Metrics:
                - Transaction Count: Number of sales transactions
                - Average Items Per Transaction: AVG(QUANTITY)
                - Payment Method Distribution: Breakdown by payment type
                """,
                metadata={"source": "metrics", "type": "business_definitions"}
            ),
            Document(
                page_content="""
                Data Quality and Business Rules:
                
                1. All transactions must have positive TOTAL_AMOUNT
                2. QUANTITY sold should be positive integers
                3. DISCOUNT_AMOUNT cannot exceed TOTAL_AMOUNT
                4. Product CURRENT_STOCK decreases with each sale
                5. UNIT_PRICE should be greater than UNIT_COST for profitability
                6. Sales dates should be within store operating period
                7. Each product must belong to a valid category
                8. Store regions follow standard geographic divisions
                
                Data Refresh Schedule:
                - FACT_SALES: Updated daily at 2 AM UTC
                - DIM_PRODUCTS: Updated weekly on Sundays
                - DIM_STORES: Updated monthly
                - DIM_DATE: Pre-populated for 10 years
                """,
                metadata={"source": "business_rules", "type": "data_quality"}
            )
        ]
        
        # Split documents into chunks
        splits = self.text_splitter.split_documents(documents)
        
        # Create vector store
        self.vector_store = FAISS.from_documents(splits, self.embeddings)
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add new documents to the vector store"""
        splits = self.text_splitter.split_documents(documents)
        if self.vector_store:
            self.vector_store.add_documents(splits)
        else:
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
    
    def retrieve_context(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve relevant documents for a query"""
        if not self.vector_store:
            return []
        
        results = self.vector_store.similarity_search(query, k=k)
        return results
    
    def get_relevant_context(self, query: str) -> str:
        """Get relevant context as a formatted string"""
        docs = self.retrieve_context(query)
        
        if not docs:
            return "No relevant context found."
        
        context = "\n\n".join([
            f"Context {i+1} (Source: {doc.metadata.get('source', 'unknown')}):\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ])
        
        return context
