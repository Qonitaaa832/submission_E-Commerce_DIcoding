import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Konfigurasi tampilan Streamlit
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

#  PATH SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ALL_PATH = os.path.join(BASE_DIR, 'all_data.csv')

#  LOAD DATA 
@st.cache_data
def load_data():
    all_data = pd.read_csv(ALL_PATH)
    # kolom tanggal dikonversi
    if 'order_purchase_timestamp' in all_data.columns:
        all_data['order_purchase_timestamp'] = pd.to_datetime(all_data['order_purchase_timestamp'])
        all_data['year'] = all_data['order_purchase_timestamp'].dt.year  # buat kolom tahun
    return all_data

all_data = load_data()

global_recent_date = all_data["order_purchase_timestamp"].dt.date.max()

# SIDEBAR 
st.sidebar.title("E-Commerce Dashboard")
menu = st.sidebar.radio("Pilih Tampilan:", ["Overview", "Customer & Seller", "RFM Analysis"])

# Filter Tahun
st.sidebar.subheader("📅 Filter Tahun")
years = sorted(all_data['year'].unique())
selected_year = st.sidebar.selectbox("Pilih Tahun", options=["2016-2018"] + [str(y) for y in years])

if selected_year != "2016-2018":
    df_filtered = all_data[all_data['year'] == int(selected_year)]
else:
    df_filtered = all_data.copy()


# PAYMENT

if menu == "Overview":
    st.title("Distribusi Nilai Transaksi per Metode Pembayaran")

    # Hitung metrik utama
    total_orders = df_filtered['order_id'].nunique()
    total_customers = df_filtered['customer_unique_id'].nunique()
    total_sellers = df_filtered['seller_id'].nunique()

    # Tampilkan metrik di 3 kolom
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Sellers", total_sellers)

    # Judul visualisasi
    st.write(f"### Distribusi Nilai Transaksi per Metode Pembayaran ({selected_year})")

    # Visualisasi boxplot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=df_filtered,
        x="payment_value",
        y="payment_type",
        showfliers=False,  # menyembunyikan outlier ekstrem agar tidak mengganggu visual
        palette="Blues",   # mengikuti palet warna dari kode awal
        ax=ax
    )

    ax.set_title("Nilai Transaksi Berdasarkan Metode Pembayaran", fontsize=14, fontweight='bold')
    ax.set_xlabel("Nilai Transaksi")
    ax.set_ylabel("Tipe Pembayaran")
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    #Tabel 
    st.write("### Tabel per Metode Pembayaran")

    payment_summary = (
        df_filtered.groupby(by="payment_type")
        .agg({
            "order_id": "nunique",
            "payment_value": ["max", "min", "mean", "std"]
        })
        .reset_index()
    )

    # Ubah nama kolom agar lebih mudah dibaca
    payment_summary.columns = [
        "Metode Pembayaran",
        "Jumlah Order",
        "Nilai Maksimum",
        "Nilai Minimum",
        "Rata-rata Nilai",
        "Standar Deviasi"
    ]

    st.dataframe(payment_summary, use_container_width=True)

    st.markdown("""
    **Insight:**  
    Metode pembayaran credit_card memiliki distribusi nilai transaksi tertinggi di setiap tahunnya dibanding metode lainnya. Dapat menerapkan strategi dengan memberikan voucher/diskon/cashback pengguna credit card dengan salah satu syarat terdapat minimal transaksi dimana ini bertujuan untuk untuk meningkatkan rata-rata nilai pembelian, mendorong pembelian berulang, dan memperkuat loyalitas pelanggan.
    """)


# CUSTOMER & SELLER

