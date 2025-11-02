# main.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os  # Pastikan ini ada

# Konfigurasi tampilan halaman Streamlit
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# --- PATH CORRECTION (FINAL) ---

# 1. Dapatkan path absolut ke folder tempat script ini (main.py) berada
#    Contoh: /Users/Anda/Proyek/submission_e-commerce_dicoding/dasboard
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Gabungkan path folder tersebut dengan nama file CSV
#    Ini akan membuat path lengkap seperti:
#    /.../dasboard/customers_df.csv
CUSTOMER_PATH = os.path.join(BASE_DIR, 'customers_df.csv')
ORDER_ITEMS_PATH = os.path.join(BASE_DIR, 'order_items_df.csv')
ORDER_PAYMENTS_PATH = os.path.join(BASE_DIR, 'order_payments_df.csv')
ORDERS_PATH = os.path.join(BASE_DIR, 'orders_df.csv')
SELLERS_PATH = os.path.join(BASE_DIR, 'sellers_dataset_df.csv')
ORDER_FULL_PATH = os.path.join(BASE_DIR, 'order_full.csv')


# --- LOAD DATA ---
@st.cache_data
def load_data():
    # 3. Gunakan variabel path yang sudah benar
    customers_df = pd.read_csv(CUSTOMER_PATH)
    order_items_df = pd.read_csv(ORDER_ITEMS_PATH)
    order_payments_df = pd.read_csv(ORDER_PAYMENTS_PATH)
    orders_df = pd.read_csv(ORDERS_PATH)
    sellers_dataset_df = pd.read_csv(SELLERS_PATH)
    order_full = pd.read_csv(ORDER_FULL_PATH)
    
    return customers_df,  order_items_df, order_payments_df, orders_df, sellers_dataset_df, order_full


# --- LOAD SEMUA DATA ---
customers_df,  order_items_df, order_payments_df, orders_df, sellers_dataset_df, order_full = load_data()
# --- SIDEBAR ---
st.sidebar.title("📊 E-Commerce Dashboard")

menu = st.sidebar.radio("Pilih Tampilan:", ["Overview", "Customer & Seller", "RFM Analysis"])

# --- 1️⃣ OVERVIEW SECTION ---
if menu == "Overview":
    st.title("🛒 E-Commerce Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(orders_df))
    col2.metric("Total Customers", customers_df['customer_id'].nunique())
    col3.metric("Total Sellers", sellers_dataset_df['seller_id'].nunique())


    # --- PAYMENT METHOD BOXPLOT ---
    st.write("### Distribusi Nilai Transaksi per Metode Pembayaran")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=order_payments_df,
        x="payment_value",
        y="payment_type",
        showfliers=False,
        palette="Blues",
        ax=ax
    )
    ax.set_title("Nilai Transaksi Berdasarkan Metode Pembayaran", fontsize=14, fontweight='bold')
    ax.set_xlabel("Nilai Transaksi (Rp)")
    ax.set_ylabel("Metode Pembayaran")
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    # --- INSIGHT ---
    st.markdown(f"**Insight:** Dari visualisasi tersebut, kita dapat melihat nilai minimal dan maksimal dari setiap metode pembayaran. Terlihat bahwa metode pembayaran menggunakan credit card memiliki nilai transaksi paling tinggi dibandingkan dengan metode pembayaran lainnya, menunjukkan bahwa pelanggan cenderung melakukan pembelian dengan nominal lebih besar saat menggunakan kartu kredit..")
    st.markdown(f"**Conclusion:** Conclution pertanyaan 1: Transaksi yang besar biasany menggunakan kredit card, sehingga untuk strategi bisnis kedepanya dapat memberikan voucher dengan dengan S&K terdapat minimal pembelian.")

