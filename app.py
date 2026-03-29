import streamlit as st
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ១. ការកំណត់ទំព័រ និង Branding ---
st.set_page_config(
    page_title="NextGen AI Trend Center", 
    layout="wide", 
    page_icon="🛡️"
)

# --- ២. ការកំណត់ Theme ហុងស៊ុយ (មាស និង ក្រហម) តាមរយៈ CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    h1, h2, h3 { color: #FFD700 !important; text-shadow: 2px 2px #FF4B4B; }
    [data-testid="stMetricValue"] { color: #FFD700 !important; }
    [data-testid="stMetricDelta"] { color: #FF4B4B !important; }
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
    .stTextArea textarea { border: 1px solid #FFD700 !important; background-color: #1e2130 !important; color: #ffffff !important; }
    </style>
    """, unsafe_allow_html=True)

# --- ៣. ប្រព័ន្ធគ្រប់គ្រង API Key (ការពារ Error លើកុំព្យូទ័រ និង Cloud) ---
api_key = None

try:
    # ព្យាយាមទាញយកពី Secrets (សម្រាប់ Cloud)
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    # បើរកមិនឃើញ (សម្រាប់ Local) វានឹងមិនបាញ់ Error ទេ
    pass

if not api_key:
    # បើគ្មាន Secret ទេ វានឹងឱ្យវាយបញ្ចូលក្នុង Sidebar
    api_key = st.sidebar.text_input("🔑 បញ្ចូល Gemini API Key:", type="password", help="យក Key ពី Google AI Studio")
    if not api_key:
        st.sidebar.info("💡 សូមបញ្ចូល API Key ក្នុង Sidebar ដើម្បីឱ្យ AI ដំណើរការ។")

# --- ៤. ចំណងជើង និងព័ត៌មានអាជីវកម្ម ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"**យុទ្ធសាស្ត្រមមី ធាតុភ្លើង ២០២៦** | 📅 {datetime.now().strftime('%d-%m-%Y')}")

# --- ៥. Sidebar សម្រាប់ Trend Settings ---
st.sidebar.divider()
st.sidebar.subheader("📊 កំណត់ការវិភាគ Trend")
default_kw = ["CCTV Cambodia", "UniFi Networking", "Hikvision AI", "IT Solution", "Smart Home"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_kw, default_kw)
timeframe = st.sidebar.selectbox("រយៈពេលវិភាគ:", ["now 7-d", "today 1-m", "today 3-m"])

# --- ៦. មុខងារទាញយកទិន្នន័យ (Google Trends) ---
@st.cache_data(ttl=3600)
def get_trends(keywords, tf):
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH', gprop='')
        df = pytrends.interest_over_time()
        return df
    except:
        return pd.DataFrame()

# --- ៧. មុខងារ AI Content Generator (Gemini 1.5 Flash) ---
def ai_generate_content(key, keyword, style):
    # កំណត់ Configuration ជាមួយ API Key ដែលបានបញ្ចូល
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    style_desc = "បែបកំប្លែង TikTok (Funny/Viral)" if style == "Funny" else "បែបបច្ចេកទេសសុទ្ធ (Professional/Tech)"
    prompt = f"អ្នកគឺជាអ្នកជំនាញ Marketing សម្រាប់ NextGen Byte-Tech។ សរសេរ Script វីដេអូខ្លីលើប្រធានបទ: {keyword}។ ស្ទីល: {style_desc}។ ភាសាខ្មែរ។"
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"បញ្ហាបច្ចេកទេស AI: {str(e)}"

# --- ៨. បង្ហាញលទ្ធផលលើ Dashboard ---
st.subheader("📈 និន្នាការទីផ្សារ IT នៅកម្ពុជា")
df_trends = get_trends(selected_keywords, timeframe)

if not df_trends.empty:
    num_cols = len(selected_keywords)
    if num_cols > 0:
        cols = st.columns(num_cols)
        for i, kw in enumerate(selected_keywords):
            if kw in df_trends.columns:
                latest = int(df_trends[kw].iloc[-1])
                cols[i].metric(label=kw, value=latest)
    
    fig = px.line(df_trends.reset_index(), x='date', y=selected_keywords, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("🔄 កំពុងរង់ចាំទិន្នន័យពី Google Trends...")

st.divider()

st.subheader("🤖 AI Script Generator")
col_left, col_right = st.columns([1, 2])

with col_left:
    target_kw = st.selectbox("ជ្រើសរើស Keyword គោលដៅ:", selected_keywords)
    content_style = st.radio("ជ្រើសរើសស្ទីលអត្ថបទ:", ["Funny", "Professional"])
    generate_btn = st.button("🚀 បង្កើត Script ឥឡូវនេះ")

with col_right:
    if generate_btn:
        if not api_key:
            st.error("❌ សូមបញ្ចូល API Key ជាមុនសិន!")
        else:
            with st.spinner('✨ AI កំពុងរៀបចំសំណេរ...'):
                script_out = ai_generate_content(api_key, target_kw, content_style)
                st.subheader("📝 លទ្ធផល៖")
                st.code(script_out, language="markdown")
