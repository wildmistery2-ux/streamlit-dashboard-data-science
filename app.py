import streamlit as st
import pandas as pd
import altair as alt

# 1. Page Setup
st.set_page_config(page_title="Geo-Flow Product Analytics", layout="wide")

# 2. Data Loading & Cleaning
@st.cache_data
def load_data():
    # Load with latin1 due to special characters in output.csv
    df = pd.read_csv("output.csv", encoding='latin1')
    
    # Clean price strings (removing commas) and convert to numeric
    for col in ['actual_price', 'selling_price']:
        df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
    
    # Fill missing ratings with the average
    df['average_rating'] = df['average_rating'].fillna(df['average_rating'].mean())
    
    return df

try:
    df = load_data()

    # 3. Sidebar Navigation
    st.sidebar.header("Dashboard Filters")
    
    # Filter by Brand
    brands = sorted(df['brand'].dropna().unique())
    selected_brands = st.sidebar.multiselect("Select Brands", brands, default=brands[:5])

    # Filter by Stock Status
    stock_status = st.sidebar.radio("Stock Availability", ["All", "In Stock", "Out of Stock"])

    # Apply Filters
    filtered_df = df[df['brand'].isin(selected_brands)]
    if stock_status == "In Stock":
        filtered_df = filtered_df[filtered_df['out_of_stock'] == False]
    elif stock_status == "Out of Stock":
        filtered_df = filtered_df[filtered_df['out_of_stock'] == True]

    # 4. Main UI - Header & Metrics
    st.title("📦 Product Insights Dashboard")
    st.markdown("Using **Altair** for declarative data visualization.")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Products", len(filtered_df))
    m2.metric("Avg. Price", f"₹{filtered_df['selling_price'].mean():,.2f}")
    m3.metric("Avg. Rating", f"{filtered_df['average_rating'].mean():.2f} ⭐")

    st.divider()

    # 5. Visualizations with Altair
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Selling Price by Brand")
        # Altair Boxplot
        box_chart = alt.Chart(filtered_df).mark_boxplot(extent='min-max').encode(
            x=alt.X('brand:N', title="Brand"),
            y=alt.Y('selling_price:Q', title="Selling Price (₹)"),
            color=alt.Color('brand:N', legend=None)
        ).properties(height=400)
        st.altair_chart(box_chart, use_container_width=True)

    with col2:
        st.subheader("Rating vs. Price Correlation")
        # Altair Interactive Scatter Plot
        scatter_chart = alt.Chart(filtered_df).mark_point(filled=True, size=60).encode(
            x=alt.X('selling_price:Q', title="Price (₹)"),
            y=alt.Y('average_rating:Q', title="Rating", scale=alt.Scale(domain=[0, 5])),
            color='brand:N',
            tooltip=['title', 'selling_price', 'average_rating']
        ).interactive().properties(height=400)
        st.altair_chart(scatter_chart, use_container_width=True)

    # 6. Detailed Data View
    with st.expander("View Raw Filtered Data"):
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Failed to load dashboard: {e}")