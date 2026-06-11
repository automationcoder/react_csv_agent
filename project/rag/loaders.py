from pathlib import Path


class DocumentLoader:
    def load(self, path: str) -> str:
        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = file_path.suffix.lower()

        if suffix == ".txt":
            return self._load_txt(file_path)

        if suffix == ".pdf":
            return self._load_pdf(file_path)

        if suffix == ".docx":
            return self._load_docx(file_path)

        raise ValueError(f"Unsupported file type: {suffix}")

    def _load_txt(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def _load_pdf(self, path: Path) -> str:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            pages.append(page.extract_text() or "")

        return "\n".join(pages)

    def _load_docx(self, path: Path) -> str:
        from docx import Document

        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)