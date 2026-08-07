from chrome_diagnostic.models import DiagnosticResult, RunMetadata


def test_result_serialization():
    result = DiagnosticResult(metadata=RunMetadata(version="1.0.0", started_at="now"))
    payload = result.as_dict()
    assert payload["metadata"]["version"] == "1.0.0"
    assert payload["samples"] == []
