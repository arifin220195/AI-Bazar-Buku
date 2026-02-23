import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. KONEKSI KE API GEMINI
try:
    # Mengambil key dari menu Secrets Streamlit
    api_key = st.secrets["api_key"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("❌ Error: API Key tidak ditemukan di menu Secrets!")

# 2. MEMBACA DATA BUKU (Mencari file bernama 'data')
@st.cache_data
def load_data():
    if os.path.exists('data.csv'):
        return pd.read_csv('data.csv')
    elif os.path.exists('data.xlsx'):
        return pd.read_excel('data.xlsx')
    else:
        return None

df = load_data()

if df is not None:
    df['Stok'] = 50 # Menambahkan stok otomatis
    # Sesuaikan kolom dengan file kamu (Judul Buku, Harga Normal, Harga Diskon)
    stok_info = df.to_string(index=False)
    
    # 3. SETTING INSTRUKSI AI
    instruction = f"""
    Kamu adalah asisten Bazar Buku 2025 yang ramah.
    DATA BUKU:
    {stok_info}
    
    TUGAS:
    - Jawab pertanyaan harga & stok dengan ceria.
    - Fokus pada 'Harga Diskon'.
    - Jika ada yang beli, minta Nama & Judul Buku.
    - Akhiri dengan kode [ORDER: Nama | Judul] jika data lengkap.
    """
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
else:
    st.error("❌ Error: File 'data.csv' atau 'data.xlsx' tidak ditemukan di GitHub!")

# 4. TAMPILAN APLIKASI
st.set_page_config(page_title="BukuBot Bazar", page_icon="📚")
st.title("📚 BukuBot Bazar 2025")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Tanya harga atau pesan buku..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    response = model.generate_content(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
