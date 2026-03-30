import streamlit as st
import google.generativeai as genai # នៅរក្សាទុកសិនតាមកូដបង តែប្តូររបៀបប្រើបន្តិច
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- ១. ការកំណត់ទំព័រ (Update តាម Log: width='stretch') ---
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

# --- ៤. មុខងារទាញទិន្នន័យ (កែសម្រួលតាម FutureWarning ក្នុង Log) ---
@st.cache_data(ttl=1800)
def get_trends_safe(keywords, tf):
    if not keywords: return pd.DataFrame()
    # បន្ថែមការកំណត់ដោះស្រាយបញ្ហា Downcasting ក្នុង Log
    pd.set_option('future.no_silent_downcasting', True) 
    
    for attempt in range(3):
        try:
            py_req = TrendReq(hl='en-US', tz=360, timeout=(15, 45))
            py_req.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            data = py_req.interest_over_time()
            if not data.empty:
                return data.drop(labels=['isPartial'], axis='columns', errors='ignore')
            time.sleep(random.uniform(2, 5))
        except:
            time.sleep(10)
            continue
    return pd.DataFrame()

def ai_call(prompt):
    if not api_key: return "❌ សូមបញ្ចូល API Key!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        return model.generate_content(prompt).text
    except Exception as e: return f"⚠️ AI Error: {str(e)}"

# --- ៥. បង្ហាញលទ្ធផល ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"📅 {datetime.now().strftime('%d-%m-%Y')}")

# ផ្នែកនិន្នាការ (Update: ប្រើ width='stretch' តាម Log)
st.subheader(f"📈 និន្នាការទីផ្សារ")
df_trends = get_trends_safe(["CCTV", "Wifi Camera", "Smart Home"], "today 1-m")

if not df_trends.empty:
    fig = px.line(df_trends.reset_index(), x='date', y=df_trends.columns, template="plotly_dark")
    # កែសម្រួលតាម Log: use_container_width -> width='stretch'
    st.plotly_chart(fig, width='stretch') 
else:
    st.error("🚫 Google Trends កំពុងជាប់រវល់។")

# --- ៦. ផ្នែក AI Script ---
st.divider()
st.subheader("🤖 AI Script Generator")
if st.button("🚀 បង្កើត Script TikTok"):
    with st.spinner('✨ កំពុងរៀបចំ...'):
        result = ai_call("សរសេរ Script TikTok សម្រាប់ហាង NextGen Byte-Tech លើប្រធានបទ CCTV ជាភាសាខ្មែរ។")
        st.code(result, language="markdown")
