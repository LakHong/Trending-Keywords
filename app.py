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

# --- ៣. ប្រព័ន្ធគ្រប់គ្រង API Key (ការពារ Error លើកុំព្យូទ័រ) ---
api_key = None

try:
    # ព្យាយាមទាញយកពី Secrets (សម្រាប់ Cloud)
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except:
    # បើរកមិនឃើញ (សម្រាប់ Local) វានឹងមិនបាញ់ Error ទេ តែទុកឱ្យអ្នកបញ្ចូលក្នុង Sidebar
    pass

if not api_key:
    api_key = st.sidebar.text_input("🔑 បញ្ចូល Gemini API Key:", type="password", help="យក Key ពី Google AI Studio")
    if not api_key:
        st.sidebar.info("💡 នៅលើកុំព្យូទ័រផ្ទាល់ខ្លួន សូមបញ្ចូល Key ក្នុង Sidebar ដើម្បីឱ្យ AI ដើរ។")

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

# --- ៧. មុខងារ AI Content Generator (Gemini) ---
def ai_generate_content(key, keyword, style):
    genai.configure(api_key=key)
    
    # កែសម្រួលមកប្រើឈ្មោះពេញលេញ និងកំណត់ឱ្យប្រើ version ចុងក្រោយ
    model = genai.GenerativeModel(model_name="gemini-1.5-flash") 
    
    style_desc = "បែបកំប្លែង TikTok" if style == "Funny" else "បែបអាជីព បច្ចេកទេស"
    prompt = f"អ្នកគឺជាអ្នកជំនាញ Marketing សម្រាប់ NextGen Byte-Tech។ សរសេរ Script វីដេអូ TikTok លើប្រធានបទ: {keyword}។ ស្ទីល: {style_desc}។ ភាសាខ្មែរ។"
    
    # បន្ថែមការត្រួតពិនិត្យការឆ្លើយតប
    response = model.generate_content(prompt)
    return response.text

# --- ៨. បង្ហាញលទ្ធផលលើ Dashboard ---
st.subheader("📈 និន្នាការទីផ្សារ IT នៅកម្ពុជា")
df_trends = get_trends(selected_keywords, timeframe)

if not df_trends.empty:
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        latest = int(df_trends[kw].iloc[-1])
        cols[i].metric(label=kw, value=latest)
    fig = px.line(df_trends.reset_index(), x='date', y=selected_keywords, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("🤖 AI Script Generator")
col_left, col_right = st.columns([1, 2])
with col_left:
    target_kw = st.selectbox("ជ្រើសរើស Keyword:", selected_keywords)
    content_style = st.radio("ជ្រើសរើសស្ទីល:", ["Funny", "Professional"])
    generate_btn = st.button("🚀 បង្កើត Script ឥឡូវនេះ")

with col_right:
    if generate_btn:
        if not api_key:
            st.error("❌ សូមបញ្ចូល API Key ក្នុង Sidebar!")
        else:
            with st.spinner('✨ AI កំពុងរៀបចំ...'):
                try:
                    script_out = ai_generate_content(api_key, target_kw, content_style)
                    st.text_area("លទ្ធផល៖", script_out, height=350)
                except Exception as e:
                    st.error(f"Error: {e}")
