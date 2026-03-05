"""Эндпоинт отправки приглашения (stateless)."""
from fastapi import APIRouter, HTTPException, status

import httpx

from config import settings
from schemas import InviteCreate, InviteResponse, InviteStatusEnum

router = APIRouter(prefix="", tags=["Invites"])


async def _ensure_idea_exists(idea_id: int) -> None:
    """Проверить, что идея существует в Idea Service."""
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


async def _ensure_user_exists(user_id: int) -> None:
    """Проверить, что пользователь существует в Auth Service (по профилю)."""
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
            detail="Кандидат не найден",
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
        "Stateless-приглашение: проверяет существование идеи и пользователя в других сервисах, "
        "но не хранит своё состояние."
    ),
)
async def create_invite(
    body: InviteCreate,
):
    """Проверить идею и кандидата и вернуть виртуальное приглашение."""
    await _ensure_idea_exists(body.idea_id)
    # Внутренне candidate_id == user_id профиля
    await _ensure_user_exists(body.candidate_id)

    return InviteResponse(
        id=0,  # виртуальный id, т.к. сервис stateless
        idea_id=body.idea_id,
        candidate_id=body.candidate_id,
        status=InviteStatusEnum.PENDING,
    )

