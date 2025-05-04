#!/usr/bin/env python
# coding: utf-8

# # 📊 Hotel Booking Dashboard (Full Streamlit + Ngrok in Colab)
# **Chạy từng ô bên dưới theo thứ tự để xem dashboard giống Tableau.**

# In[ ]:


# ✅ B1: Cài thư viện cần thiết
get_ipython().system('pip install streamlit pyngrok pandas plotly matplotlib --quiet')


# In[ ]:


# ✅ B2: Tạo app.py chứa toàn bộ mã dashboard
get_ipython().run_line_magic('%writefile', 'app.py')
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

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
    bubble_data = filtered_df.groupby(['arrival_date_day_of_month', 'day_of_week']).size().reset_index(name='count')
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    bubble_data['day_of_week'] = pd.Categorical(bubble_data['day_of_week'], categories=weekday_order, ordered=True)
    bubble_data = bubble_data.sort_values(['arrival_date_day_of_month', 'day_of_week'])
    fig2 = px.scatter(bubble_data, x='day_of_week', y='arrival_date_day_of_month', size='count', color='count', color_continuous_scale='Blues', labels={'day_of_week': 'Thứ', 'arrival_date_day_of_month': 'Ngày'}, height=350)
    fig2.update_traces(marker=dict(sizemode='diameter', line=dict(width=1, color='DarkSlateGrey')))
    fig2.update_layout(yaxis=dict(dtick=1))
    st.plotly_chart(fig2, use_container_width=True)

# ===== BIỂU ĐỒ: Waiting list =====
left2, right2 = st.columns(2)
with left2:
    st.subheader("⏳ Thời gian chờ xác nhận")
    wait_df = filtered_df.groupby('customer_type')['days_in_waiting_list'].mean().reset_index()
    fig3 = px.bar(wait_df, x='days_in_waiting_list', y='customer_type', orientation='h', color='customer_type', labels={'days_in_waiting_list': 'Ngày', 'customer_type': 'Loại khách'}, height=350)
    st.plotly_chart(fig3, use_container_width=True)

# ===== BIỂU ĐỒ: Lead Time =====
with right2:
    st.subheader("🚗 Thời gian chờ đến (Lead Time)")
    lead_df = filtered_df.groupby('customer_type')['lead_time'].mean().reset_index()
    fig4 = px.bar(lead_df, x='lead_time', y='customer_type', orientation='h', color='customer_type', labels={'lead_time': 'Ngày', 'customer_type': 'Loại khách'}, height=350)
    st.plotly_chart(fig4, use_container_width=True)


# In[ ]:


# ✅ B3: Upload file dữ liệu hotel_bookings 2.csv
from google.colab import files
uploaded = files.upload()


# In[ ]:


# ✅ B4: Mở dashboard bằng ngrok
from pyngrok import conf, ngrok
conf.get_default().auth_token = "2wdZTyL5QDHE5dGgSIRT6KiXCAp_7NqoRHHtaqFGEgP14QpNb"
public_url = ngrok.connect(addr=8501, proto="http")
import IPython
IPython.display.display(IPython.display.Markdown(f'👉 [MỞ DASHBOARD TẠI ĐÂY 🔗]({public_url})'))
get_ipython().system('streamlit run app.py &>/content/logs.txt &')

