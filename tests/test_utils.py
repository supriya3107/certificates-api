from app.utils.file_utils import safe_filename


def test_safe_filename_removes_path_traversal():
    result = safe_filename("../../etc/passwd")
    assert "/" not in result
    assert ".." not in result


def test_safe_filename_keeps_normal_names():
    assert safe_filename("pasupula supriya") == "pasupula_supriya"


def test_safe_filename_fallback():
    assert safe_filename("///") == "certificate"