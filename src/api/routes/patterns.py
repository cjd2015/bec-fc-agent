from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_patterns():
    return {"code": 0, "message": "success", "data": {"todo": "list_patterns"}}


@router.get("/{pattern_id}")
def get_pattern_detail(pattern_id: int):
    return {"code": 0, "message": "success", "data": {"pattern_id": pattern_id}}


@router.post("/{pattern_id}/progress")
def update_pattern_progress(pattern_id: int):
    return {"code": 0, "message": "success", "data": {"pattern_id": pattern_id, "todo": "update_progress"}}
