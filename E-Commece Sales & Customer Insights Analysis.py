# Import Labraries
import numpy as np
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

# Create Database Connection
conn = sqlite3.connect("ecommerce.db")
cursor = conn.cursor()

# Load Dataset 
df = pd.read_csv("ecommerce_professional_dataset.csv")
df.to_sql("orders",conn,if_exists="replace",index=False)
print("First 5 rows:")
print(df.head(5))

# Create Tables
query = "PRAGMA table_info('orders')"
print(pd.read_sql(query,conn))
print("'Orders'table create successfully")

# Data Features
print(df.shape)
print(df.info())

# Data Cleaning
print(df.duplicated())
print(df.drop_duplicates(inplace=True))
print(df.isna().sum()[df.isna().sum() > 0].sort_values())


# Convert Order date into datetime
df["Order_Date"]=pd.to_datetime(df["Order_Date"])

# Extract Month & Year
df["Month"]=df["Order_Date"].dt.month
df["Year"]=df["Order_Date"].dt.year
df.to_sql("orders",conn,if_exists="replace",index=False)


# SQL Queries

# Total Sales
query = "SELECT SUM(Sales) AS Total_Sale FROM orders"
print(pd.read_sql(query,conn))

# Total Profit
query = "SELECT SUM(Profit) AS Total_Profit FROM orders"
print(pd.read_sql(query,conn))

# Monthly Sales Trend

query = """SELECT Month , SUM(Sales) AS Monthly_Sales 
FROM orders
GROUP BY Month
ORDER BY Month"""
Monthly_Sales = pd.read_sql(query,conn)
print(Monthly_Sales)



# Top 5 Products
query = """ SELECT Product , SUM(Sales) AS Total_Sale
FROM orders
GROUP BY Product
ORDER BY Sales DESC
LIMIT 5"""

Top_Products = pd.read_sql(query,conn)
print(Top_Products)

# Category Wise Sale

query = """ SELECT Category,SUM(Sales) AS Total_Sale
FROM orders
GROUP BY Category
ORDER BY Sales DESC"""
Category_Sales = pd.read_sql(query,conn)
print(Category_Sales)


query = """ SELECT Category,SUM(Sales) AS Total_Sale
FROM orders
GROUP BY Category
ORDER BY Sales DESC
LIMIT 1"""

top_category = pd.read_sql(query,conn)
print()
print("Top Category")
print(top_category)

# Top Customers

query = """SELECT Customer_Name,SUM(Sales) AS Total_Sales
FROM orders
GROUP BY Customer_Name
ORDER BY Total_Sales DESC"""
Top_Customers = pd.read_sql(query,conn)

print(Top_Customers)


query = ("""SELECT Customer_Name,SUM(Sales) AS Total_Sales
FROM orders
GROUP BY Customer_Name
ORDER BY Total_Sales DESC
LIMIT 1
""")

top_customer = pd.read_sql(query,conn)
print()
print("Top Customer")
print(top_customer)


# City-Wise Sale

query = """ SELECT City,SUM(Sales) AS Total_Sales
FROM orders
GROUP BY City
ORDER BY Total_Sales DESC"""
Citywise_Sales = pd.read_sql(query,conn)

print(Citywise_Sales)


query = ("""SELECT City,SUM(Sales)
FROM orders
GROUP BY City 
ORDER BY SUM(Sales) DESC
LIMIT 1
""")

Top_City = pd.read_sql(query,conn)
print("Top City")
print(Top_City)

# Loss Analysis

query = """ SELECT SUM(Profit) as Total_Loss
FROM orders
WHERE Profit < 0"""
Total_Loss = pd.read_sql(query,conn)
print(Total_Loss)

# Create Customer Table

cursor.execute(
    """CREATE TABLE IF NOT EXISTS customers(
    Customer_Name TEXT,
    Customer_ID INT PRIMARY KEY,
    City TEXT)
""")
conn.commit()
# Create Product Table

cursor.execute(
    """CREATE TABLE IF NOT EXISTS products(
    Product TEXT,
    Category TEXT,
    Price REAL,
    Order_ID)
""")
cursor.execute("DROP TABLE IF EXISTS products")
conn.commit()
cursor.execute(
    """CREATE TABLE IF NOT EXISTS products(
    Product TEXT,
    Category TEXT,
    Selling_Price INT,
    Order_ID)
""")


# Create Order Table 

cursor.execute(
    """CREATE TABLE IF NOT EXISTS orderss(
    Order_ID INT,
    Order_Date TEXT,
    Customer_ID INT,
    Product TEXT,
    Quantity INT,
    Discount REAL,
    Profit REAL,
    Customer_Type TEXT)
""")
conn.commit()