# --- CUSTOMER & SELLER SECTION ---
elif menu == "Customer & Seller":
    st.title("👥 Analisis Customer & Seller per State")

    # Pastikan kolom yang digunakan tersedia
    if "customer_state" in customers_df.columns:
        bycustomer_df = customers_df.groupby("customer_state").customer_unique_id.nunique().reset_index()
        bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    else:
        st.warning("Kolom 'customer_state' tidak ditemukan di customers_df.")
        st.stop()

    if "seller_state" in sellers_dataset_df.columns:
        byseller_df = sellers_dataset_df.groupby("seller_state").seller_id.nunique().reset_index()
        byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)
    else:
        st.warning("Kolom 'seller_state' tidak ditemukan di sellers_dataset_df.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer per State (Top 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="customer_state", x="customer_count",
                    data=bycustomer_df.sort_values(by="customer_count", ascending=False).head(5), ax=ax, palette="Blues")
        st.pyplot(fig)

    with col2:
        st.subheader("Seller per State (Top 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="seller_state", x="seller_count",
                    data=byseller_df.sort_values(by="seller_count", ascending=False).head(5), ax=ax, palette="Greens")
        st.pyplot(fig)
    
    # Pastikan kolom yang digunakan tersedia
    if "customer_state" in customers_df.columns:
        bycustomer_df = customers_df.groupby("customer_state").customer_unique_id.nunique().reset_index()
        bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    else:
        st.warning("Kolom 'customer_state' tidak ditemukan di customers_df.")
        st.stop()

    if "seller_state" in sellers_dataset_df.columns:
        byseller_df = sellers_dataset_df.groupby("seller_state").seller_id.nunique().reset_index()
        byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)
    else:
        st.warning("Kolom 'seller_state' tidak ditemukan di sellers_dataset_df.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer per State (Bottom 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="customer_state", x="customer_count",
                    data=bycustomer_df.sort_values(by="customer_count", ascending=True).head(5), ax=ax, palette="Blues")
        st.pyplot(fig)

    with col2:
        st.subheader("Seller per State (Bottom 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="seller_state", x="seller_count",
                    data=byseller_df.sort_values(by="seller_count", ascending=True).head(5), ax=ax, palette="Greens")
        st.pyplot(fig)

    # --- INSIGHT ---
    
