import streamlit as st
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

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
    div.stButton > button {
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

# --- ៤. មុខងារ Google Trends (បង្កើនស្ថេរភាព) ---
@st.cache_data(ttl=3600)
def get_trends(keywords, tf):
    if not keywords: return pd.DataFrame()
    try:
        # បន្ថែមការកំណត់ដោះស្រាយបញ្ហា Downcasting តាម Log
        pd.set_option('future.no_silent_downcasting', True)
        pytrends = TrendReq(hl='en-US', tz=360, timeout=(10,25))
        pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
        df = pytrends.interest_over_time()
        if not df.empty:
            return df.drop(labels=['isPartial'], axis='columns', errors='ignore')
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# --- ៥. មុខងារ AI Analysis ---
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
st.write(f"**យុទ្ធសាស្ត្រមមី ធាតុភ្លើង ២០២៦** | 📅 {datetime.now().strftime('%d-%m-%Y')}")

# --- ៧. Sidebar Config ---
st.sidebar.subheader("📊 ការកំណត់វិភាគ")
time_map = {"៧ ថ្ងៃចុងក្រោយ": "now 7-d", "១ ខែចុងក្រោយ": "today 1-m", "៣ ខែចុងក្រោយ": "today 3-m"}
time_label = st.sidebar.selectbox("រយៈពេលវិភាគ:", list(time_map.keys()))
timeframe = time_map[time_label]

# --- ៨. ផ្នែកនិន្នាការទូទៅ ---
st.subheader(f"📈 និន្នាការទីផ្សារ: {time_label}")
general_kw = ["CCTV", "Wifi Camera", "Smart Home", "Networking"]
df_gen = get_trends(general_kw, timeframe)

if not df_gen.empty:
    fig_gen = px.line(df_gen.reset_index(), x='date', y=general_kw, template="plotly_dark")
    st.plotly_chart(fig_gen, width='stretch')
else:
    st.warning("⚠️ មិនអាចទាញទិន្នន័យបាន (Google Busy)។ សូមរង់ចាំ ២ នាទី រួច Refresh។")

st.divider()

# --- ៩. ផ្នែកប្រៀបធៀប Brand (ថ្មី!) ---
st.subheader("⚔️ Brand Market Share Comparison (Cambodia)")
brands = ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"]
selected_brands = st.multiselect("ជ្រើសរើស Brand ដើម្បីប្រៀបធៀប:", brands, default=["Hikvision", "Dahua", "Sunell"])

df_brand = get_trends(selected_brands, timeframe)

if not df_brand.empty:
    # គណនាមធ្យមភាគដើម្បីធ្វើ Pie Chart
    avg_vals = df_brand[selected_brands].mean().reset_index()
    avg_vals.columns = ['Brand', 'Search Volume']
    
    col_chart, col_insight = st.columns([2, 1])
    
    with col_chart:
        fig_pie = px.pie(avg_vals, values='Search Volume', names='Brand', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.YlOrRd,
                         template="plotly_dark")
        st.plotly_chart(fig_pie, width='stretch')
    
    with col_insight:
        top_brand = avg_vals.loc[avg_vals['Search Volume'].idxmax(), 'Brand']
        st.success(f"🏆 **{top_brand}** កំពុងមានប្រជាប្រិយភាពបំផុត!")
        
        if st.button("📋 វិភាគយុទ្ធសាស្ត្រលក់"):
            with st.spinner('🤖 AI កំពុងវិភាគ...'):
                insight_prompt = f"វិភាគទិន្នន័យ Brand IT នៅខ្មែរ: {avg_vals.to_dict()}។ ផ្ដល់យោបល់ឱ្យហាង NextGen Byte-Tech ថាគួរផ្ដោតលើ Brand ណា និងរៀបចំការលក់យ៉ាងដូចម្ដេច? (ឆ្លើយជាខ្មែរ)"
                st.info(ai_call(insight_prompt))
else:
    st.info("💡 កំពុងរង់ចាំការជ្រើសរើស Brand ឬការអនុញ្ញាតពី Google...")

st.divider()

# --- ១០. AI Script Generator ---
st.subheader("🤖 AI Script Generator")
col_left, col_right = st.columns([1, 2])

with col_left:
    target_kw = st.selectbox("ជ្រើសរើស Keyword:", selected_keywords)
    content_style = st.radio("ជ្រើសរើសស្ទីល:", ["Funny", "Professional"])
    generate_btn = st.button("🚀 បង្កើត Script ឥឡូវនេះ")

with col_right:
    if generate_btn:
        if not api_key:
            st.error("❌ សូមបញ្ចូល API Key!")
        else:
            with st.spinner('✨ AI កំពុងរៀបចំ...'):
                script_out = ai_generate_content(api_key, target_kw, content_style)
                st.code(script_out, language="markdown")
