import streamlit as st
from dotenv import load_dotenv

load_dotenv()          # reads .env if it exists

st.title("DropScout – Is this product drop-shipped?")

url = st.text_input("Paste an Amazon or Etsy URL:")

if url:
    st.success(f"You entered: {url}")
    st.info("🚧 Detection engine coming soon!")
else:
    st.write("Enter a product link to begin.")