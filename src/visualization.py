"""
Visualization Module for E-Commerce Analytics
Generates clean, interactive Plotly charts and publication-ready Matplotlib figures.
"""

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns

def plot_monthly_revenue_trend(monthly_df):
    """Interactive line chart of monthly revenue with MoM growth."""
    fig = go.Figure()
    
    # Revenue Bar
    fig.add_trace(go.Bar(
        x=monthly_df["purchase_year_month"],
        y=monthly_df["total_revenue"],
        name="Gross Revenue ($)",
        marker_color="#2E86AB",
        opacity=0.85
    ))
    
    # MoM Growth Line
    fig.add_trace(go.Scatter(
        x=monthly_df["purchase_year_month"],
        y=monthly_df["mom_growth_pct"],
        name="MoM Growth (%)",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color="#E63946", width=2.5),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Monthly Revenue Trajectory & MoM Growth Rate",
        xaxis=dict(title="Year-Month", tickangle=-45),
        yaxis=dict(title="Revenue ($)", showgrid=True),
        yaxis2=dict(
            title="MoM Growth Rate (%)",
            overlaying="y",
            side="right",
            showgrid=False
        ),
        legend=dict(x=0.01, y=0.99),
        template="plotly_white",
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig

def plot_rfm_segments_treemap(rfm_df):
    """Treemap of customer segments showing headcount and monetary value."""
    segment_summary = rfm_df.groupby("customer_segment").agg(
        customer_count=("customer_unique_id", "count"),
        total_revenue=("monetary", "sum")
    ).reset_index()

    fig = px.treemap(
        segment_summary,
        path=["customer_segment"],
        values="total_revenue",
        color="total_revenue",
        color_continuous_scale="Blues",
        hover_data=["customer_count"],
        title="Customer RFM Segmentation by Revenue Contribution"
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10))
    return fig

def plot_top_categories(df, top_n=10):
    """Bar chart for top revenue-generating product categories."""
    top_cats = (
        df.groupby("category_clean")["price"]
        .sum()
        .reset_index()
        .sort_values(by="price", ascending=False)
        .head(top_n)
    )
    
    fig = px.bar(
        top_cats,
        x="price",
        y="category_clean",
        orientation="h",
        color="price",
        color_continuous_scale="Viridis",
        title=f"Top {top_n} Product Categories by Sales Revenue",
        labels={"price": "Revenue ($)", "category_clean": "Category"}
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig

def plot_state_delivery_delays(state_df):
    """Horizontal bar chart comparing average delivery days and late delivery %."""
    fig = px.bar(
        state_df.head(15),
        x="avg_delivery_days",
        y="customer_state",
        orientation="h",
        color="late_rate_pct",
        color_continuous_scale="Reds",
        title="Delivery Lead Times and Late Delivery % by State (Top 15 Longest)",
        labels={
            "avg_delivery_days": "Avg Delivery Time (Days)",
            "customer_state": "State",
            "late_rate_pct": "Late Delivery Rate (%)"
        }
    )
    fig.update_layout(yaxis=dict(autorange="reversed"), template="plotly_white")
    return fig
