import asyncio
from pathlib import Path

from backend.app.rag.parsers.base import ParsedDocument
from backend.app.rag.parsers.docx_parser import DOCXParser
from backend.app.rag.parsers.markdown_parser import MarkdownParser
from backend.app.rag.parsers.pdf import PDFParser
from backend.app.rag.parsers.txt_parser import TXTParser


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_txt_parser(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello TXT", encoding="utf-8")

    parser = TXTParser()
    doc: ParsedDocument = run(parser.parse(file_path))

    assert len(doc.pages) == 1
    assert "Hello TXT" in doc.pages[0].text


def test_markdown_parser(tmp_path: Path):
    file_path = tmp_path / "sample.md"
    file_path.write_text("# Title\n\nContent", encoding="utf-8")

    parser = MarkdownParser()
    doc: ParsedDocument = run(parser.parse(file_path))

    assert len(doc.pages) == 1
    assert "Title" in doc.pages[0].text


def test_docx_parser(tmp_path: Path):
    from docx import Document as DocxDocument

    file_path = tmp_path / "sample.docx"
    d = DocxDocument()
    d.add_paragraph("Hello DOCX")
    d.save(file_path)

    parser = DOCXParser()
    doc: ParsedDocument = run(parser.parse(file_path))

    assert len(doc.pages) == 1
    assert "Hello DOCX" in doc.pages[0].text


def test_pdf_parser(tmp_path: Path):
    import fitz

    file_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF")
    doc.save(file_path)

    parser = PDFParser()
    parsed: ParsedDocument = run(parser.parse(file_path))

    assert len(parsed.pages) == 1
    assert "Hello PDF" in parsed.pages[0].text
