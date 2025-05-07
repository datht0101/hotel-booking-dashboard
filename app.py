import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load & xử lý dữ liệu =====
df = pd.read_csv("process_hotel.csv")
df['children'].fillna(0, inplace=True)
df['total_guests'] = df['adults'] + df['children'] + df['babies']
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['arrival_date'] = pd.to_datetime(df['reservation_status_date'], dayfirst=True, errors='coerce')
df['day_of_week'] = df['arrival_date'].dt.day_name()

# Doanh thu chỉ tính đơn không huỷ
df['revenue'] = df['adr'] * df['total_nights']
df.loc[df['is_canceled'] == 1, 'revenue'] = 0

# ===== Bộ lọc =====
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

# ===== Tổng quan =====
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số lượng đặt trước", f"{len(filtered_df):,}")
c2.metric("Số lượng huỷ", f"{filtered_df['is_canceled'].sum():,}")
c3.metric("Số lượng khách", f"{int(filtered_df[filtered_df['is_canceled'] == 0]['total_guests'].sum()):,}")
c4.metric("Doanh thu", f"{int(filtered_df['revenue'].sum()):,}")
st.markdown("---")

# ===== Tổng doanh thu theo loại khách sạn =====
st.subheader("💰 Tổng doanh thu theo loại hotel")
revenue_by_hotel = (
    filtered_df[filtered_df['is_canceled'] == 0]
    .groupby('hotel')['revenue'].sum()
    .reset_index()
    .sort_values(by='revenue', ascending=False)
)
fig1 = px.bar(revenue_by_hotel, x='hotel', y='revenue', color='hotel',
              color_discrete_map={"City Hotel": "#1f77b4", "Resort Hotel": "#ff7f0e"},
              labels={'hotel': 'Hotel', 'revenue': 'Doanh thu'})
st.plotly_chart(fig1, use_container_width=True)

# ===== Doanh thu theo tháng =====
st.subheader("📈 Xu hướng doanh thu theo tháng")
monthly_revenue = (
    filtered_df[filtered_df['is_canceled'] == 0]
    .groupby('arrival_date_month_num')['revenue'].sum()
    .sort_index()
)
fig2 = px.line(monthly_revenue, labels={"value": "Doanh thu", "arrival_date_month_num": "Tháng"})
st.plotly_chart(fig2, use_container_width=True)

# ===== Tỷ lệ huỷ theo loại khách sạn =====
st.subheader("❌ Tỷ lệ huỷ phòng theo loại hotel")
cancel_rate = filtered_df.groupby('hotel')['is_canceled'].mean().reset_index()
cancel_rate['is_canceled'] = cancel_rate['is_canceled'] * 100
fig3 = px.bar(cancel_rate, x='hotel', y='is_canceled', color='hotel',
              color_discrete_map={"City Hotel": "#1f77b4", "Resort Hotel": "#ff7f0e"},
              labels={'is_canceled': 'Tỷ lệ huỷ (%)'})
st.plotly_chart(fig3, use_container_width=True)

# ===== Trạng thái đặt phòng =====
st.subheader("📊 Phân bố trạng thái đặt phòng")
status_counts = filtered_df['reservation_status'].value_counts().reset_index()
status_counts.columns = ['status', 'count']
fig4 = px.pie(status_counts, values='count', names='status', hole=0.4)
st.plotly_chart(fig4, use_container_width=True)

# ===== Top quốc gia đặt phòng nhiều nhất =====
st.subheader("🌍 Top quốc gia đặt phòng nhiều nhất")
top_countries = (
    filtered_df['country']
    .value_counts()
    .head(8)
    .reset_index()
    .rename(columns={'index': 'country', 'country': 'bookings'})
)
fig5 = px.bar(top_countries, x='bookings', y='country', orientation='h', height=450)
st.plotly_chart(fig5, use_container_width=True)
