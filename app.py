import streamlit as st
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- ១. ការកំណត់ទំព័រ ---
st.set_page_config(page_title="NextGen AI Trend Center", layout="wide", page_icon="🛡️")

# --- ២. Theme ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 2px 2px #FF4B4B; }
    [data-testid="stMetricValue"] { color: #FFD700 !important; }
    div.stButton > button { background-color: #FFD700 !important; color: #000 !important; font-weight: bold; width: 100%; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- ៣. ប្រព័ន្ធគ្រប់គ្រង API Key ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# --- ៤. បង្កើតអថេរបម្រុងការពារ Error (Crucial Fix) ---
df_trends = pd.DataFrame()
df_compare = pd.DataFrame()

# --- ៥. Sidebar ---
st.sidebar.title("🛡️ NextGen Config")
default_kw = ["CCTV", "Wifi Camera", "Hikvision", "Dahua", "Sunell", "Smart Home", "Ezviz"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_kw, default_kw)

time_map = {"៧ ថ្ងៃចុងក្រោយ": "now 7-d", "១ ខែចុងក្រោយ": "today 1-m", "៣ ខែចុងក្រោយ": "today 3-m"}
time_label = st.sidebar.selectbox("រយៈពេលវិភាគ:", list(time_map.keys()))
time_value = time_map[time_label]

# --- ៦. មុខងារទាញទិន្នន័យ (ជំនាន់ការពារ IP Block) ---
@st.cache_data(ttl=1800)
def get_trends_safe(keywords, tf):
    if not keywords: return pd.DataFrame()
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/119.0.0.0"
    ]
    for attempt in range(3): # ព្យាយាម ៣ ដង
        try:
            py_req = TrendReq(hl='en-US', tz=360, timeout=(10, 25))
            py_req.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            data = py_req.interest_over_time()
            if not data.empty:
                return data.drop(labels=['isPartial'], axis='columns', errors='ignore')
            time.sleep(random.uniform(1, 3))
        except:
            time.sleep(5) # បើជាប់ Block ឱ្យសម្រាក ៥ វិនាទី
            continue
    return pd.DataFrame()

def ai_call(prompt):
    if not api_key: return "❌ សូមបញ្ចូល API Key!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        return model.generate_content(prompt).text
    except Exception as e: return f"⚠️ AI Error: {str(e)}"

# --- ៧. បង្ហាញលទ្ធផល ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"📅 {datetime.now().strftime('%d-%m-%Y')}")

# ផ្នែកនិន្នាការ
st.subheader(f"📈 និន្នាការទីផ្សារ: {time_label}")
df_trends = get_trends_safe(selected_keywords, time_value)

if not df_trends.empty:
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        if kw in df_trends.columns:
            avg_val = int(df_trends[kw].mean())
            cols[i].metric(label=kw, value=avg_val)
    st.plotly_chart(px.line(df_trends.reset_index(), x='date', y=[k for k in selected_keywords if k in df_trends.columns], template="plotly_dark"), use_container_width=True)
else:
    st.error("🚫 Google កំពុងរឹតត្បិត IP របស់ Server Streamlit។")
    st.info("💡 ដំណោះស្រាយ៖ សូមកុំប្តូរ Keyword ញឹកពេក។ រង់ចាំ ២ នាទី រួចចុច Refresh Browser។")

# ផ្នែកប្រៀបធៀប (ដោះស្រាយ NameError)
st.divider()
st.subheader("⚔️ Market Share Comparison")
brand_comparison = st.multiselect("ជ្រើសរើស Brand:", ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"], default=["Hikvision", "Dahua", "Sunell"])

if brand_comparison:
    df_compare = get_trends_safe(brand_comparison, time_value)
    
    if not df_compare.empty:
        avg_trends = df_compare[brand_comparison].mean().reset_index()
        avg_trends.columns = ['Brand', 'Search Volume']
        c1, c2 = st.columns([2, 1])
        with c1:
            st.plotly_chart(px.pie(avg_trends, values='Search Volume', names='Brand', hole=0.4, template="plotly_dark"), use_container_width=True)
        with c2:
            st.success(f"🏆 {avg_trends.loc[avg_trends['Search Volume'].idxmax(), 'Brand']} ឈានមុខ!")
            if st.button("📋 វិភាគយុទ្ធសាស្ត្រ"):
                st.info(ai_call(f"វិភាគ Brand: {avg_trends.to_dict()} សម្រាប់ NextGen Byte-Tech ជាខ្មែរ។"))
    else:
        st.warning("⚠️ មិនទាន់មានទិន្នន័យប្រៀបធៀប (Google Busy)។")

# --- ៨. AI Script ---
st.divider()
st.subheader("🤖 AI Script Generator")
target = st.selectbox("រើស Keyword:", selected_keywords if selected_keywords else ["CCTV"])
if st.button("🚀 បង្កើត Script"):
    st.session_state['ai_script'] = ai_call(f"សរសេរ Script TikTok សម្រាប់ NextGen Byte-Tech លើ {target} ជាខ្មែរ។")
if 'ai_script' in st.session_state:
    st.code(st.session_state['ai_script'], language="markdown")
