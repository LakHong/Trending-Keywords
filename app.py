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

# --- ៤. មុខងារទាញទិន្នន័យពី Google Trends ---
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

# បន្ថែមជម្រើស Cloud VPS & Landing Page ទៅក្នុង Sidebar Radio
category = st.sidebar.radio(
    "📁 ជ្រើសរើសវិស័យចង់វិភាគ:", 
    ["កាមេរ៉ាសុវត្ថិភាព (CCTV)", "ប្រព័ន្ធបណ្តាញ (Networking)", "សេវាកម្ម Cloud & Web (SaaS)"]
)

# --- ៨. ផ្នែកនិន្នាការទូទៅ ---
st.subheader(f"📈 និន្នាការទីផ្សារទូទៅ: {time_label}")
general_kw = ["CCTV", "Smart Home", "Networking", "Cloud VPS", "Landing Page"]
df_gen = get_trends_safe(general_kw, timeframe)

if not df_gen.empty:
    fig_gen = px.line(df_gen.reset_index(), x='date', y=general_kw, template="plotly_dark")
    st.plotly_chart(fig_gen, width='stretch')
else:
    st.warning("⚠️ មិនអាចទាញទិន្នន័យបាន (Google Busy)។ សូមរង់ចាំ ២ នាទី រួច Refresh។")

st.divider()

# --- ៩. ផ្នែកប្រៀបធៀប Brand/Service (Omni-Channel) ---
st.subheader(f"⚔️ វិភាគប្រៀបធៀបតម្រូវការលើគ្រប់បណ្តាញសង្គម ({time_label})")

# កំណត់បញ្ជី Keyword/Brand ទៅតាមវិស័យនីមួយៗ
if category == "កាមេរ៉ាសុវត្ថិភាព (CCTV)":
    brands = ["Hikvision", "Dahua", "Sunell", "Ezviz", "Imou"]
    default_select = ["Hikvision", "Dahua", "Sunell"]
    fb_weights = {"Hikvision": 1.3, "Dahua": 1.2, "Sunell": 0.9, "Ezviz": 1.5, "Imou": 1.4}
    tt_weights = {"Hikvision": 0.6, "Dahua": 0.5, "Sunell": 0.3, "Ezviz": 1.7, "Imou": 1.6}

elif category == "ប្រព័ន្ធបណ្តាញ (Networking)":
    brands = ["MikroTik", "UniFi", "Fortigate", "Ruijie", "Cisco"]
    default_select = ["MikroTik", "UniFi", "Fortigate"]
    fb_weights = {"MikroTik": 1.4, "UniFi": 1.3, "Fortigate": 1.5, "Ruijie": 1.2, "Cisco": 1.1}
    tt_weights = {"MikroTik": 0.3, "UniFi": 0.5, "Fortigate": 0.2, "Ruijie": 0.6, "Cisco": 0.3}

else:  # សេវាកម្ម Cloud & Web (SaaS)
    brands = ["Cloud VPS", "Landing Page", "Web Hosting", "Website Design", "Domain Name"]
    default_select = ["Cloud VPS", "Landing Page", "Website Design"]
    # ទីផ្សារសេវាកម្ម Web គឺដើរខ្លាំងលើ FB និង Google រីឯ Landing Page គឺពេញនិយមផ្សព្វផ្សាយខ្លាំងលើ TikTok
    fb_weights = {
        "Cloud VPS": 1.4, 
        "Landing Page": 1.5, 
        "Web Hosting": 1.2, 
        "Website Design": 1.4, 
        "Domain Name": 1.1
    }
    tt_weights = {
        "Cloud VPS": 0.1,      # ស្ទើរតែគ្មានអ្នកលេង TikTok រកទិញ VPS ឡើយ
        "Landing Page": 0.9,   # ពេញនិយមខ្លាំងសម្រាប់ Business Coach ណែនាំលើ TikTok
        "Web Hosting": 0.2, 
        "Website Design": 0.7,  # មានការបង្ហាញ Template ស្អាតៗលើ TikTok
        "Domain Name": 0.3
    }

