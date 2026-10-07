import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# Page Configuration & CSS Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="HRDI Executive Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS สำหรับปรับแต่งความสวยงามและการ์ด KPI
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
    }
    .kpi-card {
        background-color: #1e222d;
        border: 1px solid #2e3440;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #8f9ba8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .kpi-value {
        color: #ffffff;
        font-size: 1.7rem;
        font-weight: 700;
    }
    .kpi-subtext {
        color: #00d26a;
        font-size: 0.8rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Data Loading
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("HRDI-TPmap.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ ไม่สามารถโหลดไฟล์ข้อมูล HRDI-TPmap.csv ได้: {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar Controls (Interactive Widgets)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/analytics.png", width=60)
    st.title("ตัวกรองข้อมูล")
    st.caption("ระบบวิเคราะห์เชิงพื้นที่และสถิติประชากร")
    st.divider()

    # Filter 1: Province Selectbox
    provinces = ["ทั้งหมด"] + sorted(df["Province"].dropna().unique().tolist())
    selected_province = st.selectbox("📌 เลือกจังหวัด", provinces)

    filtered_df = df.copy()
    if selected_province != "ทั้งหมด":
        filtered_df = filtered_df[filtered_df["Province"] == selected_province]

    # Filter 2: TPMaps Multiselect
    tpmap_options = sorted(filtered_df["TPMaps"].dropna().unique().tolist())
    selected_tpmap = st.multiselect(
        "🎯 เลือกสถานะ TPMaps", 
        tpmap_options, 
        default=tpmap_options
    )

    if selected_tpmap:
        filtered_df = filtered_df[filtered_df["TPMaps"].isin(selected_tpmap)]

    # Filter 3: Height Range Slider
    min_h, max_h = int(df["Height"].min()), int(df["Height"].max())
    selected_height = st.slider(
        "⛰️ ระดับความสูงจากระดับน้ำทะเล (ม.)", 
        min_h, max_h, (min_h, max_h)
    )

    filtered_df = filtered_df[
        (filtered_df["Height"] >= selected_height[0]) & 
        (filtered_df["Height"] <= selected_height[1])
    ]
    
    st.divider()
    st.markdown(f"**แสดงข้อมูล:** `{len(filtered_df):,} / {len(df):,}` หมู่บ้าน")

# ---------------------------------------------------------
# Main Header & Metric Cards
# ---------------------------------------------------------
st.title("📊 HRDI Executive Analytics Dashboard")
st.markdown("ศูนย์ข้อมูลสรุปสถิติหมู่บ้าน ประชากร และสัดส่วนคนจนเป้าหมายจำแนกตามพื้นที่")

# KPI Summary Cards (4 Columns)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">จำนวนหมู่บ้าน</div>
        <div class="kpi-value">{len(filtered_df):,}</div>
        <div class="kpi-subtext">แห่ง</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ประชากรรวม</div>
        <div class="kpi-value">{filtered_df['CountOfPopulation'].sum():,}</div>
        <div class="kpi-subtext">คน</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">จำนวนครัวเรือน</div>
        <div class="kpi-value">{filtered_df['CountOfHousehold'].sum():,}</div>
        <div class="kpi-subtext">ครัวเรือน</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    avg_h = filtered_df['Height'].mean() if not filtered_df.empty else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">ความสูงพื้นที่เฉลี่ย</div>
        <div class="kpi-value">{avg_h:.1f}</div>
        <div class="kpi-subtext">เมตร รทก.</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Analytics Tabs (Multiple Chart Types)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 สัดส่วน & โครงสร้าง", 
    "🗺️ โครงสร้างรายพื้นที่ (Treemap)", 
    "⛰️ การวิเคราะห์ความสูงพื้นที่", 
    "📋 ตารางข้อมูล"
])

# ---------------------------------------------------------
# Tab 1: Bar Chart & Donut Chart
# ---------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("1.1 จำนวนหมู่บ้านแบ่งตามสถานะ TPMaps (Bar Chart)")
        if not filtered_df.empty:
            tpmap_counts = filtered_df["TPMaps"].value_counts().reset_index()
            tpmap_counts.columns = ["TPMaps", "จำนวนหมู่บ้าน"]

            fig_bar = px.bar(
                tpmap_counts,
                x="TPMaps",
                y="จำนวนหมู่บ้าน",
                color="TPMaps",
                text="จำนวนหมู่บ้าน",
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            fig_bar.update_traces(textposition='outside')
            fig_bar.update_layout(showlegend=False, xaxis_title=None, height=420)
            st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("1.2 สัดส่วนเปอร์เซ็นต์ TPMaps (Donut Chart)")
        if not filtered_df.empty:
            fig_pie = px.pie(
                tpmap_counts,
                names="TPMaps",
                values="จำนวนหมู่บ้าน",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template="plotly_dark"
            )
            fig_pie.update_traces(textinfo='percent+label')
            fig_pie.update_layout(showlegend=False, height=420)
            st.plotly_chart(fig_pie, use_container_width=True)

# ---------------------------------------------------------
# Tab 2: Treemap
# ---------------------------------------------------------
with tab2:
    st.subheader("2. โครงสร้างจำนวนหมู่บ้านจำแนกตาม จังหวัด -> อำเภอ (Treemap)")
    if not filtered_df.empty:
        fig_tree = px.treemap(
            filtered_df,
            path=['Province', 'Ampoe', 'TPMaps'],
            values='CountOfHousehold',
            color='TPMaps',
            color_discrete_sequence=px.colors.qualitative.Set3,
            template="plotly_dark"
        )
        fig_tree.update_layout(height=520)
        st.plotly_chart(fig_tree, use_container_width=True)

# ---------------------------------------------------------
# Tab 3: Scatter Plot & Box Plot
# ---------------------------------------------------------
with tab3:
    col_scat, col_box = st.columns([1.2, 1])

    with col_scat:
        st.subheader("3.1 สัดส่วน TPMaps vs ความสูงพื้นที่ (Scatter Plot)")
        if not filtered_df.empty:
            fig_scatter = px.scatter(
                filtered_df,
                x="Height",
                y="PropOfTPMaps",
                size="CountOfPopulation",
                color="TPMaps",
                hover_name="MooBan",
                hover_data=["Ampoe", "Province"],
                labels={
                    "Height": "ระดับความสูงพื้นที่ (เมตร)", 
                    "PropOfTPMaps": "สัดส่วนคนจนเป้าหมาย (%)"
                },
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_scatter.update_layout(height=450)
            st.plotly_chart(fig_scatter, use_container_width=True)

    with col_box:
        st.subheader("3.2 การกระจายตัวระดับความสูงตาม TPMaps (Box Plot)")
        if not filtered_df.empty:
            fig_box = px.box(
                filtered_df,
                x="TPMaps",
                y="Height",
                color="TPMaps",
                labels={"Height": "ความสูง (เมตร)"},
                template="plotly_dark",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig_box.update_layout(showlegend=False, height=450)
            st.plotly_chart(fig_box, use_container_width=True)

# ---------------------------------------------------------
# Tab 4: Data Table
# ---------------------------------------------------------
with tab4:
    st.subheader("4. รายละเอียดข้อมูลรายหมู่บ้าน")
    st.dataframe(
        filtered_df[[
            "Province", "Ampoe", "Tambon", "MooBan", 
            "CountOfHousehold", "CountOfPopulation", "Height", "TPMaps", "PropOfTPMaps"
        ]],
        use_container_width=True,
        height=450
    )