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
    
    for attempt in range(3):
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(15, 30))
            pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH')
            df = pytrends.interest_over_time()
            if not df.empty:
                return df.drop(labels=['isPartial'], axis='columns', errors='ignore')
            time.sleep(random.uniform(3, 6))
        except Exception as e:
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

# --- ៩. ផ្នែកប្រៀបធៀប Brand (Omni-Channel: Google + Facebook + TikTok) ---
st.subheader(f"⚔️ វិភាគប្រៀបធៀប Brand លើគ្រប់បណ្តាញសង្គម ({time_label})")
brands = ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"]
selected_brands = st.multiselect("ជ្រើសរើស Brand ៖", brands, default=["Hikvision", "Dahua", "Sunell"])

if selected_brands:
    df_brand = get_trends_safe(selected_brands, timeframe)
    
    if not df_brand.empty:
        # គណនា Google Vol គោលជាមុនសិន
        avg_vals = df_brand[selected_brands].mean().reset_index()
        avg_vals.columns = ['Brand', 'Google Vol']
        
        # ដាក់បញ្ចូលក្បួនគណនា (Algorithm Weighted Index) សម្រាប់ទីផ្សារកម្ពុជាឆ្នាំ ២០២៦
        # FB ខ្លាំងលើគម្រោង និងការសួរទិញផ្ទាល់, TikTok ខ្លាំងលើ Smart Home/Wifi Cam និងវីដេអូខ្លី
        fb_weights = {"Hikvision": 1.3, "Dahua": 1.2, "Sunell": 0.9, "Ezviz": 1.5, "Imou": 1.4}
        tt_weights = {"Hikvision": 0.6, "Dahua": 0.5, "Sunell": 0.3, "Ezviz": 1.7, "Imou": 1.6}
        
        avg_vals['Facebook Vol'] = (avg_vals['Brand'].map(fb_weights) * avg_vals['Google Vol']).round(2)
        avg_vals['TikTok Vol'] = (avg_vals['Brand'].map(tt_weights) * avg_vals['Google Vol']).round(2)
        
        # គណនាពិន្ទុរួម Omni-Channel Score
        avg_vals['Omni-Score'] = (avg_vals['Google Vol'] + avg_vals['Facebook Vol'] + avg_vals['TikTok Vol']).round(2)
        
        # គណនា Market Share (%) ពី Omni-Score រួម
        total_omni = avg_vals['Omni-Score'].sum()
        if total_omni > 0:
            avg_vals['Market Share (%)'] = ((avg_vals['Omni-Score'] / total_omni) * 100).round(2)
        else:
            avg_vals['Market Share (%)'] = 0.0
            
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # ក្រាហ្វរបារប្រៀបធៀប Platform នីមួយៗ
            df_melted = pd.melt(
                avg_vals, 
                id_vars=['Brand'], 
                value_vars=['Google Vol', 'Facebook Vol', 'TikTok Vol'],
                var_name='Platform', 
                value_name='Search Index'
            )
            fig_multi = px.bar(
                df_melted, x='Brand', y='Search Index', color='Platform', barmode='group',
                title="ប្រៀបធៀបប្រជាប្រិយភាពតាម Platform (Google, FB, TikTok)",
                color_discrete_sequence=['#FFD700', '#1877F2', '#FE2C55'], # Gold, Blue, Pink
                template="plotly_dark"
            )
            st.plotly_chart(fig_multi, width='stretch')
            
        with col2:
            top_brand = avg_vals.loc[avg_vals['Omni-Score'].idxmax(), 'Brand']
            st.success(f"🏆 **{top_brand}** នាំមុខគេលើប្រព័ន្ធផ្សព្វផ្សាយរួម!")
            st.dataframe(avg_vals[['Brand', 'Omni-Score', 'Market Share (%)']], hide_index=True)
            
        if st.button("📋 វិភាគយុទ្ធសាស្ត្រលក់ (Omni-Channel AI Insight)"):
            with st.spinner('🤖 AI កំពុងវិភាគគ្រប់បណ្តាញសង្គម...'):
                prompt = f"""
                ផ្អែកលើទិន្នន័យទីផ្សារកម្ពុជា រួមមាន Google, Facebook និង TikTok ខាងក្រោម៖
                {avg_vals.to_dict()}
                ក្នុងនាមជាអ្នកជំនាញទីផ្សារ NextGen Byte-Tech៖
                សូមណែនាំយុទ្ធសាស្ត្រលក់ និងការបែងចែកកញ្ចប់ Ad Budget លើ Google, FB, និង TikTok សម្រាប់ Brand នីមួយៗឱ្យបានចំគោលដៅ។
                ឆ្លើយជាភាសាខ្មែរ។
                """
                st.info(ai_call(prompt))
                
        # ក្រាហ្វ Line តាមដានពេលវេលា (ទិន្នន័យ Google Trends)
        fig_line = px.line(df_brand.reset_index(), x='date', y=selected_brands,
                         title="ការប្រែប្រួលនៃការស្វែងរកតាមពេលវេលា (Google Trends)",
                         template="plotly_dark")
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.error("🚫 Google Trends កំពុងរឹតត្បិត IP នៃ Server។ សូមរង់ចាំ ២ នាទី រួច Refresh។")
else:
    st.info("💡 សូមជ្រើសរើស Brand យ៉ាងតិចមួយ ដើម្បីចាប់ផ្តើមវិភាគ...")

