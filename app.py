# streamlit_data_catalog_app.py
import streamlit as st
import pandas as pd
from PIL import Image
import webbrowser
import sqlalchemy
from sqlalchemy import create_engine, inspect, text

st.set_page_config(layout="wide", page_title="Data Catalog Navigator")
st.title("🏨 Hotel Booking Data Catalog")

# --------- Top-level configuration ---------
kaggle_url = "https://www.kaggle.com/datasets/saadharoon27/hotel-booking-dataset/data"
cleaning_strategy_img = "images/cleaning_strategy.png"
masking_strategy_img = "images/masking_strategy.png"

# --------- Navigation section ---------
st.markdown("### 📁 Data Source")
if st.button("🔗 View Raw Excel (Kaggle)"):
    webbrowser.open_new_tab(kaggle_url)

st.image("images/data_pipeline_diagram.png", caption="End-to-End Data Flow")

# --------- Pipeline block (clickable paths) ---------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Excel (Raw)")
    st.image("images/excel_icon.png", width=60)
    st.write("Source: hotel_booking.csv")
    if st.button("View on Kaggle"):
        webbrowser.open_new_tab(kaggle_url)

with col2:
    st.markdown("#### Data Cleaning")
    if st.button("Show Cleaning Strategy"):
        st.image(Image.open(cleaning_strategy_img), caption="Cleaning Strategy")

with col3:
    st.markdown("#### hotel_dw_test")
    if st.button("Test Cleaning Strategy"):
        st.image(Image.open(cleaning_strategy_img), caption="Cleaning Strategy")
    if st.button("Test Masking Strategy"):
        st.image(Image.open(masking_strategy_img), caption="Masking Strategy")

with col4:
    st.markdown("#### hotel_dw_prod")
    if st.button("Prod Cleaning Strategy"):
        st.image(Image.open(cleaning_strategy_img), caption="Cleaning Strategy")
    if st.button("Prod Masking Strategy"):
        st.image(Image.open(masking_strategy_img), caption="Masking Strategy")

# --------- Database Explorer ---------
st.markdown("---")
st.markdown("### 🗂️ Explore Database Metadata")

# Sidebar login and DB selection
st.sidebar.markdown("## DB Connection Settings")
db_choice = st.sidebar.selectbox("Choose Environment", ["hotel_dw", "hotel_dw_test", "hotel_dw_prod"])
role_user = st.sidebar.selectbox("Login as User", ["dba_1", "developer_1", "engineer_1", "analyst_1"])

user_credentials = {
    "dba_1": {"user": "dba_1", "password": ""},
    "developer_1": {"user": "developer_1", "password": ""},
    "engineer_1": {"user": "engineer_1", "password": ""},
    "analyst_1": {"user": "analyst_1", "password": ""},
}

if st.sidebar.button("🔌 Connect to Database"):
    try:
        user = user_credentials[role_user]["user"]
        password = user_credentials[role_user]["password"]
        conn_str = f"postgresql+psycopg2://{user}:{password}@localhost:5431/{db_choice}"
        engine = create_engine(conn_str)
        inspector = sqlalchemy.inspect(engine)

        st.success(f"Connected as `{role_user}` to `{db_choice}`")

        st.markdown("#### 🔐 Role Access Info")
        st.markdown(f"**User**: `{role_user}`")
        st.markdown("**Accessible Tables:**")
        tables = inspector.get_table_names()
        st.write(tables)

        for table in tables:
            st.markdown(f"---\n### 📊 Table: `{table}`")
            columns = inspector.get_columns(table)
            df = pd.DataFrame(columns)
            df.rename(columns={"name": "Column", "type": "Type", "nullable": "Nullable"}, inplace=True)
            df["Primary Key"] = False
            df["PII"] = df["Column"].isin(["name", "email", "phone_number", "credit_card", "arrival_date", "reservation_status_date"])
            st.dataframe(df.style.apply(lambda x: ['background-color: salmon' if v else '' for v in x["PII"]], axis=1), use_container_width=True)

            if table == "dim_customer":
                st.markdown("#### 📈 Classification Distribution")
                try:
                    query = text("SELECT classification, COUNT(*) FROM dim_customer GROUP BY classification")
                    with engine.connect() as conn:
                        result = conn.execute(query).fetchall()
                    class_df = pd.DataFrame(result, columns=["Classification", "Count"])
                    st.bar_chart(class_df.set_index("Classification"))
                except Exception as e:
                    st.warning(f"⚠️ Cannot access classification breakdown: {e}")

    except Exception as e:
        st.error(f"Failed to connect or load metadata: {e}")
