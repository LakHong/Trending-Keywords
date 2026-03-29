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
    api_key = st.sidebar.text_input("🔑 បញ្ចូល Gemini API Key:", type="password")

# --- ៤. Sidebar & ការកំណត់ Trend ---
st.sidebar.title("🛡️ NextGen Config")
st.sidebar.divider()

# បញ្ជី Keywords ថ្មី (បន្ថែម Dahua, Sunell និងកាត់ពាក្យបច្ចេកទេសពេកចេញ)
default_kw = ["CCTV", "Wifi Camera", "Hikvision", "Dahua", "Sunell", "Smart Home", "Ezviz"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_kw, default_kw)

time_map = {
    "៧ ថ្ងៃចុងក្រោយ (Hot Trend)": "now 7-d",
    "១ ខែចុងក្រោយ (Monthly)": "today 1-m",
    "៣ ខែចុងក្រោយ (Quarterly)": "today 3-m"
}
time_label = st.sidebar.selectbox("រយៈពេលវិភាគ:", list(time_map.keys()))
time_value = time_map[time_label]

# --- ៥. មុខងារជំនួយ (Functions) ---
@st.cache_data(ttl=3600)
def get_trends(keywords, tf):
    try:
        py_req = TrendReq(hl='en-US', tz=360)
        py_req.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
        return py_req.interest_over_time()
    except:
        return pd.DataFrame()

def ai_call(prompt):
    if not api_key: return "❌ សូមបញ្ចូល API Key!"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3-flash-preview')
        return model.generate_content(prompt).text
    except Exception as e:
        return f"⚠️ AI Error: {str(e)}"

# --- ៦. ចំណងជើងលើអេក្រង់ ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"**យុទ្ធសាស្ត្រមមី ធាតុភ្លើង ២០២៦** | 📅 {datetime.now().strftime('%d-%m-%Y')}")

# --- ៧. បង្ហាញក្រាហ្វនិន្នាការទូទៅ (កែសម្រួលដើម្បីកុំឱ្យចេញលេខ ០) ---
st.subheader(f"📈 និន្នាការទីផ្សារ: {time_label}")
df_trends = get_trends(selected_keywords, time_value)

if not df_trends.empty:
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        if kw in df_trends.columns:
            # កែសម្រួល៖ ប្រើមធ្យមភាគ (mean) ជំនួសឱ្យតម្លៃចុងក្រោយ ដើម្បីឱ្យលេខលោតស្អាត
            avg_val = int(df_trends[kw].mean()) 
            cols[i].metric(label=kw, value=avg_val)
    
    fig = px.line(df_trends.reset_index(), x='date', y=selected_keywords, template="plotly_dark")
    st.plotly_chart(fig, width='stretch')
else:
    st.warning("⚠️ Google Trends កំពុងមមាញឹក។ សូមរង់ចាំ ១ នាទី រួច Refresh ទំព័រឡើងវិញ។")

# --- ៨. ការប្រៀបធៀប Brand (Market Share) ---
st.divider()
st.subheader("⚔️ ការប្រៀបធៀបកេរ្តិ៍ឈ្មោះ Brand (Market Share)")

brand_comparison = st.multiselect(
    "ជ្រើសរើស Brand ដើម្បីប្រៀបធៀប:", 
    ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou", "Ubiquiti"],
    default=["Hikvision", "Dahua", "Sunell"]
)

df_compare = pd.DataFrame() # បង្កើតទុកជាមុនការពារ Error

if brand_comparison:
    try:
        py_comp = TrendReq(hl='en-US', tz=360)
        py_comp.build_payload(brand_comparison, cat=0, timeframe=time_value, geo='KH')
        df_compare = py_comp.interest_over_time()
        
        if not df_compare.empty:
            avg_trends = df_compare[brand_comparison].mean().reset_index()
            avg_trends.columns = ['Brand', 'Search Volume']
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig_pie = px.pie(avg_trends, values='Search Volume', names='Brand', 
                                title="ចំណែកនៃការស្វែងរកក្នុងទីផ្សារ", hole=0.4, 
                                template="plotly_dark")
                st.plotly_chart(fig_pie, width='stretch')
            with c2:
                top_b = avg_trends.loc[avg_trends['Search Volume'].idxmax(), 'Brand']
                st.success(f"🏆 **{top_b}** ឈានមុខគេ!")
                
                if st.button("📋 វិភាគយុទ្ធសាស្ត្រដោយ AI"):
                    p = f"វិភាគទិន្នន័យ Brand IT ខ្មែរ: {avg_trends.to_dict()}។ សរសេរយុទ្ធសាស្ត្រលក់ឱ្យ NextGen Byte-Tech ជាខេមរភាសា។"
                    st.info(ai_call(p))
    except:
        st.error("⚠️ មិនអាចទាញយកទិន្នន័យប្រៀបធៀបបានទេ។ សូមផ្ដោតលើក្រាហ្វខាងលើសិន។")

# --- ៩. AI Script Generator ---
st.divider()
st.subheader("🤖 NextGen AI Script Generator")
col_l, col_r = st.columns([1, 2])

with col_l:
    target = st.selectbox("រើស Keyword សម្រាប់ Content:", selected_keywords)
    style = st.radio("ស្ទីលសំណេរ:", ["កំប្លែង TikTok (Funny)", "អាជីពទុកចិត្តបាន (Professional)"])
    if st.button("🚀 បង្កើត Script ឥឡូវនេះ"):
        with st.spinner('✨ កំពុងរៀបចំ...'):
            full_prompt = f"សរសេរ Script TikTok បែប Soft-sell សម្រាប់ហាង NextGen Byte-Tech លើប្រធានបទ {target} ស្ទីល {style} ជាភាសាខ្មែរ។"
            st.session_state['ai_script'] = ai_call(full_prompt)

with col_r:
    if 'ai_script' in st.session_state:
        st.code(st.session_state['ai_script'], language="markdown")
