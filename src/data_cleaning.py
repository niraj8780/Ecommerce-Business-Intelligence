"""
Data Cleaning and Preprocessing Pipeline
Cleans and standardizes raw Brazilian E-Commerce data.
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def get_db_connection(db_path=None):
    if db_path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, "data", "processed", "ecommerce.db")
    return sqlite3.connect(db_path)

def load_clean_master_data(db_path=None):
    """
    Loads and joins all relational tables into a unified master dataframe,
    performing date conversions and feature engineering.
    """
    conn = get_db_connection(db_path)
    
    query = """
    SELECT 
        o.order_id,
        o.customer_id,
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        o.order_status,
        o.order_purchase_timestamp,
        o.order_approved_at,
        o.order_delivered_carrier_date,
        o.order_delivered_customer_date,
        o.order_estimated_delivery_date,
        oi.order_item_id,
        oi.product_id,
        oi.seller_id,
        oi.price,
        oi.freight_value,
        (oi.price + oi.freight_value) AS total_item_value,
        COALESCE(p.product_category_name, 'uncategorized') AS product_category_name,
        p.product_weight_g,
        op.payment_type,
        op.payment_installments,
        op.payment_value,
        r.review_score
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN order_payments op ON o.order_id = op.order_id AND op.payment_sequential = 1
    LEFT JOIN order_reviews r ON o.order_id = r.order_id
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()

    # Convert timestamps
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Feature Engineering
    df["purchase_year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["purchase_date"] = df["order_purchase_timestamp"].dt.date
    df["purchase_day_name"] = df["order_purchase_timestamp"].dt.day_name()
    df["purchase_hour"] = df["order_purchase_timestamp"].dt.hour

    # Delivery performance metrics
    df["delivery_duration_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / (24 * 3600)

    df["estimated_delivery_days"] = (
        df["order_estimated_delivery_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / (24 * 3600)

    df["is_late"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    ).astype(int)

    df["days_delayed"] = np.where(
        df["is_late"] == 1,
        (df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]).dt.total_seconds() / (24 * 3600),
        0.0
    )

    # Clean category names (replace underscores with spaces & title case)
    df["category_clean"] = df["product_category_name"].str.replace("_", " ").str.title()

    return df

if __name__ == "__main__":
    df = load_clean_master_data()
    print(f"Data cleaned successfully. Shape: {df.shape}")
    print(df.head(3))
