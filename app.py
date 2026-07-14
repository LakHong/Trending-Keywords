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

# --- ៤. មុខងារទាញទិន្នន័យ (ជំនាន់ការពារការ Block IP ជាមួយ proxies) ---
@st.cache_data(ttl=1800)
def get_trends_safe(keywords, tf):
    if not keywords: return pd.DataFrame()
    pd.set_option('future.no_silent_downcasting', True)
    
    # ប្រសិនបើបងមាន Proxy ផ្ទាល់ខ្លួន (ឧទាហរណ៍៖ Webshare, Oxylabs, ឬ Free Proxy)
    # បងអាចដាក់បញ្ចូលក្នុងទម្រង់នេះ៖
    # proxy_list = ["http://user:pass@ip:port", "http://ip:port"]
    
    for attempt in range(3):
        try:
            # បង្កើត TrendReq ដោយមិនកំណត់ proxies ជាមុន (សាកល្បងធម្មតា)
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(15, 30))
            pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            df = pytrends.interest_over_time()
            if not df.empty:
                return df.drop(labels=['isPartial'], axis='columns', errors='ignore')
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            # ប្រសិនបើជួបកំហុស (Google Block) វានឹងរង់ចាំ រួចព្យាយាមម្តងទៀត
            time.sleep(random.uniform(5, 10))
            continue
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
df_gen = get_trends_safe(general_kw, timeframe)

if not df_gen.empty:
    fig_gen = px.line(df_gen.reset_index(), x='date', y=general_kw, template="plotly_dark")
    st.plotly_chart(fig_gen, width='stretch')
else:
    st.warning("⚠️ មិនអាចទាញទិន្នន័យបាន (Google Busy)។ សូមរង់ចាំ ២ នាទី រួច Refresh។")

st.divider()

# --- ៩. ផ្នែកប្រៀបធៀប Brand (ថ្មី!) ---
st.subheader(f"⚔️ ការប្រៀបធៀបនិន្នាការ Brand ({time_label})")
brands = ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"]
selected_brands = st.multiselect("ជ្រើសរើស Brand ៖", brands, default=["Hikvision", "Dahua", "Sunell"])

if selected_brands:
    df_brand = get_trends_safe(selected_brands, timeframe)
    
    if not df_brand.empty:
        # ការគណនាមធ្យមភាគ និងកំណើនទីផ្សារ
        avg_vals = df_brand[selected_brands].mean().reset_index()
        avg_vals.columns = ['Brand', 'Search Volume']
        
        # គណនា Market Share (%)
        total_search = avg_vals['Search Volume'].sum()
        if total_search > 0:
            avg_vals['Market Share (%)'] = (avg_vals['Search Volume'] / total_search) * 100
            avg_vals['Market Share (%)'] = avg_vals['Market Share (%)'].round(2)
        else:
            avg_vals['Market Share (%)'] = 0.0
            
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # បង្ហាញក្រាហ្វ Pie
            fig_pie = px.pie(avg_vals, values='Market Share (%)', names='Brand', hole=0.4,
                             title="ចំណែកទីផ្សារ (Market Share)",
                             color_discrete_sequence=px.colors.sequential.YlOrRd,
                             template="plotly_dark")
            st.plotly_chart(fig_pie, width='stretch')
            
        with col2:
            top_brand = avg_vals.loc[avg_vals['Search Volume'].idxmax(), 'Brand']
            st.success(f"🏆 **{top_brand}** នាំមុខគេពេលនេះ!")
            st.dataframe(avg_vals[['Brand', 'Market Share (%)']], hide_index=True)
            
        if st.button("📋 វិភាគយុទ្ធសាស្ត្រលក់ (AI Insight)"):
            with st.spinner('🤖 AI កំពុងវិភាគ...'):
                prompt = f"""
                ផ្អែកលើទិន្នន័យទីផ្សារកម្ពុជាខាងក្រោម៖
                {avg_vals.to_dict()}
                ក្នុងនាមជាអ្នកជំនាញទីផ្សារ NextGen Byte-Tech៖
                សូមណែនាំថាតើយើងគួរផ្ដោតលើ Brand ណាដើម្បីចំណេញច្រើន ហើយត្រូវរៀបចំយុទ្ធសាស្ត្រលក់យ៉ាងដូចម្ដេច?
                ឆ្លើយជាភាសាខ្មែរ។
                """
                st.info(ai_call(prompt))
                
        # ក្រាហ្វ Line សម្រាប់តាមដានពេលវេលា
        fig_line = px.line(df_brand.reset_index(), x='date', y=selected_brands,
                         title="ការប្រែប្រួលនៃការស្វែងរកតាមពេលវេលា",
                         template="plotly_dark")
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.error("🚫 Google Trends កំពុងរឹតត្បិត IP នៃ Server។ សូមរង់ចាំ ២ នាទី រួច Refresh។")
else:
    st.info("💡 សូមជ្រើសរើស Brand យ៉ាងតិចមួយ ដើម្បីចាប់ផ្តើមវិភាគ...")

