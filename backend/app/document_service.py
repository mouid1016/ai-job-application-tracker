from io import BytesIO
from pathlib import Path
from uuid import uuid4
from zipfile import BadZipFile, ZipFile

from docx import Document as DocxDocument
from fastapi import HTTPException, UploadFile, status
from pypdf import PdfReader

from .config import settings


ALLOWED_EXTENSIONS = {".pdf", ".docx"}
CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def upload_directory() -> Path:
    directory = Path(settings.upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def clean_filename(filename: str | None) -> str:
    cleaned = Path(filename or "cv").name.strip()
    return cleaned[:255] or "cv"


def validate_document(filename: str, content: bytes) -> tuple[str, str]:
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF and DOCX files are supported",
        )
    if extension == ".pdf" and not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="This file is not a valid PDF")
    if extension == ".docx":
        try:
            with ZipFile(BytesIO(content)) as archive:
                if "word/document.xml" not in archive.namelist():
                    raise HTTPException(status_code=400, detail="This file is not a valid DOCX document")
        except BadZipFile:
            raise HTTPException(status_code=400, detail="This file is not a valid DOCX document") from None
    return extension, CONTENT_TYPES[extension]


def extract_text(extension: str, content: bytes) -> str:
    try:
        if extension == ".pdf":
            reader = PdfReader(BytesIO(content))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:
            document = DocxDocument(BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="The document could not be read") from exc

    normalised = "\n".join(line.strip() for line in text.splitlines() if line.strip()).strip()
    if not normalised:
        raise HTTPException(
            status_code=422,
            detail="No readable text was found. Scanned-image PDFs are not supported yet",
        )
    return normalised


async def read_upload(file: UploadFile) -> tuple[str, str, bytes, str]:
    filename = clean_filename(file.filename)
    maximum = settings.max_upload_size_mb * 1024 * 1024
    content = await file.read(maximum + 1)
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    if len(content) > maximum:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"CV files must be {settings.max_upload_size_mb} MB or smaller",
        )
    extension, content_type = validate_document(filename, content)
    return filename, content_type, content, extract_text(extension, content)


def store_document(content: bytes, content_type: str) -> str:
    extension = ".pdf" if content_type == "application/pdf" else ".docx"
    stored_filename = f"{uuid4().hex}{extension}"
    (upload_directory() / stored_filename).write_bytes(content)
    return stored_filename


def document_path(stored_filename: str) -> Path:
    path = upload_directory() / Path(stored_filename).name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="CV file not found")
    return path


def remove_document(stored_filename: str) -> None:
    path = upload_directory() / Path(stored_filename).name
    path.unlink(missing_ok=True)
