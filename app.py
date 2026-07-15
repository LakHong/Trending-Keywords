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
    page_title="NextGen AI Trend & Biz Center", 
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

# --- ៦. ប្រព័ន្ធរក្សាទិន្នន័យ CDP & CRM (Session State) ---
if 'crm_data' not in st.session_state:
    st.session_state['crm_data'] = pd.DataFrame([
        {"ID": 1001, "ឈ្មោះ": "ស៊ាន ហេង", "ទូរស័ព្ទ": "096XXXXXXX", "សេវាកម្ម": "Cloud VPS", "ស្ថានភាព": "Lead", "កាលបរិច្ឆេទ": "14-07-2026"},
        {"ID": 1002, "ឈ្មោះ": "លីដា ណារ៉េត", "ទូរស័ព្ទ": "012XXXXXXX", "សេវាកម្ម": "Landing Page", "ស្ថានភាព": "Contacted", "កាលបរិច្ឆេទ": "15-07-2026"},
        {"ID": 1003, "ឈ្មោះ": "ក្រុមហ៊ុន អង្គរ តិច", "ទូរស័ព្ទ": "088XXXXXXX", "សេវាកម្ម": "Networking", "ស្ថានភាព": "Won", "កាលបរិច្ឆេទ": "15-07-2026"}
    ])

if 'cdp_logs' not in st.session_state:
    st.session_state['cdp_logs'] = pd.DataFrame([
        {"ម៉ោង": "13:02", "ប្រភពចរាចរណ៍": "TikTok Ads", "សកម្មភាព": "ចុចមើលគំរូ Landing Page", "ឧបករណ៍": "Mobile (iOS)"},
        {"ម៉ោង": "13:05", "ប្រភពចរាចរណ៍": "Google Search", "សកម្មភាព": "ស្វែងរកតម្លៃ Cloud VPS", "ឧបករណ៍": "Desktop (Windows)"},
        {"ម៉ោង": "13:10", "ប្រភពចរាចរណ៍": "Facebook Page", "សកម្មភាព": "ចុចប៊ូតុងផ្ញើសារសួរតម្លៃ Cam", "ឧបករណ៍": "Mobile (Android)"}
    ])

# --- ៧. Main UI (Header) ---
st.title("🛡️ NextGen Byte-Tech: AI Intelligence Hub")
st.write(f"**យុទ្ធសាស្ត្រមមី ធាតុភ្លើង ២០២៦** | 📅 {datetime.now().strftime('%d-%m-%Y')}")

# --- ៨. Navigation Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Trends", "🤖 AI Content Creator", "🤝 CRM & Customer Tracking", "📂 CDP Event Tracker"])

