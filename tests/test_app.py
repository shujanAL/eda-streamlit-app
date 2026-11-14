from io import BytesIO
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from streamlit_app import MAX_FILE_SIZE, clean_data, csv_download, load_csv


class Upload(BytesIO):
    def __init__(self, content: bytes, name: str = "data.csv", size: int | None = None):
        super().__init__(content)
        self.name = name
        self.size = len(content) if size is None else size


def test_load_csv_reads_valid_upload() -> None:
    result = load_csv(Upload(b"name,score\nAda,10\nGrace,20\n"))
    assert result.to_dict("records") == [
        {"name": "Ada", "score": 10},
        {"name": "Grace", "score": 20},
    ]


@pytest.mark.parametrize(
    ("upload", "message"),
    [
        (Upload(b"a\n1\n", name="data.txt"), ".csv extension"),
        (Upload(b"a\n1\n", size=MAX_FILE_SIZE + 1), "10 MB limit"),
        (Upload(b"a\n"), "empty"),
    ],
)
def test_load_csv_rejects_invalid_uploads(upload: Upload, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        load_csv(upload)


def test_clean_data_removes_duplicates_and_missing_rows() -> None:
    source = pd.DataFrame(
        {"name": ["Ada", "Ada", "Grace"], "score": [10.0, 10.0, None]}
    )
    result = clean_data(source, remove_duplicates=True, remove_missing=True)
    assert result.to_dict("records") == [{"name": "Ada", "score": 10.0}]
    assert len(source) == 3


def test_csv_download_is_utf8_without_index() -> None:
    payload = csv_download(pd.DataFrame({"city": ["الرياض"], "value": [7]}))
    assert payload.decode("utf-8") == "city,value\nالرياض,7\n"


def test_app_starts_without_exceptions() -> None:
    app_path = Path(__file__).parents[1] / "streamlit_app.py"
    app = AppTest.from_file(app_path).run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "EDA Data Explorer"
    assert "Please upload a CSV file" in app.info[0].value


def test_analysis_renders_statistics_charts_cleaning_and_download() -> None:
    source = """
import pandas as pd
from streamlit_app import render_analysis

render_analysis(pd.DataFrame({
    "name": ["Ada", "Ada", "Grace"],
    "score": [10.0, 10.0, None],
}))
"""
    app = AppTest.from_string(source).run(timeout=30)
    assert not app.exception
    assert len(app.metric) == 4
    assert len(app.selectbox) == 2
    assert len(app.dataframe) == 5
    assert len(app.get("download_button")) == 1
    assert app.sidebar.checkbox[0].value is True
    assert app.sidebar.checkbox[1].value is False