# --- ១០. AI Script Generator (Updated: Funny, Professional Styles & Save Function) ---
st.divider()
st.subheader("🤖 AI Script Generator")

# បង្កើត Session State សម្រាប់ផ្ទុកទិន្នន័យដែលបាន Save
if 'saved_scripts' not in st.session_state:
    st.session_state['saved_scripts'] = []

col_input, col_display = st.columns([1, 2])

with col_input:
    # បញ្ជី Keyword សម្រាប់ជ្រើសរើស
    all_options = list(set(selected_brands + general_kw))
    target_kw = st.selectbox("រើសប្រធានបទផលិត Content:", all_options)
    
    # ការជ្រើសរើសស្ទីលសំណេរ
    script_style = st.radio(
        "ជ្រើសរើសស្ទីលសំណេរ:",
        ["បែបកំប្លែង TikTok (Funny)", "បែបអាជីព (Professional)"],
        index=0
    )
    
    generate_btn = st.button("🚀 បង្កើត Script ឥឡូវនេះ")
    
    # ប៊ូតុង Save Script
    save_btn = st.button("💾 រក្សាទុក Script នេះ")

with col_display:
    script_result = ""
    
    if generate_btn:
        if api_key:
            with st.spinner('✨ AI កំពុងរៀបចំសំណេរ...'):
                style_context = ""
                if "Funny" in script_style:
                    style_context = "បែបកំប្លែង ឌឺដងតិចៗ ប្រើពាក្យយុវវ័យទាន់សម័យ (Slang) សមស្របសម្រាប់ TikTok Reels"
                else:
                    style_context = "បែបអាជីព ផ្ដោតលើបច្ចេកទេស ទំនុកចិត្ត និងអត្ថប្រយោជន៍សម្រាប់អាជីវកម្ម"

                prompt = f"""
                អ្នកគឺជាអ្នកជំនាញមាតិកា (Content Creator) ឱ្យហាង NextGen Byte-Tech នៅកម្ពុជា។
                សូមសរសេរ Script វីដេអូខ្លីលើប្រធានបទ: {target_kw}។
                ស្ទីលសំណេរ: {style_context}។
                ភាសា: ខ្មែរ។
                រចនาสម្ព័ន្ធ: មាន Hook (ទាក់ទាញដើមវីដេអូ), Body (ខ្លឹមសារ), និង CTA (ជំរុញឱ្យអតិថិជនទាក់ទងមកហាង).
                """
                
                script_result = ai_call(prompt)
                st.session_state['current_script'] = script_result # រក្សាទុកក្នុង Session បណ្ដោះអាសន្ន
                
                st.markdown(f"### 📝 លទ្ធផល ({script_style})")
                st.code(script_result, language="markdown")
        else:
            st.warning("⚠️ សូមបញ្ចូល Gemini API Key នៅក្នុង Sidebar ជាមុនសិន!")

    # ដំណើរការមុខងារ Save
    if save_btn:
        if 'current_script' in st.session_state and st.session_state['current_script']:
            new_save = {
                "topic": target_kw,
                "style": script_style,
                "date": datetime.now().strftime('%d-%m-%Y %H:%M'),
                "content": st.session_state['current_script']
            }
            # បន្ថែមចូលក្នុងបញ្ជី
            st.session_state['saved_scripts'].append(new_save)
            st.success("✅ បានរក្សាទុក Script ចូលក្នុងបញ្ជីដោយជោគជ័យ!")
        else:
            st.warning("⚠️ គ្មាន Script ដែលត្រូវ Save ទេ។ សូមបង្កើត Script មុនពេលចុច Save។")

# --- ១១. បង្ហាញ Script ដែលបាន Save (Saved Scripts List) ---
if st.session_state['saved_scripts']:
    st.divider()
    st.subheader("📂 ស្គ្រីបដែលបានរក្សាទុក (Saved Scripts)")
    
    # បង្ហាញជាទម្រង់ Expanders
    for idx, item in enumerate(st.session_state['saved_scripts']):
        with st.expander(f"📌 [{item['date']}] {item['topic']} - {item['style']}"):
            st.code(item['content'], language="markdown")
            
            # ប៊ូតុងលុបចេញពីបញ្ជី
            if st.button("🗑️ លុប", key=f"del_{idx}"):
                st.session_state['saved_scripts'].pop(idx)
                st.rerun() # Refresh ទំព័រ
