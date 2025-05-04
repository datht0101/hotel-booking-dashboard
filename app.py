import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load & xử lý dữ liệu =====
df = pd.read_csv("hotel_bookings 2.csv")
df['children'].fillna(0, inplace=True)
df['total_guests'] = df['adults'] + df['children'] + df['babies']
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['revenue'] = df['adr'] * df['total_nights']
df['arrival_date'] = pd.to_datetime(df['reservation_status_date'], dayfirst=True, errors='coerce')
df['day_of_week'] = df['arrival_date'].dt.day_name()

# ===== Bộ lọc ngang =====
col1, col2, col3, col4 = st.columns(4)
with col1:
    deposit_filter = st.selectbox("Deposit Type", ["All"] + sorted(df['deposit_type'].unique()))
with col2:
    month_filter = st.selectbox("Arrival Date Month", ["All"] + sorted(df['arrival_date_month'].unique()))
with col3:
    year_filter = st.selectbox("Arrival Date Year", ["All"] + sorted(df['arrival_date_year'].astype(str).unique()))
with col4:
    cancel_filter = st.selectbox("Is Canceled", ["All", 0, 1])

# ===== Áp dụng bộ lọc =====
filtered_df = df.copy()
if deposit_filter != "All":
    filtered_df = filtered_df[filtered_df['deposit_type'] == deposit_filter]
if month_filter != "All":
    filtered_df = filtered_df[filtered_df['arrival_date_month'] == month_filter]
if year_filter != "All":
    filtered_df = filtered_df[filtered_df['arrival_date_year'] == int(year_filter)]
if cancel_filter != "All":
    filtered_df = filtered_df[filtered_df['is_canceled'] == int(cancel_filter)]

# ===== Chỉ số tổng quan =====
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số lượng đặt trước", f"{len(filtered_df):,}")
c2.metric("Số lượng huỷ", f"{filtered_df['is_canceled'].sum():,}")
c3.metric("Số lượng khách", f"{int(filtered_df['total_guests'].sum()):,}")
c4.metric("Doanh thu", f"{int(filtered_df['revenue'].sum()):,}")
st.markdown("---")

# ===== BIỂU ĐỒ: Booking vs Canceled =====
left1, right1 = st.columns(2)
with left1:
    st.subheader("📦 Đặt phòng vs Hủy")
    booking_data = filtered_df['is_canceled'].value_counts().rename({0: 'Booking', 1: 'Canceled'}).reset_index()
    booking_data.columns = ['Status', 'Count']
    fig1 = px.bar(booking_data, x='Status', y='Count', color='Status', labels={'Count': 'Số lượng'}, height=350)
    st.plotly_chart(fig1, use_container_width=True)

# ===== BIỂU ĐỒ: Bubble calendar =====
with right1:
    st.subheader("📅 Theo dõi đặt phòng")
    heatmap_data = filtered_df.groupby(['arrival_date_day_of_month', 'day_of_week']).size().reset_index(name='count')
    heatmap_pivot = heatmap_data.pivot(index='arrival_date_day_of_month', columns='day_of_week', values='count').fillna(0)

    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot[weekday_order]

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.heatmap(
        heatmap_pivot,
        cmap="Blues",
        linewidths=0.2,
        linecolor="white",
        square=True,
        cbar_kws={"label": "Bookings"}
    )
    ax.set_xlabel("Thứ", fontsize=11)
    ax.set_ylabel("Ngày", fontsize=11)
    st.pyplot(fig)

# ===== BIỂU ĐỒ: Waiting list =====
left2, right2 = st.columns(2)
with left2:
    st.subheader("⏳ Thời gian chờ xác nhận")
    wait_df = filtered_df.groupby('customer_type')['days_in_waiting_list'].mean().reset_index()
    fig3 = px.bar(wait_df, x='days_in_waiting_list', y='customer_type', orientation='h', color='customer_type',
                  labels={'days_in_waiting_list': 'Ngày', 'customer_type': 'Loại khách'}, height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ===== BIỂU ĐỒ: Lead Time =====
with right2:
    st.subheader("🚗 Thời gian chờ đến")
    lead_df = filtered_df.groupby('customer_type')['lead_time'].mean().reset_index()
    fig4 = px.bar(lead_df, x='lead_time', y='customer_type', orientation='h', color='customer_type',
                  labels={'lead_time': 'Ngày', 'customer_type': 'Loại khách'}, height=350)
    st.plotly_chart(fig4, use_container_width=True)
