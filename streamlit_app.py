import streamlit as st
import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import plotly.express as px

# Function to connect to the PostgreSQL database
def get_db_connection():
    conn = psycopg2.connect(
        host="gowridb.cp8imqo0okli.ap-south-1.rds.amazonaws.com",
        port=5432,
        database="postgres",
        user="postgres",
        password="rootroot80"
    )
    return conn

# Function to execute a query and return the result as a pandas DataFrame
def run_query(query):
    conn = get_db_connection()
    if conn is None:
        return None
    try:
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return None
    finally:
        conn.close()

import base64
import os

def set_background_image_local():
    image_path = "Retailorder image.jpg"
    
    if not os.path.exists(image_path):
        st.error("Background image not found. Please check the file path.")
        return
    
    with open(image_path, "rb") as file:
        data = file.read()
    base64_image = base64.b64encode(data).decode("utf-8")
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpeg;base64,{base64_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}     
        </style>
        """,
        unsafe_allow_html=True
    ) 

# Call the function
set_background_image_local()


# Streamlit UI
st.title("Retail Order Dashboard")
# Input fields for user
nav = st.sidebar.radio("Select Queries", ["queries_by_guvi", "my_own_queries"])

# Split queries into two sections
queries_by_guvi = {
        "Top 10 highest revenue generating products": 
            'SELECT "product id", SUM("list price" * "quantity") AS total_revenue FROM df1_orders GROUP BY "product id" ORDER BY total_revenue DESC LIMIT 10;',
        "Top 5 cities with the highest profit margins": 
            'SELECT o."city", SUM(d."profit") AS total_profit FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."city" ORDER BY total_profit DESC LIMIT 5;',
        "Total discount given for each category": 
            'SELECT o."category", SUM(d."discount amount") AS total_discount FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY total_discount DESC;',
        "Average sales price per product category": 
            'SELECT "category", AVG("sales price") AS average_sales_price FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category";',
        "The highest average sale price":
            'SELECT "region",AVG("sales price") AS "average sales price" FROM df1_order o JOIN df1_orders d on o."sub category"=d."sub category" GROUP BY o."region",d."sales price" ORDER BY "average sales price" DESC;',
        "Total profit per category": 
            'SELECT "category", SUM("profit") AS total_profit FROM df1_orders d JOIN df1_order o ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY total_profit DESC;',
        "Top 3 segments with the highest quantity of orders": 
            'SELECT "category", "quantity" AS highest_quantity FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category", d."quantity" ORDER BY highest_quantity DESC LIMIT 3;',
        "Average discount percentage given per region": 
            'SELECT "region", AVG("discount percent") AS avg_discount_percent FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."region" ORDER BY avg_discount_percent DESC;',
        "Product category with the highest total profit": 
            'SELECT "category", SUM("profit") AS highest_total_profit FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY highest_total_profit DESC LIMIT 1;',
        "Total revenue generated per year": 
            'SELECT "year", SUM("sales price" * "quantity") AS total_revenue FROM df1_orders GROUP BY "year" ORDER BY "year";',
}

my_own_queries = {
        "Total revenue per product category": 
            'SELECT "category", SUM("sales price" * "quantity") AS total_revenue FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY total_revenue DESC;',
        "Top 5 products by profit": 
            'SELECT "category", o."sub category", SUM("profit") AS products_by_profit FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category", o."sub category" ORDER BY products_by_profit DESC LIMIT 5;',
        "Average sales price per sub category": 
            'SELECT d."sub category", AVG("sales price") AS avg_sales_price FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY d."sub category" ORDER BY d."sub category";',
        "Total discount amount given by category": 
            'SELECT "category", SUM("discount amount") AS total_discount_amount FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY total_discount_amount DESC;',
        "Total orders per segment": 
            'SELECT COUNT(DISTINCT "order id") AS total_orders FROM df1_order;',
        "Profit margin per city": 
            'SELECT o."city", SUM(d."profit") AS total_profit FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."city" ORDER BY total_profit DESC LIMIT 10;',
        "Average profit per category": 
            'SELECT "category", AVG("profit") AS average_profit FROM df1_orders d JOIN df1_order o ON o."sub category" = d."sub category" GROUP BY o."category" ORDER BY average_profit DESC;',
        "Top 3 cities by revenue": 
            'SELECT o."city", SUM(d."list price" * d."quantity") AS revenue FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."city" ORDER BY revenue DESC LIMIT 3;',
        "Products with no profit": 
            'SELECT "product id" FROM df1_orders GROUP BY "product id" HAVING SUM("profit") = 0 LIMIT 3;',
        "Top 3 countries with high sales by segment": 
            'SELECT "country", "segment", SUM("sales price") AS high_sales FROM df1_order o JOIN df1_orders d ON o."sub category" = d."sub category" GROUP BY o."country", o."segment" ORDER BY high_sales DESC LIMIT 3;'
}
if nav == "queries_by_guvi":
    st.subheader("Queries by GUVI")
    query = st.selectbox("Select a query to visualize:", list(queries_by_guvi.keys()))
    selected_query_set = queries_by_guvi
elif nav == "my_own_queries":
    st.subheader("My Own Queries")
    query = st.selectbox("Select a query to visualize:", list(my_own_queries.keys()))
    selected_query_set = my_own_queries
else:
    query = None

# Execute and visualize selected query
if query:
    result_df = run_query(selected_query_set[query])
    if result_df is not None:
        st.dataframe(result_df)


# Execute and visualize based on selected query
       
    if query == "Top 10 highest revenue generating products":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["product id"], result_df["total_revenue"], color='skyblue')
            plt.title("Top 10 Highest Revenue Generating Products")
            plt.xlabel("Product ID")
            plt.ylabel("Total Revenue")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Top 5 cities with the highest profit margins":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["city"], result_df["total_profit"], color='lightgreen')
            plt.title("Top 5 Cities with the Highest Profit Margins")
            plt.xlabel("City")
            plt.ylabel("Total Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Total discount given for each category":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["total_discount"], color='orange')
            plt.title("Total Discount Given for Each Category")
            plt.xlabel("Category")
            plt.ylabel("Total Discount")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Average sales price per product category":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["average_sales_price"], color='purple')
            plt.title("Average Sales Price Per Product Category")
            plt.xlabel("Category")
            plt.ylabel("Average Sales Price")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query== "Total profit per category":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["total_profit"], color='violet')
            plt.title("Total Profit Per Category")
            plt.xlabel("Category")
            plt.ylabel("Total Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Top 3 segments with the highest quantity of orders":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["highest_quantity"], color='magenta')
            plt.title("Top 3 Segments with the Highest Quantity of Orders")
            plt.xlabel("Category")
            plt.ylabel("Highest Quantity")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Average discount percentage given per region":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["region"], result_df["avg_discount_percent"], color='salmon')
            plt.title("Average Discount Percentage Given Per Region")
            plt.xlabel("Region")
            plt.ylabel("Average Discount Percentage")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Product category with the highest total profit":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["highest_total_profit"], color='orange')
            plt.title("Product Category with the Highest Total Profit")
            plt.xlabel("Category")
            plt.ylabel("Total Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Total revenue generated per year":
        result_df = run_query(queries_by_guvi[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.plot(result_df["year"], result_df["total_revenue"], marker='o', color='blue')
            plt.title("Total Revenue Generated Per Year")
            plt.xlabel("Year")
            plt.ylabel("Total Revenue")
            st.pyplot(plt)

    elif query == "Total revenue per product category":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["total_revenue"], color='lightblue')
            plt.title("Total Revenue Per Product Category")
            plt.xlabel("Category")
            plt.ylabel("Total Revenue")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Top 5 products by profit":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["sub category"], result_df["products_by_profit"], color='gold')
            plt.title("Top 5 Products by Profit")
            plt.xlabel("Sub Category")
            plt.ylabel("Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Average sales price per sub category":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["sub category"], result_df["avg_sales_price"], color='pink')
            plt.title("Average Sales Price Per Sub Category")
            plt.xlabel("Sub Category")
            plt.ylabel("Average Sales Price")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Total discount amount given by category":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["total_discount_amount"], color='lightcoral')
            plt.title("Total Discount Amount Given by Category")
            plt.xlabel("Category")
            plt.ylabel("Total Discount Amount")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Total orders per segment":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            st.write(f"Total Orders: {result_df['total_orders'][0]}")

    elif query == "Profit margin per city":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["city"], result_df["total_profit"], color='lightseagreen')
            plt.title("Profit Margin Per City")
            plt.xlabel("City")
            plt.ylabel("Total Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Average profit per category":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["category"], result_df["average_profit"], color='lightgray')
            plt.title("Average Profit Per Category")
            plt.xlabel("Category")
            plt.ylabel("Average Profit")
            plt.xticks(rotation=45)
            st.pyplot(plt)

    elif query == "Top 3 cities by revenue":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["city"], result_df["revenue"], color='purple')
            plt.title("Top 3 Cities by Revenue")
            plt.xlabel("City")
            plt.ylabel("Revenue")
            plt.xticks(rotation=45)
            st.pyplot(plt)
            
    elif query == "Products with no profit":
        result_df = run_query(my_own_queries[query])
        if result_df is not None and not result_df.empty:
            st.write("These are the products that have no profit:")
        else:
            st.write("All products are generating profit.")            
    
    elif query == "Top 3 countries with high sales by segment":
        result_df = run_query(my_own_queries[query])
        if result_df is not None:
            plt.figure(figsize=(10, 6))
            plt.bar(result_df["country"], result_df["high_sales"], color='orange')
            plt.title("Top 3 Countries with High Sales by Segment")
            plt.xlabel("Country")
            plt.ylabel("High Sales")
            plt.xticks(rotation=45)
            st.pyplot(plt)
    else:
        st.warning("No data available for this query.")
else:
    st.warning("Please select a query.")        

st.text("Thank you for using the dashboard!")
