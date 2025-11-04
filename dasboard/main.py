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

    total_orders = df_filtered['order_id'].nunique()
    total_customers = df_filtered['customer_unique_id'].nunique()
    total_sellers = df_filtered['seller_id'].nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Sellers", total_sellers)

    st.write(f"### Distribusi Nilai Transaksi per Metode Pembayaran ({selected_year})")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=df_filtered,
        x="payment_value",
        y="payment_type",
        showfliers=False,
        palette="coolwarm",
        ax=ax
    )
    ax.set_xlabel("Nilai Transaksi (Rp)")
    ax.set_ylabel("Metode Pembayaran")
    ax.set_title("Distribusi Nilai Transaksi Berdasarkan Metode Pembayaran", fontsize=14, fontweight='bold')
    st.pyplot(fig)

    st.markdown("""
    **Insight:**  
    Metode pembayaran credit_card memiliki distribusi nilai transaksi tertinggi di setiap tahunnya dibanding metode lainnya. Dapat menerapkan strategi dengan memberikan voucher/diskon/cashback pengguna credit card dengan salah satu syarat terdapat minimal transaksi dimana ini bertujuan untuk untuk meningkatkan rata-rata nilai pembelian, mendorong pembelian berulang, dan memperkuat loyalitas pelanggan.
    """)


# CUSTOMER & SELLER

elif menu == "Customer & Seller":
    st.title(f"👥 Analisis Customer & Seller per State ({selected_year})")

    # --- TOP SELLER & CUSTOMER ---
    bycustomer_df = df_filtered.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    byseller_df = df_filtered.groupby("seller_state")["seller_id"].nunique().reset_index()
    byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏆 Top 5 State dengan Customer Terbanyak")
        top_customer = bycustomer_df.sort_values(by="customer_count", ascending=False).head(5)

        # Visualisasi
        fig, ax = plt.subplots()
        sns.barplot(data=top_customer, y="customer_state", x="customer_count", palette="Blues", ax=ax)
        ax.set_xlabel("Total Customer")
        ax.set_ylabel("State")
        st.pyplot(fig)

        # Tabel
        st.write("**Tabel: Top 5 State dengan Customer Terbanyak**")
        st.dataframe(top_customer.rename(columns={
            "customer_state": "Negara Bagian",
            "customer_count": "Total Customer"
        }))

    with col2:
        st.subheader("🏆 Top 5 State dengan Seller Terbanyak")
        top_seller = byseller_df.sort_values(by="seller_count", ascending=False).head(5)

        # Visualisasi
        fig, ax = plt.subplots()
        sns.barplot(data=top_seller, y="seller_state", x="seller_count", palette="Greens", ax=ax)
        ax.set_xlabel("Total Seller")
        ax.set_ylabel("State")
        st.pyplot(fig)

        # Tabel
        st.write("**Tabel: Top 5 State dengan Seller Terbanyak**")
        st.dataframe(top_seller.rename(columns={
            "seller_state": "Negara Bagian",
            "seller_count": "Total Seller"
        }))

    # --- Insight Strategis ---
    st.markdown(f"""
    **Insight:**  
    Negara bagian dengan jumlah penjual dan pembeli tertinggi setiap tahunnya yaitu **SP**.  
    Strategi yang diusulkan: **mempertahankan loyalitas pelanggan di wilayah SP** dengan program seperti *voucher gratis ongkir*  
    atau *diskon eksklusif bagi pembeli aktif*.  
    Tujuannya adalah menjaga **retensi pelanggan** dan **meningkatkan frekuensi pembelian** di pasar terbesar tersebut.
    """)

    # --- BOTTOM SELLER & CUSTOMER ---
    col3, col4 = st.columns(2)

    with col3:
        st.subheader(" 5 Negara dengan Customer Sedikit")
        bottom_customer = bycustomer_df.sort_values(by="customer_count", ascending=True).head(5)

        fig, ax = plt.subplots()
        sns.barplot(data=bottom_customer, y="customer_state", x="customer_count", palette="Blues", ax=ax)
        ax.set_xlabel("Total Customer")
        ax.set_ylabel("State")
        st.pyplot(fig)

        # Tabel
        st.write("**Tabel: 5 State dengan Customer Sedikit**")
        st.dataframe(bottom_customer.rename(columns={
            "customer_state": "Negara Bagian",
            "customer_count": "Total Customer"
        }))

    with col4:
        st.subheader(" 5 Negara dengan Seller Sedikit")
        bottom_seller = byseller_df.sort_values(by="seller_count", ascending=True).head(5)

        fig, ax = plt.subplots()
        sns.barplot(data=bottom_seller, y="seller_state", x="seller_count", palette="Greens", ax=ax)
        ax.set_xlabel("Total Seller")
        ax.set_ylabel("State")
        st.pyplot(fig)

        # Tabel
        st.write("**Tabel: 5 State dengan Seller Sedikit**")
        st.dataframe(bottom_seller.rename(columns={
            "seller_state": "Negara Bagian",
            "seller_count": "Total Seller"
        }))

    
    st.markdown(f"""
        **Insight:**  
        Strategi untuk customer dan penjual paling sedikit di setiap negara dapat menerapkan diskon/cashback khusus wilayah serta voucher khusus untuk pelanggan yang mengajak teman/referal. Hal ini bertujuan untuk menarik minat pembelian pertama, meningkatkan aktivitas transaksi, serta membangun loyalitas pelanggan baru di wilayah dengan tingkat transaksi rendah.
        """)

