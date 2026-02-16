"""
Synthetic Supply Chain Data Generator
======================================

Generates realistic multi-channel retail/e-commerce data for analytics.
Creates sales transactions, inventory snapshots, vendor shipments.

Author: Deepthi Desharaju
Date: February 2026
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from faker import Faker
import random
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
Faker.seed(42)
np.random.seed(42)
random.seed(42)


class SupplyChainDataGenerator:
    """
    Generates synthetic supply chain data for retail/e-commerce analytics.
    """
    
    # Product categories and subcategories
    CATEGORIES = {
        'Electronics': ['Laptops', 'Phones', 'Tablets', 'Accessories'],
        'Clothing': ['Men', 'Women', 'Kids', 'Shoes'],
        'Home & Kitchen': ['Furniture', 'Appliances', 'Decor', 'Cookware'],
        'Sports': ['Equipment', 'Apparel', 'Outdoor', 'Fitness'],
        'Books': ['Fiction', 'Non-Fiction', 'Textbooks', 'Children']
    }
    
    BRANDS = [
        'TechPro', 'StyleMax', 'HomeEssentials', 'ActiveLife', 'ReadMore',
        'InnovateTech', 'FashionForward', 'ComfortHome', 'SportElite', 'BookNook'
    ]
    
    STORE_TYPES = ['Retail', 'Online', 'Warehouse']
    
    US_REGIONS = ['Northeast', 'Southeast', 'Midwest', 'Southwest', 'West']
    
    def __init__(self, num_products=1000, num_stores=50, num_vendors=20):
        """
        Initialize data generator.
        
        Args:
            num_products: Number of unique SKUs to generate
            num_stores: Number of store locations
            num_vendors: Number of vendor/suppliers
        """
        self.num_products = num_products
        self.num_stores = num_stores
        self.num_vendors = num_vendors
        
        # Master data
        self.products = None
        self.stores = None
        self.vendors = None
        self.customers = None
        
    def generate_products(self) -> pd.DataFrame:
        """Generate product master data."""
        logger.info(f"Generating {self.num_products} products...")
        
        products = []
        for i in range(self.num_products):
            category = random.choice(list(self.CATEGORIES.keys()))
            subcategory = random.choice(self.CATEGORIES[category])
            brand = random.choice(self.BRANDS)
            
            # Generate SKU
            sku = f"{category[:3].upper()}{subcategory[:3].upper()}{i:04d}"
            
            # Pricing based on category
            if category == 'Electronics':
                unit_cost = round(random.uniform(50, 800), 2)
            elif category == 'Clothing':
                unit_cost = round(random.uniform(10, 150), 2)
            elif category == 'Home & Kitchen':
                unit_cost = round(random.uniform(20, 500), 2)
            else:
                unit_cost = round(random.uniform(5, 100), 2)
            
            unit_price = round(unit_cost * random.uniform(1.3, 2.5), 2)  # Markup
            
            products.append({
                'product_id': i + 1,
                'sku': sku,
                'product_name': f"{brand} {subcategory} {fake.color_name()}",
                'category': category,
                'subcategory': subcategory,
                'brand': brand,
                'unit_cost': unit_cost,
                'unit_price': unit_price,
                'supplier': f"Vendor {random.randint(1, self.num_vendors)}"
            })
        
        self.products = pd.DataFrame(products)
        return self.products
    
    def generate_stores(self) -> pd.DataFrame:
        """Generate store master data."""
        logger.info(f"Generating {self.num_stores} stores...")
        
        stores = []
        for i in range(self.num_stores):
            region = random.choice(self.US_REGIONS)
            store_type = random.choice(self.STORE_TYPES)
            
            stores.append({
                'store_id': i + 1,
                'store_name': f"Store {i + 1:03d}",
                'store_type': store_type,
                'region': region,
                'city': fake.city(),
                'state': fake.state_abbr(),
                'opened_date': fake.date_between(start_date='-5y', end_date='-1y')
            })
        
        self.stores = pd.DataFrame(stores)
        return self.stores
    
    def generate_vendors(self) -> pd.DataFrame:
        """Generate vendor master data."""
        logger.info(f"Generating {self.num_vendors} vendors...")
        
        vendors = []
        for i in range(self.num_vendors):
            vendors.append({
                'vendor_id': i + 1,
                'vendor_name': fake.company(),
                'vendor_country': random.choice(['USA', 'China', 'Germany', 'Japan', 'Mexico']),
                'avg_lead_time_days': random.randint(3, 30),
                'reliability_score': round(random.uniform(70, 99), 1)
            })
        
        self.vendors = pd.DataFrame(vendors)
        return self.vendors
    
    def generate_sales(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Generate sales transactions.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            DataFrame of sales transactions
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        days = (end - start).days
        
        logger.info(f"Generating sales data for {days} days...")
        
        sales = []
        transaction_id = 1
        
        # Generate daily sales
        for day in range(days):
            current_date = start + timedelta(days=day)
            
            # More sales on weekends
            is_weekend = current_date.weekday() >= 5
            base_transactions = 200 if is_weekend else 150
            
            # Seasonal boost (Q4 holidays)
            if current_date.month in [11, 12]:
                base_transactions = int(base_transactions * 1.5)
            
            # Random variation
            num_transactions = int(base_transactions * random.uniform(0.8, 1.2))
            
            for _ in range(num_transactions):
                product = self.products.sample(1).iloc[0]
                store = self.stores.sample(1).iloc[0]
                
                quantity = random.choices(
                    [1, 2, 3, 4, 5],
                    weights=[50, 25, 15, 7, 3]
                )[0]
                
                # Discount probability
                has_discount = random.random() < 0.15  # 15% of sales have discount
                discount_pct = random.uniform(0.05, 0.3) if has_discount else 0
                
                unit_price = product['unit_price']
                discount_amount = round(unit_price * discount_pct * quantity, 2)
                total_revenue = round(unit_price * quantity - discount_amount, 2)
                cost_of_goods = round(product['unit_cost'] * quantity, 2)
                profit = round(total_revenue - cost_of_goods, 2)
                
                sales.append({
                    'transaction_id': transaction_id,
                    'sale_date': current_date.strftime('%Y-%m-%d'),
                    'product_id': product['product_id'],
                    'store_id': store['store_id'],
                    'customer_segment': random.choice(['Regular', 'Premium', 'VIP']),
                    'quantity_sold': quantity,
                    'unit_price': unit_price,
                    'discount_amount': discount_amount,
                    'total_revenue': total_revenue,
                    'cost_of_goods': cost_of_goods,
                    'profit': profit
                })
                
                transaction_id += 1
        
        logger.info(f"Generated {len(sales)} sales transactions")
        return pd.DataFrame(sales)
    
    def generate_inventory_snapshots(self, date: str) -> pd.DataFrame:
        """
        Generate inventory snapshot for a specific date.
        
        Args:
            date: Date for snapshot (YYYY-MM-DD)
            
        Returns:
            DataFrame of inventory levels
        """
        logger.info(f"Generating inventory snapshot for {date}...")
        
        inventory = []
        
        for _, product in self.products.iterrows():
            for _, store in self.stores.iterrows():
                # Base inventory level depends on product category
                if product['category'] == 'Electronics':
                    base_units = random.randint(10, 100)
                elif product['category'] == 'Clothing':
                    base_units = random.randint(20, 200)
                else:
                    base_units = random.randint(15, 150)
                
                units_on_hand = max(0, int(base_units * random.uniform(0.5, 1.5)))
                units_on_order = random.randint(0, 50) if units_on_hand < base_units * 0.3 else 0
                
                reorder_point = int(base_units * 0.2)
                safety_stock = int(reorder_point * 0.5)
                
                # Calculate days of supply (assuming avg 5 units sold per day)
                daily_demand = 5
                days_of_supply = units_on_hand / daily_demand if daily_demand > 0 else 0
                
                inventory.append({
                    'snapshot_date': date,
                    'product_id': product['product_id'],
                    'store_id': store['store_id'],
                    'units_on_hand': units_on_hand,
                    'units_on_order': units_on_order,
                    'reorder_point': reorder_point,
                    'safety_stock': safety_stock,
                    'days_of_supply': round(days_of_supply, 1)
                })
        
        logger.info(f"Generated {len(inventory)} inventory records")
        return pd.DataFrame(inventory)
    
    def save_to_csv(self, output_dir: str = "data/raw"):
        """Save all generated data to CSV files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.products.to_csv(output_path / 'products.csv', index=False)
        self.stores.to_csv(output_path / 'stores.csv', index=False)
        self.vendors.to_csv(output_path / 'vendors.csv', index=False)
        
        logger.info(f"All data saved to {output_dir}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Generate synthetic supply chain data'
    )
    parser.add_argument(
        '--months',
        type=int,
        default=24,
        help='Number of months of sales data to generate (default: 24)'
    )
    parser.add_argument(
        '--products',
        type=int,
        default=1000,
        help='Number of products/SKUs (default: 1000)'
    )
    parser.add_argument(
        '--stores',
        type=int,
        default=50,
        help='Number of stores (default: 50)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw',
        help='Output directory for CSV files (default: data/raw)'
    )
    
    args = parser.parse_args()
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.months * 30)
    
    # Initialize generator
    generator = SupplyChainDataGenerator(
        num_products=args.products,
        num_stores=args.stores,
        num_vendors=20
    )
    
    # Generate master data
    generator.generate_products()
    generator.generate_stores()
    generator.generate_vendors()
    
    # Generate transactional data
    sales_df = generator.generate_sales(
        start_date=start_date.strftime('%Y-%m-%d'),
        end_date=end_date.strftime('%Y-%m-%d')
    )
    
    # Generate current inventory snapshot
    inventory_df = generator.generate_inventory_snapshots(
        date=end_date.strftime('%Y-%m-%d')
    )
    
    # Save to CSV
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    generator.products.to_csv(output_path / 'products.csv', index=False)
    generator.stores.to_csv(output_path / 'stores.csv', index=False)
    generator.vendors.to_csv(output_path / 'vendors.csv', index=False)
    sales_df.to_csv(output_path / 'sales.csv', index=False)
    inventory_df.to_csv(output_path / 'inventory_snapshot.csv', index=False)
    
    # Summary statistics
    logger.info("\n=== Data Generation Summary ===")
    logger.info(f"Products: {len(generator.products)}")
    logger.info(f"Stores: {len(generator.stores)}")
    logger.info(f"Vendors: {len(generator.vendors)}")
    logger.info(f"Sales Transactions: {len(sales_df)}")
    logger.info(f"Inventory Records: {len(inventory_df)}")
    logger.info(f"\nTotal Revenue: ${sales_df['total_revenue'].sum():,.2f}")
    logger.info(f"Total Profit: ${sales_df['profit'].sum():,.2f}")
    logger.info(f"Avg Transaction Value: ${sales_df['total_revenue'].mean():.2f}")
    logger.info(f"\nFiles saved to: {output_path}")


if __name__ == "__main__":
    main()
