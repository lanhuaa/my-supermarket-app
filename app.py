import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os


# ========== 页面基础配置 ==========
st.set_page_config(
    page_title="超市运营监控平台",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ========== 读取真实销售数据 ==========
@st.cache_data(ttl=300)
def load_sales_data(path: str, file_mtime: float) -> pd.DataFrame:
    """读取 Excel 并做基础清洗.

    file_mtime 参与缓存键, 当文件更新时间变化或超过 ttl 时会自动重新加载.
    """
    df = pd.read_excel(path)
    # 先统一清洗列名：去掉引号和首尾空格
    clean_cols = []
    for c in df.columns:
        if isinstance(c, str):
            c_clean = c.replace('"', "").replace("'", "").strip()
        else:
            c_clean = c
        clean_cols.append(c_clean)
    df.columns = clean_cols

    # 如果不存在标准列名 "销售地区", 尝试自动纠正（例如命名略有不同）
    if "销售地区" not in df.columns:
        # 简单规则：如果只有一列包含 "地区" 二字, 则认为它是销售地区
        candidate_cols = [c for c in df.columns if "地区" in str(c)]
        if len(candidate_cols) == 1:
            df = df.rename(columns={candidate_cols[0]: "销售地区"})
        # 你也可以在这里按需要继续扩展规则

    # 确保日期为 datetime 类型
    if not pd.api.types.is_datetime64_any_dtype(df["日期"]):
        df["日期"] = pd.to_datetime(df["日期"])
    return df

data_path = "supermarket_sales.xlsx"

try:
    file_mtime = os.path.getmtime(data_path)
    raw_df = load_sales_data(data_path, file_mtime)
except FileNotFoundError:
    st.error("未找到数据文件 `supermarket_sales.xlsx`，请将文件放在项目根目录后刷新页面。")
    st.stop()

# 排序并增加仅日期列，便于筛选
raw_df = raw_df.sort_values("日期").copy()
raw_df["日期_仅日期"] = raw_df["日期"].dt.date


# ========== 侧边栏：基于真实数据的筛选条件 ==========
with st.sidebar:
    st.markdown("## ⚙️ 筛选条件")

    min_date = raw_df["日期_仅日期"].min()
    max_date = raw_df["日期_仅日期"].max()

    date_range = st.date_input(
        "日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    category_options = sorted(raw_df["产品类别"].unique().tolist())
    selected_categories = st.multiselect(
        "产品类别",
        options=category_options,
        default=category_options,
    )

    region_options = sorted(raw_df["销售地区"].unique().tolist())
    selected_regions = st.multiselect(
        "销售地区（城市）",
        options=region_options,
        default=region_options,
    )

mask = (
    (raw_df["日期_仅日期"] >= date_range[0])
    & (raw_df["日期_仅日期"] <= date_range[1])
    & (raw_df["产品类别"].isin(selected_categories))
    & (raw_df["销售地区"].isin(selected_regions))
)
filtered_df = raw_df[mask]


# ========== 页面标题与头部区域（Header） ==========
st.markdown(
    """
    <style>
    .main-title {
        font-size: 30px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .sub-title {
        font-size: 13px;
        color: #4b5563;
        margin-bottom: 0.75rem;
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .logo-mark {
        width: 36px;
        height: 36px;
        border-radius: 999px;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-weight: 700;
        font-size: 18px;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35);
    }
    .logo-text-main {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }
    .logo-text-sub {
        font-size: 12px;
        color: #6b7280;
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background-color: #ecfdf3;
        border: 1px solid #bbf7d0;
        color: #16a34a;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background-color: #16a34a;
        box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.25);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown(
        """
        <div class="header-logo">
            <div class="logo-mark">SS</div>
            <div>
                <div class="logo-text-main">Supermart Analytics</div>
                <div class="logo-text-sub">超市经营数据 · 销售洞察与趋势监控</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_right:
    st.markdown(
        """
        <div style="display:flex;justify-content:flex-end;">
            <span class="status-badge">
                <span class="status-dot"></span>
                数据就绪
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('<div class="main-title">超市销售数据看板</div>', unsafe_allow_html=True)

date_range_text = f"{date_range[0]} 至 {date_range[1]}"
subtitle_text = (
    f"数据文件：supermarket_sales.xlsx ｜ 当前筛选日期：{date_range_text} ｜ "
    f"维度：产品类别、商品、销售地区、每日销售额"
)
st.markdown(f'<div class="sub-title">{subtitle_text}</div>', unsafe_allow_html=True)


# ========== 概览：卡片展示 ==========
st.markdown("### 概览")

if filtered_df.empty:
    st.warning("当前筛选条件下没有数据，请调整日期或产品类别。")
else:
    total_sales = float(filtered_df["总金额"].sum())
    total_orders = int(len(filtered_df))
    unique_products = int(filtered_df["商品名称"].nunique())

    # 销售趋势分析：最近 7 天 vs 之前 7 天
    daily_sales = (
        filtered_df.groupby("日期_仅日期")["总金额"]
        .sum()
        .reset_index(name="销售额")
        .sort_values("日期_仅日期")
    )

    recent_7 = daily_sales.tail(7)
    if len(daily_sales) > 7:
        prev_7 = daily_sales.tail(14).head(7)
        prev_avg = prev_7["销售额"].mean()
        recent_avg = recent_7["销售额"].mean()
        if prev_avg > 0:
            trend_pct = (recent_avg - prev_avg) / prev_avg * 100
        else:
            trend_pct = 0.0
    else:
        trend_pct = 0.0

    trend_direction = "上涨" if trend_pct >= 0 else "下降"
    trend_display_pct = abs(trend_pct)
    trend_color = "#16a34a" if trend_direction == "上涨" else "#dc2626"

    # 大号趋势文字
    st.markdown(
        f'<div style="font-size: 28px; font-weight: 700; color: {trend_color}; margin-bottom: 0.75rem;">'
        f'最近销售额{trend_direction}了 {trend_display_pct:.1f}%'
        f"</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总销售额", f"¥{total_sales:,.2f}")
    with col2:
        st.metric("订单条数", f"{total_orders:,}")
    with col3:
        st.metric("商品种类数", f"{unique_products:,}")

st.markdown("---")


# ========== 销售趋势：折线图 ==========
st.markdown("### 销售趋势（按日汇总）")

if not filtered_df.empty:
    daily_sales = (
        filtered_df.groupby("日期_仅日期")["总金额"]
        .sum()
        .reset_index(name="销售额")
        .sort_values("日期_仅日期")
    )

    trend_chart = px.line(
        daily_sales.tail(30),  # 最近 30 天数据，如果不足则全用
        x="日期_仅日期",
        y="销售额",
        markers=True,
        template="plotly_white",
    )
    trend_chart.update_traces(line_color="#2563eb")
    trend_chart.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis_title="日期",
        yaxis_title="销售额（¥）",
    )

    st.plotly_chart(trend_chart, use_container_width=True)
else:
    st.info("暂无数据用于绘制销售趋势。")

st.markdown("---")


# ========== 销售结构：按产品类别占比 ==========
st.markdown("### 销售结构（按产品类别占比）")

if not filtered_df.empty:
    category_sales = (
        filtered_df.groupby("产品类别")["总金额"]
        .sum()
        .reset_index(name="销售额")
    )

    category_pie = px.pie(
        category_sales,
        names="产品类别",
        values="销售额",
        hole=0.3,
    )
    category_pie.update_traces(textposition="inside", textinfo="percent+label")
    category_pie.update_layout(margin=dict(l=10, r=10, t=30, b=10))

    st.plotly_chart(category_pie, use_container_width=True)
else:
    st.info("暂无数据用于绘制销售结构。")

st.markdown("---")


# ========== 中国销售地图：按城市分布 ==========
st.markdown("### 中国销售地图（按城市销售额）")

if not filtered_df.empty:
    # 预定义城市经纬度（简单示例，可按需扩展）
    CITY_COORDS = {
        "北京": (39.9042, 116.4074),
        "天津": (39.3434, 117.3616),
        "上海": (31.2304, 121.4737),
        "广州": (23.1291, 113.2644),
        "深圳": (22.5431, 114.0579),
        "杭州": (30.2741, 120.1551),
        "南京": (32.0603, 118.7969),
        "成都": (30.5728, 104.0668),
        "重庆": (29.5630, 106.5516),
        "武汉": (30.5928, 114.3055),
        "西安": (34.3416, 108.9398),
    }

    city_sales = (
        filtered_df.groupby("销售地区")["总金额"]
        .sum()
        .reset_index(name="销售额")
    )

    city_sales["lat"] = city_sales["销售地区"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    city_sales["lon"] = city_sales["销售地区"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])
    city_sales = city_sales.dropna(subset=["lat", "lon"])

    if not city_sales.empty:
        city_map_fig = px.scatter_geo(
            city_sales,
            lat="lat",
            lon="lon",
            hover_name="销售地区",
            size="销售额",
            color="销售额",
            color_continuous_scale="Blues",
            projection="natural earth",
        )
        city_map_fig.update_layout(
            margin=dict(l=10, r=10, t=30, b=10),
            geo=dict(
                scope="asia",
                lonaxis=dict(range=[70, 140]),
                lataxis=dict(range=[15, 55]),
            ),
        )

        st.plotly_chart(city_map_fig, use_container_width=True)
    else:
        st.info("当前筛选条件下没有可用于绘制地图的城市数据。")
else:
    st.info("当前筛选条件下没有可用于绘制地图的城市数据。")

st.markdown("---")


# ========== 最新订单：表格 ==========
st.markdown("### 最新销售明细")

if not filtered_df.empty:
    search_keyword = st.text_input("按商品名称搜索", value="")

    orders_view = filtered_df.sort_values("日期", ascending=False).copy()

    if search_keyword:
        orders_view = orders_view[
            orders_view["商品名称"].str.contains(search_keyword, case=False, na=False)
        ]

    st.dataframe(
        orders_view[["日期", "产品类别", "商品名称", "销售数量", "单价", "总金额"]],
        use_container_width=True,
        height=400,
        hide_index=True,
    )
else:
    st.info("当前筛选条件下没有销售明细。")

