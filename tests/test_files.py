"""Goal 2: a learner's own file as the source for the Topic Builder."""
import base64
import io
import zipfile

import pytest
from fastapi.testclient import TestClient

from app import builder, files, limits, llm_client, main

PARA = "Volcanoes form where magma reaches the surface of the earth through cracks in the crust."
OTHER = "Rivers carry water from mountains to the sea and shape valleys over many years."


def docx(paragraphs):
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    body = "".join(f'<w:p><w:r><w:t>{p}</w:t></w:r></w:p>' for p in paragraphs)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("word/document.xml", f'<w:document xmlns:w="{w}"><w:body>{body}</w:body></w:document>')
    return buf.getvalue()


def test_reads_word_and_text_files():
    assert PARA in files.read("notes.docx", docx([PARA] * 5))
    assert PARA in files.read("notes.TXT", (PARA + "\n\n") .encode() * 5)


def test_refuses_bad_files():
    with pytest.raises(files.FileError, match="PDF, a Word"):
        files.read("photo.png", b"x" * 1000)
    with pytest.raises(files.FileError, match="too little text"):
        files.read("short.txt", b"Hello.")
    with pytest.raises(files.FileError, match="PDF could not be read"):
        files.read("broken.pdf", b"%PDF-1.4 not really a pdf" * 50)
    with pytest.raises(files.FileError, match="Word file"):
        files.read("broken.docx", b"not a zip" * 100)
    with pytest.raises(files.FileError, match="25 MB"):
        files.read("big.txt", b"x" * (files.MAX_BYTES + 1))


def test_select_keeps_short_files_and_picks_the_topic_in_long_ones():
    assert files.select(PARA) == PARA
    long = "\n\n".join([OTHER] * 200 + [PARA] * 3 + [OTHER] * 200)
    picked = files.select(long, "How do volcanoes form?")
    assert len(picked) <= files.MAX_CHARS and picked.count("Volcanoes") == 3
    spread = files.select(long)  # no topic: pieces from the whole file
    assert len(spread) <= files.MAX_CHARS and spread


def test_upload_builds_a_topic_from_the_file(monkeypatch):
    monkeypatch.setattr(llm_client, "PROVIDER", "mock")
    monkeypatch.setattr(limits, "DAILY_CALL_BUDGET", 0)
    builder._CACHE.clear()
    c = TestClient(main.app)
    data = base64.b64encode(docx([PARA] * 10)).decode()
    t = c.post("/api/topic", json={"text": "", "file": {"name": "Week 3 notes.docx", "data": data}}).json()
    assert t["source"] == {"kind": "file", "name": "Week 3 notes.docx"} and len(t["cases"]) == 3
    assert t["cases"][0]["source"] == t["source"]
    r = c.post("/api/session", json={"case": t["cases"][0]})
    assert r.status_code == 200  # the file source survives the recheck
    bad = c.post("/api/topic", json={"file": {"name": "x.pdf", "data": "!!not base64!!"}})
    assert bad.status_code == 400
    png = c.post("/api/topic", json={"file": {"name": "x.png", "data": data}})
    assert png.status_code == 400 and "PDF, a Word" in png.json()["detail"]
    builder._CACHE.clear()


def test_file_names_are_cleaned():
    assert builder.clean_source({"kind": "file", "name": "<script>notes</script>.pdf"})["name"] == "scriptnotesscript.pdf"
    assert builder.clean_source({"kind": "file", "name": ""}) == {"kind": "file", "name": "your file"}
