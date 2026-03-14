import os
import uuid
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models.photo import Photo


async def save_photo(
    file: UploadFile,
    project_id: uuid.UUID,
    photo_type: str,
    user_id: uuid.UUID,
    db: Session,
) -> Photo:
    """Save uploaded photo to disk and create DB record."""
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    photo = Photo(
        project_id=project_id,
        uploaded_by=user_id,
        filename=filename,
        file_path=file_path,
        photo_type=photo_type,
        status="pending",
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo
