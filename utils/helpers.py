import logging
import re
from fastapi import HTTPException, status

# Configure Application Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("resume_analyzer")


def clean_text(text: str) -> str:
    """
    Clean extracted PDF text by normalizing whitespace, removing null characters,
    and trimming excessive empty lines.
    """
    if not text:
        return ""
    
    # Replace null characters
    text = text.replace("\x00", "")
    
    # Replace multiple empty lines with maximum 2 newlines
    text = re.sub(r'\n\s*\n', '\n\n', text)
    
    # Replace multiple spaces/tabs with single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    return text.strip()


def format_bytes(size: int) -> str:
    """Format file size in bytes to human-readable string (KB/MB)."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"


class CustomAppException(HTTPException):
    """Base custom exception for Resume Analyzer application."""
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class InvalidFileTypeError(CustomAppException):
    """Raised when file extension or MIME type is invalid."""
    def __init__(self, detail: str = "Invalid file type. Only PDF files are allowed."):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)


class FileSizeExceededError(CustomAppException):
    """Raised when uploaded file exceeds maximum allowed size."""
    def __init__(self, detail: str = "File size exceeds maximum limit of 10MB."):
        super().__init__(detail=detail, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)


class PDFProcessingError(CustomAppException):
    """Raised when pdfplumber fails to extract text or PDF is corrupted."""
    def __init__(self, detail: str = "Failed to process PDF resume. The file may be corrupted or password protected."):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class GeminiAnalysisError(CustomAppException):
    """Raised when Gemini API fails to process analysis."""
    def __init__(self, detail: str = "Failed to perform analysis. Please check your Gemini API key or try again later."):
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)
