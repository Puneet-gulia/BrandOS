"""Knowledge API endpoints."""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from apps.api.dependencies import KnowledgeServiceDep, SettingsDep
from packages.shared.errors import ExtractionError
from packages.shared.models.brand import BrandInput, BrandInputType, BrandProfile

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeExtractRequest(BaseModel):
    """Request payload for extracting brand profile."""
    input_type: str
    url: Optional[str] = None
    text: Optional[str] = None
    document_filename: Optional[str] = None
    document_content: Optional[str] = None


class BrandProfileResponse(BaseModel):
    """Response containing the extracted brand profile."""
    profile: BrandProfile


@router.post("/extract", response_model=BrandProfileResponse)
async def extract_brand_profile(
    request: KnowledgeExtractRequest, service: KnowledgeServiceDep
) -> BrandProfileResponse:
    """Extract a brand profile from a URL or text."""
    try:
        input_type_enum = BrandInputType(request.input_type.upper())
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid input type: {request.input_type}") from exc

    brand_input = BrandInput(
        input_type=input_type_enum,
        url=request.url,
        text=request.text,
        document_filename=request.document_filename,
        document_content=request.document_content,
    )

    try:
        profile = await service.extract_brand_profile(brand_input)
        return BrandProfileResponse(profile=profile)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error during extraction") from exc


@router.post("/extract-file", response_model=BrandProfileResponse)
async def extract_from_file(
    service: KnowledgeServiceDep,
    settings: SettingsDep,
    file: UploadFile = File(...),
    extra_context: Optional[str] = Form(None),
) -> BrandProfileResponse:
    """Extract a brand profile from an uploaded document."""
    if not file.filename:
        raise HTTPException(status_code=422, detail="Filename missing from upload")

    content_bytes = await file.read()
    
    if len(content_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Max size is {settings.max_upload_size_bytes} bytes."
        )

    try:
        profile = await service.extract_from_document(
            filename=file.filename,
            content_bytes=content_bytes,
            extra_context=extra_context,
        )
        return BrandProfileResponse(profile=profile)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error during file extraction") from exc
