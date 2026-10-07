import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page Configuration & Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="HRDI Smart Spatial Analytics Pro",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Glassmorphism UI (CSS)
st.markdown("""
<style>
    .stApp {
        background: #0b0f19;
    }
    .main-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 50%, #0b0f19 100%);
        padding: 28px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .main-title {
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
    }
    .main-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 6px;
    }
    .glass-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(56, 189, 248, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.3);
    }
    .card-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .card-value {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 8px 0;
    }
    .card-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-blue { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-green { background: rgba(74, 222, 128, 0.2); color: #4ade80; }
    .badge-purple { background: rgba(192, 132, 252, 0.2); color: #c084fc; }
    .badge-orange { background: rgba(251, 146, 60, 0.2); color: #fb923c; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load & Cache Data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("HRDI-TPmap.csv")
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลได้: {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar - Control Panel
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎛️ ตัวกรองการวิเคราะห์")
    st.caption("ระบบกรองข้อมูลเชิงพื้นที่และสถิติเป้าหมาย")
    st.divider()

    province_list = ["ทั้งหมด (All Provinces)"] + sorted(df["Province"].dropna().unique().tolist())
    selected_province = st.selectbox("📍 เลือกจังหวัด", province_list)

    filtered_df = df.copy()
    if selected_province != "ทั้งหมด (All Provinces)":
        filtered_df = filtered_df[filtered_df["Province"] == selected_province]

    tpmap_options = sorted(filtered_df["TPMaps"].dropna().unique().tolist())
    selected_tpmap = st.multiselect("🎯 สถานะ TPMaps", tpmap_options, default=tpmap_options)
    if selected_tpmap:
        filtered_df = filtered_df[filtered_df["TPMaps"].isin(selected_tpmap)]

    forest_options = ["ทั้งหมด"] + sorted(filtered_df["ForestType"].dropna().unique().tolist())
    selected_forest = st.selectbox("🌲 ประเภทพื้นที่ป่าไม้", forest_options)
    if selected_forest != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["ForestType"] == selected_forest]

    min_h, max_h = int(df["Height"].min()), int(df["Height"].max())
    selected_height = st.slider("⛰️ ช่วงความสูงพื้นที่ (เมตร รทก.)", min_h, max_h, (min_h, max_h))
    
    filtered_df = filtered_df[
        (filtered_df["Height"] >= selected_height[0]) & 
        (filtered_df["Height"] <= selected_height[1])
    ]

    st.divider()
    st.metric(label="📊 จำนวนหมู่บ้านที่พบ", value=f"{len(filtered_df):,} แห่ง", delta=f"{len(filtered_df)/len(df)*100:.1f}% ของทั้งหมด")

# ---------------------------------------------------------
# Main Banner & Metric Cards
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🗺️ HRDI Spatial Analytics & TPMaps Intelligence</h1>
    <div class="main-subtitle">ระบบวิเคราะห์ข้อมูลเชิงพื้นที่สูง ประชากรเป้าหมาย และสถิติตำแหน่งภูมิศาสตร์แบบตอบสนองทันที</div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-label">หมู่บ้านทั้งหมด</div>
        <div class="card-value">{len(filtered_df):,}</div>
        <span class="card-badge badge-blue">แห่งในระบบ</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    pop_total = filtered_df['CountOfPopulation'].sum()
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-label">ประชากรรวม</div>
        <div class="card-value">{pop_total:,.0f}</div>
        <span class="card-badge badge-green">คน</span>
    </div>
    """, unsafe_allow_html=True)

