import pandas as pd
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import urllib
from babel.numbers import format_currency
from func  import DataAnalyzer, BrazilMapPlotter
sns.set(style='dark')
st.set_option('deprecation.showPyplotGlobalUse', False)

# Dataset
datetime_cols = ["order_approved_at", "order_delivered_carrier_date", "order_delivered_customer_date", "order_estimated_delivery_date", "order_purchase_timestamp", "shipping_limit_date"]
all_df = pd.read_csv("all_data.csv")
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

# Geolocation Dataset
geolocation = pd.read_csv('geolocation.csv')
data = geolocation.drop_duplicates(subset='customer_unique_id')

for col in datetime_cols:
    all_df[col] = pd.to_datetime(all_df[col])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

# Sidebar
with st.sidebar:
    # Title
    st.title("Caturdianta")

    # Logo Image
    st.image("gcl.png")

    # Date Range
    start_date, end_date = st.date_input(
        label="Pilih Tanggal",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )

# Main
main_df = all_df[(all_df["order_approved_at"] >= str(start_date)) & 
                 (all_df["order_approved_at"] <= str(end_date))]

function = DataAnalyzer(main_df)
map_plot = BrazilMapPlotter(data, plt, mpimg, urllib, st)

sum_order_items_df = function.total_penjualan_df()
daily_orders_df = function.tingkat_penjualan()
review_score, common_score = function.rating_skor_df()
state, most_common_state = function.demographic_state()
order_status, common_status = function.order_status_df()

# Title
st.title('Dashboard E-Commerce')

# total penjualan
st.subheader("Produk Terjual")
col1, col2 = st.columns(2)

with col1:
    total_items = sum_order_items_df["product_count"].sum()
    st.markdown(f"Total Barang: **{total_items}**")

with col2:
    avg_items = sum_order_items_df["product_count"].mean()
    st.markdown(f"Rata-Rata Barang: **{avg_items}**")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(45, 25))

colors = ["#068DA9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# First barchart
sns.barplot(
    x="product_count", 
    y="product_category_name_english", 
    data=sum_order_items_df.head(5),
    legend=False,
    hue="product_category_name_english", 
    palette=colors, 
    ax=ax[0]
)

ax[0].set_ylabel(None)
ax[0].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[0].set_title("Penjualan produk tertinggi", loc="center", fontsize=50)
ax[0].tick_params(axis ='y', labelsize=35)
ax[0].tick_params(axis ='x', labelsize=30)

# Second barchart
sns.barplot(
    x="product_count", 
    y="product_category_name_english", 
    data=sum_order_items_df.sort_values(by="product_count", ascending=True).head(5), 
    palette=colors,
    legend=False,
    hue="product_category_name_english",  
    ax=ax[1]
)
ax[1].set_ylabel(None)
ax[1].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Penjualan produk terendah", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

most_sold_item = sum_order_items_df.loc[sum_order_items_df["product_count"].idxmax(), "product_category_name_english"]
least_sold_item = sum_order_items_df.loc[sum_order_items_df["product_count"].idxmin(), "product_category_name_english"]

with st.expander("Lihat Penjelasan"):
    st.write(f"Grafik ditas menunjukan barang dengan tingkat penjualan tertinggi adalah **{most_sold_item}** dan barang yang memiliki tingkat penjualan terendah adalah **{least_sold_item}**")
    
# Tingkat penjualan
st.subheader("penjualan Harian")

col1, col2 = st.columns(2)

with col1:
    total_order = daily_orders_df["order_count"].sum()
    st.markdown(f"Total Penjualan: **{total_order}**")

with col2:
    total_revenue = format_currency(daily_orders_df["revenue"].sum(), "IDR", locale="id_ID")
    st.markdown(f"Total Keuntungan: **{total_revenue}**")

max_order_date = daily_orders_df[daily_orders_df["order_count"] == daily_orders_df["order_count"].max()]["order_approved_at"].dt.date.iloc[0]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", labelsize=15)
st.pyplot(fig)

with st.expander("Lihat Penjelasan"):
    st.write(f"Grafik di atas menunjukan total penjualan harian adalah  {total_order} dan memiliki total keuntungan sebesar {total_revenue} dengan tanggal penjualan yaitu pada tanggal {max_order_date}")

# Customer Demographic
st.subheader("Demografi Pelanggan Per Kota")
most_common_state = state.customer_state.value_counts().index[0]
st.markdown(f"Kota Paling Banyak: **{most_common_state}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=state.customer_state.value_counts().index,
            y=state.customer_count.values,
            hue=state.customer_state.value_counts().index,
            data=state,
            palette=["#068DA9" if score == most_common_state else "#D3D3D3" for score in state.customer_state.value_counts().index]
            )

plt.title("Jumlah pelanggan per kota", fontsize=15)
plt.xlabel("Kota")
plt.ylabel("Jumlah Konsumen")
plt.xticks(fontsize=12)
st.pyplot(fig)

with st.expander("Lihat Penjelasan"):
    st.write(f"Grafik di atas menunjukan demografi pelanggan yang diketahui kota dengan pelanggan terbanyak adalah **{most_common_state}**")

# Pelanggan Demographic Order Status
st.subheader("Demografi Pelanggan Berdasarkan Order Status")
common_status_ = order_status.value_counts().index[0]
st.markdown(f"Order Status Paling Banyak: **{common_status_}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=order_status.index,
            y=order_status.values,
            hue=order_status.index,
            order=order_status.index,
            palette=["#068DA9" if score == common_status else "#D3D3D3" for score in order_status.index]
            )

plt.title("Order Status", fontsize=15)
plt.xlabel("Status")
plt.ylabel("Jumlah")
plt.xticks(fontsize=12)
st.pyplot(fig)

with st.expander("Lihat Penjelasan"):
    st.write(f"Grafik di atas menunjukan order status paling banyak adalah Delivered dengan total order **{common_status_}**")

# Pelanggan Demographic Geolocation
st.subheader("Demografi Konsumen")
map_plot.plot()

with st.expander("Lihat Penjelasan"):
    st.write(f"Grafik di atas menunjukan order status paling banyak adalah **{common_status_}**")

# Review Score
st.subheader("Rating skor")
col1,col2 = st.columns(2)

with col1:
    avg_review_score = review_score.mean()
    st.markdown(f"Rata-rata Rating: **{avg_review_score}**")

with col2:
    most_common_review_score = review_score.value_counts().index[0]
    st.markdown(f"Rating Terbanyak: **{most_common_review_score}**")

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x=review_score.index, 
            y=review_score.values,
            legend=False,  
            order=review_score.index,
            palette=["#068DA9" if score == common_score else "#D3D3D3" for score in review_score.index]
            )

plt.title("Rating kepuasan pelanggan", fontsize=15)
plt.xlabel("Rating")
plt.ylabel("Jumlah")
plt.xticks(fontsize=12)
st.pyplot(fig)

# Footer
st.caption('Copyright (C) Caturdianta 2023')