# ================= TAB 1: MARKET TRENDS =================
with tab1:
    st.sidebar.subheader("📊 ការកំណត់វិភាគ")
    time_map = {"៧ ថ្ងៃចុងក្រោយ": "now 7-d", "១ ខែចុងក្រោយ": "today 1-m", "៣ ខែចុងក្រោយ": "today 3-m"}
    time_label = st.sidebar.selectbox("រយៈពេលវិភាគ:", list(time_map.keys()), key="time_select")
    timeframe = time_map[time_label]

    category = st.sidebar.radio(
        "📁 ជ្រើសរើសវិស័យចង់វិភាគ:", 
        ["កាមេរ៉ាសុវត្ថិភាព (CCTV)", "ប្រព័ន្ធបណ្តាញ (Networking)", "សេវាកម្ម Cloud & Web (SaaS)"],
        key="cat_radio"
    )

    st.subheader(f"📈 និន្នាការទីផ្សារទូទៅ: {time_label}")
    general_kw = ["CCTV", "Smart Home", "Networking", "Cloud VPS", "Landing Page"]
    df_gen = get_trends_safe(general_kw, timeframe)

    if not df_gen.empty:
        fig_gen = px.line(df_gen.reset_index(), x='date', y=general_kw, template="plotly_dark")
        st.plotly_chart(fig_gen, use_container_width=True)
    else:
        st.warning("⚠️ មិនអាចទាញទិន្នន័យបាន (Google Busy)។ សូមរង់ចាំ ២ នាទី រួច Refresh។")

    st.divider()

    # វិភាគប្រៀបធៀប Brand
    st.subheader(f"⚔️ វិភាគប្រៀបធៀបតម្រូវការលើគ្រប់បណ្តាញសង្គម ({time_label})")
    
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
    else:
        brands = ["Cloud VPS", "Landing Page", "Web Hosting", "Website Design", "Domain Name"]
        default_select = ["Cloud VPS", "Landing Page", "Website Design"]
        fb_weights = {"Cloud VPS": 1.4, "Landing Page": 1.5, "Web Hosting": 1.2, "Website Design": 1.4, "Domain Name": 1.1}
        tt_weights = {"Cloud VPS": 0.1, "Landing Page": 0.9, "Web Hosting": 0.2, "Website Design": 0.7, "Domain Name": 0.3}

    selected_brands = st.multiselect("ជ្រើសរើស សេវាកម្ម/ពាក្យគន្លឹះ ដើម្បីប្រៀបធៀប ៖", brands, default=default_select, key="sel_brands")

    if selected_brands:
        df_brand = get_trends_safe(selected_brands, timeframe)
        if not df_brand.empty:
            avg_vals = df_brand[selected_brands].mean().reset_index()
            avg_vals.columns = ['Brand', 'Google Vol']
            
            avg_vals['Facebook Vol'] = (avg_vals['Brand'].map(fb_weights) * avg_vals['Google Vol']).round(2)
            avg_vals['TikTok Vol'] = (avg_vals['Brand'].map(tt_weights) * avg_vals['Google Vol']).round(2)
            avg_vals['Omni-Score'] = (avg_vals['Google Vol'] + avg_vals['Facebook Vol'] + avg_vals['TikTok Vol']).round(2)
            
            total_omni = avg_vals['Omni-Score'].sum()
            avg_vals['Market Share (%)'] = ((avg_vals['Omni-Score'] / total_omni) * 100).round(2) if total_omni > 0 else 0.0
                
            col1, col2 = st.columns([2, 1])
            with col1:
                df_melted = pd.melt(avg_vals, id_vars=['Brand'], value_vars=['Google Vol', 'Facebook Vol', 'TikTok Vol'], var_name='Platform', value_name='Search Index')
                fig_multi = px.bar(df_melted, x='Brand', y='Search Index', color='Platform', barmode='group', title="ប្រៀបធៀបប្រជាប្រិយភាពតាម Platform", color_discrete_sequence=['#FFD700', '#1877F2', '#FE2C55'], template="plotly_dark")
                st.plotly_chart(fig_multi, use_container_width=True)
            with col2:
                top_brand = avg_vals.loc[avg_vals['Omni-Score'].idxmax(), 'Brand']
                st.success(f"🏆 **{top_brand}** នាំមុខគេ!")
                st.dataframe(avg_vals[['Brand', 'Omni-Score', 'Market Share (%)']], hide_index=True)

