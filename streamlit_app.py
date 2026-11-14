
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="EDA Data Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("EDA Data Explorer")
st.write("Upload a CSV file to explore and analyze your data.")

uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)

if uploaded_file is None:
    st.info("Please upload a CSV file to get started.")
else:
    try:
        max_file_size = 10 * 1024 * 1024

        if uploaded_file.size > max_file_size:
            st.error("File size exceeds the 10 MB limit.")
            st.stop()

        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.error("The uploaded CSV file is empty.")
            st.stop()

        st.success("CSV file uploaded successfully!")

        # Sidebar controls
        st.sidebar.header("Data Cleaning")

        remove_duplicates = st.sidebar.checkbox(
            "Remove duplicate rows", value=True
        )
        remove_missing = st.sidebar.checkbox(
            "Remove rows with missing values", value=False
        )

        cleaned_df = df.copy()

        if remove_duplicates:
            cleaned_df = cleaned_df.drop_duplicates()

        if remove_missing:
            cleaned_df = cleaned_df.dropna()

        st.subheader("Cleaned Data Preview")
        st.dataframe(cleaned_df.head())

        st.download_button(
            label="Download Cleaned CSV",
            data=cleaned_df.to_csv(index=False).encode("utf-8"),
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

        # Data quality metrics
        st.subheader("Data Quality Summary")

        rows, columns = df.shape
        missing_values = df.isna().sum().sum()
        duplicate_rows = df.duplicated().sum()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Rows", rows)
        col2.metric("Columns", columns)
        col3.metric("Missing Values", missing_values)
        col4.metric("Duplicate Rows", duplicate_rows)

        # Missing values by column
        st.subheader("Missing Values by Column")

        missing_summary = pd.DataFrame({
            "Missing Count": df.isna().sum(),
            "Missing Percentage": (
                df.isna().mean() * 100
            ).round(2)
        })

        st.dataframe(missing_summary)

        # Numerical analysis
        st.subheader("Numerical Summary")

        numerical_data = df.select_dtypes(include="number")

        if numerical_data.shape[1] == 0:
            st.warning("No numerical columns found.")
        else:
            st.dataframe(numerical_data.describe())

            st.subheader("Numerical Visualization")

            selected_column = st.selectbox(
                "Select a numerical column",
                numerical_data.columns
            )

            st.bar_chart(
                numerical_data[selected_column]
                .dropna()
                .value_counts()
                .sort_index()
            )

        # Categorical analysis
        st.subheader("Categorical Analysis")

        categorical_data = df.select_dtypes(
            include=["object", "category", "string", "bool"]
        )

        if categorical_data.shape[1] == 0:
            st.warning("No categorical columns found.")
        else:
            selected_category = st.selectbox(
                "Select a categorical column",
                categorical_data.columns
            )

            category_counts = (
                categorical_data[selected_category].value_counts()
            )

            st.dataframe(category_counts.rename("Count"))
            st.bar_chart(category_counts)

    except pd.errors.EmptyDataError:
        st.error("The CSV file contains no data.")

    except pd.errors.ParserError:
        st.error("The CSV file format is invalid.")

    except UnicodeDecodeError:
        st.error("The CSV file encoding is not supported.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
