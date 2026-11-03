from pathlib import Path
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".py", ".pdf"}


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path).expanduser()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    if extension == ".pdf":
        reader = PdfReader(path)
        pages = []

        for page in reader.pages:
            text = page.extract_text(extraction_mode="layout")

            if text and text.strip():
                pages.append(text)

        return "\n".join(pages)