# ================= TAB 2: AI CONTENT CREATOR =================
with tab2:
    st.subheader("🤖 AI Content Generator")
    if 'saved_scripts' not in st.session_state:
        st.session_state['saved_scripts'] = []

    col_input, col_display = st.columns([1, 2])
    with col_input:
        target_kw = st.selectbox("រើសប្រធានបទផលិត Content:", ["Cloud VPS", "Landing Page", "MikroTik", "CCTV", "Smart Home"])
        target_platform = st.selectbox("រើសប្រព័ន្ធផ្សព្វផ្សាយ:", ["Facebook Post", "TikTok Video Script"])
        script_style = st.radio("ជ្រើសរើសស្ទីលសំណេរ:", ["បែបកំប្លែង (Funny)", "បែបអាជីព (Professional)"], key="style_radio")
        generate_btn = st.button("🚀 បង្កើត Content ឥឡូវនេះ")
        save_btn = st.button("💾 រក្សាទុក Content នេះ")

    with col_display:
        if generate_btn:
            if api_key:
                with st.spinner('✨ AI កំពុងរៀបចំ...'):
                    style_context = "បែបកំប្លែង ឌឺដងពីការប្រើ Hosting ថោកៗឧស្សាហ៍គាំង" if "Funny" in script_style else "បែបអាជីព ផ្ដោតលើល្បឿន និងសុវត្ថិភាព"
                    prompt = f"សរសេរ {target_platform} លើប្រធានបទ {target_kw} ជាភាសាខ្មែរ ស្ទីល {style_context} ឱ្យហាង NextGen Byte-Tech។"
                    script_result = ai_call(prompt)
                    st.session_state['current_script'] = script_result 
                    st.markdown(f"### 📝 លទ្ធផល ({script_style})")
                    st.code(script_result, language="markdown")
            else:
                st.warning("⚠️ សូមបញ្ចូល API Key ក្នុង Sidebar!")

        if save_btn and 'current_script' in st.session_state:
            new_save = {"topic": target_kw, "platform": target_platform, "style": script_style, "date": datetime.now().strftime('%d-%m-%Y %H:%M'), "content": st.session_state['current_script']}
            st.session_state['saved_scripts'].append(new_save)
            st.success("✅ បានរក្សាទុកជោគជ័យ!")

