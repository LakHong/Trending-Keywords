import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime

# កែសម្រួលតាម Log: បំបាត់ FutureWarning របស់ Pandas
pd.set_option('future.no_silent_downcasting', True)

import google.generativeai as genai
from pytrends.request import TrendReq
import plotly.express as px

# --- ១. ការកំណត់ទំព័រ (Update តាម Log 2026) ---
st.set_page_config(page_title="NextGen AI Trend Center", layout="wide", page_icon="🛡️")

# --- ២. Theme ហុងស៊ុយ ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 2px 2px #FF4B4B; }
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; width: 100%; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- ៣. API Key ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# --- ៤. មុខងារទាញទិន្នន័យ (Robust Version) ---
@st.cache_data(ttl=1800)
def get_trends_safe(keywords, tf):
    if not keywords: return pd.DataFrame()
    for attempt in range(3):
        try:
            py_req = TrendReq(hl='en-US', tz=360, timeout=(20, 45))
            py_req.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            data = py_req.interest_over_time()
            if not data.empty:
                return data.drop(labels=['isPartial'], axis='columns', errors='ignore')
            time.sleep(random.uniform(3, 7))
        except:
            time.sleep(10)
            continue
    return pd.DataFrame()

# --- ៥. Main UI ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.sidebar.title("⚙️ Config")
default_kw = ["CCTV", "Hikvision", "Dahua", "Sunell", "Smart Home"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_kw, default_kw)

# បង្ហាញក្រាហ្វ
st.subheader("📈 និន្នាការទីផ្សារកម្ពុជា")
df_trends = get_trends_safe(selected_keywords, "today 1-m")

if not df_trends.empty:
    fig = px.line(df_trends.reset_index(), x='date', y=[k for k in selected_keywords if k in df_trends.columns], template="plotly_dark")
    # កែសម្រួលតាម Log: ប្រើ width='stretch' ជំនួស use_container_width
    st.plotly_chart(fig, width='stretch')
else:
    st.error("🚫 Google Trends កំពុងជាប់រវល់ (Rate Limit)។")
    st.info("💡 ដំណោះស្រាយ៖ បងត្រូវរង់ចាំ ៥-១០ នាទី រួច Reboot App ក្នុង Streamlit Dashboard។")

# --- ៦. AI Script ---
st.divider()
st.subheader("🤖 AI Script Generator")
if st.button("🚀 បង្កើត Script TikTok"):
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        prompt = f"សរសេរ Script TikTok សម្រាប់ហាង NextGen Byte-Tech លើប្រធានបទ {selected_keywords[0] if selected_keywords else 'CCTV'} ជាភាសាខ្មែរ។"
        st.write(model.generate_content(prompt).text)
    else:
        st.warning("Please enter API Key")
