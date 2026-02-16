# Power BI Dashboard Guide

**Building Executive Dashboards for Supply Chain Analytics**

---

## 🎯 Dashboard Overview

Create 3 interactive Power BI pages to showcase your analytics skills.

---

## 📊 Dashboard 1: Executive Overview

### KPI Cards (Top Row)
- **Total Revenue**: `SUM(fact_sales[TOTAL_REVENUE])`
- **Total Profit**: `SUM(fact_sales[PROFIT])`
- **Avg Transaction**: `AVERAGE(fact_sales[TOTAL_REVENUE])`
- **Total Transactions**: `COUNT(fact_sales[SALES_KEY])`

### Visualizations

**1. Revenue Trend (Line Chart)**
- X-axis: `fact_sales[SALE_DATE]`
- Y-axis: `SUM(fact_sales[TOTAL_REVENUE])`
- Legend: `dim_products[CATEGORY]`

**2. Sales by Category (Bar Chart)**
- Axis: `dim_products[CATEGORY]`
- Values: `SUM(fact_sales[TOTAL_REVENUE])`
- Sort: Descending by revenue

**3. Top 10 Products (Table)**
- Columns:
  - `dim_products[PRODUCT_NAME]`
  - `SUM(fact_sales[QUANTITY_SOLD])`
  - `SUM(fact_sales[TOTAL_REVENUE])`
  - `SUM(fact_sales[PROFIT])`
- Sort: By revenue descending
- Top N filter: 10

**4. Profit Margin by Category (Column Chart)**
- Axis: `dim_products[CATEGORY]`
- Values: Custom DAX Measure:
  ```dax
  Profit Margin % = 
  DIVIDE(
      SUM(fact_sales[PROFIT]),
      SUM(fact_sales[TOTAL_REVENUE]),
      0
  ) * 100
  ```

---

## 📦 Dashboard 2: Product & Store Performance

### Visualizations

**1. Sales by Store Type (Donut Chart)**
- Legend: `dim_stores[STORE_TYPE]`
- Values: `SUM(fact_sales[TOTAL_REVENUE])`

**2. Regional Performance (Map)**
- Location: `dim_stores[STATE]`
- Size: `SUM(fact_sales[TOTAL_REVENUE])`
- Color: `SUM(fact_sales[PROFIT])`

**3. Product Performance Matrix**
- Rows: `dim_products[CATEGORY]`
- Columns: `dim_stores[REGION]`
- Values: `SUM(fact_sales[TOTAL_REVENUE])`
- Conditional formatting: Color scale

**4. Discount Impact**
- X-axis: `fact_sales[DISCOUNT_PCT]` (custom measure)
- Y-axis: `SUM(fact_sales[QUANTITY_SOLD])`
- Scatter plot with trend line

---

## 📅 Dashboard 3: Time Intelligence

### DAX Measures

**Month-over-Month Growth:**
```dax
MoM Growth % = 
VAR CurrentMonth = SUM(fact_sales[TOTAL_REVENUE])
VAR PreviousMonth = 
    CALCULATE(
        SUM(fact_sales[TOTAL_REVENUE]),
        DATEADD(dim_date[CALENDAR_DATE], -1, MONTH)
    )
RETURN
    DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0) * 100
```

**Year-to-Date Revenue:**
```dax
YTD Revenue = 
TOTALYTD(
    SUM(fact_sales[TOTAL_REVENUE]),
    dim_date[CALENDAR_DATE]
)
```

### Visualizations

**1. Monthly Trends (Line + Column Chart)**
- X-axis: `dim_date[MONTH_NAME]`
- Column: `SUM(fact_sales[TOTAL_REVENUE])`
- Line: `MoM Growth %` (custom measure)

**2. Weekday vs Weekend (Bar Chart)**
- Axis: `dim_date[IS_WEEKEND]`
- Values: `SUM(fact_sales[TOTAL_REVENUE])`

**3. Holiday Season Impact**
- Axis: `dim_date[IS_HOLIDAY_SEASON]`
- Values: `SUM(fact_sales[TOTAL_REVENUE])`
- Comparison with non-holiday periods

---

## 🔗 Connecting to Snowflake

### Step 1: Get Data
1. Open Power BI Desktop
2. Get Data → Snowflake
3. Enter connection details:
   - Server: `VYUVIGG-RVB11850.snowflakecomputing.com`
   - Warehouse: `COMPUTE_WH`
   - Database: `SUPPLY_CHAIN_ANALYTICS`

### Step 2: Import Tables
Import these tables from `MARTS_MARTS` schema:
- `FACT_SALES`
- `DIM_PRODUCTS`
- `DIM_STORES`
- `DIM_DATE`

### Step 3: Create Relationships
Power BI should auto-detect, but verify:
- `fact_sales[PRODUCT_KEY]` → `dim_products[PRODUCT_KEY]` (Many-to-One)
- `fact_sales[STORE_KEY]` → `dim_stores[STORE_KEY]` (Many-to-One)
- `fact_sales[DATE_KEY]` → `dim_date[DATE_KEY]` (Many-to-One)

---

## 🎨 Design Tips

### Color Scheme
- Primary: Blues and greens (professional)
- Revenue: Green shades
- Profit: Blue shades
- Alerts/Issues: Orange/Red

### Best Practices
1. **Keep it simple** - Max 4-5 visuals per page
2. **Use white space** - Don't cram everything
3. **Consistent formatting** - Same fonts, colors
4. **Add tooltips** - Hover details for more info
5. **Mobile-friendly** - Test on phone layout

### Filters/Slicers
Add these slicers for interactivity:
- Date range picker
- Product category dropdown
- Store region dropdown
- Store type (Retail, Online, Warehouse)

---

## 📸 Taking Screenshots

For your GitHub/Portfolio:

1. **Full page screenshots** - Show complete dashboards
2. **Specific visuals** - Highlight interesting insights
3. **Before/after filters** - Show interactivity
4. **Mobile view** - Prove responsive design

Save as PNG, add to `dashboards/screenshots/` folder.

---

## 🚀 Publishing Options

### Option 1: Power BI Service (Free)
- Publish to workspace
- Share view-only link
- Embed in portfolio website

### Option 2: Export to PDF
- File → Export → PDF
- Include in GitHub repo
- Show in interviews

### Option 3: Screenshots Only
- Capture key visuals
- Add to README
- Portfolio website

---

## ✅ Dashboard Checklist

- [ ] Connected to Snowflake MARTS_MARTS schema
- [ ] Imported all 4 tables
- [ ] Verified relationships
- [ ] Created DAX measures (profit margin, MoM growth)
- [ ] Built 3 dashboard pages
- [ ] Added slicers/filters
- [ ] Tested interactivity
- [ ] Took screenshots
- [ ] Saved .pbix file to `dashboards/` folder

---

**Time Estimate:** 2-3 hours to build all 3 dashboards

**Next:** Take screenshots → Update README → Push to GitHub!
