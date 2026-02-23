import streamlit as st
import google.generativeai as genai
import pandas as pd
import os

# 1. KONFIGURASI API (Ambil dari Secrets Streamlit)
try:
    api_key = st.secrets["api_key"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("❌ API Key tidak ditemukan! Pastikan sudah isi 'api_key' di menu Secrets.")

# 2. MEMBACA DATA CSV
@st.cache_data
def load_data():
    # Pastikan file di GitHub kamu namanya 'bazar buku.csv'
    file_name = 'buku.csv'
    if os.path.exists(file_name):
        # Membaca CSV (Pandas otomatis mengenali koma sebagai pemisah)
        return pd.read_csv(file_name)
    else:
        return None

df = load_data()

if df is not None:
    # Mengambil semua data untuk diberikan ke AI
    # Kolom: Judul Buku, Harga Normal, Harga Diskon, Stock
    stok_info = df.to_string(index=False)
    
    # 3. SETTING INSTRUKSI AI
    instruction = f"""
    Kamu adalah asisten penjualan ramah di Bazar Buku 2025.
    Gunakan data berikut untuk menjawab pelanggan:
    
    {stok_info}
    
    TUGAS:
    1. Beritahu harga diskon dengan semangat.
    2. Jika stok (Stock) masih 50, katakan "Stok masih tersedia, tapi cepat habis!".
    3. Jika ada yang mau pesan, kamu WAJIB meminta: Nama Lengkap & Judul Buku.
    4. Setelah mereka memberi Nama & Judul, tulis kode ini di akhir: [ORDER: Nama | Judul]
    """
    model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction)
else:
    st.error("❌ File 'bazar buku.csv' tidak ditemukan di GitHub kamu!")

# 4. TAMPILAN DASHBOARD
st.set_page_config(page_title="BukuBot Bazar", page_icon="📚")
st.title("📚 BukuBot Bazar 2025")
st.markdown("---")

# Session State untuk simpan chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Munculkan pesan chat lama
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input Chat
if prompt := st.chat_input("Tanya harga buku..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Respon dari AI
    try:
        response = model.generate_content(prompt)
        bot_text = response.text
        
        with st.chat_message("assistant"):
            st.markdown(bot_text)
        st.session_state.messages.append({"role": "assistant", "content": bot_text})
    except Exception as e:
        st.error(f"AI Error: {e}")

