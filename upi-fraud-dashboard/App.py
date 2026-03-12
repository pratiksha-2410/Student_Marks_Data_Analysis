import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("UPI Digital Fraud Analysis Dashboard")

df = pd.read_csv("upi_data.csv")

st.subheader("Dataset Preview")
st.write(df.head())

st.subheader("Transaction Amount Distribution")

fig, ax = plt.subplots()
ax.hist(df["amount"], bins=20)

st.pyplot(fig)