import io
from pathlib import Path
from fastapi import UploadFile
import pdfplumber

from config import settings
from utils.helpers import (
    logger,
    clean_text,
    InvalidFileTypeError,
    FileSizeExceededError,
    PDFProcessingError
)


class PDFService:
    """Service handling PDF file validation and text extraction using pdfplumber."""

    @staticmethod
    def validate_pdf(file: UploadFile, file_content: bytes) -> None:
        """
        Validate uploaded file extension, MIME type, and maximum file size.
        """
        # Validate File Extension
        filename = file.filename or ""
        ext = Path(filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            logger.warning(f"Validation failed: Invalid extension '{ext}' for file '{filename}'")
            raise InvalidFileTypeError("Invalid file extension. Only .pdf files are supported.")

        # Validate File Content Size
        content_size = len(file_content)
        if content_size == 0:
            logger.warning(f"Validation failed: Empty file uploaded '{filename}'")
            raise InvalidFileTypeError("Uploaded PDF file is empty.")

        if content_size > settings.MAX_UPLOAD_SIZE_BYTES:
            logger.warning(f"Validation failed: File size {content_size} exceeds limit {settings.MAX_UPLOAD_SIZE_BYTES}")
            raise FileSizeExceededError(
                f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
            )

        logger.info(f"PDF validation successful for file '{filename}' ({content_size} bytes)")

    @staticmethod
    def extract_text(file_content: bytes) -> str:
        """
        Extract readable text from PDF bytes using pdfplumber.
        Handles corrupted files, encrypted PDFs, and empty text.
        """
        extracted_pages = []

        try:
            with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                if len(pdf.pages) == 0:
                    raise PDFProcessingError("The uploaded PDF has no pages.")

                for page_number, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text()
                        if text:
                            extracted_pages.append(text)
                    except Exception as page_err:
                        logger.warning(f"Failed to extract text from page {page_number}: {str(page_err)}")

        except PDFProcessingError:
            raise
        except Exception as e:
            logger.error(f"Error opening or reading PDF: {str(e)}", exc_info=True)
            raise PDFProcessingError(
                "Could not parse PDF file. The file may be corrupted, encrypted, or invalid."
            )

        combined_text = "\n".join(extracted_pages)
        cleaned_text = clean_text(combined_text)

        if not cleaned_text or len(cleaned_text.strip()) < 30:
            logger.warning("Extracted text is empty or too short.")
            raise PDFProcessingError(
                "Could not extract sufficient text from the PDF. "
                "If this is a scanned image/photo resume, please provide a PDF containing selectable text."
            )

        logger.info(f"Successfully extracted {len(cleaned_text)} characters from PDF.")
        return cleaned_text