with col3:
    house_total = filtered_df['CountOfHousehold'].sum()
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-label">ครัวเรือนทั้งหมด</div>
        <div class="card-value">{house_total:,.0f}</div>
        <span class="card-badge badge-purple">ครัวเรือน</span>
    </div>
    """, unsafe_allow_html=True)

with col4:
    avg_height = filtered_df['Height'].mean() if not filtered_df.empty else 0
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-label">ความสูงเฉลี่ย</div>
        <div class="card-value">{avg_height:.1f}</div>
        <span class="card-badge badge-orange">เมตร รทก.</span>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Tabs Section
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 ภาพรวมสถิติ", 
    "🗺️ แผนที่เชิงพื้นที่ (Interactive Map)", 
    "📈 การวิเคราะห์เชิงลึก", 
    "📁 ค้นหา & ส่งออกข้อมูล"
])

# Tab 1: Overview Charts
with tab1:
    c_left, c_right = st.columns([1.3, 1])
    
    with c_left:
        st.subheader("📌 Top 10 จังหวัดที่มีจำนวนหมู่บ้านเป้าหมายสูงสุด")
        if not filtered_df.empty:
            prov_counts = filtered_df['Province'].value_counts().head(10).reset_index()
            prov_counts.columns = ['Province', 'Count']
            
            fig_prov = px.bar(
                prov_counts,
                x='Count',
                y='Province',
                orientation='h',
                text='Count',
                color='Count',
                color_continuous_scale='Electric',
                template="plotly_dark"
            )
            fig_prov.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=420)
            st.plotly_chart(fig_prov, use_container_width=True)

    with c_right:
        st.subheader("🍰 สัดส่วนกลุ่มเป้าหมาย TPMaps")
        if not filtered_df.empty:
            tp_counts = filtered_df['TPMaps'].value_counts().reset_index()
            tp_counts.columns = ['TPMaps', 'Count']
            
            fig_donut = px.pie(
                tp_counts,
                names='TPMaps',
                values='Count',
                hole=0.55,
                color_discrete_sequence=px.colors.sequential.Plasma,
                template="plotly_dark"
            )
            fig_donut.update_traces(textinfo='percent+label', marker=dict(line=dict(color='#000000', width=2)))
            fig_donut.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig_donut, use_container_width=True)

# Tab 2: Map
with tab2:
    st.subheader("🌐 แผนที่แสดงจุดตำแหน่งเชิงพิกัดและความสูง")
    
    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude']).copy()
    
    if not map_df.empty:
        # สลับ Latitude กับ Longitude ให้ถูกต้อง
        map_data = pd.DataFrame({
            'latitude': map_df['Longitude'],
            'longitude': map_df['Latitude']
        })
        st.map(map_data, zoom=6)
    else:
        st.warning("ไม่พบข้อมูลพิกัดภูมิศาสตร์ตามเงื่อนไขที่เลือก")

# Tab 3: Deep Dive Analytics
with tab3:
    c_box, c_scat = st.columns([1, 1.2])
    
    with c_box:
        st.subheader("📦 การกระจายตัวระดับความสูงตาม TPMaps")
        if not filtered_df.empty:
            fig_box = px.box(
                filtered_df,
                x="TPMaps",
                y="Height",
                color="TPMaps",
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig_box.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig_box, use_container_width=True)

    with c_scat:
        st.subheader("📉 ความสัมพันธ์: ความสูง vs สัดส่วน TPMaps")
        if not filtered_df.empty:
            fig_scatter = px.scatter(
                filtered_df,
                x="Height",
                y="PropOfTPMaps",
                size="CountOfPopulation",
                color="TPMaps",
                hover_name="MooBan",
                labels={"Height": "ความสูง (เมตร)", "PropOfTPMaps": "สัดส่วน TPMaps (%)"},
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_scatter.update_layout(height=420)
            st.plotly_chart(fig_scatter, use_container_width=True)

# Tab 4: Table, Quick Search & Download
with tab4:
    st.subheader("📑 ตารางค้นหาข้อมูลรายหมู่บ้าน")
    
    search_query = st.text_input("🔍 ค้นหาด่วน (ชื่อหมู่บ้าน / ตำบล / อำเภอ):", "")
    
    table_df = filtered_df.copy()
    if search_query:
        table_df = table_df[
            table_df['MooBan'].astype(str).str.contains(search_query, case=False, na=False) |
            table_df['Tambon'].astype(str).str.contains(search_query, case=False, na=False) |
            table_df['Ampoe'].astype(str).str.contains(search_query, case=False, na=False)
        ]
        
    cols_to_show = ["Province", "Ampoe", "Tambon", "MooBan", "CountOfHousehold", "CountOfPopulation", "Height", "ForestType", "TPMaps", "PropOfTPMaps"]
    st.dataframe(table_df[cols_to_show], use_container_width=True, height=400)
    
    csv_data = table_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 ดาวน์โหลดข้อมูลชุดนี้เป็น CSV",
        data=csv_data,
        file_name="HRDI_filtered_data.csv",
        mime="text/csv"
    )