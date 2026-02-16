# 🚀 Tableau Quick Start - Copy This!

**Quick reference while building dashboards**

---

## 🔗 Snowflake Connection Info (COPY THESE)

```
Server: VYUVIGG-RVB11850.snowflakecomputing.com
Username: Deepthi
Password: DeepthiD2211@7893190472
Warehouse: COMPUTE_WH
Database: SUPPLY_CHAIN_ANALYTICS
Schema: MARTS_MARTS
```

---

## 📊 Tables to Import

☑️ **FACT_SALES** (main table - 18,226 rows)  
☑️ **DIM_PRODUCTS** (100 products)  
☑️ **DIM_STORES** (10 stores)  
☑️ **DIM_DATE** (730 dates)  

**Joins:** Tableau will auto-detect based on key names!

---

## 🎨 Dashboard 1: Executive Overview (Build This First!)

### KPI Cards (Top Row - 4 cards)

**Card 1: Total Revenue**
- Drag: `Total Revenue` → Text
- Format: Currency, $12.2M
- Font size: 48pt

**Card 2: Total Profit**
- Drag: `Profit` → Text  
- Format: Currency, $5.8M
- Font size: 48pt

**Card 3: Transaction Count**
- Drag: `Sales Key` → Text
- Change to: COUNT(DISTINCT)
- Shows: 18,226

**Card 4: Avg Transaction**
- Create Calculated Field:
  - Name: `Avg Transaction`
  - Formula: `SUM([Total Revenue]) / COUNTD([Sales Key])`
- Format: Currency, $667

---

### Chart 1: Revenue Trend Line

**Steps:**
1. Drag `Sale Date` → Columns
2. Click dropdown → Select "Month"
3. Drag `Total Revenue` → Rows
4. Drag `Category` → Color (from dim_products)
5. Right-click chart → Add Trend Line

**Result:** Multi-colored line chart showing revenue over time

---

### Chart 2: Sales by Category (Bar Chart)

**Steps:**
1. Drag `Category` → Rows
2. Drag `Total Revenue` → Columns
3. Sort descending (click toolbar sort icon)
4. Drag `Total Revenue` → Color (creates gradient)
5. Show labels: Click "Show Mark Labels" button

**Result:** Horizontal bars sorted by revenue

---

### Chart 3: Top 10 Products (Table)

**Steps:**
1. Drag `Product Name` → Rows
2. Drag these to Columns (in order):
   - `Quantity Sold` (SUM)
   - `Total Revenue` (SUM)
   - `Profit` (SUM)
3. Add Filter:
   - Right-click `Product Name` → Filter
   - Top tab → By field
   - Top 10 by `Total Revenue`
4. Format numbers:
   - Revenue & Profit: Currency
   - Quantity: Whole number

**Result:** Clean table with top performers

---

## 🎨 Calculated Fields You'll Need

**Copy-paste these formulas:**

### Profit Margin %
```
Name: Profit Margin %
Formula: SUM([Profit]) / SUM([Total Revenue]) * 100
```

### Is Weekend
```
Name: Is Weekend  
Formula: IF DATEPART('weekday', [Sale Date]) IN (1, 7) THEN "Weekend" ELSE "Weekday" END
```

### Avg Transaction
```
Name: Avg Transaction
Formula: SUM([Total Revenue]) / COUNTD([Sales Key])
```

---

## 🎨 Color Palette (Copy These Hex Codes)

**Use these for consistency:**

- **Primary Blue:** #1F77B4
- **Success Green:** #2CA02C  
- **Revenue Orange:** #FF7F0E
- **Profit Purple:** #9467BD
- **Alert Red:** #D62728

---

## 📐 Dashboard Layout Settings

**Dashboard Size:**
- Desktop: 1600 x 900 px (best for screenshots)
- OR Automatic (responsive)

**Background:** White (#FFFFFF)

**Titles:**
- Font: Arial
- Size: 18pt (dashboard title), 14pt (chart titles)
- Color: Dark gray (#333333)

---

## 🎯 Quick Wins (If Short on Time)

**Minimum Viable Dashboard (30 minutes):**

Build just these 5:
1. Revenue KPI card
2. Profit KPI card  
3. Revenue trend line
4. Category bar chart
5. Top 10 products table

Arrange on one dashboard → Screenshot → Done!

**Still proves Tableau skills!**

---

## 📸 Screenshot Checklist

When ready to screenshot:

- [ ] Full dashboard view
- [ ] Clear, high resolution
- [ ] All text readable
- [ ] Filters visible (if you added them)
- [ ] Save as: `dashboards/screenshots/executive_tableau.png`

---

## ✅ Publishing to Tableau Public

**Steps:**
1. File → Save to Tableau Public As...
2. Sign in (create account with deepthid2211@gmail.com)
3. Workbook name: `Supply Chain Analytics Platform`
4. Description: "Supply chain analytics with Snowflake + dbt + ML"
5. Tags: supply-chain, analytics, snowflake, dbt
6. Click Save
7. **COPY THE PUBLIC LINK!**
   - You'll get: `https://public.tableau.com/profile/[username]/viz/[workbook]`
   - Save this for README!

---

## 🚨 Common Issues & Fixes

**Issue: Can't connect to Snowflake**
- Check: Warehouse running in Snowflake UI
- Try: Add full server address with `.snowflakecomputing.com`
- Verify: Username/password (case-sensitive!)

**Issue: Joins not working**
- Use: "Left Join" from FACT_SALES to dimension tables
- Match: `PRODUCT_KEY` to `PRODUCT_KEY`, etc.

**Issue: Numbers look wrong**
- Check: Aggregation (SUM vs AVG vs COUNT)
- Format: Right-click → Format → Number

**Issue: Charts look messy**
- Solution: Start simple, add one element at a time
- Use: "Show Me" panel for chart type suggestions

---

## ⏱️ Time Budget

- **Connection:** 10 min
- **KPI Cards:** 15 min
- **Charts:** 30 min
- **Dashboard Layout:** 15 min
- **Publishing:** 10 min
- **Screenshots:** 10 min

**Total:** ~90 minutes for solid dashboard!

---

**You got this! 🎨**

Follow the steps in order, take your time, and ask Echo if you get stuck!
