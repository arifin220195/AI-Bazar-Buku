import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. AMBIL API KEY DARI SECRETS
try:
    api_key = st.secrets["api_key"]
    genai.configure(api_key=api_key)
except:
    st.error("❌ API Key 'api_key' tidak ditemukan di Secrets Streamlit!")

# 2. BACA FILE EXCEL
@st.cache_data
def load_excel():
    # Mencari file .xlsx di folder GitHub
    for file in os.listdir('.'):
        if file.endswith('.xlsx'):
            return pd.read_excel(file)
    return None

df = load_excel()

if df is not None:
    df['Stok'] = 50 # Stok otomatis 50
    # Mengambil kolom: Judul Buku, Harga Normal, Harga Diskon
    stok_info = df.to_string(index=False)
    
    # 3. SETTING AI
    instruction = f"Kamu asisten bazar ramah. Stok: {stok_info}. Jika pesan, minta Nama & Judul. Beri kode [ORDER: Nama | Judul]"
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
else:
    st.error("❌ File .xlsx tidak ditemukan di GitHub!")

# 4. TAMPILAN CHAT
st.title("📚 BukuBot Bazar 2025")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya harga buku..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = model.generate_content(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