# RFM ANALYSIS

elif menu == "RFM Analysis":
    st.title(f"💎 Analisis RFM (Recency, Frequency, Monetary) — {selected_year}")

    if "order_purchase_timestamp" in df_filtered.columns:
        recent_date = df_filtered["order_purchase_timestamp"].max()

        rfm_df = df_filtered.groupby("customer_unique_id", as_index=False).agg({
            "order_purchase_timestamp": "max",
            "order_id": "nunique",
            "payment_value": "sum"
        }).rename(columns={
            "order_purchase_timestamp": "last_purchase_date",
            "order_id": "frequency",
            "payment_value": "monetary"
        })

        # Hitung recency
        rfm_df["recency"] = (recent_date - rfm_df["last_purchase_date"]).dt.days

        # Hitung skor RFM
        rfm_df["RFM_score"] = (
            rfm_df["recency"].rank(ascending=True)
            + rfm_df["frequency"].rank(ascending=False)
            + rfm_df["monetary"].rank(ascending=False)
        )

        # 🔹 Tambahkan kolom ID singkat (4 karakter terakhir)
        rfm_df["customer_id"] = rfm_df["customer_unique_id"].astype(str).str[-4:]

        # Tampilkan top 5 pelanggan terbaik berdasarkan skor RFM
        best_customer = rfm_df.sort_values(by="RFM_score", ascending=True).head(5)

        st.subheader("Top 5 Pelanggan Terbaik Berdasarkan Skor RFM")
        st.dataframe(best_customer[["customer_id", "recency", "frequency", "monetary", "RFM_score"]])

        # Visualisasi menggunakan ID singkat
        fig, ax = plt.subplots(1, 3, figsize=(18, 6))
        sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency").head(5), ax=ax[0], palette="crest")
        sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1], palette="cool")
        sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2], palette="magma")

        ax[0].set_title("Recency (Terbaru)")
        ax[1].set_title("Frequency (Transaksi Terbanyak)")
        ax[2].set_title("Monetary (Pembelian Tertinggi)")

        st.pyplot(fig)

        st.markdown(f"""
        **Insight:**  
        Recency Menunjukkan pelanggan dengan waktu pembelian terakhir paling baru — artinya pelanggan yang masih aktif. Dengan sumbu-X = ID pelanggan dan Sumbu-Y = total belanja. Frequency menunjukkan pelanggan yang paling sering melakukan transaksi. Dengan Sumbu-X = ID pelanggan dan Sumbu-Y = Jumlah transaksi.
                    Monetary meruapakan pelanggan dengan total pengeluaran tertinggi selama periode analisis. Dengan Sumbu-X = ID pelanggan dan Sumbu-Y = Nilai total pembelian. pelanggan dengan frekuensi tinggi dan nilai transaksi besar dapat dikategorikan sebagai customer loyal. Dapat memberikan kategori membership berdasarkan jumlah transaksi atau total pesanan yang dilakukan dalam jangka waktu yang di tentunakan (6 bulan) dimana kategori tersebut mendapatkan spesial voucher, diskon dan promo produk lainnya.
        """)