# Insert Data Into table


cursor.execute("""
INSERT OR IGNORE INTO customers(Customer_Name,Customer_ID,City)
SELECT DISTINCT Customer_Name,Customer_ID,City
FROM orders
""")
conn.commit()

cursor.execute("""
INSERT OR IGNORE INTO products(Product,Category,Selling_Price)
SELECT DISTINCT Product,Category,Selling_Price
FROM orders""")

query=("""
SELECT c.Customer_Name,c.City, SUM(Sales) AS Total_Sales
FROM orders o
JOIN customers c ON c.Customer_ID = o.Customer_ID
GROUP BY c.Customer_Name,c.City
ORDER BY Total_Sales DESC
""")
print(pd.read_sql(query,conn))

# RFM Scoring 

query = ("""
SELECT Customer_ID,
MAX(Order_Date) AS Last_Order,
COUNT(Order_ID) AS Frequency,               
SUM(Sales) AS Monetary 
FROM orders
GROUP BY Customer_ID
""")
rfm = (pd.read_sql(query,conn))

# Calculate Recency

rfm["Last_Order"] = pd.to_datetime(rfm["Last_Order"])
latest_date = rfm["Last_Order"].max()

rfm["Recency"] = (latest_date - rfm["Last_Order"]).dt.days
print("\n\n")
print(rfm[["Customer_ID","Recency"]].to_string(index=False))

#Calculate Frequency

query = ("""
SELECT Customer_ID, COUNT(Order_ID) AS Frequency
FROM orders
GROUP BY Customer_ID
""")

rfmF = pd.read_sql(query,conn)
rfmF = rfm["Frequency"]
print()
print(rfm[["Customer_ID","Frequency"]].to_string(index=False))

#Calculate Monetory

query = ("""
SELECT SUM(Sales) AS Monetary
FROM orders
GROUP BY Customer_ID
""")

rfmM = pd.read_sql(query,conn)
rfmM = rfm["Monetary"]
print()
print(rfm[["Customer_ID","Monetary"]].to_string(index=False))

# Total Revenue
query = """SELECT ROUND(SUM(Sales),2) || 'Rs' AS Total_Revenue
FROM orders"""
Total_Revenue = pd.read_sql(query,conn)
print("Total Revenue")
print(Total_Revenue)

#Total Profit Margin

query = ("""
SELECT 
    ROUND(SUM(Profit)/SUM(Sales) * 100,2) || '%'
    AS Profit_Margin
FROM orders
""")
Total_Profit_Margin = pd.read_sql(query,conn)
print("Total Profit Margin")
print(Total_Profit_Margin)

# Discount Impact Analysis

query = """SELECT 
    Discount,
    Profit as Avg_Profit
FROM orders
GROUP BY Discount
ORDER BY Discount"""

Discount_analysis = pd.read_sql(query,conn)
print(Discount_analysis[["Discount","Avg_Profit"]].to_string(index=False))

# Inventory Insights

query = """SELECT Product, SUM(Quantity) as Total_Quantity
FROM orders
GROUP BY Product
ORDER BY Total_Quantity DESC"""

Inventory_Insights = pd.read_sql(query,conn)
print(Inventory_Insights)


# Visiual Analysis
import matplotlib.pyplot as plt

query = """
SELECT 
    strftime('%Y-%m', Order_Date) AS Month,
    SUM(Sales) AS Total_Sales,
    SUM(Profit) AS Total_Profit,
    ROUND((SUM(Profit)/SUM(Sales))*100,2) AS Profit_Margin
FROM orders
GROUP BY Month
ORDER BY Month
"""

kpi_data = pd.read_sql(query, conn)

plt.figure()

plt.plot(kpi_data["Month"], kpi_data["Total_Sales"])
plt.plot(kpi_data["Month"], kpi_data["Total_Profit"])
plt.plot(kpi_data["Month"], kpi_data["Profit_Margin"])

plt.xticks(rotation=45)
plt.xlabel("Month")
plt.ylabel("Value")
plt.title("Monthly Sales, Profit & Profit Margin Trend")

plt.legend(["Sales", "Profit", "Profit Margin"])

plt.show()


# Business Recommandations
print("\n Business Recommndations \n")
print("1.Reduce high discount on low margin products\n")
print("2.Focus marketing on high value customers\n")
print("3.Promote profitable categories\n")
print("4.Retarget at-risk customers\n")

# Save New CSV File

df.to_csv("ecommerce_professional_dataset.csv",index=False)
