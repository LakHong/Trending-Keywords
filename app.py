import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. ការកំណត់ទំព័រ និង Branding
st.set_page_config(page_title="NextGen Trend Intelligence", layout="wide")
st.title("🛡️ NextGen Byte-Tech: Market Intelligence Dashboard")
st.markdown(f"**កាលបរិច្ឆេទបច្ចុប្បន្ន:** {datetime.now().strftime('%Y-%m-%d')}")

# 2. Sidebar សម្រាប់កំណត់ពាក្យគន្លឹះ
st.sidebar.header("Trend Settings")
default_keywords = ["CCTV", "UniFi", "Cyber Security", "IT Solution", "Smart Home"]
selected_keywords = st.sidebar.multiselect("ជ្រើសរើស Keywords:", default_keywords, default_keywords)

timeframe = st.sidebar.selectbox("រយៈពេល:", ["now 7-d", "today 1-m", "today 3-m"])

# 3. មុខងារទាញយកទិន្នន័យ (Caching ដើម្បីឱ្យ Dashboard ដើរលឿន)
@st.cache_data
def fetch_trend_data(keywords, tf):
    pytrends = TrendReq(hl='en-US', tz=360)
    pytrends.build_payload(keywords, cat=0, timeframe=tf, geo='KH', gprop='')
    data = pytrends.interest_over_time()
    related = pytrends.related_queries()
    return data, related

# បង្ហាញដំណើរការទាញយក
with st.spinner('កំពុងទាញយកទិន្នន័យពី Google Trends...'):
    df, related_data = fetch_trend_data(selected_keywords, timeframe)

if not df.empty:
    # 4. Metrics បង្ហាញពីការចាប់អារម្មណ៍ចុងក្រោយ
    st.subheader("📊 សន្ទុះទីផ្សារបច្ចុប្បន្ន (Interest Metrics)")
    cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        latest_val = int(df[kw].iloc[-1])
        prev_val = int(df[kw].iloc[-2])
        delta = latest_val - prev_val
        cols[i].metric(label=kw, value=latest_val, delta=f"{delta}%")

    # 5. ក្រាហ្វវិភាគនិន្នាការ (Interactive Chart)
    st.subheader("📈 ក្រាហ្វនិន្នាការតាមពេលវេលា (Trend Analysis)")
    df_reset = df.reset_index()
    fig = px.line(df_reset, x='date', y=selected_keywords, 
                 title="Market Interest Level in Cambodia",
                 labels={'value': 'Interest Level', 'date': 'Date'},
                 template="plotly_dark") # ប្រើ Dark Mode ឱ្យសមនឹងស្ទីល IT
    st.plotly_chart(fig, use_container_width=True)

    # 6. ពាក្យគន្លឹះដែលពាក់ព័ន្ធ (Related Queries)
    st.subheader("🔍 ពាក្យគន្លឹះដែលកំពុងហក់ឡើងខ្លាំង (Related Queries)")
    rel_cols = st.columns(len(selected_keywords))
    for i, kw in enumerate(selected_keywords):
        with rel_cols[i]:
            st.write(f"**Top under '{kw}':**")
            if related_data[kw]['top'] is not None:
                st.dataframe(related_data[kw]['top'], hide_index=True)
            else:
                st.write("រកមិនឃើញទិន្នន័យ។")
else:
    st.error("មិនអាចទាញយកទិន្នន័យបានទេ។ សូមព្យាយាមម្តងទៀត ឬប្តូរ Keywords។")

st.divider()
st.caption("NextGen Byte-Tech Intelligence System - Powered by Streamlit & Python")