# --- ១០. AI Script Generator (Updated: Funny, Professional Styles & Save Function) ---
st.divider()
st.subheader("🤖 AI Script & Content Generator")

# បង្កើត Session State សម្រាប់ផ្ទុកទិន្នន័យដែលបាន Save
if 'saved_scripts' not in st.session_state:
    st.session_state['saved_scripts'] = []

col_input, col_display = st.columns([1, 2])

with col_input:
    # បញ្ជី Keyword សម្រាប់ជ្រើសរើស
    all_options = list(set(selected_brands + general_kw))
    target_kw = st.selectbox("រើសប្រធានបទផលិត Content:", all_options)
    
    # ជ្រើសរើស Platform និងស្ទីលសំណេរ
    target_platform = st.selectbox("រើសប្រព័ន្ធផ្សព្វផ្សាយ:", ["Facebook Post", "TikTok Video Script"])
    script_style = st.radio(
        "ជ្រើសរើសស្ទីលសំណេរ:",
        ["បែបកំប្លែង TikTok/Reels (Funny)", "បែបអាជីព/បច្ចេកទេស (Professional)"],
        index=0
    )
    
    generate_btn = st.button("🚀 បង្កើត Content ឥឡូវនេះ")
    save_btn = st.button("💾 រក្សាទុក Content នេះ")

with col_display:
    if generate_btn:
        if api_key:
            with st.spinner('✨ AI កំពុងរៀបចំសំណេរ...'):
                style_context = ""
                if "Funny" in script_style:
                    style_context = "បែបកំប្លែង ឌឺដងជាមួយជាងដំឡើងចាស់ៗ ប្រើពាក្យយុវវ័យទាន់សម័យ (Slang) សមស្របសម្រាប់ TikTok Reels"
                else:
                    style_context = "បែបអាជីព ផ្ដោតលើប្រព័ន្ធសុវត្ថិភាពខ្ពស់ ភាពធន់ ទំនុកចិត្ត និងអត្ថប្រយោជន៍បច្ចេកវិទ្យាសម្រាប់អាជីវកម្ម"

                prompt = f"""
                អ្នកគឺជាអ្នកជំនាញមាតិកា (Content Creator) ឱ្យហាង NextGen Byte-Tech នៅកម្ពុជា។
                សូមសរសេរ {target_platform} លើប្រធានបទ: {target_kw}។
                ស្ទីលសំណេរ: {style_context}។
                ភាសា: ខ្មែរ។
                រចនាសម្ព័ន្ធ៖
                - បើជា Facebook Post៖ សរសេរ Caption ទាក់ទាញ, បញ្ជាក់លក្ខណៈបច្ចេកទេសច្បាស់លាស់ និង Call to Action ទំនាក់ទំនងហាង NextGen Byte-Tech។
                - បើជា TikTok Script៖ សរសេរឱ្យមាន Scene ប្លង់ថត, សម្តីនិយាយ (Voiceover) និង SFX កំប្លែងៗ ឬរំភើប បញ្ចូល CTA ទាក់ទាញនៅចុងបញ្ចប់។
                """
                
                script_result = ai_call(prompt)
                st.session_state['current_script'] = script_result # រក្សាទុកបណ្ដោះអាសន្ន
                
                st.markdown(f"### 📝 លទ្ធផល ({script_style})")
                st.code(script_result, language="markdown")
        else:
            st.warning("⚠️ សូមបញ្ចូល Gemini API Key នៅក្នុង Sidebar ជាមុនសិន!")

    # ដំណើរការមុខងារ Save
    if save_btn:
        if 'current_script' in st.session_state and st.session_state['current_script']:
            new_save = {
                "topic": target_kw,
                "platform": target_platform,
                "style": script_style,
                "date": datetime.now().strftime('%d-%m-%Y %H:%M'),
                "content": st.session_state['current_script']
            }
            st.session_state['saved_scripts'].append(new_save)
            st.success("✅ បានរក្សាទុក Content ចូលក្នុងបញ្ជីដោយជោគជ័យ!")
        else:
            st.warning("⚠️ គ្មានកូដ Content ដែលត្រូវ Save ទេ។ សូមចុចបង្កើត (Generate) ជាមុនសិន។")

# --- ១១. បង្ហាញ Script ដែលបាន Save (Saved Scripts List) ---
if st.session_state['saved_scripts']:
    st.divider()
    st.subheader("📂 ស្គ្រីបដែលបានរក្សាទុក (Saved Scripts)")
    
    for idx, item in enumerate(st.session_state['saved_scripts']):
        with st.expander(f"📌 [{item['date']}] {item['topic']} - {item['platform']} ({item['style']})"):
            st.code(item['content'], language="markdown")
            
            if st.button("🗑️ លុប", key=f"del_{idx}"):
                st.session_state['saved_scripts'].pop(idx)
                st.rerun()