# --- RFM SECTION ---
elif menu == "RFM Analysis":
    st.title("💎 RFM (Recency, Frequency, Monetary) Analysis")

    # Pastikan merge berhasil
    if "order_id" in order_items_df.columns and "order_id" in order_payments_df.columns:
        order_full = pd.merge(order_items_df, order_payments_df, how="left", on="order_id")
    else:
        st.error("Kolom 'order_id' tidak ditemukan pada salah satu dataset!")
        st.stop()

    # Cek keberadaan kolom yang diperlukan
    required_cols = {"shipping_limit_date", "order_item_id", "price"}
    if not required_cols.issubset(order_full.columns):
        st.error(f"Kolom berikut tidak ditemukan di order_full: {required_cols - set(order_full.columns)}")
        st.stop()

    # Hitung nilai RFM
    rfm_df = order_full.groupby("order_id", as_index=False).agg({
        "shipping_limit_date": "max",
        "order_item_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["order_id", "max_shipping_limit_date", "frequency", "monetary"]

    rfm_df["max_shipping_limit_date"] = pd.to_datetime(rfm_df["max_shipping_limit_date"]).dt.date
    recent_date = rfm_df["max_shipping_limit_date"].max()
    rfm_df["recency"] = rfm_df["max_shipping_limit_date"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_shipping_limit_date", axis=1, inplace=True)
    rfm_df["order_short_id"] = rfm_df["order_id"].astype(str).str[:4]

    # Tampilkan tabel dan visualisasi
    st.write("### Tabel RFM")
    st.dataframe(rfm_df.head())

    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    sns.barplot(y="recency", x="order_short_id",
                data=rfm_df.sort_values(by="recency").head(5), ax=ax[0], palette="cool")
    ax[0].set_title("By Recency")
    sns.barplot(y="frequency", x="order_short_id",
                data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1], palette="crest")
    ax[1].set_title("By Frequency")
    sns.barplot(y="monetary", x="order_short_id",
                data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2], palette="rocket")
    ax[2].set_title("By Monetary")

    st.pyplot(fig)


# main.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi tampilan halaman Streamlit
st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    customers_df = pd.read_csv("customers_df.csv")
    order_items_df = pd.read_csv("order_items_df.csv")
    order_payments_df = pd.read_csv("order_payments_df.csv")
    orders_df = pd.read_csv("orders_df.csv")
    sellers_dataset_df = pd.read_csv("sellers_dataset_df.csv")
    order_full = pd.read_csv("order_full.csv")
    
    return customers_df,  order_items_df, order_payments_df, orders_df, sellers_dataset_df, order_full


# --- LOAD SEMUA DATA ---
customers_df,  order_items_df, order_payments_df, orders_df, sellers_dataset_df, order_full = load_data()

# --- SIDEBAR ---
st.sidebar.title("📊 E-Commerce Dashboard")

menu = st.sidebar.radio("Pilih Tampilan:", ["Overview", "Customer & Seller", "RFM Analysis"])

# --- 1️⃣ OVERVIEW SECTION ---
if menu == "Overview":
    st.title("🛒 E-Commerce Dataset Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", len(orders_df))
    col2.metric("Total Customers", customers_df['customer_id'].nunique())
    col3.metric("Total Sellers", sellers_dataset_df['seller_id'].nunique())


    # --- PAYMENT METHOD BOXPLOT ---
    st.write("### Distribusi Nilai Transaksi per Metode Pembayaran")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(
        data=order_payments_df,
        x="payment_value",
        y="payment_type",
        showfliers=False,
        palette="Blues",
        ax=ax
    )
    ax.set_title("Nilai Transaksi Berdasarkan Metode Pembayaran", fontsize=14, fontweight='bold')
    ax.set_xlabel("Nilai Transaksi (Rp)")
    ax.set_ylabel("Metode Pembayaran")
    ax.grid(True, linestyle="--", alpha=0.5)
    st.pyplot(fig)

    # --- INSIGHT ---
    st.markdown(f"**Insight:** Dari visualisasi tersebut, kita dapat melihat nilai minimal dan maksimal dari setiap metode pembayaran. Terlihat bahwa metode pembayaran menggunakan credit card memiliki nilai transaksi paling tinggi dibandingkan dengan metode pembayaran lainnya, menunjukkan bahwa pelanggan cenderung melakukan pembelian dengan nominal lebih besar saat menggunakan kartu kredit..")
    st.markdown(f"**Conclusion:** Conclution pertanyaan 1: Transaksi yang besar biasany menggunakan kredit card, sehingga untuk strategi bisnis kedepanya dapat memberikan voucher dengan dengan S&K terdapat minimal pembelian.")

# --- CUSTOMER & SELLER SECTION ---
elif menu == "Customer & Seller":
    st.title("👥 Analisis Customer & Seller per State")

    # Pastikan kolom yang digunakan tersedia
    if "customer_state" in customers_df.columns:
        bycustomer_df = customers_df.groupby("customer_state").customer_unique_id.nunique().reset_index()
        bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    else:
        st.warning("Kolom 'customer_state' tidak ditemukan di customers_df.")
        st.stop()

    if "seller_state" in sellers_dataset_df.columns:
        byseller_df = sellers_dataset_df.groupby("seller_state").seller_id.nunique().reset_index()
        byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)
    else:
        st.warning("Kolom 'seller_state' tidak ditemukan di sellers_dataset_df.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer per State (Top 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="customer_state", x="customer_count",
                    data=bycustomer_df.sort_values(by="customer_count", ascending=False).head(5), ax=ax, palette="Blues")
        st.pyplot(fig)

    with col2:
        st.subheader("Seller per State (Top 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="seller_state", x="seller_count",
                    data=byseller_df.sort_values(by="seller_count", ascending=False).head(5), ax=ax, palette="Greens")
        st.pyplot(fig)
    
    # Pastikan kolom yang digunakan tersedia
    if "customer_state" in customers_df.columns:
        bycustomer_df = customers_df.groupby("customer_state").customer_unique_id.nunique().reset_index()
        bycustomer_df.rename(columns={"customer_unique_id": "customer_count"}, inplace=True)
    else:
        st.warning("Kolom 'customer_state' tidak ditemukan di customers_df.")
        st.stop()

    if "seller_state" in sellers_dataset_df.columns:
        byseller_df = sellers_dataset_df.groupby("seller_state").seller_id.nunique().reset_index()
        byseller_df.rename(columns={"seller_id": "seller_count"}, inplace=True)
    else:
        st.warning("Kolom 'seller_state' tidak ditemukan di sellers_dataset_df.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer per State (Bottom 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="customer_state", x="customer_count",
                    data=bycustomer_df.sort_values(by="customer_count", ascending=True).head(5), ax=ax, palette="Blues")
        st.pyplot(fig)

    with col2:
        st.subheader("Seller per State (Bottom 5)")
        fig, ax = plt.subplots()
        sns.barplot(y="seller_state", x="seller_count",
                    data=byseller_df.sort_values(by="seller_count", ascending=True).head(5), ax=ax, palette="Greens")
        st.pyplot(fig)

    # --- INSIGHT ---
    
