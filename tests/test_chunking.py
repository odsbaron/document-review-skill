from doc_review_agent.chunking import chunk_document, chunk_text


def test_short_text_is_single_chunk():
    chunks = chunk_text("Just one short paragraph.", max_chars=500)
    assert chunks == ["Just one short paragraph."]


def test_empty_text_returns_no_chunks():
    assert chunk_text("   \n\n  ", max_chars=500) == []


def test_chunks_respect_max_chars_and_overlap():
    paragraphs = [f"Paragraph {index}. " + "x" * 120 for index in range(30)]
    text = "\n\n".join(paragraphs)

    chunks = chunk_text(text, max_chars=500, overlap_chars=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
    # The next chunk starts with the tail of the previous one.
    tail = chunks[0][-100:].lstrip()
    assert chunks[1].startswith(tail)


def test_long_paragraph_is_split():
    text = "y" * 1000
    chunks = chunk_text(text, max_chars=300, overlap_chars=0)
    assert len(chunks) >= 4
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_heading_sections_are_tracked():
    text = (
        "# Title\n\nIntro paragraph.\n\n"
        "## Options\n\n" + ("Option detail. " * 40) + "\n\n"
        "## Risks\n\n" + ("Risk detail. " * 40)
    )

    chunks = chunk_document(text, max_chars=300, overlap_chars=0)

    sections = [chunk.section for chunk in chunks]
    assert any(section == "Title > Options" for section in sections)
    assert any(section == "Title > Risks" for section in sections)


def test_single_chunk_document_keeps_section():
    chunks = chunk_document("# Only Title\n\nBody.", max_chars=500)
    assert len(chunks) == 1
    assert chunks[0].section == "Only Title"
