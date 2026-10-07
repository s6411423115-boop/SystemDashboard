import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="HRDI TPmap Dashboard",
    page_icon="📊",
    layout="wide"
)

# โหลดข้อมูล
@st.cache_data
def load_data():
    df = pd.read_csv("HRDI-TPmap.csv")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"เกิดข้อผิดพลาดในการโหลดไฟล์ HRDI-TPmap.csv: {e}")
    st.stop()

# หัวข้อแอปพลิเคชัน
st.title("📊 HRDI-TPmap Data Dashboard")
st.markdown("ระบบวิเคราะห์ข้อมูลหมู่บ้าน ประชากร และระดับความยากจน (TPMap)")

# ---------------------------------------------------------
# Interactive Widgets (Sidebar Filters)
# ---------------------------------------------------------
st.sidebar.header("🎯 ตัวกรองข้อมูล (Filters)")

# Widget 1: Selectbox สำหรับเลือกจังหวัด
province_list = ["ทั้งหมด"] + sorted(df["Province"].dropna().unique().tolist())
selected_province = st.sidebar.selectbox("เลือกจังหวัด", province_list)

# กรองข้อมูลเบื้องต้นตามจังหวัด
filtered_df = df.copy()
if selected_province != "ทั้งหมด":
    filtered_df = filtered_df[filtered_df["Province"] == selected_province]

# Widget 2: Multiselect สำหรับเลือกกลุ่ม TPMaps
tpmap_list = sorted(filtered_df["TPMaps"].dropna().unique().tolist())
selected_tpmap = st.sidebar.multiselect("เลือกสถานะ TPMaps", tpmap_list, default=tpmap_list)

if selected_tpmap:
    filtered_df = filtered_df[filtered_df["TPMaps"].isin(selected_tpmap)]

# Widget 3: Slider สำหรับกรองระดับความสูงพื้นที่ (Height)
min_height = int(df["Height"].min())
max_height = int(df["Height"].max())
selected_height = st.sidebar.slider("ระดับความสูงจากระดับน้ำทะเล (เมตร)", min_height, max_height, (min_height, max_height))

filtered_df = filtered_df[
    (filtered_df["Height"] >= selected_height[0]) & 
    (filtered_df["Height"] <= selected_height[1])
]

# ---------------------------------------------------------
# แสดงผลสรุปภาพรวม (KPI Metrics)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("จำนวนหมู่บ้าน", f"{len(filtered_df):,} แห่ง")
col2.metric("ประชากรรวม", f"{filtered_df['CountOfPopulation'].sum():,} คน")
col3.metric("จำนวนครัวเรือน", f"{filtered_df['CountOfHousehold'].sum():,} ครัวเรือน")
col4.metric("ความสูงเฉลี่ย", f"{filtered_df['Height'].mean():.1f} เมตร")

st.divider()

# ---------------------------------------------------------
# กราฟที่ 1: Bar Chart แสดงจำนวนหมู่บ้านจำแนกตามกลุ่ม TPMaps
# ---------------------------------------------------------
st.subheader("1. สัดส่วนสถานะคนจนเป้าหมาย (TPMaps)")
if not filtered_df.empty:
    tpmap_counts = filtered_df["TPMaps"].value_counts().reset_index()
    tpmap_counts.columns = ["TPMaps", "จำนวนหมู่บ้าน"]
    
    fig_bar = px.bar(
        tpmap_counts, 
        x="TPMaps", 
        y="จำนวนหมู่บ้าน", 
        color="TPMaps",
        text="จำนวนหมู่บ้าน",
        title="จำนวนหมู่บ้านจำแนกตามกลุ่มสถานะ TPMaps",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")

# ---------------------------------------------------------
# กราฟที่ 2: Scatter Plot แสดงความสัมพันธ์ระหว่างความสูงกับสัดส่วน TPMaps
# ---------------------------------------------------------
st.subheader("2. ความสัมพันธ์ระหว่างระดับความสูง (Height) กับ สัดส่วน TPMaps")
if not filtered_df.empty:
    fig_scatter = px.scatter(
        filtered_df,
        x="Height",
        y="PropOfTPMaps",
        size="CountOfPopulation",
        color="TPMaps",
        hover_name="MooBan",
        hover_data=["Tambon", "Ampoe", "Province"],
        title="ระดับความสูงพื้นที่ vs สัดส่วนคนจนเป้าหมาย (PropOfTPMaps)",
        labels={"Height": "ระดับความสูง (เมตร)", "PropOfTPMaps": "สัดส่วนคนจนเป้าหมาย (%)"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("ไม่พบข้อมูลตามเงื่อนไขที่เลือก")

# ---------------------------------------------------------
# ตารางแสดงข้อมูล
# ---------------------------------------------------------
with st.expander("📄 ดูตารางข้อมูลรายละเอียด"):
    st.dataframe(filtered_df[["Province", "Ampoe", "Tambon", "MooBan", "CountOfHousehold", "CountOfPopulation", "Height", "TPMaps", "PropOfTPMaps"]])