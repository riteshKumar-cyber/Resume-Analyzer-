from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from services.pdf_service import PDFService
from services.gemini_service import GeminiService
from utils.helpers import logger, CustomAppException

router = APIRouter(prefix="/api", tags=["Resume Analysis"])

gemini_service = GeminiService()


@router.get("/health", summary="Health Check Endpoint")
async def health_check():
    """Returns the operational status of the service."""
    return {
        "status": "online",
        "service": "Resume Analyzer API",
        "version": "1.0.0"
    }


@router.post("/analyze", summary="Analyze PDF Resume")
async def analyze_resume_endpoint(file: UploadFile = File(...)):
    """
    Upload and analyze a PDF resume.
    
    - **file**: PDF Resume file (max 10MB)
    
    Returns structured analysis containing ATS score, skills breakdown,
    strengths, weaknesses, suggestions, roadmap, and interview prep tips.
    """
    logger.info(f"Received resume analysis request for file: '{file.filename}'")

    try:
        # Read file content asynchronously
        file_content = await file.read()

        # Step 1: Validate PDF File (type, size, format)
        PDFService.validate_pdf(file, file_content)

        # Step 2: Extract readable text using pdfplumber
        extracted_text = PDFService.extract_text(file_content)

        # Step 3: Call analysis service for evaluation
        analysis_result = gemini_service.analyze_resume(extracted_text)

        logger.info(f"Resume analysis completed successfully for '{file.filename}'")

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "success": True,
                "message": "Resume analyzed successfully.",
                "filename": file.filename,
                "data": analysis_result
            }
        )

    except CustomAppException as custom_err:
        logger.warning(f"Handled application exception: {custom_err.detail}")
        raise custom_err
    except Exception as err:
        logger.error(f"Unhandled error in analyze_resume_endpoint: {str(err)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected internal error occurred: {str(err)}"
        )
