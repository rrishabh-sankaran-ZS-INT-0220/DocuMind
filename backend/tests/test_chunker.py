from backend.app.rag.parsers.base import ParsedDocument, ParsedPage
from backend.app.rag.pipeline.chunker import Chunk, chunk_document


def make_text(word: str, count: int) -> str:
    return " ".join([word] * count)


def test_chunk_document_single_page_respects_max_tokens_and_overlap():
    # 600 tokens -> should produce 2 chunks with overlap.
    text = make_text("token", 600)
    page = ParsedPage(page_number=1, text=text, section_title="Section 1")
    parsed = ParsedDocument(pages=[page])

    chunks = chunk_document(parsed, max_tokens=512, overlap=64)

    assert len(chunks) == 2
    assert chunks[0].page == 1
    assert chunks[0].section == "Section 1"

    first_tokens = chunks[0].text.split()
    second_tokens = chunks[1].text.split()

    assert len(first_tokens) <= 512
    assert len(second_tokens) <= 512

    # Overlap: first 64 tokens of second chunk should match last 64 of first.
    assert first_tokens[-64:] == second_tokens[:64]


def test_chunk_document_avoids_tiny_tail():
    # 520 tokens with 512 max and 64 overlap -> expect 1 chunk because tail is small.
    text = make_text("token", 520)
    page = ParsedPage(page_number=1, text=text, section_title=None)
    parsed = ParsedDocument(pages=[page])

    chunks = chunk_document(parsed, max_tokens=512, overlap=64)

    assert len(chunks) == 1
    assert len(chunks[0].text.split()) == 520


def test_chunk_document_multiple_pages_preserves_page_metadata():
    page1 = ParsedPage(page_number=1, text=make_text("p1", 300), section_title="Intro")
    page2 = ParsedPage(page_number=2, text=make_text("p2", 300), section_title="Body")
    parsed = ParsedDocument(pages=[page1, page2])

    chunks = chunk_document(parsed, max_tokens=256, overlap=64)

    pages = {c.page for c in chunks}
    sections = {c.section for c in chunks}

    assert pages == {1, 2}
    assert sections == {"Intro", "Body"}
