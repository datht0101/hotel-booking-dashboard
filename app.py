import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load dữ liệu =====
df = pd.read_csv("process_hotel.csv")

# ===== Kiểm tra & tạo thêm cột nếu thiếu =====
if 'total_guests' not in df.columns:
    df['children'].fillna(0, inplace=True)
    df['total_guests'] = df['adults'] + df['children'] + df['babies']

if 'total_nights' not in df.columns:
    df['total_nights'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']

if 'revenue' not in df.columns:
    df['revenue'] = df.apply(
        lambda row: row['adr'] * row['total_nights'] if row['is_canceled'] == 0 else 0,
        axis=1
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

# ===== Hiển thị các chỉ số tổng quan =====
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số lượng đặt trước", f"{len(filtered_df):,}")
c2.metric("Tỷ lệ huỷ phòng", f"{100 * filtered_df['is_canceled'].mean():.2f}%")
c3.metric("Số lượng khách", f"{int(filtered_df[filtered_df['is_canceled'] == 0]['total_guests'].sum()):,}")
c4.metric("Tổng doanh thu", f"{filtered_df['revenue'].sum():,.2f}")

st.markdown("---")

# ===== BIỂU ĐỒ: Doanh thu theo loại hotel =====
st.subheader("Tổng doanh thu theo loại hotel")
rev_by_hotel = filtered_df.groupby("hotel")['revenue'].sum().reset_index()
colors = ['#1f77b4' if h == 'City Hotel' else '#FFA500' for h in rev_by_hotel['hotel']]
fig1 = px.bar(rev_by_hotel, x='hotel', y='revenue', text_auto='.2s', color='hotel', color_discrete_sequence=colors)
st.plotly_chart(fig1, use_container_width=True)

# ===== BIỂU ĐỒ: Xu hướng doanh thu theo tháng =====
st.subheader("📈 Xu hướng doanh thu theo tháng")
monthly_revenue = filtered_df.groupby('arrival_date_month_num')['revenue'].sum().reset_index()
month_names = df[['arrival_date_month_num', 'arrival_date_month']].drop_duplicates().sort_values('arrival_date_month_num')
monthly_revenue = pd.merge(monthly_revenue, month_names, on='arrival_date_month_num')
fig2 = px.line(monthly_revenue.sort_values('arrival_date_month_num'), x='arrival_date_month', y='revenue', markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ===== BIỂU ĐỒ: Tỷ lệ huỷ theo loại hotel =====
st.subheader("Tỷ lệ huỷ phòng theo loại hotel")
cancel_rate = filtered_df.groupby('hotel')['is_canceled'].mean().reset_index()
cancel_rate['cancel_percent'] = cancel_rate['is_canceled'] * 100
fig3 = px.bar(cancel_rate, x='hotel', y='cancel_percent', color='hotel',
              color_discrete_sequence=colors, text_auto='.2f')
st.plotly_chart(fig3, use_container_width=True)

# ===== BIỂU ĐỒ: Trạng thái đặt phòng =====
st.subheader("Phân bổ trạng thái đặt phòng")
status_count = filtered_df['reservation_status'].value_counts().reset_index()
status_count.columns = ['status', 'count']
fig4 = px.pie(status_count, values='count', names='status', hole=0.5)
st.plotly_chart(fig4, use_container_width=True)

# ===== BIỂU ĐỒ: Top quốc gia đặt nhiều =====
st.subheader("🌍 Top quốc gia đặt phòng nhiều nhất")
top_countries = (
    filtered_df['country'].value_counts().head(8).reset_index()
    .rename(columns={'index': 'country', 'country': 'bookings'})
)
fig5 = px.bar(top_countries, x='bookings', y='country', orientation='h', text_auto='.2s')
fig5.update_layout(height=400)
st.plotly_chart(fig5, use_container_width=True)
