import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("📊 Hotel Booking Dashboard")

# ===== Load dữ liệu và xử lý =====
df = pd.read_csv("process_hotel.csv")

# Nếu chưa có cột doanh thu thì thêm
if "revenue" not in df.columns:
    df["total_nights"] = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["revenue"] = df.apply(
        lambda row: row["adr"] * row["total_nights"] if row["is_canceled"] == 0 else 0, axis=1
    )

# ===== KPIs =====
col1, col2, col3, col4 = st.columns(4)
col1.metric("Số lượng đặt trước", f"{len(df):,}")
col2.metric("Tỷ lệ huỷ phòng", f"{df['is_canceled'].mean() * 100:.2f}%")
col3.metric("ADR trung bình", f"{df['adr'].mean():,.2f}")
col4.metric("Tổng doanh thu", f"{df['revenue'].sum():,.2f}")

st.markdown("---")

# ===== Tổng doanh thu theo loại khách sạn =====
st.subheader("Tổng doanh thu theo loại hotel")
revenue_by_hotel = df.groupby("hotel")["revenue"].sum().reset_index()
fig1 = px.bar(revenue_by_hotel, x="hotel", y="revenue", text="revenue", labels={"revenue": "Doanh thu"})
st.plotly_chart(fig1, use_container_width=True)

# ===== Xu hướng doanh thu theo tháng =====
df["month"] = pd.Categorical(df["arrival_date_month"],
    categories=[
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ],
    ordered=True
)
rev_month = df.groupby("month")["revenue"].sum().reset_index()
st.subheader("Xu hướng doanh thu theo tháng")
fig2 = px.line(rev_month, x="month", y="revenue", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ===== Tỷ lệ huỷ phòng theo loại khách sạn =====
st.subheader("Tỷ lệ huỷ phòng theo loại hotel")
cancel_rate = df.groupby("hotel")["is_canceled"].mean().reset_index()
cancel_rate["cancel_rate"] = cancel_rate["is_canceled"] * 100
fig3 = px.bar(cancel_rate, x="hotel", y="cancel_rate", text="cancel_rate", labels={"cancel_rate": "Tỷ lệ hủy (%)"})
st.plotly_chart(fig3, use_container_width=True)

# ===== Phân bố trạng thái đặt phòng =====
st.subheader("Phân bố trạng thái đặt phòng")
status_dist = df["reservation_status"].value_counts(normalize=True).reset_index()
status_dist.columns = ["status", "ratio"]
status_dist["ratio"] *= 100
fig4 = px.pie(status_dist, names="status", values="ratio", hole=0.5)
st.plotly_chart(fig4, use_container_width=True)

# ===== Top quốc gia đặt phòng nhiều nhất =====
st.subheader("Top quốc gia đặt phòng nhiều nhất")
top_countries = df["country"].value_counts().nlargest(8).reset_index()
top_countries.columns = ["country", "bookings"]
fig5 = px.bar(top_countries, x="country", y="bookings", text="bookings", orientation="h")
fig5.update_layout(yaxis=dict(autorange="reversed"))
st.plotly_chart(fig5, use_container_width=True)
