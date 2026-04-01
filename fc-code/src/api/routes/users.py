from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.models.user import User, UserProfile
from src.schemas.user import UserProfileUpdate

router = APIRouter()


@router.get("/profile")
def get_profile(username: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    return {
        "code": 0,
        "message": "success",
        "data": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "status": user.status,
            "profile": {
                "target_level": getattr(profile, "target_level", None),
                "current_level": getattr(profile, "current_level", None),
                "industry_background": getattr(profile, "industry_background", None),
                "learning_goal": getattr(profile, "learning_goal", None),
                "learning_preference": getattr(profile, "learning_preference", None),
            },
        },
    }


@router.put("/profile")
def update_profile(
    payload: UserProfileUpdate,
    username: str = Query(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()

    updates = payload.model_dump(exclude_none=True) if payload else {}
    for field, value in updates.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return {
        "code": 0,
        "message": "success",
        "data": {
            "username": user.username,
            "profile": {
                "target_level": profile.target_level,
                "current_level": profile.current_level,
                "industry_background": profile.industry_background,
                "learning_goal": profile.learning_goal,
                "learning_preference": profile.learning_preference,
            },
        },
    }
