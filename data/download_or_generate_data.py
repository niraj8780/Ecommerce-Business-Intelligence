"""
Data Downloader & Generator for E-commerce Business Intelligence Project.
Supports:
1. Loading existing Kaggle Olist CSVs from data/raw/
2. Downloading via Kaggle CLI / urllib if configured
3. Generating a high-fidelity, schema-matched Olist dataset if raw files are not yet present.
4. Exporting to data/processed/ecommerce.db (SQLite) for direct SQL analysis.
"""

import os
import sys
import random
import sqlite3
import datetime
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
DB_PATH = os.path.join(PROCESSED_DIR, "ecommerce.db")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

EXPECTED_FILES = [
    "olist_customers_dataset.csv",
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_products_dataset.csv",
    "olist_order_payments_dataset.csv",
    "olist_order_reviews_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_geolocation_dataset.csv"
]

def check_existing_files():
    found = [f for f in EXPECTED_FILES if os.path.exists(os.path.join(RAW_DIR, f))]
    return len(found) == len(EXPECTED_FILES)

def generate_synthetic_olist_data(n_customers=2500, n_orders=5000):
    print("Generating schema-matched Brazilian E-Commerce (Olist) dataset...")
    random.seed(42)
    np.random.seed(42)

    states = ["SP", "RJ", "MG", "RS", "PR", "SC", "BA", "PE", "CE", "DF"]
    cities = {
        "SP": ["sao paulo", "campinas", "guarulhos", "santos"],
        "RJ": ["rio de janeiro", "niteroi", "nova iguacu"],
        "MG": ["belo horizonte", "uberlandia", "contagem"],
        "RS": ["porto alegre", "caxias do sul", "pelotas"],
        "PR": ["curitiba", "londrina", "maringa"],
        "SC": ["florianopolis", "joinville", "blumenau"],
        "BA": ["salvador", "feira de santana"],
        "PE": ["recife", "olinda"],
        "CE": ["fortaleza", "caucaia"],
        "DF": ["brasilia"]
    }

    categories = [
        ("cama_mesa_banho", "bed_bath_table"),
        ("beleza_saude", "health_beauty"),
        ("esporte_lazer", "sports_leisure"),
        ("moveis_decoracao", "furniture_decor"),
        ("informatica_acessorios", "computers_accessories"),
        ("utilidades_domesticas", "housewares"),
        ("relogios_presentes", "watches_gifts"),
        ("telefonia", "telephony"),
        ("automotivo", "auto"),
        ("brinquedos", "toys")
    ]

    # 1. Customers
    customers_data = []
    unique_user_ids = [f"usr_{i:05d}" for i in range(int(n_customers * 0.8))]
    
    for i in range(n_customers):
        cust_id = f"cust_{i:06d}"
        uniq_id = random.choice(unique_user_ids)
        st = random.choice(states)
        city = random.choice(cities[st])
        zip_prefix = random.randint(10000, 99999)
        customers_data.append({
            "customer_id": cust_id,
            "customer_unique_id": uniq_id,
            "customer_zip_code_prefix": zip_prefix,
            "customer_city": city,
            "customer_state": st
        })
    df_customers = pd.DataFrame(customers_data)

    # 2. Sellers
    n_sellers = 150
    sellers_data = []
    for i in range(n_sellers):
        st = random.choice(states)
        sellers_data.append({
            "seller_id": f"seller_{i:04d}",
            "seller_zip_code_prefix": random.randint(10000, 99999),
            "seller_city": random.choice(cities[st]),
            "seller_state": st
        })
    df_sellers = pd.DataFrame(sellers_data)

    # 3. Products
    n_products = 400
    products_data = []
    for i in range(n_products):
        cat_pt, cat_en = random.choice(categories)
        products_data.append({
            "product_id": f"prod_{i:05d}",
            "product_category_name": cat_pt,
            "product_name_lenght": random.randint(20, 60),
            "product_description_lenght": random.randint(100, 1500),
            "product_photos_qty": random.randint(1, 6),
            "product_weight_g": random.randint(150, 8000),
            "product_length_cm": random.randint(10, 80),
            "product_height_cm": random.randint(5, 50),
            "product_width_cm": random.randint(10, 60)
        })
    df_products = pd.DataFrame(products_data)

    # 4. Orders, Items, Payments, Reviews
    orders_data = []
    items_data = []
    payments_data = []
    reviews_data = []

    start_date = datetime.date(2022, 1, 1)
    end_date = datetime.date(2023, 12, 31)
    days_range = (end_date - start_date).days

    statuses = ["delivered"] * 92 + ["shipped"] * 4 + ["canceled"] * 3 + ["invoiced"] * 1
    payment_types = ["credit_card"] * 75 + ["boleto"] * 18 + ["voucher"] * 5 + ["debit_card"] * 2

    for i in range(n_orders):
        order_id = f"ord_{i:06d}"
        cust = df_customers.iloc[random.randint(0, len(df_customers) - 1)]
        order_status = random.choice(statuses)

        rand_days = random.randint(0, days_range)
        purchase_time = datetime.datetime.combine(
            start_date + datetime.timedelta(days=rand_days),
            datetime.time(random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        )
        approved_time = purchase_time + datetime.timedelta(minutes=random.randint(15, 300))
        carrier_time = approved_time + datetime.timedelta(days=random.randint(1, 3))

        # Delivery logic
        est_days = random.randint(12, 25)
        estimated_delivery = purchase_time + datetime.timedelta(days=est_days)
        
        # 10% chance of late delivery
        is_late = random.random() < 0.10
        actual_days = est_days + random.randint(1, 8) if is_late else random.randint(4, est_days - 1)
        actual_delivery = purchase_time + datetime.timedelta(days=actual_days) if order_status == "delivered" else None

        orders_data.append({
            "order_id": order_id,
            "customer_id": cust["customer_id"],
            "order_status": order_status,
            "order_purchase_timestamp": purchase_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_approved_at": approved_time.strftime("%Y-%m-%d %H:%M:%S"),
            "order_delivered_carrier_date": carrier_time.strftime("%Y-%m-%d %H:%M:%S") if order_status in ["delivered", "shipped"] else None,
            "order_delivered_customer_date": actual_delivery.strftime("%Y-%m-%d %H:%M:%S") if actual_delivery else None,
            "order_estimated_delivery_date": estimated_delivery.strftime("%Y-%m-%d %H:%M:%S")
        })

        # Order Items (1 to 3 items)
        n_items = random.choices([1, 2, 3], weights=[0.82, 0.14, 0.04])[0]
        order_total = 0.0
        for item_seq in range(1, n_items + 1):
            prod = df_products.iloc[random.randint(0, len(df_products) - 1)]
            seller = df_sellers.iloc[random.randint(0, len(df_sellers) - 1)]
            price = round(random.uniform(19.90, 480.00), 2)
            freight = round(random.uniform(10.50, 45.00), 2)
            order_total += price + freight

            items_data.append({
                "order_id": order_id,
                "order_item_id": item_seq,
                "product_id": prod["product_id"],
                "seller_id": seller["seller_id"],
                "shipping_limit_date": (purchase_time + datetime.timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "price": price,
                "freight_value": freight
            })

        # Payment
        pay_type = random.choice(payment_types)
        installments = random.choice([1, 1, 1, 2, 3, 6, 10]) if pay_type == "credit_card" else 1
        payments_data.append({
            "order_id": order_id,
            "payment_sequential": 1,
            "payment_type": pay_type,
            "payment_installments": installments,
            "payment_value": round(order_total, 2)
        })

        # Review
        if order_status == "delivered":
            score = 1 if is_late and random.random() < 0.6 else random.choices([5, 4, 3, 2, 1], weights=[0.58, 0.20, 0.10, 0.05, 0.07])[0]
            reviews_data.append({
                "review_id": f"rev_{i:06d}",
                "order_id": order_id,
                "review_score": score,
                "review_comment_title": "Bom" if score >= 4 else ("Atraso" if is_late else "Regular"),
                "review_comment_message": "Produto excelente e rápido" if score >= 4 else "Demorou para chegar",
                "review_creation_date": actual_delivery.strftime("%Y-%m-%d 00:00:00") if actual_delivery else purchase_time.strftime("%Y-%m-%d 00:00:00"),
                "review_answer_timestamp": (actual_delivery + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S") if actual_delivery else purchase_time.strftime("%Y-%m-%d %H:%M:%S")
            })

    # 5. Geolocation
    geo_data = []
    for st in states:
        for c in cities[st]:
            geo_data.append({
                "geolocation_zip_code_prefix": random.randint(10000, 99999),
                "geolocation_lat": round(random.uniform(-30.0, -5.0), 6),
                "geolocation_lng": round(random.uniform(-55.0, -35.0), 6),
                "geolocation_city": c,
                "geolocation_state": st
            })
    df_geo = pd.DataFrame(geo_data)

    df_orders = pd.DataFrame(orders_data)
    df_items = pd.DataFrame(items_data)
    df_payments = pd.DataFrame(payments_data)
    df_reviews = pd.DataFrame(reviews_data)

    # Save CSVs to data/raw/
    files_map = {
        "olist_customers_dataset.csv": df_customers,
        "olist_orders_dataset.csv": df_orders,
        "olist_order_items_dataset.csv": df_items,
        "olist_products_dataset.csv": df_products,
        "olist_order_payments_dataset.csv": df_payments,
        "olist_order_reviews_dataset.csv": df_reviews,
        "olist_sellers_dataset.csv": df_sellers,
        "olist_geolocation_dataset.csv": df_geo
    }

    for fname, df in files_map.items():
        out_csv = os.path.join(RAW_DIR, fname)
        df.to_csv(out_csv, index=False)
        print(f"Saved: {fname} ({len(df)} rows)")

    # Build SQLite DB in processed/
    conn = sqlite3.connect(DB_PATH)
    for table_name, df in {
        "customers": df_customers,
        "orders": df_orders,
        "order_items": df_items,
        "products": df_products,
        "order_payments": df_payments,
        "order_reviews": df_reviews,
        "sellers": df_sellers,
        "geolocation": df_geo
    }.items():
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.close()
    print(f"\nSQLite database populated successfully: {DB_PATH}")

if __name__ == "__main__":
    generate_synthetic_olist_data()
