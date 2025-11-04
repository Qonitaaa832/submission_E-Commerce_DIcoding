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
    Metode pembayaran dengan nilai transaksi tertinggi cenderung menggunakan **Credit Card**, 
    sedangkan transaksi dengan nominal rendah lebih banyak menggunakan **voucher**.
    """)


# CUSTOMER & SELLER

elif menu == "Customer & Seller":
    st.title(f"👥 Analisis Customer & Seller per State ({selected_year})")
    #Top Seller dan Customer
    bycustomer_df = df_filtered.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    byseller_df = df_filtered.groupby("seller_state")["seller_id"].nunique().reset_index()
    byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 State dengan Customer Terbanyak")
        fig, ax = plt.subplots()
        sns.barplot(data=bycustomer_df.sort_values(by="customer_count", ascending=False).head(5),
                    y="customer_state", x="customer_count", palette="Blues", ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("5 State dengan Seller Terbanyak")
        fig, ax = plt.subplots()
        sns.barplot(data=byseller_df.sort_values(by="seller_count", ascending=False).head(5),
                    y="seller_state", x="seller_count", palette="Greens", ax=ax)
        st.pyplot(fig)
    
    st.markdown(f"""
    **Insight:**  
    Distribusi pelanggan dan penjual per negara bagian menunjukkan konsentrasi utama di wilayah tertentu {selected_year if selected_year != '2016-2018' else 'analisis total periode'}.
    """)

    #Bottom seller dan Customer

    bycustomer_df = df_filtered.groupby("customer_state")["customer_unique_id"].nunique().reset_index()
    bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)

    byseller_df = df_filtered.groupby("seller_state")["seller_id"].nunique().reset_index()
    byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("5 State dengan Customer Sedikit")
        fig, ax = plt.subplots()
        sns.barplot(data=bycustomer_df.sort_values(by="customer_count", ascending=True).head(5),
                    y="customer_state", x="customer_count", palette="Blues", ax=ax)
        st.pyplot(fig)

    with col2:
        st.subheader("5 State dengan Seller Sedikit")
        fig, ax = plt.subplots()
        sns.barplot(data=byseller_df.sort_values(by="seller_count", ascending=True).head(5),
                    y="seller_state", x="seller_count", palette="Greens", ax=ax)
        st.pyplot(fig)
    


# RFM ANALYSIS

elif menu == "RFM Analysis":
    st.title(f" Analisis RFM (Recency, Frequency, Monetary) — {selected_year}")

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
        rfm_df["RFM_score"] = rfm_df["recency"].rank(ascending=True) + \
                              rfm_df["frequency"].rank(ascending=False) + \
                              rfm_df["monetary"].rank(ascending=False)

        best_customer = rfm_df.sort_values(by="RFM_score", ascending=True).head(5)

        st.subheader("Top 5 Pelanggan Terbaik Berdasarkan Skor RFM")
        st.dataframe(best_customer)

        # Visualisasi
        fig, ax = plt.subplots(1, 3, figsize=(18, 6))
        sns.barplot(y="recency", x="customer_unique_id", data=rfm_df.sort_values(by="recency").head(5), ax=ax[0], palette="crest")
        sns.barplot(y="frequency", x="customer_unique_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1], palette="cool")
        sns.barplot(y="monetary", x="customer_unique_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2], palette="magma")

        ax[0].set_title("Recency (Terbaru)")
        ax[1].set_title("Frequency (Transaksi Terbanyak)")
        ax[2].set_title("Monetary (Pembelian Tertinggi)")
        st.pyplot(fig)

        st.write("### 📋 Tabel RFM (Customer ID disingkat)")
        st.dataframe(rfm_df[['short_customer_id', 'recency', 'frequency', 'monetary']].head(15))

        st.markdown(f"""
        **Insight:**  
        Pelanggan dengan nilai *monetary* tertinggi memberikan kontribusi terbesar terhadap total pendapatan.  
        Strategi bisnis di tahun {selected_year if selected_year != '2016-2018' else 'periode analisis penuh'} 
        dapat difokuskan pada **retensi pelanggan bernilai tinggi** melalui program loyalitas, diskon eksklusif, 
        atau layanan premium.
        """)
