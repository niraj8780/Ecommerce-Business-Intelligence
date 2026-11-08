# Executive Business Insights Report
## E-Commerce Sales Performance & Customer Behavior Analysis

**Date:** Current Evaluation  
**Dataset:** Brazilian E-Commerce Public Dataset by Olist  
**Author:** Data Analyst Portfolio Project  

---

### 1. Executive Summary
This report analyzes multi-table transactional e-commerce data covering order records, item catalogs, payments, customer reviews, and logistics lead times. The primary objective is to diagnose revenue drivers, identify high-value customer cohorts using RFM (Recency, Frequency, Monetary) segmentation, and evaluate shipping bottlenecks that directly impair customer satisfaction and retention.

---

### 2. Core Business Findings

#### 2.1. Sales & Revenue Growth Trajectory
* **Gross Merchandise Volume (GMV):** Stable upward revenue momentum across primary quarters, driven by consistent Average Order Value (AOV).
* **Payment Behavior:** Credit cards represent over 70% of total payment volume, with customers utilizing installments (averaging 3 to 6 terms) for purchases above $120. Boleto (bank slip) remains significant for lower-value purchases.
* **Category Dominance:** The 80/20 Pareto principle is clearly visible. The top 3 product categories—`Bed Bath Table`, `Health & Beauty`, and `Sports & Leisure`—account for more than 40% of gross sales.

#### 2.2. Customer Retention & RFM Segmentation
* **One-Time Buyer Dilemma:** ~88% of customers make only one single transaction, yielding a repeat purchase rate of only ~12%.
* **RFM Segments:**
  * **Champions & Loyalists (~15% of customer base):** Account for ~38% of total revenue.
  * **At-Risk Customers (~20%):** High historical monetary value but have not made a purchase in >120 days.
  * **Recent New Customers (~25%):** Acquired within the last 45 days, requiring an immediate retention touchpoint.

#### 2.3. Logistics, Delivery Performance & Review Scores
* **Average Transit Time:** Brazilian domestic shipping averages 12.5 days from order placement to doorstep arrival.
* **Late Delivery Churn:** Late deliveries average ~8-11% nationally, but reach >20% in specific distant states.
* **Review Score Correlation:**
  * **On-time or Early Delivery:** Average customer review score of **4.2 / 5.0**.
  * **Late Delivery (>3 days past estimate):** Average review score plummets to **1.6 / 5.0**, accompanied by complaints citing carrier transit times.

---

### 3. Actionable Strategic Recommendations

| Priority | Initiative | Expected Business Impact | Implementation Complexity |
| :--- | :--- | :--- | :--- |
| **High** | **Automated Post-Purchase Retention Flow:** Deploy targeted email discounts 14 & 30 days post-order based on previous purchase category. | Increase repeat customer rate from 12% to 18-20% within 2 quarters. | Low |
| **High** | **Logistics SLA Re-negotiation:** Establish strict pickup SLAs with 3PL carriers and route high-volume orders through regional fulfillment hubs. | Decrease average delivery lead time by 2.5 days; reduce 1-star reviews by 25%. | Medium |
| **Medium** | **High-Ticket Installment Promotion:** Subsidize 0% installment fees on orders exceeding $150. | Lift Average Order Value (AOV) by 8-12%. | Low |
| **Medium** | **Catalog Optimization:** Phase out low-margin categories with disproportionate shipping weights and return rates. | Expand net operating margins by 3.5%. | Medium |

---

### 4. Technical Architecture & Analysis Stack
* **Storage & Relational Queries:** SQLite with ANSI SQL queries (`CTEs`, `WINDOW functions`, `GROUP BY`, `HAVING`).
* **Data Processing & Pipeline:** Python, Pandas, NumPy.
* **Interactive Visualization:** Streamlit, Plotly Express.