# --- RFM SECTION ---
elif menu == "RFM Analysis":
    st.title("💎 RFM (Recency, Frequency, Monetary) Analysis")

    # Pastikan merge berhasil
    if "order_id" in order_items_df.columns and "order_id" in order_payments_df.columns:
        order_full = pd.merge(order_items_df, order_payments_df, how="left", on="order_id")
    else:
        st.error("Kolom 'order_id' tidak ditemukan pada salah satu dataset!")
        st.stop()

    # Cek keberadaan kolom yang diperlukan
    required_cols = {"shipping_limit_date", "order_item_id", "price"}
    if not required_cols.issubset(order_full.columns):
        st.error(f"Kolom berikut tidak ditemukan di order_full: {required_cols - set(order_full.columns)}")
        st.stop()

    # Hitung nilai RFM
    rfm_df = order_full.groupby("order_id", as_index=False).agg({
        "shipping_limit_date": "max",
        "order_item_id": "nunique",
        "price": "sum"
    })
    rfm_df.columns = ["order_id", "max_shipping_limit_date", "frequency", "monetary"]

    rfm_df["max_shipping_limit_date"] = pd.to_datetime(rfm_df["max_shipping_limit_date"]).dt.date
    recent_date = rfm_df["max_shipping_limit_date"].max()
    rfm_df["recency"] = rfm_df["max_shipping_limit_date"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_shipping_limit_date", axis=1, inplace=True)
    rfm_df["order_short_id"] = rfm_df["order_id"].astype(str).str[:4]

    # Tampilkan tabel dan visualisasi
    st.write("### Tabel RFM")
    st.dataframe(rfm_df.head())

    fig, ax = plt.subplots(1, 3, figsize=(18, 6))
    sns.barplot(y="recency", x="order_short_id",
                data=rfm_df.sort_values(by="recency").head(5), ax=ax[0], palette="cool")
    ax[0].set_title("By Recency")
    sns.barplot(y="frequency", x="order_short_id",
                data=rfm_df.sort_values(by="frequency", ascending=False).head(5), ax=ax[1], palette="crest")
    ax[1].set_title("By Frequency")
    sns.barplot(y="monetary", x="order_short_id",
                data=rfm_df.sort_values(by="monetary", ascending=False).head(5), ax=ax[2], palette="rocket")
    ax[2].set_title("By Monetary")

    st.pyplot(fig)


