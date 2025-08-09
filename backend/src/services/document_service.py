"""
Document processing service for file handling and text extraction.
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from models.chat import ChatDocument, DocumentChunk

logger = logging.getLogger(__name__)


class DocumentService:
    """Service for document management and processing."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_document(
        self,
        file: UploadFile,
        user_id: UUID,
        tenant_id: UUID,
        session_id: UUID | None = None,
    ) -> ChatDocument:
        """Upload and save a document."""
        try:
            # Create upload directory if it doesn't exist
            upload_dir = Path(settings.upload_path) / str(tenant_id) / str(user_id)
            upload_dir.mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            file_extension = (
                file.filename.split(".")[-1].lower() if "." in file.filename else ""
            )
            unique_filename = (
                f"{uuid4()}.{file_extension}" if file_extension else str(uuid4())
            )
            file_path = upload_dir / unique_filename

            # Save file to disk
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Get file size
            file_size = len(content)

            # Create database record
            document = ChatDocument(
                tenant_id=tenant_id,
                user_id=user_id,
                session_id=session_id,
                filename=file.filename,
                content_type=file.content_type or "application/octet-stream",
                file_size=file_size,
                file_path=str(file_path),
                processed=False,
            )

            self.db.add(document)
            await self.db.commit()
            await self.db.refresh(document)

            logger.info(f"Document uploaded: {document.id} - {file.filename}")

            return document

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error uploading document: {e}")
            # Clean up file if database save failed
            if "file_path" in locals() and file_path.exists():
                file_path.unlink()
            raise

    async def get_user_documents(
        self,
        user_id: UUID,
        tenant_id: UUID,
        session_id: UUID | None = None,
        processed: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ChatDocument]:
        """Get user's documents."""
        try:
            query = (
                select(ChatDocument)
                .where(
                    ChatDocument.user_id == user_id, ChatDocument.tenant_id == tenant_id
                )
                .order_by(ChatDocument.uploaded_at.desc())
                .limit(limit)
                .offset(offset)
            )

            if session_id:
                query = query.where(ChatDocument.session_id == session_id)

            if processed is not None:
                query = query.where(ChatDocument.processed == processed)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting user documents: {e}")
            return []

    async def get_document(
        self, document_id: UUID, user_id: UUID
    ) -> ChatDocument | None:
        """Get a specific document."""
        try:
            query = select(ChatDocument).where(
                ChatDocument.id == document_id, ChatDocument.user_id == user_id
            )

            result = await self.db.execute(query)
            return result.scalar_one_or_none()

        except Exception as e:
            logger.error(f"Error getting document: {e}")
            return None

    async def delete_document(self, document_id: UUID, user_id: UUID) -> bool:
        """Delete a document."""
        try:
            document = await self.get_document(document_id, user_id)
            if not document:
                return False

            # Delete file from disk
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()

            # Delete from database (this will cascade to chunks)
            await self.db.delete(document)
            await self.db.commit()

            logger.info(f"Document deleted: {document_id}")
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting document: {e}")
            return False

    async def process_document(self, document_id: UUID) -> bool:
        """Process a document for RAG (extract and chunk text)."""
        try:
            # Get document
            query = select(ChatDocument).where(ChatDocument.id == document_id)
            result = await self.db.execute(query)
            document = result.scalar_one_or_none()

            if not document:
                return False

            # Extract text from document
            text_content = await self._extract_text(
                document.file_path, document.content_type
            )
            if not text_content:
                return False

            # Chunk the text
            chunks = await self._chunk_text(text_content)

            # Save chunks to database
            chunk_objects = []
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    document_id=document_id,
                    content=chunk_text,
                    chunk_index=i,
                    metadata={
                        "page": None,
                        "section": None,
                    },  # TODO: Extract from document
                    token_count=await self._count_tokens(chunk_text),
                )
                chunk_objects.append(chunk)

            # Save all chunks
            self.db.add_all(chunk_objects)

            # Update document status
            document.processed = True
            document.processed_at = datetime.now()
            document.chunks_count = len(chunks)
            document.processing_metadata = {
                "chunks_created": len(chunks),
                "total_tokens": sum(
                    chunk.token_count for chunk in chunk_objects if chunk.token_count
                ),
                "processing_time": datetime.now().isoformat(),
            }

            await self.db.commit()

            logger.info(
                f"Document processed: {document_id} - {len(chunks)} chunks created"
            )
            return True

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error processing document: {e}")
            return False

    async def get_document_chunks(
        self, document_id: UUID, limit: int = 50, offset: int = 0
    ) -> list[DocumentChunk]:
        """Get chunks for a document."""
        try:
            query = (
                select(DocumentChunk)
                .where(DocumentChunk.document_id == document_id)
                .order_by(DocumentChunk.chunk_index)
                .limit(limit)
                .offset(offset)
            )

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting document chunks: {e}")
            return []

    async def search_documents(
        self, query: str, user_id: UUID, tenant_id: UUID, limit: int = 10
    ) -> list[DocumentChunk]:
        """Search document chunks (basic text search for now)."""
        try:
            # Basic text search - in production, use vector search
            search_query = (
                select(DocumentChunk)
                .join(ChatDocument, DocumentChunk.document_id == ChatDocument.id)
                .where(
                    ChatDocument.user_id == user_id,
                    ChatDocument.tenant_id == tenant_id,
                    ChatDocument.processed,
                    DocumentChunk.content.ilike(f"%{query}%"),
                )
                .order_by(DocumentChunk.chunk_index)
                .limit(limit)
            )

            result = await self.db.execute(search_query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []

    async def _extract_text(self, file_path: str, content_type: str) -> str | None:
        """Extract text from different file types."""
        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                return None

            # Handle different file types
            if content_type == "text/plain" or file_path.endswith(".txt"):
                return await self._extract_from_txt(file_path)
            elif content_type == "application/pdf" or file_path.endswith(".pdf"):
                return await self._extract_from_pdf(file_path)
            elif content_type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ] or file_path.endswith(".docx"):
                return await self._extract_from_docx(file_path)
            elif content_type == "text/markdown" or file_path.endswith(".md"):
                return await self._extract_from_txt(file_path)  # Markdown is text
            else:
                # Try to read as text for unknown types
                try:
                    return await self._extract_from_txt(file_path)
                except Exception:
                    logger.warning(f"Unsupported file type: {content_type}")
                    return None

        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return None

    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from plain text file."""
        async with aiofiles.open(file_path, encoding="utf-8", errors="ignore") as f:
            return await f.read()

    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            import pypdf

            text = ""
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()

            # Run PDF processing in thread pool
            def process_pdf():
                try:
                    from io import BytesIO

                    pdf_reader = pypdf.PdfReader(BytesIO(content))
                    text_parts = []
                    for page in pdf_reader.pages:
                        text_parts.append(page.extract_text())
                    return "\n\n".join(text_parts)
                except Exception as e:
                    logger.error(f"Error processing PDF: {e}")
                    return ""

            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, process_pdf)
            return text

        except Exception as e:
            logger.error(f"Error extracting from PDF: {e}")
            return ""

    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            import python_docx

            def process_docx():
                try:
                    doc = python_docx.Document(file_path)
                    text_parts = []
                    for paragraph in doc.paragraphs:
                        text_parts.append(paragraph.text)
                    return "\n".join(text_parts)
                except Exception as e:
                    logger.error(f"Error processing DOCX: {e}")
                    return ""

            loop = asyncio.get_event_loop()
            text = await loop.run_in_executor(None, process_docx)
            return text

        except Exception as e:
            logger.error(f"Error extracting from DOCX: {e}")
            return ""

    async def _chunk_text(self, text: str) -> list[str]:
        """Chunk text into smaller pieces."""
        try:
            # Simple chunking by character count with overlap
            chunk_size = settings.chunk_size
            overlap = settings.chunk_overlap

            if len(text) <= chunk_size:
                return [text]

            chunks = []
            start = 0

            while start < len(text):
                end = start + chunk_size

                # Try to end at a sentence or paragraph boundary
                if end < len(text):
                    # Look for sentence end
                    sentence_end = text.rfind(".", start, end)
                    if sentence_end > start + chunk_size // 2:
                        end = sentence_end + 1
                    else:
                        # Look for word boundary
                        word_boundary = text.rfind(" ", start, end)
                        if word_boundary > start + chunk_size // 2:
                            end = word_boundary

                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)

                # Move start position with overlap
                start = max(start + chunk_size - overlap, end)

                if start >= len(text):
                    break

            return chunks

        except Exception as e:
            logger.error(f"Error chunking text: {e}")
            return [text]  # Return original text as single chunk

    async def _count_tokens(self, text: str) -> int:
        """Count tokens in text (approximate)."""
        try:
            # Simple approximation: ~4 characters per token
            return len(text) // 4
        except Exception:
            return 0
