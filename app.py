import streamlit as st
import google.generativeai as genai
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- ១. ការកំណត់ទំព័រ និង Branding ---
st.set_page_config(page_title="NextGen AI Trend Center", layout="wide", page_icon="🛡️")

# Custom CSS ដើម្បីឱ្យមើលទៅបែប Tech & Modern
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; border: 1px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ NextGen Byte-Tech: AI Intelligence Center")
st.write(f"**យុទ្ធសាស្ត្រឆ្នាំមមី ធាតុភ្លើង ២០២៦** | កាលបរិច្ឆេទ៖ {datetime.now().strftime('%d-%m-%Y')}")

# --- ២. Sidebar Configuration ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100)
st.sidebar.header("⚙️ ការកំណត់ប្រព័ន្ធ")

api_key = st.sidebar.text_input("បញ្ចូល Gemini API Key:", type="password", help="យក Key ពី Google AI Studio")

st.sidebar.divider()
st.sidebar.subheader("📊 ការកំណត់ Trend")
default_kw = ["CCTV Cambodia", "UniFi Networking", "Hikvision AI", "IT Solution", "Smart Home"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords តាមដាន:", default_kw, default_kw)
timeframe = st.sidebar.selectbox("រយៈពេលវិភាគ:", ["now 7-d", "today 1-m", "today 3-m"])

# --- ៣. មុខងារទាញយកទិន្នន័យ (Google Trends) ---
@st.cache_data(ttl=3600) # រក្សាទិន្នន័យទុក ១ ម៉ោងដើម្បីកុំឱ្យ Google Block
def get_trends(keywords, tf):
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH', gprop='')
        df = pytrends.interest_over_time()
        related = pytrends.related_queries()
        return df, related
    except:
        return pd.DataFrame(), {}

# --- ៤. មុខងារ AI Content Generator (Gemini) ---
def ai_generate_content(key, keyword, style):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-pro')
    
    style_prompt = ""
    if style == "កំប្លែង និងទាក់ទាញ (Funny/Viral)":
        style_prompt = "សរសេរបែបកំប្លែងៗ ប្រើភាសាយុវវ័យ TikTok ចូលចិត្ត មានការប្រៀបធៀបប្លែកៗ ប៉ុន្តែនៅតែលក់ដាច់។"
    else:
        style_prompt = "សរសេរបែបអាជីព (Professional) ផ្ដោតលើបច្ចេកទេស និងទំនុកចិត្ត ស័ក្តិសមសម្រាប់ម្ចាស់អាជីវកម្ម និងក្រុមហ៊ុន។"

    prompt = f"""
    អ្នកគឺជាអ្នកឯកទេស Content Marketing សម្រាប់ក្រុមហ៊ុន "{st.session_state.get('biz_name', 'NextGen Byte-Tech')}" នៅកម្ពុជា។
    សូមសរសេរ Script វីដេអូ TikTok ខ្លី (ក្រោម ៦០ វិនាទី) លើប្រធានបទ: {keyword}។
    
    លក្ខខណ្ឌ៖
    1. ស្ទីល៖ {style_prompt}
    2. ភាសា៖ ខ្មែរ ១០០%។
    3. រចនាសម្ព័ន្ធ៖ មាន Hook (ទាក់ទាញ), Body (ខ្លឹមសារបច្ចេកទេសខ្លីៗ), និង Call to Action (ឱ្យទាក់ទងមក Telegram)។
    4. បន្ថែម Hashtags សមស្របនឹងឆ្នាំ ២០២៦។
    """
    response = model.generate_content(prompt)
    return response.text

# --- ៥. បង្ហាញ Dashboard ---

# ផ្នែកទី ១៖ ការវិភាគ Trend
st.subheader("📈 វិភាគសន្ទុះទីផ្សារនៅកម្ពុជា")
df_trends, rel_queries = get_trends(selected_keywords, timeframe)

if not df_trends.empty:
    # បង្ហាញ Metrics
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        val = int(df_trends[kw].iloc[-1])
        diff = int(df_trends[kw].iloc[-1] - df_trends[kw].iloc[-2])
        cols[i].metric(label=kw, value=val, delta=f"{diff}%")

    # ក្រាហ្វ Plotly
    fig = px.line(df_trends.reset_index(), x='date', y=selected_keywords, 
                  title="Trend Activity (Google/TikTok Proxy Data)",
                  template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ មិនអាចទាញយកទិន្នន័យបានទេ (Google Trends អាចនឹងរវល់)។ សូមព្យាយាម Refresh ម្តងទៀត។")

st.divider()

# ផ្នែកទី ២៖ AI Script Generator
st.subheader("🤖 NextGen AI Script Writer")
col_a, col_b = st.columns([1, 2])

with col_a:
    st.write("រៀបចំ Content ដោយប្រើ AI")
    target_kw = st.selectbox("ជ្រើសរើស Keyword គោលដៅ:", selected_keywords)
    content_style = st.radio("ជ្រើសរើសស្ទីលអត្ថបទ:", ["កំប្លែង និងទាក់ទាញ (Funny/Viral)", "បច្ចេកទេសសុទ្ធ (Professional/Tech)"])
    generate_btn = st.button("🚀 បង្កើត Script ឥឡូវនេះ")

with col_b:
    if generate_btn:
        if not api_key:
            st.error("❌ សូមបញ្ចូល Gemini API Key ក្នុង Sidebar ជាមុនសិន!")
        else:
            with st.spinner('Gemini AI កំពុងវិភាគ និងសរសេរ...'):
                try:
                    script = ai_generate_content(api_key, target_kw, content_style)
                    st.success(f"Script សម្រាប់ {target_kw} រួចរាល់ហើយ!")
                    st.text_area("Copy យកទៅប្រើប្រាស់:", script, height=350)
                except Exception as e:
                    st.error(f"Error: {e}")

st.divider()
st.caption("© 2026 NextGen Byte-Tech Intelligence Dashboard | បង្កើតឡើងដោយក្បួនហុងស៊ុយអធិរាជ និងបច្ចេកវិទ្យា AI")