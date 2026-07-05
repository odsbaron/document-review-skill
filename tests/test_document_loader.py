from doc_review_agent.document_loader import load_document, read_text_best_effort


def test_utf8_text_is_readable(tmp_path):
    path = tmp_path / "doc.md"
    path.write_text("# 提案\n\n我们必须立即行动。", encoding="utf-8")
    document = load_document(path)
    assert "必须" in document.text
    assert document.kind == "markdown"


def test_gb18030_text_is_readable(tmp_path):
    path = tmp_path / "doc.md"
    path.write_bytes("# 提案\n\n我们必须立即行动。".encode("gb18030"))
    document = load_document(path)
    assert "必须" in document.text


def test_utf8_bom_is_stripped(tmp_path):
    path = tmp_path / "doc.txt"
    path.write_bytes(b"\xef\xbb\xbfhello")
    assert read_text_best_effort(path) == "hello"
