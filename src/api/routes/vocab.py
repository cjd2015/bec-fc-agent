from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_vocab():
    return {"code": 0, "message": "success", "data": {"todo": "list_vocab"}}


@router.get("/{vocab_id}")
def get_vocab_detail(vocab_id: int):
    return {"code": 0, "message": "success", "data": {"vocab_id": vocab_id}}


@router.post("/{vocab_id}/progress")
def update_vocab_progress(vocab_id: int):
    return {"code": 0, "message": "success", "data": {"vocab_id": vocab_id, "todo": "update_progress"}}
