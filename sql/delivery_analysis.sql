-- ====================================================================
-- DELIVERY & LOGISTICS OPERATIONS ANALYSIS
-- Business Questions:
-- 1. What is the average delivery time across Brazil?
-- 2. What percentage of orders are delivered late compared to estimated dates?
-- 3. Which states have the longest shipping delays?
-- 4. How does delivery delay directly impact customer review scores?
-- ====================================================================

-- 1. Overall Delivery Performance KPIs
SELECT 
    COUNT(order_id) AS total_delivered_orders,
    ROUND(AVG(JULIANDAY(order_delivered_customer_date) - JULIANDAY(order_purchase_timestamp)), 1) AS avg_delivery_time_days,
    ROUND(AVG(JULIANDAY(order_estimated_delivery_date) - JULIANDAY(order_delivered_customer_date)), 1) AS avg_days_ahead_of_estimate,
    SUM(CASE WHEN JULIANDAY(order_delivered_customer_date) > JULIANDAY(order_estimated_delivery_date) THEN 1 ELSE 0 END) AS late_deliveries_count,
    ROUND(
        SUM(CASE WHEN JULIANDAY(order_delivered_customer_date) > JULIANDAY(order_estimated_delivery_date) THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(order_id), 
        2
    ) AS late_delivery_rate_pct
FROM orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NOT NULL;


-- 2. Delivery Time & Delay Rates by Customer State
SELECT 
    c.customer_state,
    COUNT(o.order_id) AS total_orders,
    ROUND(AVG(JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_purchase_timestamp)), 1) AS avg_delivery_days,
    ROUND(
        SUM(CASE WHEN JULIANDAY(o.order_delivered_customer_date) > JULIANDAY(o.order_estimated_delivery_date) THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(o.order_id), 
        2
    ) AS late_delivery_pct,
    ROUND(AVG(oi.freight_value), 2) AS avg_freight_cost
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;


-- 3. Impact of Delivery Delays on Customer Review Ratings
SELECT 
    CASE 
        WHEN JULIANDAY(o.order_delivered_customer_date) <= JULIANDAY(o.order_estimated_delivery_date) THEN 'On-Time / Early'
        WHEN JULIANDAY(o.order_delivered_customer_date) - JULIANDAY(o.order_estimated_delivery_date) <= 3 THEN 'Late (1-3 Days)'
        ELSE 'Severely Late (>3 Days)'
    END AS delivery_performance_bucket,
    COUNT(DISTINCT o.order_id) AS order_count,
    ROUND(AVG(r.review_score), 2) AS average_review_score,
    ROUND(SUM(CASE WHEN r.review_score >= 4 THEN 1.0 ELSE 0.0 END) * 100.0 / COUNT(DISTINCT o.order_id), 1) AS satisfaction_rate_pct
FROM orders o
JOIN order_reviews r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY delivery_performance_bucket
ORDER BY average_review_score DESC;


-- 4. Seller Fulfillment Speed (Time to Carrier Handoff)
SELECT 
    s.seller_state,
    COUNT(DISTINCT oi.order_id) AS orders_fulfilled,
    ROUND(AVG(JULIANDAY(o.order_delivered_carrier_date) - JULIANDAY(o.order_approved_at)), 1) AS avg_days_to_carrier
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN sellers s ON oi.seller_id = s.seller_id
WHERE o.order_delivered_carrier_date IS NOT NULL
  AND o.order_approved_at IS NOT NULL
GROUP BY s.seller_state
HAVING orders_fulfilled >= 10
ORDER BY avg_days_to_carrier ASC;