# ================= TAB 3: CRM (CUSTOMER TRACKING) =================
with tab3:
    st.subheader("🤝 CRM - ប្រព័ន្ធគ្រប់គ្រង និងតាមដានអតិថិជន")
    
    # ផ្នែកបញ្ចូលទិន្នន័យអតិថិជនថ្មី
    with st.expander("➕ បន្ថែមអតិថិជនថ្មី (Add New Lead)"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_name = st.text_input("ឈ្មោះអតិថិជន / ក្រុមហ៊ុន:")
        with c2:
            new_phone = st.text_input("លេខទូរស័ព្ទ:")
        with c3:
            new_service = st.selectbox("សេវាកម្មដែលចាប់អារម្មណ៍:", ["Cloud VPS", "Landing Page", "CCTV", "Networking"])
        
        c4, c5 = st.columns(2)
        with c4:
            new_status = st.selectbox("ស្ថានភាពបច្ចុប្បន្ន:", ["Lead", "Contacted", "Won", "Lost"])
        with c5:
            add_lead_btn = st.button("💾 បញ្ចូលក្នុងប្រព័ន្ធ CRM")
            
        if add_lead_btn and new_name:
            new_row = {
                "ID": random.randint(1004, 9999),
                "ឈ្មោះ": new_name,
                "ទូរស័ព្ទ": new_phone,
                "សេវាកម្ម": new_service,
                "ស្ថានភាព": new_status,
                "កាលបរិច្ឆេទ": datetime.now().strftime('%d-%m-%Y')
            }
            st.session_state['crm_data'] = pd.concat([st.session_state['crm_data'], pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"✅ បានបញ្ចូលឈ្មោះ {new_name} ទៅក្នុង CRM រួចរាល់!")

    # បង្ហាញតារាងអតិថិជន
    st.write("### 📋 បញ្ជីអតិថិជនទាំងអស់")
    st.dataframe(st.session_state['crm_data'], use_container_width=True)

    # ប៊ូតុង AI ជួយវិភាគយុទ្ធសាស្ត្រលក់លម្អិត
    st.write("---")
    st.write("💡 **AI ជំនួយការលក់៖** ចុចប៊ូតុងខាងក្រោមដើម្បីឱ្យ AI វិភាគទិន្នន័យ CRM របស់បង រួចរៀបចំរបៀបចរចាបិទការលក់ឱ្យបានលឿន។")
    if st.button("🤖 វិភាគវិធីសាស្រ្តបិទការលក់ (AI Sales Closer)"):
        if api_key:
            with st.spinner("🤖 AI កំពុងវិភាគប្រវត្តិ CRM..."):
                crm_dict = st.session_state['crm_data'].to_dict(orient='records')
                prompt = f"""
                នេះជាបញ្ជី CRM របស់ហាង NextGen Byte-Tech ៖
                {crm_dict}
                ក្នុងនាមជាអ្នកជំនាញ Sales បិទការលក់៖
                ១. ផ្អែកលើស្ថានភាពនីមួយៗ (Lead, Contacted) តើយើងគួរ Follow up ភ្ញៀវទាំងនេះដោយរបៀបណាដើម្បីឱ្យបាន Won ទាំងអស់?
                ២. ចំពោះអ្នកចាប់អារម្មណ៍ 'Cloud VPS' និង 'Landing Page' តើគួរនិយាយអូសទាញបែបណាឱ្យគេប្តេជ្ញាចិត្តទិញភ្លាមៗ?
                ឆ្លើយជាភាសាខ្មែរ បែបណែនាំយុទ្ធសាស្ត្រខ្លីៗ និងងាយអនុវត្ត។
                """
                st.info(ai_call(prompt))
        else:
            st.warning("⚠️ សូមបញ្ចូល API Key ក្នុង Sidebar!")

# ================= TAB 4: CDP (EVENT TRACKER) =================
with tab4:
    st.subheader("📂 CDP - ប្រព័ន្ធត្រួតពិនិត្យឥរិយាបថអតិថិជន (Real-time Event Log)")
    st.write("ប្រព័ន្ធចាប់សកម្មភាពភ្ញៀវដែលចូលមកកាន់ប្រព័ន្ធផ្សព្វផ្សាយ និង Landing Page របស់ NextGen Byte-Tech៖")
    
    # Simulate Real-time Client Visit (សាកល្បងបង្កើត Event ថ្មីៗដោយស្វ័យប្រវត្ត)
    if st.button("🔄 ចាប់យកចរាចរណ៍អតិថិជនថ្មី (Simulate Visitor Activity)"):
        platforms = ["Facebook Ads", "Google Organic", "TikTok Search", "Direct Link"]
        actions = ["ចុចមើលតម្លៃ Cloud VPS", "ដោនឡូតកាតាឡុក កាមេរ៉ា", "ចុចសួរព័ត៌មាន Landing Page", "មើលតម្លៃ Switch / Router"]
        devices = ["Mobile (iOS)", "Desktop (Mac)", "Mobile (Android)", "Desktop (Windows)"]
        
        simulated_event = {
            "ម៉ោង": datetime.now().strftime('%H:%M:%S'),
            "ប្រភពចរាចរណ៍": random.choice(platforms),
            "សកម្មភាព": random.choice(actions),
            "ឧបករណ៍": random.choice(devices)
        }
        st.session_state['cdp_logs'] = pd.concat([pd.DataFrame([simulated_event]), st.session_state['cdp_logs']], ignore_index=True)
        st.success("🛰️ CDP ចាប់បានសកម្មភាពចូលមើលថ្មី ១ ករណី!")

    st.dataframe(st.session_state['cdp_logs'], use_container_width=True)

    # ក្រាហ្វវិភាគប្រភពចរាចរណ៍ពី CDP
    st.write("### 📊 ក្រាហ្វវិភាគប្រភពចរាចរណ៍អតិថិជន (Traffic Source Share)")
    if not st.session_state['cdp_logs'].empty:
        traffic_counts = st.session_state['cdp_logs']['ប្រភពចរាចរណ៍'].value_counts().reset_index()
        traffic_counts.columns = ['ប្រភពចរាចរណ៍', 'ចំនួនដង']
        fig_pie = px.pie(traffic_counts, values='ចំនួនដង', names='ប្រភពចរាចរណ៍', hole=0.4, color_discrete_sequence=px.colors.sequential.YlOrRd, template="plotly_dark")
        st.plotly_chart(fig_pie, use_container_width=True)
