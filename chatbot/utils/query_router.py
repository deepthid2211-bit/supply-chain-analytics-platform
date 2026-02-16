"""
Query router to intelligently route questions to SQL generation or RAG retrieval
"""

import os
from typing import Dict, Any, Optional
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser


class QueryRouter:
    """Route user queries to appropriate handlers and generate responses"""
    
    def __init__(self, snowflake_connector, rag_engine):
        """Initialize query router"""
        self.sf_connector = snowflake_connector
        self.rag_engine = rag_engine
        
        # Initialize LLM - Priority: Claude > Groq > OpenAI
        if os.getenv("ANTHROPIC_API_KEY"):
            # Use Claude (excellent for SQL generation!)
            self.llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0,
                anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
            )
            self.llm_provider = "Claude"
        elif os.getenv("GROQ_API_KEY"):
            # Use Groq for faster, free inference
            self.llm = ChatOpenAI(
                model="mixtral-8x7b-32768",
                temperature=0,
                api_key=os.getenv("GROQ_API_KEY"),
                base_url="https://api.groq.com/openai/v1"
            )
            self.llm_provider = "Groq"
        else:
            self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
            self.llm_provider = "OpenAI"
        
        # Get schema information
        self.schema_info = self.sf_connector.get_schema_info()
    
    def _classify_query(self, query: str) -> str:
        """Classify query type: data_query, explanation, or general"""
        
        classification_prompt = ChatPromptTemplate.from_template("""
        Classify the following user question into one of these categories:
        - data_query: Questions that need data from database (sales, revenue, products, etc.)
        - explanation: Questions about how things work, definitions, business rules
        - general: General conversation or greetings
        
        Question: {query}
        
        Respond with only one word: data_query, explanation, or general
        """)
        
        chain = classification_prompt | self.llm | StrOutputParser()
        classification = chain.invoke({"query": query}).strip().lower()
        
        return classification
    
    def _generate_sql(self, query: str, context: str) -> str:
        """Generate SQL query from natural language"""
        
        schema_str = self._format_schema_info()
        
        sql_prompt = ChatPromptTemplate.from_template("""
        You are a SQL expert. Generate a Snowflake SQL query to answer the user's question.
        
        Database Schema:
        {schema}
        
        Relevant Context:
        {context}
        
        User Question: {query}
        
        Rules:
        1. Use fully qualified table names (SUPPLY_CHAIN_ANALYTICS.MARTS_MARTS.table_name)
        2. Include appropriate JOINs based on foreign keys
        3. Use aggregate functions when asking for totals, averages, etc.
        4. Add ORDER BY and LIMIT clauses when asking for "top" items
        5. Use date functions for time-based analysis
        6. Return ONLY the SQL query, no explanations
        
        SQL Query:
        """)
        
        chain = sql_prompt | self.llm | StrOutputParser()
        sql_query = chain.invoke({
            "schema": schema_str,
            "context": context,
            "query": query
        })
        
        # Clean up the SQL
        sql_query = sql_query.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        return sql_query.strip()
    
    def _format_schema_info(self) -> str:
        """Format schema information as string"""
        schema_str = ""
        for table_name, columns in self.schema_info.items():
            schema_str += f"\n{table_name}:\n"
            for col in columns:
                schema_str += f"  - {col['COLUMN_NAME']} ({col['DATA_TYPE']})\n"
        return schema_str
    
    def _generate_natural_response(self, query: str, df: Optional[pd.DataFrame], 
                                   sql_query: Optional[str] = None) -> str:
        """Generate natural language response from query results"""
        
        if df is None or df.empty:
            return "I couldn't find any data matching your query. Please try rephrasing your question."
        
        # Create summary of results
        summary = f"Found {len(df)} results. "
        
        if len(df.columns) >= 2:
            # Describe the data
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                first_numeric = numeric_cols[0]
                summary += f"The total {first_numeric} is {df[first_numeric].sum():,.2f}. "
                
                if len(df) <= 10:
                    summary += f"Here are all the results:\n\n"
                    for idx, row in df.head(10).iterrows():
                        summary += f"• {row.iloc[0]}: {row.iloc[1]:,.2f}\n"
                else:
                    summary += f"Top 10 results shown below."
        
        return summary
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main entry point to process user queries"""
        
        try:
            # Classify query
            query_type = self._classify_query(query)
            
            if query_type == "general":
                return {
                    "answer": "Hello! I'm your Supply Chain Analytics assistant. I can help you analyze sales data, product performance, store metrics, and more. What would you like to know?",
                    "dataframe": None
                }
            
            # Get relevant context from RAG
            context = self.rag_engine.get_relevant_context(query)
            
            if query_type == "explanation":
                # Use RAG context directly for explanations
                explanation_prompt = ChatPromptTemplate.from_template("""
                Use the following context to answer the user's question.
                
                Context:
                {context}
                
                Question: {query}
                
                Provide a clear, helpful answer based on the context.
                """)
                
                chain = explanation_prompt | self.llm | StrOutputParser()
                answer = chain.invoke({"context": context, "query": query})
                
                return {
                    "answer": answer,
                    "dataframe": None
                }
            
            # For data queries, generate and execute SQL
            sql_query = self._generate_sql(query, context)
            
            # Execute query
            df = self.sf_connector.execute_query(sql_query)
            
            # Generate natural language response
            answer = self._generate_natural_response(query, df, sql_query)
            
            # Add SQL query to response (for transparency)
            answer += f"\n\n<details>\n<summary>SQL Query Used</summary>\n\n```sql\n{sql_query}\n```\n</details>"
            
            return {
                "answer": answer,
                "dataframe": df,
                "sql_query": sql_query
            }
            
        except Exception as e:
            return {
                "answer": f"I encountered an error processing your query: {str(e)}\n\nPlease try rephrasing your question or check the Snowflake connection.",
                "dataframe": None,
                "error": str(e)
            }
