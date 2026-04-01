from fastapi import APIRouter

router = APIRouter()


@router.get("")
def list_scenes():
    return {"code": 0, "message": "success", "data": {"todo": "list_scenes"}}


@router.get("/{scene_id}")
def get_scene_detail(scene_id: int):
    return {"code": 0, "message": "success", "data": {"scene_id": scene_id}}


@router.post("/{scene_id}/start")
def start_scene(scene_id: int):
    return {"code": 0, "message": "success", "data": {"scene_id": scene_id, "todo": "start_scene"}}


@router.post("/{scene_id}/message")
def send_scene_message(scene_id: int):
    return {"code": 0, "message": "success", "data": {"scene_id": scene_id, "todo": "send_message"}}


@router.post("/{scene_id}/finish")
def finish_scene(scene_id: int):
    return {"code": 0, "message": "success", "data": {"scene_id": scene_id, "todo": "finish_scene"}}
