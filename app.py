import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load dữ liệu =====
df = pd.read_csv("process_hotel.csv")

# ===== Tính toán thêm cột =====
df['children'].fillna(0, inplace=True)
df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
df['arrival_date'] = pd.to_datetime(df['reservation_status_date'], dayfirst=True, errors='coerce')
df['day_of_week'] = df['arrival_date'].dt.day_name()

# Doanh thu chỉ tính cho booking không bị huỷ
df['revenue'] = df.apply(
    lambda row: row['adr'] * row['total_nights'] if row['is_canceled'] == 0 else 0, axis=1
)

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

# ===== Chỉ số tổng quan =====
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số lượng đặt trước", f"{len(filtered_df):,}")
c2.metric("Số lượng huỷ", f"{filtered_df['is_canceled'].sum():,}")
c3.metric("Số lượng khách", f"{int(filtered_df[filtered_df['is_canceled'] == 0]['total_guests'].sum()):,}")
c4.metric("Doanh thu", f"{int(filtered_df['revenue'].sum()):,}")
st.markdown("---")

# ===== Biểu đồ: Doanh thu theo loại khách sạn =====
st.subheader("🏨 Tổng doanh thu theo loại hotel")
hotel_rev = filtered_df[filtered_df['is_canceled'] == 0].groupby('hotel')['revenue'].sum().reset_index()
colors = ['#1f77b4' if hotel != 'Resort Hotel' else '#ff7f0e' for hotel in hotel_rev['hotel']]
fig1 = px.bar(hotel_rev, x='hotel', y='revenue', color='hotel', color_discrete_sequence=colors,
              labels={'revenue': 'Doanh thu', 'hotel': 'Loại hotel'}, height=400)
st.plotly_chart(fig1, use_container_width=True)

# ===== Biểu đồ: Top quốc gia đặt phòng =====
st.subheader("🌍 Top quốc gia đặt phòng nhiều nhất")
top_countries = (
    filtered_df[filtered_df['is_canceled'] == 0]['country']
    .value_counts()
    .head(10)
    .reset_index()
    .rename(columns={'index': 'country', 'country': 'bookings'})
)
fig2 = px.bar(top_countries, x='bookings', y='country', orientation='h',
              color='country', height=500, width=1000)
st.plotly_chart(fig2, use_container_width=True)

# ===== Biểu đồ: Tỷ lệ huỷ theo loại hotel =====
st.subheader("📉 Tỷ lệ huỷ phòng theo loại hotel")
cancel_rate = (
    filtered_df.groupby('hotel')['is_canceled']
    .mean().reset_index()
)
cancel_rate['cancel_rate'] = cancel_rate['is_canceled'] * 100
fig3 = px.bar(cancel_rate, x='hotel', y='cancel_rate',
              color='hotel', color_discrete_sequence=colors,
              labels={'cancel_rate': 'Tỷ lệ huỷ (%)'}, height=400)
st.plotly_chart(fig3, use_container_width=True)

# ===== Biểu đồ: Trạng thái đặt phòng =====
st.subheader("📦 Phân bố trạng thái đặt phòng")
status_data = (
    filtered_df['reservation_status']
    .value_counts(normalize=True)
    .reset_index()
    .rename(columns={'index': 'status', 'reservation_status': 'percentage'})
)
status_data['percentage'] *= 100
fig4 = px.pie(status_data, values='percentage', names='status',
              title='Trạng thái đặt phòng', hole=0.4)
st.plotly_chart(fig4, use_container_width=True)
