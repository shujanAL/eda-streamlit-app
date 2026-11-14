from __future__ import annotations

from typing import BinaryIO

import pandas as pd
import streamlit as st


MAX_FILE_SIZE = 10 * 1024 * 1024


def load_csv(uploaded_file: BinaryIO) -> pd.DataFrame:
    """Validate and parse a Streamlit CSV upload."""
    name = getattr(uploaded_file, "name", "")
    if not name.lower().endswith(".csv"):
        raise ValueError("Please upload a file with a .csv extension.")

    size = getattr(uploaded_file, "size", None)
    if size is not None and size > MAX_FILE_SIZE:
        raise ValueError("File size exceeds the 10 MB limit.")

    dataframe = pd.read_csv(uploaded_file)
    if dataframe.empty:
        raise ValueError("The uploaded CSV file is empty.")
    return dataframe


def clean_data(
    dataframe: pd.DataFrame,
    *,
    remove_duplicates: bool,
    remove_missing: bool,
) -> pd.DataFrame:
    """Apply the cleaning controls without mutating the uploaded data."""
    cleaned = dataframe.copy()
    if remove_duplicates:
        cleaned = cleaned.drop_duplicates()
    if remove_missing:
        cleaned = cleaned.dropna()
    return cleaned


def csv_download(dataframe: pd.DataFrame) -> bytes:
    """Return a UTF-8 CSV payload suitable for Streamlit downloads."""
    return dataframe.to_csv(index=False, lineterminator="\n").encode("utf-8")


def render_analysis(df: pd.DataFrame) -> None:
    st.success("CSV file uploaded successfully!")

    st.sidebar.header("Data Cleaning")
    remove_duplicates = st.sidebar.checkbox("Remove duplicate rows", value=True)
    remove_missing = st.sidebar.checkbox(
        "Remove rows with missing values", value=False
    )
    cleaned_df = clean_data(
        df,
        remove_duplicates=remove_duplicates,
        remove_missing=remove_missing,
    )

    st.subheader("Cleaned Data Preview")
    st.dataframe(cleaned_df.head())
    st.download_button(
        label="Download Cleaned CSV",
        data=csv_download(cleaned_df),
        file_name="cleaned_data.csv",
        mime="text/csv",
    )

    st.subheader("Data Quality Summary")
    rows, columns = df.shape
    missing_values = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", rows)
    col2.metric("Columns", columns)
    col3.metric("Missing Values", missing_values)
    col4.metric("Duplicate Rows", duplicate_rows)

    st.subheader("Missing Values by Column")
    missing_summary = pd.DataFrame(
        {
            "Missing Count": df.isna().sum(),
            "Missing Percentage": (df.isna().mean() * 100).round(2),
        }
    )
    st.dataframe(missing_summary)

    st.subheader("Unique Values by Column")
    unique_summary = pd.DataFrame(
        {
            "Column": df.columns,
            "Unique Values": df.nunique(dropna=True).values,
        }
    )
    st.dataframe(unique_summary)

    st.subheader("Numerical Summary")
    numerical_data = df.select_dtypes(include="number")
    if numerical_data.shape[1] == 0:
        st.warning("No numerical columns found.")
    else:
        st.dataframe(numerical_data.describe())
        st.subheader("Numerical Visualization")
        selected_column = st.selectbox(
            "Select a numerical column", numerical_data.columns
        )
        st.bar_chart(
            numerical_data[selected_column].dropna().value_counts().sort_index()
        )

    st.subheader("Categorical Analysis")
    categorical_data = df.select_dtypes(
        include=["object", "category", "string", "bool"]
    )
    if categorical_data.shape[1] == 0:
        st.warning("No categorical columns found.")
    else:
        selected_category = st.selectbox(
            "Select a categorical column", categorical_data.columns
        )
        category_counts = categorical_data[selected_category].value_counts()
        st.dataframe(category_counts.rename("Count"))
        st.bar_chart(category_counts)


def main() -> None:
    st.set_page_config(
        page_title="EDA Data Explorer",
        page_icon="📊",
        layout="wide",
    )
    st.title("EDA Data Explorer")
    st.write("Upload a CSV file to explore and analyze your data.")
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file is None:
        st.info("Please upload a CSV file to get started.")
        return

    try:
        render_analysis(load_csv(uploaded_file))
    except pd.errors.EmptyDataError:
        st.error("The CSV file contains no data.")
    except pd.errors.ParserError:
        st.error("The CSV file format is invalid.")
    except UnicodeDecodeError:
        st.error("The CSV file encoding is not supported.")
    except ValueError as error:
        st.error(str(error))
    except Exception:
        st.error("An unexpected error occurred while processing the CSV file.")


if __name__ == "__main__":
    main()
