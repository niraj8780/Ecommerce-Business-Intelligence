"""
Business Analysis & Statistics Engine
Handles RFM segmentation, cohort metrics, sales analytics, and operational KPIs.
"""

import pandas as pd
import numpy as np

def calculate_sales_kpis(df):
    """Calculates top-level business KPIs."""
    delivered_df = df[df["order_status"] == "delivered"]
    
    total_orders = delivered_df["order_id"].nunique()
    total_customers = delivered_df["customer_unique_id"].nunique()
    total_revenue = delivered_df["price"].sum()
    total_freight = delivered_df["freight_value"].sum()
    gross_sales = total_revenue + total_freight
    
    # AOV per order
    order_totals = delivered_df.groupby("order_id")["total_item_value"].sum()
    aov = order_totals.mean() if len(order_totals) > 0 else 0.0
    
    # Customer repeat rate
    cust_order_counts = delivered_df.groupby("customer_unique_id")["order_id"].nunique()
    repeat_rate = (cust_order_counts > 1).sum() / len(cust_order_counts) * 100 if len(cust_order_counts) > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "gross_sales": round(gross_sales, 2),
        "total_freight": round(total_freight, 2),
        "total_orders": int(total_orders),
        "total_customers": int(total_customers),
        "average_order_value": round(aov, 2),
        "repeat_customer_rate_pct": round(repeat_rate, 2)
    }

def calculate_monthly_trends(df):
    """Calculates monthly sales volume, revenue, and month-over-month growth."""
    delivered = df[df["order_status"] == "delivered"].copy()
    
    monthly = delivered.groupby("purchase_year_month").agg(
        total_revenue=("price", "sum"),
        order_count=("order_id", "nunique"),
        unique_buyers=("customer_unique_id", "nunique")
    ).reset_index()
    
    monthly["total_revenue"] = monthly["total_revenue"].round(2)
    monthly["mom_growth_pct"] = (monthly["total_revenue"].pct_change() * 100).round(2).fillna(0.0)
    monthly["aov"] = (monthly["total_revenue"] / monthly["order_count"]).round(2)
    
    return monthly

def calculate_rfm_segments(df):
    """
    Performs Recency, Frequency, Monetary (RFM) customer segmentation.
    Assigns behavioral segment tags to each customer.
    """
    delivered = df[df["order_status"] == "delivered"].copy()
    snapshot_date = delivered["order_purchase_timestamp"].max()

    rfm = delivered.groupby("customer_unique_id").agg(
        recency=("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("total_item_value", "sum"),
        state=("customer_state", "first"),
        city=("customer_city", "first")
    ).reset_index()

    rfm["monetary"] = rfm["monetary"].round(2)

    # Binning scores 1 to 5 using qcut or rank-based percentiles
    rfm["r_score"] = pd.qcut(rfm["recency"].rank(method="first", ascending=False), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["f_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["m_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)

    # Segment classification rule
    def assign_segment(row):
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f <= 2:
            return "Recent / New"
        elif r <= 2 and f >= 3:
            return "At Risk"
        elif r <= 2 and f <= 2:
            return "Lost / Dormant"
        else:
            return "Potential Loyalists"

    rfm["customer_segment"] = rfm.apply(assign_segment, axis=1)
    return rfm

def calculate_delivery_operations(df):
    """Evaluates delivery speed, delay ratios, and geographic performance."""
    delivered = df[df["order_status"] == "delivered"].copy()
    
    avg_delivery_time = delivered["delivery_duration_days"].mean()
    late_orders_count = delivered["is_late"].sum()
    late_order_rate = (late_orders_count / len(delivered)) * 100 if len(delivered) > 0 else 0.0

    state_delivery = delivered.groupby("customer_state").agg(
        total_orders=("order_id", "nunique"),
        avg_delivery_days=("delivery_duration_days", "mean"),
        late_rate_pct=("is_late", lambda x: (x.sum() / len(x)) * 100),
        avg_freight=("freight_value", "mean")
    ).round(2).reset_index().sort_values(by="avg_delivery_days", ascending=False)

    return {
        "avg_delivery_days": round(avg_delivery_time, 1),
        "late_order_rate_pct": round(late_order_rate, 2),
        "late_orders_count": int(late_orders_count),
        "state_delivery_df": state_delivery
    }
