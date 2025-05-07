import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load dữ liệu =====
df = pd.read_csv("process_hotel.csv")

# ===== Tổng quan chỉ số =====
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Số lượng đặt trước", f"{df.shape[0]:,}")
with col2:
    cancel_rate = df["is_canceled"].mean() * 100
    st.metric("Tỷ lệ huỷ phòng", f"{cancel_rate:.2f}%")
with col3:
    st.metric("ADR trung bình", f"{df['adr'].mean():.2f}")
with col4:
    st.metric("Tổng doanh thu", f"{df['revenue'].sum():,.2f}")

st.markdown("---")

# ===== Tổng doanh thu theo loại hotel =====
st.subheader("💰 Tổng doanh thu theo loại hotel")
revenue_by_hotel = df.groupby("hotel")["revenue"].sum().reset_index()
color_map = {"City Hotel": "steelblue", "Resort Hotel": "darkorange"}
fig1 = px.bar(revenue_by_hotel, x="hotel", y="revenue", color="hotel", 
              color_discrete_map=color_map, text_auto='.2s')
fig1.update_layout(showlegend=False)
st.plotly_chart(fig1, use_container_width=True)

# ===== Xu hướng doanh thu theo tháng =====
st.subheader("📈 Xu hướng doanh thu theo tháng")
month_revenue = df.groupby("arrival_date_month_num")["revenue"].sum().reset_index()
month_names = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
month_revenue["month"] = month_revenue["arrival_date_month_num"].map(month_names)
month_revenue = month_revenue.sort_values("arrival_date_month_num")
fig2 = px.line(month_revenue, x="month", y="revenue", markers=True, text="revenue")
fig2.update_traces(textposition="top center")
st.plotly_chart(fig2, use_container_width=True)

# ===== Tỷ lệ huỷ theo loại hotel =====
st.subheader("❌ Tỷ lệ huỷ phòng theo loại hotel")
cancel_rate_hotel = df.groupby("hotel")["is_canceled"].mean().reset_index()
cancel_rate_hotel["cancel_rate"] = cancel_rate_hotel["is_canceled"] * 100
fig3 = px.bar(cancel_rate_hotel, x="hotel", y="cancel_rate", color="hotel", 
              color_discrete_map=color_map, text_auto='.2f')
fig3.update_layout(showlegend=False, yaxis_title="Cancel Rate (%)")
st.plotly_chart(fig3, use_container_width=True)

# ===== Phân bổ trạng thái đặt phòng =====
st.subheader("📊 Phân bổ trạng thái đặt phòng")
status_counts = df["reservation_status"].value_counts().reset_index()
status_counts.columns = ["status", "count"]
fig4 = px.pie(status_counts, names="status", values="count", hole=0.4)
st.plotly_chart(fig4, use_container_width=True)

# ===== Top quốc gia đặt phòng nhiều nhất =====
st.subheader("🌍 Top quốc gia đặt phòng nhiều nhất")
top_countries = df["country"].value_counts().head(8).reset_index()
top_countries.columns = ["country", "bookings"]
fig5 = px.bar(top_countries, x="bookings", y="country", orientation='h',
              text="bookings", height=500)
fig5.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig5, use_container_width=True)
