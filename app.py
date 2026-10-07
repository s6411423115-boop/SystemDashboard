import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# ---------------------------------------------------------
# Page Configuration & Theme
# ---------------------------------------------------------
st.set_page_config(
    page_title="HRDI Smart Spatial Analytics",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Glassmorphism UI (CSS)
st.markdown("""
<style>
    /* Dark Premium Background */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Header Styling */
    .main-header {
        background: linear-gradient(135deg, #1e2640 0%, #0e1117 100%);
        padding: 24px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 24px;
    }
    .main-title {
        color: #ffffff;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
    }
    .main-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-top: 6px;
    }

    /* Glass Cards for Metrics */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        text-align: left;
    }
    .card-label {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .card-value {
        color: #f8fafc;
        font-size: 2rem;
        font-weight: 800;
        margin: 6px 0;
    }
    .card-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
    .badge-orange { background: rgba(249, 115, 22, 0.2); color: #fb923c; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load & Cache Data
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("HRDI-TPmap.csv")
    # คลีนข้อมูลพิกัดละติจูด/ลองจิจูด
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดข้อมูลได้: {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar - Advanced Control Panel
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🎛️ ตัวกรองการวิเคราะห์")
    st.caption("ระบบกรองข้อมูลเชิงพื้นที่และสถิติเป้าหมาย")
    st.divider()

    # 1. เลือกจังหวัด
    province_list = ["ทั้งหมด (All Provinces)"] + sorted(df["Province"].dropna().unique().tolist())
    selected_province = st.selectbox("📍 จังหวัด", province_list)

    filtered_df = df.copy()
    if selected_province != "ทั้งหมด (All Provinces)":
        filtered_df = filtered_df[filtered_df["Province"] == selected_province]

    # 2. เลือกสถานะ TPMaps
    tpmap_options = sorted(filtered_df["TPMaps"].dropna().unique().tolist())
    selected_tpmap = st.multiselect("🎯 สถานะ TPMaps", tpmap_options, default=tpmap_options)
    if selected_tpmap:
        filtered_df = filtered_df[filtered_df["TPMaps"].isin(selected_tpmap)]

    # 3. เลือกประเภทป่าไม้ (ForestType)
    forest_options = ["ทั้งหมด"] + sorted(filtered_df["ForestType"].dropna().unique().tolist())
    selected_forest = st.selectbox("🌲 ประเภทพื้นที่ป่าไม้", forest_options)
    if selected_forest != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["ForestType"] == selected_forest]

    # 4. Range Slider ความสูง
    min_h, max_h = int(df["Height"].min()), int(df["Height"].max())
    selected_height = st.slider("⛰️ ความสูงพื้นที่ (เมตร รทก.)", min_h, max_h, (min_h, max_h))
    
    filtered_df = filtered_df[
        (filtered_df["Height"] >= selected_height[0]) & 
        (filtered_df["Height"] <= selected_height[1])
    ]

    st.divider()
    st.markdown(f"📊 **จำนวนที่พบ:** `{len(filtered_df):,}` / `{len(df):,}` หมู่บ้าน")

# ---------------------------------------------------------
# Main Banner & KPI Cards
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1 class="main-title">🗺️ HRDI Spatial Analytics & TPMaps Intelligence</h1>
    <div class="main-subtitle">ระบบวิเคราะห์ข้อมูลพื้นที่สูง ประชากรเป้าหมาย และการกระจายตัวเชิงภูมิศาสตร์</div>
</div>
""", unsafe_allow_html=True)

# 4 Executive Glass Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <div class="card-label">หมู่บ้านทั้งหมด</div>
        <div class="card-value">{len(filtered_df):,}</div>
        <span class="card-badge badge-blue">แห่ง</span>
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
    "🗺️ แผนที่พิกัด 3 มิติ (3D Spatial Map)", 
    "📈 การวิเคราะห์เชิงลึก", 
    "📁 ข้อมูลรายหมู่บ้าน & Export"
])

# Tab 1: Overview Charts
with tab1:
    c_left, c_right = st.columns([1.2, 1])
    
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
                color_continuous_scale='Blues',
                template="plotly_dark"
            )
            fig_prov.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=400)
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
                hole=0.5,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            fig_donut.update_traces(textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_donut, use_container_width=True)

# Tab 2: 3D PyDeck Map
with tab2:
    st.subheader("🌐 แผนที่ 3D แสดงจุดตำแหน่งและความสูงของหมู่บ้าน")
    
    # กรองเฉพาะแถบที่มีพิกัด Latitude & Longitude สมบูรณ์
    map_df = filtered_df.dropna(subset=['Latitude', 'Longitude'])
    
    if not map_df.empty:
        # กำหนดตำแหน่งจุดศูนย์กลางของแผนที่
        center_lat = map_df['Latitude'].mean()
        center_lon = map_df['Longitude'].mean()
        
        # PyDeck ColumnLayer (3D Columns)
        layer = pdk.Layer(
            "ColumnLayer",
            data=map_df,
            get_position=["Longitude", "Latitude"],
            get_elevation="Height",
            elevation_scale=5,
            radius=400,
            get_fill_color=["Height * 0.15", "120", "220", 200],
            pickable=True,
            auto_highlight=True,
        )
        
        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=8,
            pitch=45,
            bearing=0
        )
        
        r = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "html": "<b>หมู่บ้าน:</b> {MooBan}<br/><b>ตำบล:</b> {Tambon}<br/><b>อำเภอ:</b> {Ampoe}<br/><b>จังหวัด:</b> {Province}<br/><b>ความสูง:</b> {Height} เมตร",
                "style": {"backgroundColor": "#1e293b", "color": "white"}
            }
        )
        st.pydeck_chart(r)
    else:
        st.warning("ไม่พบข้อมูลพิกัดภูมิศาสตร์ (Latitude/Longitude) ตามเงื่อนไขที่เลือก")

# Tab 3: Deep Dive Correlations
with tab3:
    c_box, c_scat = st.columns([1, 1.2])
    
    with c_box:
        st.subheader("📦 การกระจายตัว")