"""Эндпоинт отправки приглашения (stateless)."""
import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from auth_deps import get_current_user_id
from config import settings
from schemas import InviteCreate, InviteResponse, InviteStatusEnum

router = APIRouter(prefix="", tags=["Invites"])


def _ensure_inviter_is_idea_owner(idea_payload: dict, user_id: int) -> None:
    owner = idea_payload.get("owner_id")
    if owner is not None and owner != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Приглашать кандидатов может только владелец идеи",
        )


async def _fetch_idea_payload(idea_id: int) -> dict:
    url = f"{settings.ideas_url.rstrip('/')}/ideas/{idea_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Idea Service недоступен: {exc}",
            ) from exc
    if resp.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Идея не найдена",
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка Idea Service: {resp.status_code}",
        )
    return resp.json()


async def _ensure_user_exists(user_id: int) -> None:
    url = f"{settings.auth_url.rstrip('/')}/profiles/{user_id}"
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Auth Service недоступен: {exc}",
            ) from exc
    if resp.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Ошибка Auth Service: {resp.status_code}",
        )


@router.post(
    "/invite",
    response_model=InviteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Отправить приглашение кандидату",
    description=(
        "Stateless-приглашение: проверяет идею в Idea Service и пользователя в Auth Service, "
        "состояние не хранится. candidate_id — это user_id из Auth."
    ),
)
async def create_invite(
    body: InviteCreate,
    user_id: int = Depends(get_current_user_id),
):
    idea_payload = await _fetch_idea_payload(body.idea_id)
    _ensure_inviter_is_idea_owner(idea_payload, user_id)
    await _ensure_user_exists(body.candidate_id)

    return InviteResponse(
        id=0,
        idea_id=body.idea_id,
        candidate_id=body.candidate_id,
        status=InviteStatusEnum.PENDING,
    )
