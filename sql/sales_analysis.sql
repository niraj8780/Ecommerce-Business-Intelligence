-- ====================================================================
-- SALES PERFORMANCE ANALYSIS
-- Business Questions:
-- 1. What is the total gross revenue, order volume, and Average Order Value (AOV)?
-- 2. What is the monthly revenue trajectory and month-over-month (MoM) growth?
-- 3. Which product categories generate the highest revenue?
-- 4. How are customers paying, and what is the credit installment breakdown?
-- ====================================================================

-- 1. Executive Sales KPIs
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    ROUND(SUM(oi.price), 2) AS total_product_revenue,
    ROUND(SUM(oi.freight_value), 2) AS total_freight_revenue,
    ROUND(SUM(oi.price + oi.freight_value), 2) AS gross_merchandise_value,
    ROUND(AVG(order_totals.order_value), 2) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN (
    SELECT order_id, SUM(price + freight_value) AS order_value
    FROM order_items
    GROUP BY order_id
) order_totals ON o.order_id = order_totals.order_id
WHERE o.order_status = 'delivered';


-- 2. Monthly Revenue Trend & Month-over-Month (MoM) Growth Rate
WITH monthly_sales AS (
    SELECT 
        strftime('%Y-%m', o.order_purchase_timestamp) AS year_month,
        COUNT(DISTINCT o.order_id) AS orders_count,
        ROUND(SUM(oi.price), 2) AS monthly_revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY strftime('%Y-%m', o.order_purchase_timestamp)
)
SELECT 
    year_month,
    orders_count,
    monthly_revenue,
    LAG(monthly_revenue, 1) OVER (ORDER BY year_month) AS previous_month_revenue,
    ROUND(
        (monthly_revenue - LAG(monthly_revenue, 1) OVER (ORDER BY year_month)) * 100.0 / 
        NULLIF(LAG(monthly_revenue, 1) OVER (ORDER BY year_month), 0), 
        2
    ) AS mom_growth_pct
FROM monthly_sales
ORDER BY year_month;


-- 3. Top 10 Revenue-Generating Product Categories
SELECT 
    COALESCE(p.product_category_name, 'Uncategorized') AS category,
    COUNT(DISTINCT oi.order_id) AS order_volume,
    COUNT(oi.product_id) AS items_sold,
    ROUND(SUM(oi.price), 2) AS total_revenue,
    ROUND(AVG(oi.price), 2) AS average_item_price,
    ROUND(SUM(oi.price) * 100.0 / (SELECT SUM(price) FROM order_items), 2) AS pct_of_total_revenue
FROM order_items oi
LEFT JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;


-- 4. Payment Method Breakdown & Installment Patterns
SELECT 
    payment_type,
    COUNT(DISTINCT order_id) AS transaction_count,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS avg_transaction_value,
    ROUND(AVG(payment_installments), 1) AS avg_installments
FROM order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- 5. Peak Sales Hours & Weekly Purchase Patterns
SELECT 
    strftime('%w', order_purchase_timestamp) AS day_of_week, -- 0=Sunday, 6=Saturday
    strftime('%H', order_purchase_timestamp) AS hour_of_day,
    COUNT(order_id) AS total_orders
FROM orders
WHERE order_status = 'delivered'
GROUP BY day_of_week, hour_of_day
ORDER BY total_orders DESC
LIMIT 15;
