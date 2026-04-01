from fastapi import APIRouter

router = APIRouter()


@router.get("/pending")
def list_pending_review():
    return {"code": 0, "message": "success", "data": {"todo": "pending_review"}}


@router.post("/{content_id}")
def submit_review(content_id: int):
    return {"code": 0, "message": "success", "data": {"content_id": content_id, "todo": "submit_review"}}
