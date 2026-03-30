import streamlit as st
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime
import time
import random

# --- ១. ការកំណត់ទំព័រ និង Branding ---
st.set_page_config(
    page_title="NextGen AI Trend Center", 
    layout="wide", 
    page_icon="🛡️"
)

# --- ២. ការកំណត់ Theme ហុងស៊ុយ (មាស និង ក្រហម) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 2px 2px #FF4B4B; }
    [data-testid="stMetricValue"] { color: #FFD700 !important; }
    div.stButton > button:first-child {
        background-color: #FFD700 !important;
        color: #000000 !important;
        border-radius: 12px;
        border: 2px solid #FF4B4B !important;
        font-weight: bold;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #FF4B4B !important;
        color: #FFFFFF !important;
    }
    .stTextArea textarea { border: 1px solid #FFD700 !important; background-color: #1e2130 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ៣. ប្រព័ន្ធគ្រប់គ្រង API Key ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    api_key = st.sidebar.text_input("🔑 Gemini API Key:", type="password")

# --- ៤. Sidebar Config ---
st.sidebar.title("🛡️ NextGen Config")
# ប្រើ Keywords សាមញ្ញៗដើម្បីកាត់បន្ថយ Error
default_kw = ["CCTV", "Wifi Camera", "Hikvision", "Dahua", "Sunell", "Smart Home", "Ezviz"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_kw, default_kw)

time_map = {
    "៧ ថ្ងៃចុងក្រោយ (Hot Trend)": "now 7-d",
    "១ ខែចុងក្រោយ (Monthly)": "today 1-m",
    "៣ ខែចុងក្រោយ (Quarterly)": "today 3-m"
}
time_label = st.sidebar.selectbox("រយៈពេលវិភាគ:", list(time_map.keys()))
time_value = time_map[time_label]

# --- ៥. មុខងារទាញទិន្នន័យដែលមានប្រព័ន្ធការពារ (get_trends_safe) ---
@st.cache_data(ttl=1800)
def get_trends_safe(keywords, tf):
    if not keywords: return pd.DataFrame()
    
    # បញ្ជី User-Agent ដើម្បីបញ្ឆោត Google
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    for attempt in range(5):
        try:
            # ជ្រើសរើស User-Agent ដោយចៃដន្យ
            headers = {'User-Agent': random.choice(user_agents)}
            
            # បង្កើត Request ជាមួយ Timeout
            py_req = TrendReq(hl='en-US', tz=360, timeout=(15, 30), backoff_factor=0.2)
            py_req.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            data = py_req.interest_over_time()
            
            if not data.empty:
                return data.drop(labels=['isPartial'], axis='columns', errors='ignore')
            
            # បើទិន្នន័យទទេ រង់ចាំបន្តិចតាម Exponential Backoff
            wait_time = (2 ** attempt) + random.random()
            time.sleep(wait_time)
            
        except Exception:
            # បើជាប់ Error ត្រូវរង់ចាំយូរជាងមុន
            wait_time = (3 ** attempt) + random.random()
            time.sleep(wait_time)
            continue
            
    return pd.DataFrame()

def ai_call(prompt):
    if not api_key: return "❌ សូមបញ្ចូល API Key!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# --- ៦. Main UI ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"📅 {datetime.now().strftime('%d-%m-%Y')}")

# បង្ហាញក្រាហ្វនិន្នាការ
st.subheader(f"📈 និន្នាការទីផ្សារ: {time_label}")
df_trends = get_trends_safe(selected_keywords, time_value)

if not df_trends.empty:
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        if kw in df_trends.columns:
            # បង្ហាញតម្លៃមធ្យមភាគដើម្បីកុំឱ្យចេញលេខ ០
            avg_val = int(df_trends[kw].mean()) 
            cols[i].metric(label=kw, value=avg_val)
    
    fig = px.line(df_trends.reset_index(), x='date', y=[k for k in selected_keywords if k in df_trends.columns], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    # បង្ហាញសារណែនាំនៅពេល Google Block
    st.error("🚫 Google កំពុងរឹតត្បិតការចូលប្រើបណ្តោះអាសន្ន (Rate Limit)។")
    st.info("💡 ដំណោះស្រាយ៖ សូមរង់ចាំ ២ ទៅ ៥ នាទី រួចចុច Refresh ក្នុង Browser ឡើងវិញ។")

# --- ៧. ប្រៀបធៀប Brand & AI Insight ---
st.divider()
st.subheader("⚔️ Market Share Comparison")
brand_comparison = st.multiselect("ជ្រើសរើស Brand:", ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"], default=["Hikvision", "Dahua", "Sunell"])

# បង្កើត DataFrame ទទេទុកជាមុនដើម្បីការពារ NameError
df_compare = get_trends_safe(brand_comparison, time_value)

if not df_compare.empty:
    avg_trends = df_compare[brand_comparison].mean().reset_index()
    avg_trends.columns = ['Brand', 'Search Volume']
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_pie = px.pie(avg_trends, values='Search Volume', names='Brand', hole=0.4, template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        top_b = avg_trends.loc[avg_trends['Search Volume'].idxmax(), 'Brand']
        st.success(f"🏆 **{top_b}** ឈានមុខគេ!")
        if st.button("📋 វិភាគយុទ្ធសាស្ត្រ"):
            st.info(ai_call(f"វិភាគ Brand IT ខ្មែរ: {avg_trends.to_dict()}។ ផ្ដល់យោបល់លក់ឱ្យ NextGen Byte-Tech ជាភាសាខ្មែរ។"))
else:
    st.warning("⚠️ មិនទាន់អាចទាញទិន្នន័យប្រៀបធៀបបានទេ (Google Busy)។")

# --- ៨. AI Script Generator ---
st.divider()
st.subheader("🤖 AI Script Generator")
target = st.selectbox("រើស Keyword សម្រាប់ផលិត Content:", selected_keywords if selected_keywords else ["CCTV"])
if st.button("🚀 បង្កើត Script ឥឡូវនេះ"):
    with st.spinner('✨ កំពុងរៀបចំ...'):
        st.session_state['ai_script'] = ai_call(f"សរសេរ Script TikTok បែបទាក់ទាញសម្រាប់ហាង NextGen Byte-Tech លើប្រធានបទ {target} ជាភាសាខ្មែរ។")

if 'ai_script' in st.session_state:
    st.code(st.session_state['ai_script'], language="markdown")
