"""A learner's own file as the source for the Topic Builder (Goal 2). Plain
code, no AI.

The page sends a PDF, Word (.docx) or text file. Its text is read here, then
the parts that match the learner's topic are picked (simple keyword RAG, so a
long file still fits in one Builder call). The file itself is never saved.
"""
import io
import re
import zipfile
from xml.etree import ElementTree

MAX_BYTES = 25 * 1024 * 1024  # lecture slides with pictures are often over 10 MB
MAX_PAGES = 300
MAX_CHARS = 12000  # the same budget as the Wikipedia source
CHUNK_CHARS = 800
KINDS = {".pdf": "PDF", ".docx": "Word", ".txt": "text", ".md": "text"}

# Words that say nothing about the topic, so they do not count as a match.
_STOP = set("""a an the and or but so of to in on at for with by from as is are was were be been it its this that
these those what which who how why when where do does did can could should would will about into than then there
their they them you your we our i me my not no yes all any some more most very just also only file chapter part""".split())

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class FileError(ValueError):
    """The file could not be used. The message is safe to show the learner."""


def kind(name):
    ext = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in KINDS:
        raise FileError("Please upload a PDF, a Word file (.docx) or a text file.")
    return ext


def _pdf(data):
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise FileError("This PDF is locked with a password, so it cannot be read.")
        return "\n\n".join((page.extract_text() or "") for page in reader.pages[:MAX_PAGES])
    except (PdfReadError, ValueError, KeyError, TypeError) as e:
        if isinstance(e, FileError):
            raise
        raise FileError("This PDF could not be read, so please try another file.") from e


def _docx(data):
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            root = ElementTree.fromstring(z.read("word/document.xml"))
    except (zipfile.BadZipFile, KeyError, ElementTree.ParseError) as e:
        raise FileError("This Word file could not be read, so please save it as .docx and try again.") from e
    return "\n\n".join("".join(t.text or "" for t in p.iter(f"{_W}t")) for p in root.iter(f"{_W}p"))


def read(name, data):
    """The plain text of the file, or FileError."""
    if len(data) > MAX_BYTES:
        raise FileError("This file is larger than 25 MB, so please upload a smaller one.")
    ext = kind(name)
    if ext == ".pdf":
        text = _pdf(data)
    elif ext == ".docx":
        text = _docx(data)
    else:
        text = data.decode("utf-8", errors="replace")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 300:
        raise FileError("This file has too little text to build cases from. A scanned PDF has pictures of pages, "
                        "not text, so it cannot be read.")
    return text


def chunks(text):
    """Pieces of about CHUNK_CHARS, cut at paragraph ends where possible."""
    out, cur = [], ""
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        while len(para) > CHUNK_CHARS:  # one very long paragraph is cut at a sentence end
            cut = para.rfind(". ", 0, CHUNK_CHARS)
            cut = cut + 1 if cut > CHUNK_CHARS // 2 else CHUNK_CHARS
            if cur:
                out.append(cur)
                cur = ""
            out.append(para[:cut].strip())
            para = para[cut:].strip()
        if cur and len(cur) + len(para) > CHUNK_CHARS:
            out.append(cur)
            cur = ""
        cur = f"{cur}\n{para}".strip()
    if cur:
        out.append(cur)
    return [c for c in out if c]


def _words(text):
    return {w[:-1] if len(w) > 4 and w.endswith("s") else w  # "vaccines" matches "vaccine"
            for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP and len(w) > 2}


def select(text, topic=""):
    """Up to MAX_CHARS of the file, in its own order. With a topic, the pieces
    that share the most words with it; without one, pieces spread over the
    whole file, so a long file is not judged by its first pages only."""
    if len(text) <= MAX_CHARS:
        return text
    parts = chunks(text)
    want = _words(topic)
    if want:
        ranked = sorted(range(len(parts)), key=lambda i: (-len(want & _words(parts[i])), i))
    else:
        step = max(1, len(parts) // max(1, MAX_CHARS // CHUNK_CHARS))
        ranked = list(range(0, len(parts), step)) + [i for i in range(len(parts)) if i % step]
    picked, size = [], 0
    for i in ranked:
        if size + len(parts[i]) + 2 > MAX_CHARS:  # + 2 for the blank line that joins them
            continue
        picked.append(i)
        size += len(parts[i]) + 2
    return "\n\n".join(parts[i] for i in sorted(picked))
