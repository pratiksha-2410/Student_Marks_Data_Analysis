# Import Labraries

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Create Database Connection
conn = sqlite3.connect("Customer_Churn.db")
cursor = conn.cursor()

# Load Dataset

df = pd.read_csv("ecommerce_customer_churn_dataset.csv")
df.to_sql("orders",conn,if_exists="append",index=False)
print(df.head(10))