elif menu == "Customer & Seller":
    st.title(f"👥 Analisis Customer & Seller per State ({selected_year})")

    # --- Kelompokkan Customer & Seller berdasarkan State ---
    bycustomer_df = df_filtered.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    byseller_df = df_filtered.groupby("seller_state")["seller_id"].nunique().reset_index()
    byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)

    # --- Visualisasi Customer ---
    st.subheader(" Negara dengan Jumlah Customer Terbanyak & Sedikit")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(
        x="customer_count", y="customer_state",
        data=bycustomer_df.sort_values(by="customer_count", ascending=False).head(5),
        palette=colors, ax=ax[0]
    )
    ax[0].set_title("Top 5 Negara dengan Customer Terbanyak", fontsize=13)
    ax[0].set_xlabel("Total Customer")
    ax[0].set_ylabel(None)

    sns.barplot(
        x="customer_count", y="customer_state",
        data=bycustomer_df.sort_values(by="customer_count", ascending=True).head(5),
        palette=colors, ax=ax[1]
    )
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Top 5 Negara dengan Customer Sedikit", fontsize=13)
    ax[1].set_xlabel("Total Customer")
    ax[1].set_ylabel(None)

    plt.suptitle("Analisis Customer per State", fontsize=16)
    st.pyplot(fig)
    
     # --- Tabel Customer ---
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Tabel: 5 Negara dengan Customer Terbanyak**")
        st.dataframe(bycustomer_df.sort_values(by="customer_count", ascending=False).head(5)
                     .rename(columns={"customer_state": "Negara Bagian", "customer_count": "Total Customer"}))
    with col2:
        st.write("**Tabel: 5 Negara dengan Customer Sedikit**")
        st.dataframe(bycustomer_df.sort_values(by="customer_count", ascending=True).head(5)
                     .rename(columns={"customer_state": "Negara Bagian", "customer_count": "Total Customer"}))
        
    # --- Insight Strategis ---
    st.markdown(f"""
    **Insight:**  
    Perbedaan jumlah pelanggan antara negara SP dan RR sangat signifikan, yaitu sekitar puluhan ribu pelanggan, menunjukkan konsentrasi pelanggan yang sangat besar di wilayah SP dibandingkan negara bagian lainnya. 
                 strategi yang diusulkan adalah: mempertahankan loyalitas di pasar negara "SP" dengan voucher gratis ongkir. al ini bertujuan untuk menjaga retensi pelanggan dan meningkatkan frekuensi pembelian pada wilayah dengan basis pelanggan terbesar. untuk pelanggan dengan jumlah sedikit, dapat diberikan diskon/cashback khusus wilayah serta voucher khusus untuk pelanggan yang mengajak teman/referal. Hal ini bertujuan untuk menarik minat pembelian pertama, meningkatkan aktivitas transaksi, serta membangun loyalitas pelanggan baru di wilayah dengan tingkat transaksi rendah.
    """)

    # --- Visualisasi Seller ---
    st.subheader(" Negara dengan Jumlah Seller Terbanyak & Sedikit")

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))

    sns.barplot(
        x="seller_count", y="seller_state",
        data=byseller_df.sort_values(by="seller_count", ascending=False).head(5),
        palette=colors, ax=ax[0]
    )
    ax[0].set_title("Top 5 Negara dengan Seller Terbanyak", fontsize=13)
    ax[0].set_xlabel("Total Seller")
    ax[0].set_ylabel(None)

    sns.barplot(
        x="seller_count", y="seller_state",
        data=byseller_df.sort_values(by="seller_count", ascending=True).head(5),
        palette=colors, ax=ax[1]
    )
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Top 5 Negara dengan Seller Sedikit", fontsize=13)
    ax[1].set_xlabel("Total Seller")
    ax[1].set_ylabel(None)

    plt.suptitle("Analisis Seller per State", fontsize=16)
    st.pyplot(fig)

     # --- Tabel Seller ---
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Tabel: 5 Negara dengan Seller Terbanyak**")
        st.dataframe(byseller_df.sort_values(by="seller_count", ascending=False).head(5)
                     .rename(columns={"seller_state": "Negara Bagian", "seller_count": "Total Seller"}))
    with col2:
        st.write("**Tabel: 5 Negara dengan Seller Sedikit**")
        st.dataframe(byseller_df.sort_values(by="seller_count", ascending=True).head(5)
                     .rename(columns={"seller_state": "Negara Bagian", "seller_count": "Total Seller"}))
    


    st.markdown(f"""
        **Insight:**  
        Berdasarkan visualisai dapat kita lihat selisih seller SP dengan negara bagian lainnya cukup besar. Kemungkinan seller belum merata di negara bagian lainnya.
                strategi untuk negara yang memiliki penjual terbanyak yaitu Menawarkan program seller ekslusif yang memberikan keuntungan tambahan seperti promosi produk prioritas atau biaya layanan yang lebih rendah serta memberikan tingkatan badge untuk penjual berdasarkan performal aktif dan order.
        """)

