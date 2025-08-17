"""
Document upload and management API endpoints.
"""

import logging
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import CurrentUser, get_current_user
from config.settings import settings
from database.session import get_db
from models.chat import DocumentResponse, DocumentUploadResponse
from services.document_service import DocumentService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: UUID | None = Form(None),
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a document for processing."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
            )

        # Check file extension
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in settings.allowed_upload_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {', '.join(settings.allowed_upload_extensions)}",
            )

        # Check file size
        content = await file.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {settings.max_upload_size} bytes",
            )

        # Reset file pointer
        await file.seek(0)

        # Create document service
        doc_service = DocumentService(db)

        # Upload and save document
        document = await doc_service.upload_document(
            file=file,
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            session_id=session_id,
        )

        logger.info(f"Document uploaded: {document.id} by user {current_user.user_id}")

        return DocumentUploadResponse.from_orm(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        ) from e


@router.get("/", response_model=list[DocumentResponse])
async def get_user_documents(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    session_id: UUID | None = None,
    processed: bool | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """Get user's documents."""
    try:
        doc_service = DocumentService(db)

        documents = await doc_service.get_user_documents(
            user_id=current_user.user_id,
            tenant_id=current_user.tenant_id,
            session_id=session_id,
            processed=processed,
            limit=limit,
            offset=offset,
        )

        return [DocumentResponse.from_orm(doc) for doc in documents]

    except Exception as e:
        logger.error(f"Error getting user documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get documents",
        ) from e


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document."""
    try:
        doc_service = DocumentService(db)

        document = await doc_service.get_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        return DocumentResponse.from_orm(document)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document",
        ) from e


@router.post("/{document_id}/process")
async def process_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process a document for RAG (extract and chunk text)."""
    try:
        doc_service = DocumentService(db)

        # Check if document exists and belongs to user
        document = await doc_service.get_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        if document.processed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document already processed",
            )

        # Process document asynchronously
        success = await doc_service.process_document(document_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process document",
            )

        logger.info(f"Document processing started: {document_id}")

        return {"message": "Document processing started", "document_id": document_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process document",
        ) from e


@router.delete("/{document_id}")
async def delete_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a document."""
    try:
        doc_service = DocumentService(db)

        success = await doc_service.delete_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        logger.info(f"Document deleted: {document_id}")

        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        ) from e


@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0,
):
    """Get chunks for a processed document."""
    try:
        doc_service = DocumentService(db)

        # Check if document exists and belongs to user
        document = await doc_service.get_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        chunks = await doc_service.get_document_chunks(
            document_id=document_id, limit=limit, offset=offset
        )

        return {
            "status": "success",
            "data": {
                "document_id": document_id,
                "chunks": [
                    {
                        "id": str(chunk.id),
                        "content": chunk.content,
                        "chunk_index": chunk.chunk_index,
                        "metadata": chunk.metadata,
                        "token_count": chunk.token_count,
                    }
                    for chunk in chunks
                ],
                "total": len(chunks),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document chunks",
        ) from e


@router.get("/{document_id}/download")
async def download_document(
    document_id: UUID,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Download a document."""
    try:
        from fastapi.responses import FileResponse

        doc_service = DocumentService(db)

        # Check if document exists and belongs to user
        document = await doc_service.get_document(
            document_id=document_id, user_id=current_user.user_id
        )

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        # Check if file exists
        file_path = Path(document.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document file not found on disk",
            )

        return FileResponse(
            path=str(file_path),
            filename=document.filename,
            media_type=document.content_type,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document",
        ) from e
