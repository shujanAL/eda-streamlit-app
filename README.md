# EDA Streamlit App

An interactive CSV Data Explorer built with Python,
Pandas, and Streamlit.

## Features
- CSV upload and validation
- Data quality metrics
- Missing-value analysis
- Numerical and categorical summaries
- Interactive charts
- Data cleaning and CSV download

## Installation

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Python 3.11 through 3.14 is supported by the pinned dependency ranges.

## Usage
1. Upload a CSV dataset.
2. Explore data quality and statistics.
3. Select columns to visualize.
4. Choose cleaning options in the sidebar.
5. Download the cleaned CSV file.

## Project Files
- streamlit_app.py
- requirements.txt
- README.md
- .gitignore
- sample_data.csv

## Testing

```bash
pip install -r requirements-dev.txt
pytest
```

The automated suite covers valid and invalid CSV uploads, size and extension
validation, duplicate/missing-row cleaning, UTF-8 CSV downloads, and app startup.

## Deployment
Streamlit Community Cloud

Live URL: https://shujan-eda-explorer.streamlit.app
