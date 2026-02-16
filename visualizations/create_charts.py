"""
Supply Chain Analytics Visualizations
======================================

Generate professional charts from Snowflake data warehouse.
Creates PNG images for GitHub portfolio.

Author: Deepthi Desharaju
Date: February 2026
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import snowflake.connector
import yaml
import logging
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Professional color scheme
COLORS = {
    'primary': '#2E86AB',      # Blue
    'secondary': '#A23B72',    # Purple
    'success': '#06A77D',      # Green
    'warning': '#F18F01',      # Orange
    'danger': '#C73E1D'        # Red
}

class SupplyChainVisualizer:
    """Generate visualizations from Snowflake data."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize with Snowflake connection."""
        self.config = self._load_config(config_path)
        self.output_dir = Path("dashboards/screenshots")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self, config_path: str) -> dict:
        """Load Snowflake config."""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)['snowflake']
    
    def connect_snowflake(self):
        """Connect to Snowflake."""
        return snowflake.connector.connect(
            user=self.config['user'],
            password=self.config['password'],
            account=self.config['account'],
            warehouse=self.config['warehouse'],
            database=self.config['database'],
            insecure_mode=True
        )
    
    def query_data(self, query: str) -> pd.DataFrame:
        """Execute query and return DataFrame."""
        conn = self.connect_snowflake()
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    
    def chart_1_executive_kpis(self):
        """KPI Summary Card."""
        logger.info("Creating Chart 1: Executive KPIs...")
        
        query = """
        SELECT 
            SUM(TOTAL_REVENUE) as total_revenue,
            SUM(PROFIT) as total_profit,
            COUNT(DISTINCT SALES_KEY) as total_transactions,
            AVG(TOTAL_REVENUE) as avg_transaction,
            SUM(PROFIT) / SUM(TOTAL_REVENUE) * 100 as profit_margin_pct
        FROM MARTS_MARTS.FACT_SALES
        """
        
        df = self.query_data(query)
        
        fig, axes = plt.subplots(2, 3, figsize=(16, 8))
        fig.suptitle('Supply Chain Analytics - Executive KPIs', fontsize=20, fontweight='bold', y=0.98)
        
        # KPI 1: Total Revenue
        axes[0, 0].text(0.5, 0.6, f"${df['TOTAL_REVENUE'].iloc[0]:,.0f}", 
                       ha='center', va='center', fontsize=36, fontweight='bold', color=COLORS['primary'])
        axes[0, 0].text(0.5, 0.3, 'Total Revenue', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[0, 0].axis('off')
        
        # KPI 2: Total Profit
        axes[0, 1].text(0.5, 0.6, f"${df['TOTAL_PROFIT'].iloc[0]:,.0f}", 
                       ha='center', va='center', fontsize=36, fontweight='bold', color=COLORS['success'])
        axes[0, 1].text(0.5, 0.3, 'Total Profit', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[0, 1].axis('off')
        
        # KPI 3: Transactions
        axes[0, 2].text(0.5, 0.6, f"{int(df['TOTAL_TRANSACTIONS'].iloc[0]):,}", 
                       ha='center', va='center', fontsize=36, fontweight='bold', color=COLORS['secondary'])
        axes[0, 2].text(0.5, 0.3, 'Total Transactions', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[0, 2].axis('off')
        
        # KPI 4: Avg Transaction
        axes[1, 0].text(0.5, 0.6, f"${df['AVG_TRANSACTION'].iloc[0]:,.2f}", 
                       ha='center', va='center', fontsize=36, fontweight='bold', color=COLORS['warning'])
        axes[1, 0].text(0.5, 0.3, 'Avg Transaction Value', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[1, 0].axis('off')
        
        # KPI 5: Profit Margin
        axes[1, 1].text(0.5, 0.6, f"{df['PROFIT_MARGIN_PCT'].iloc[0]:.1f}%", 
                       ha='center', va='center', fontsize=36, fontweight='bold', color=COLORS['success'])
        axes[1, 1].text(0.5, 0.3, 'Profit Margin', 
                       ha='center', va='center', fontsize=14, color='gray')
        axes[1, 1].axis('off')
        
        # Info panel
        axes[1, 2].text(0.5, 0.7, '3 Months of Data', ha='center', fontsize=12, fontweight='bold')
        axes[1, 2].text(0.5, 0.5, 'Nov 2025 - Feb 2026', ha='center', fontsize=10, color='gray')
        axes[1, 2].text(0.5, 0.3, '100 Products | 10 Stores', ha='center', fontsize=10, color='gray')
        axes[1, 2].axis('off')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '01_executive_kpis.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 01_executive_kpis.png")
    
    def chart_2_revenue_trend(self):
        """Revenue trend over time."""
        logger.info("Creating Chart 2: Revenue Trend...")
        
        query = """
        SELECT 
            DATE_TRUNC('MONTH', s.SALE_DATE) as month,
            p.CATEGORY,
            SUM(s.TOTAL_REVENUE) as revenue
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_PRODUCTS p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        GROUP BY 1, 2
        ORDER BY 1, 2
        """
        
        df = self.query_data(query)
        df['MONTH'] = pd.to_datetime(df['MONTH'])
        
        plt.figure(figsize=(14, 6))
        
        for category in df['CATEGORY'].unique():
            cat_data = df[df['CATEGORY'] == category]
            plt.plot(cat_data['MONTH'], cat_data['REVENUE'], marker='o', linewidth=2.5, label=category)
        
        plt.title('Revenue Trend by Product Category', fontsize=18, fontweight='bold', pad=20)
        plt.xlabel('Month', fontsize=12, fontweight='bold')
        plt.ylabel('Revenue ($)', fontsize=12, fontweight='bold')
        plt.legend(title='Category', title_fontsize=11, fontsize=10, loc='best')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.savefig(self.output_dir / '02_revenue_trend.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 02_revenue_trend.png")
    
    def chart_3_category_performance(self):
        """Sales by category bar chart."""
        logger.info("Creating Chart 3: Category Performance...")
        
        query = """
        SELECT 
            p.CATEGORY,
            SUM(s.TOTAL_REVENUE) as revenue,
            SUM(s.PROFIT) as profit,
            COUNT(DISTINCT s.SALES_KEY) as transactions
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_PRODUCTS p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        GROUP BY 1
        ORDER BY 2 DESC
        """
        
        df = self.query_data(query)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Revenue by category
        axes[0].barh(df['CATEGORY'], df['REVENUE'], color=COLORS['primary'], alpha=0.8)
        axes[0].set_xlabel('Revenue ($)', fontsize=12, fontweight='bold')
        axes[0].set_title('Revenue by Category', fontsize=14, fontweight='bold')
        axes[0].grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(df['REVENUE']):
            axes[0].text(v, i, f' ${v:,.0f}', va='center', fontsize=10)
        
        # Profit by category
        axes[1].barh(df['CATEGORY'], df['PROFIT'], color=COLORS['success'], alpha=0.8)
        axes[1].set_xlabel('Profit ($)', fontsize=12, fontweight='bold')
        axes[1].set_title('Profit by Category', fontsize=14, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(df['PROFIT']):
            axes[1].text(v, i, f' ${v:,.0f}', va='center', fontsize=10)
        
        plt.suptitle('Category Performance Analysis', fontsize=18, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / '03_category_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 03_category_performance.png")
    
    def chart_4_top_products(self):
        """Top 10 products by revenue."""
        logger.info("Creating Chart 4: Top Products...")
        
        query = """
        SELECT 
            p.PRODUCT_NAME,
            p.CATEGORY,
            SUM(s.QUANTITY_SOLD) as units_sold,
            SUM(s.TOTAL_REVENUE) as revenue,
            SUM(s.PROFIT) as profit
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_PRODUCTS p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        GROUP BY 1, 2
        ORDER BY 4 DESC
        LIMIT 10
        """
        
        df = self.query_data(query)
        
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Create bars
        bars = ax.barh(range(len(df)), df['REVENUE'], color=COLORS['primary'], alpha=0.8)
        
        # Color code by category
        category_colors = {cat: COLORS[key] for cat, key in zip(
            df['CATEGORY'].unique(), ['primary', 'success', 'warning', 'secondary', 'danger']
        )}
        for i, (idx, row) in enumerate(df.iterrows()):
            bars[i].set_color(category_colors.get(row['CATEGORY'], COLORS['primary']))
        
        ax.set_yticks(range(len(df)))
        ax.set_yticklabels([name[:40] + '...' if len(name) > 40 else name for name in df['PRODUCT_NAME']], fontsize=10)
        ax.set_xlabel('Revenue ($)', fontsize=12, fontweight='bold')
        ax.set_title('Top 10 Products by Revenue', fontsize=18, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, v in enumerate(df['REVENUE']):
            ax.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)
        
        # Legend for categories
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor=category_colors[cat], label=cat) 
                          for cat in df['CATEGORY'].unique()]
        ax.legend(handles=legend_elements, title='Category', loc='lower right', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '04_top_products.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 04_top_products.png")
    
    def chart_5_store_performance(self):
        """Store performance analysis."""
        logger.info("Creating Chart 5: Store Performance...")
        
        query = """
        SELECT 
            st.STORE_TYPE,
            st.REGION,
            SUM(s.TOTAL_REVENUE) as revenue,
            SUM(s.PROFIT) as profit,
            COUNT(DISTINCT s.SALES_KEY) as transactions
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_STORES st ON s.STORE_KEY = st.STORE_KEY
        GROUP BY 1, 2
        ORDER BY 3 DESC
        """
        
        df = self.query_data(query)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Revenue by store type
        store_type_revenue = df.groupby('STORE_TYPE')['REVENUE'].sum().sort_values(ascending=False)
        colors_list = [COLORS['primary'], COLORS['success'], COLORS['warning']]
        axes[0].pie(store_type_revenue.values, labels=store_type_revenue.index, autopct='%1.1f%%',
                   colors=colors_list, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        axes[0].set_title('Revenue by Store Type', fontsize=14, fontweight='bold')
        
        # Revenue by region
        region_revenue = df.groupby('REGION')['REVENUE'].sum().sort_values(ascending=True)
        axes[1].barh(region_revenue.index, region_revenue.values, color=COLORS['secondary'], alpha=0.8)
        axes[1].set_xlabel('Revenue ($)', fontsize=12, fontweight='bold')
        axes[1].set_title('Revenue by Region', fontsize=14, fontweight='bold')
        axes[1].grid(axis='x', alpha=0.3)
        
        for i, v in enumerate(region_revenue.values):
            axes[1].text(v, i, f' ${v:,.0f}', va='center', fontsize=10)
        
        plt.suptitle('Store & Regional Performance', fontsize=18, fontweight='bold', y=1.02)
        plt.tight_layout()
        plt.savefig(self.output_dir / '05_store_performance.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 05_store_performance.png")
    
    def chart_6_profit_analysis(self):
        """Profit margin analysis."""
        logger.info("Creating Chart 6: Profit Analysis...")
        
        query = """
        SELECT 
            p.CATEGORY,
            p.SUBCATEGORY,
            SUM(s.TOTAL_REVENUE) as revenue,
            SUM(s.PROFIT) as profit,
            SUM(s.PROFIT) / NULLIF(SUM(s.TOTAL_REVENUE), 0) * 100 as profit_margin_pct
        FROM MARTS_MARTS.FACT_SALES s
        JOIN MARTS_MARTS.DIM_PRODUCTS p ON s.PRODUCT_KEY = p.PRODUCT_KEY
        GROUP BY 1, 2
        HAVING SUM(s.TOTAL_REVENUE) > 10000
        ORDER BY 5 DESC
        LIMIT 15
        """
        
        df = self.query_data(query)
        
        plt.figure(figsize=(14, 8))
        
        # Create scatter plot
        scatter = plt.scatter(df['REVENUE'], df['PROFIT_MARGIN_PCT'], 
                            s=df['PROFIT']/50, alpha=0.6, 
                            c=range(len(df)), cmap='viridis')
        
        # Add labels for top performers
        for idx, row in df.head(5).iterrows():
            plt.annotate(row['SUBCATEGORY'], 
                        xy=(row['REVENUE'], row['PROFIT_MARGIN_PCT']),
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
        
        plt.xlabel('Revenue ($)', fontsize=12, fontweight='bold')
        plt.ylabel('Profit Margin (%)', fontsize=12, fontweight='bold')
        plt.title('Profit Margin vs Revenue (Bubble size = Profit)', fontsize=18, fontweight='bold', pad=20)
        plt.grid(True, alpha=0.3)
        
        # Add reference lines
        plt.axhline(y=df['PROFIT_MARGIN_PCT'].mean(), color='red', linestyle='--', 
                   linewidth=1.5, alpha=0.7, label=f"Avg Margin: {df['PROFIT_MARGIN_PCT'].mean():.1f}%")
        plt.legend(fontsize=10)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / '06_profit_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        logger.info("✅ Saved: 06_profit_analysis.png")
    
    def generate_all_charts(self):
        """Generate all visualizations."""
        logger.info("\n🎨 Starting visualization generation...")
        logger.info(f"Output directory: {self.output_dir}\n")
        
        self.chart_1_executive_kpis()
        self.chart_2_revenue_trend()
        self.chart_3_category_performance()
        self.chart_4_top_products()
        self.chart_5_store_performance()
        self.chart_6_profit_analysis()
        
        logger.info("\n✅ ✅ ✅ ALL CHARTS GENERATED! ✅ ✅ ✅")
        logger.info(f"\n📁 Saved 6 charts to: {self.output_dir}")
        logger.info("\nCharts created:")
        logger.info("  1. Executive KPIs (summary dashboard)")
        logger.info("  2. Revenue Trend (line chart)")
        logger.info("  3. Category Performance (bar charts)")
        logger.info("  4. Top 10 Products (horizontal bar)")
        logger.info("  5. Store Performance (pie + bar)")
        logger.info("  6. Profit Analysis (scatter plot)")
        logger.info("\n🚀 Ready to add to GitHub!")


if __name__ == "__main__":
    visualizer = SupplyChainVisualizer()
    visualizer.generate_all_charts()
