from chrome_diagnostic.chrome import ChromeProcessInfo


def test_process_model_does_not_contain_command_line_or_url_fields():
    fields = ChromeProcessInfo.__dataclass_fields__
    assert "command_line" not in fields
    assert "url" not in fields
    assert "profile_directory" in fields