selected_brands = st.multiselect(f"ជ្រើសរើស សេវាកម្ម/ពាក្យគន្លឹះ ដើម្បីប្រៀបធៀប ៖", brands, default=default_select)

if selected_brands:
    df_brand = get_trends_safe(selected_brands, timeframe)
    
    if not df_brand.empty:
        avg_vals = df_brand[selected_brands].mean().reset_index()
        avg_vals.columns = ['Brand', 'Google Vol']
        
        avg_vals['Facebook Vol'] = (avg_vals['Brand'].map(fb_weights) * avg_vals['Google Vol']).round(2)
        avg_vals['TikTok Vol'] = (avg_vals['Brand'].map(tt_weights) * avg_vals['Google Vol']).round(2)
        avg_vals['Omni-Score'] = (avg_vals['Google Vol'] + avg_vals['Facebook Vol'] + avg_vals['TikTok Vol']).round(2)
        
        total_omni = avg_vals['Omni-Score'].sum()
        if total_omni > 0:
            avg_vals['Market Share (%)'] = ((avg_vals['Omni-Score'] / total_omni) * 100).round(2)
        else:
            avg_vals['Market Share (%)'] = 0.0
            
        col1, col2 = st.columns([2, 1])
        
        with col1:
            df_melted = pd.melt(
                avg_vals, 
                id_vars=['Brand'], 
                value_vars=['Google Vol', 'Facebook Vol', 'TikTok Vol'],
                var_name='Platform', 
                value_name='Search Index'
            )
            fig_multi = px.bar(
                df_melted, x='Brand', y='Search Index', color='Platform', barmode='group',
                title=f"ប្រៀបធៀបប្រជាប្រិយភាពសេវាកម្ម តាម Platform",
                color_discrete_sequence=['#FFD700', '#1877F2', '#FE2C55'], 
                template="plotly_dark"
            )
            st.plotly_chart(fig_multi, width='stretch')
            
        with col2:
            top_brand = avg_vals.loc[avg_vals['Omni-Score'].idxmax(), 'Brand']
            st.success(f"🏆 **{top_brand}** មានតម្រូវការរួមខ្ពស់ជាងគេក្នុងពេលនេះ!")
            st.dataframe(avg_vals[['Brand', 'Omni-Score', 'Market Share (%)']], hide_index=True)
            
        if st.button("📋 វិភាគយុទ្ធសាស្ត្រលក់ (Omni-Channel AI Insight)"):
            with st.spinner('🤖 AI កំពុងវិភាគតម្រូវការ Cloud VPS និង Landing Page...'):
                prompt = f"""
                ផ្អែកលើទិន្នន័យស្វែងរកសេវាកម្ម Cloud / Web ខាងក្រោម៖
                {avg_vals.to_dict()}
                ក្នុងនាមជាម្ចាស់អាជីវកម្ម NextGen Byte-Tech ដែលចង់លក់សេវាកម្ម Cloud VPS និង Landing Page បន្ថែម៖
                ១. តើទិន្នន័យខាងលើបង្ហាញពីឱកាសអ្វីខ្លះក្នុងការចាប់ម៉ូយនៅខ្មែរ?
                ២. គួររៀបចំកញ្ចប់សេវាកម្ម (Package Solution) យ៉ាងដូចម្តេចដើម្បីទាក់ទាញចិត្តអ្នកលក់អនឡាញ និងក្រុមហ៊ុន SME?
                ៣. ផ្តល់យុទ្ធសាស្ត្រលក់ និង Marketing ឱ្យចំ Target Group នីមួយៗ។
                ឆ្លើយជាភាសាខ្មែរ បែបអាជីព និងអនុវត្តបានភ្លាមៗ។
                """
                st.info(ai_call(prompt))
                
        fig_line = px.line(df_brand.reset_index(), x='date', y=selected_brands,
                         title="ការប្រែប្រួលនៃការស្វែងរកតាមពេលវេលា (Google Trends)",
                         template="plotly_dark")
        st.plotly_chart(fig_line, width='stretch')
    else:
        st.error("🚫 Google Trends កំពុងរឹតត្បិត IP នៃ Server។ សូមរង់ចាំ ២ នាទី រួច Refresh។")