# RFM ANALYSIS

elif menu == "RFM Analysis":
    st.title(f"📊 RFM Analysis ({selected_year})")

    # --- Hitung RFM dari data yang sudah difilter (berdasarkan tahun yang dipilih) ---
    rfm_df = df_filtered.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max",   # tanggal terakhir transaksi
        "order_id": "nunique",               # jumlah pesanan unik
        "payment_value": "sum"               # total pendapatan
    })

    # Ubah nama kolom agar lebih mudah dipahami
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]

    # Hitung recency (berapa hari sejak transaksi terakhir)
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"]).dt.date
    recent_date = df_filtered["order_purchase_timestamp"].max().date()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    # Tambahkan ID pendek untuk visualisasi
    rfm_df["short_id"] = rfm_df["customer_id"].astype(str).str[:4]

    # --- RFM Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Recency (days)", round(rfm_df["recency"].mean(), 1))
    col2.metric("Average Frequency", round(rfm_df["frequency"].mean(), 2))
    col3.metric("Average Monetary", f"{rfm_df['monetary'].mean():,.2f}")

    # --- Visualisasi RFM ---
    st.write("### RFM Parameters")

    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
    colors = ["#72BCD4"] * 5

    # By Recency (semakin kecil semakin baik)
    sns.barplot(
        y="recency", x="short_id",
        data=rfm_df.sort_values(by="recency", ascending=True).head(5),
        palette=colors, ax=ax[0]
    )
    ax[0].set_title("By Recency (days)", fontsize=15)
    ax[0].set_xlabel(None)
    ax[0].set_ylabel(None)
    ax[0].tick_params(axis='x', labelsize=13)

    # By Frequency
    sns.barplot(
        y="frequency", x="short_id",
        data=rfm_df.sort_values(by="frequency", ascending=False).head(5),
        palette=colors, ax=ax[1]
    )
    ax[1].set_title("By Frequency", fontsize=15)
    ax[1].set_xlabel(None)
    ax[1].set_ylabel(None)
    ax[1].tick_params(axis='x', labelsize=13)

    # By Monetary
    sns.barplot(
        y="monetary", x="short_id",
        data=rfm_df.sort_values(by="monetary", ascending=False).head(5),
        palette=colors, ax=ax[2]
    )
    ax[2].set_title("By Monetary", fontsize=15)
    ax[2].set_xlabel(None)
    ax[2].set_ylabel(None)
    ax[2].tick_params(axis='x', labelsize=13)

    plt.suptitle("Best Customers Based on RFM Parameters", fontsize=18)
    st.pyplot(fig)

    # --- Tabel Data RFM ---
    st.write("### Data RFM")
    st.dataframe(rfm_df.head(10))


    # --- Insight ---
    st.markdown("""
    **Insight:**  
    Pelanggan dengan nilai *Recency* rendah berarti baru saja melakukan pembelian,  
    sementara *Frequency* tinggi menunjukkan loyalitas pelanggan yang kuat.  
    Pelanggan dengan *Monetary* tinggi berpotensi menjadi target utama untuk program loyalitas  
    seperti *exclusive offer* atau *member reward* agar tetap aktif bertransaksi.
    """)

