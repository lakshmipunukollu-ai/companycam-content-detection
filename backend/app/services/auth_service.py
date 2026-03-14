from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.auth.jwt_handler import hash_password, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin


def register_user(db: Session, data: UserRegister) -> dict:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=data.role or "contractor",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(str(user.id), user.role)
    return {"access_token": token, "token_type": "bearer", "user": user}


def login_user(db: Session, data: UserLogin) -> dict:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(str(user.id), user.role)
    return {"access_token": token, "token_type": "bearer", "user": user}