else:
    st.info("💡 សូមជ្រើសរើស សេវាកម្ម/ពាក្យគន្លឹះ យ៉ាងតិចមួយ ដើម្បីចាប់ផ្តើមវិភាគ...")

# --- ១០. AI Content Creator (Facebook & TikTok) ---
st.divider()
st.subheader("🤖 AI Content Creator (Facebook & TikTok)")

if 'saved_scripts' not in st.session_state:
    st.session_state['saved_scripts'] = []

col_input, col_display = st.columns([1, 2])

with col_input:
    all_options = list(set(selected_brands + general_kw))
    target_kw = st.selectbox("រើសប្រធានបទផលិត Content:", all_options)
    
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
                    style_context = "បែបកំប្លែង ឌឺដងជាមួយការប្រើប្រាស់ Hosting ថោកៗឧស្សាហ៍គាំង ឬការធុញទ្រាន់នឹងការលក់អនឡាញគ្មាន Website/Landing Page ច្បាស់លាស់ ប្រើពាក្យយុវវ័យទាន់សម័យ (Slang)"
                else:
                    style_context = "បែបអាជីព ផ្ដោតលើល្បឿនលឿន (High Performance Cloud VPS), សុវត្ថិភាពទិន្នន័យ (Data Security), ភាពងាយស្រួលនៃការបិទការលក់ (High Conversion Landing Page) សម្រាប់អាជីវកម្មខ្នាតតូចនិងមធ្យម"

                prompt = f"""
                អ្នកគឺជាអ្នកជំនាញមាតិកា (Content Creator) ឱ្យហាង NextGen Byte-Tech នៅកម្ពុជា។
                សូមសរសេរ {target_platform} លើប្រធានបទ: {target_kw}។
                ស្ទីលសំណេរ: {style_context}។
                ភាសា: ខ្មែរ។
                រចនាសម្ព័ន្ធ៖
                - បើជា Facebook Post៖ សរសេរ Caption ទាក់ទាញ, បញ្ជាក់អត្ថប្រយោជន៍ និង Call to Action ទំនាក់ទំនងមក NextGen Byte-Tech ដើម្បីទទួលបានការពិគ្រោះយោបល់ឥតគិតថ្លៃ។
                - បើជា TikTok Script៖ សរសេរឱ្យមាន Scene ប្លង់ថត, សម្តីនិយាយ (Voiceover) និង SFX កំប្លែងៗ ឬរំភើប បញ្ចូល CTA ទាក់ទាញនៅចុងបញ្ចប់។
                """
                
                script_result = ai_call(prompt)
                st.session_state['current_script'] = script_result 
                
                st.markdown(f"### 📝 លទ្ធផល ({script_style})")
                st.code(script_result, language="markdown")
        else:
            st.warning("⚠️ សូមបញ្ចូល Gemini API Key នៅក្នុង Sidebar ជាមុនសិន!")

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

# --- ១១. Saved Scripts List ---
if st.session_state['saved_scripts']:
    st.divider()
    st.subheader("📂 ស្គ្រីបដែលបានរក្សាទុក (Saved Scripts)")
    
    for idx, item in enumerate(st.session_state['saved_scripts']):
        with st.expander(f"📌 [{item['date']}] {item['topic']} - {item['platform']} ({item['style']})"):
            st.code(item['content'], language="markdown")
            
            if st.button("🗑️ លុប", key=f"del_{idx}"):
                st.session_state['saved_scripts'].pop(idx)
                st.rerun()
