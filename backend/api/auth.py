
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from models.user import User
from schemas.auth import UserCreate, UserResponse
from core.security import hash_password
from schemas.auth import UserLogin, TokenResponse
from core.security import verify_password, create_access_token
from core.dependencies import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(user_data: UserCreate, db: Session = Depends(get_db)):

    # Check whether the email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Prepare user data
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed_password,
        gender=user_data.gender,
        date_of_birth=user_data.date_of_birth
    )

    # Save user in MySQL
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return new_user

@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):

    # Find user by email
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    # Check whether user exists and password is correct
    if not user or not verify_password(
        user_data.password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Check whether account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate JWT access token
    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
