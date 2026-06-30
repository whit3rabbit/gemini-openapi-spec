from generate_drift_reports import _sdk_candidate_path


def test_file_search_download_media_sdk_path():
    assert _sdk_candidate_path("file_search_stores.py", "{clean_id}?alt=media") == (
        "/v1beta/fileSearchStores/{fileSearchStore}/media/{media}",
        "high",
    )
