from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from database import auth_get_user, auth_refresh, auth_sign_in, auth_sign_out, auth_sign_up

router = APIRouter(prefix="/auth", tags=["auth"])


# ── 请求体 ────────────────────────────────────────────────────────────────────

class AuthIn(BaseModel):
    email:    str = ""
    password: str = ""


# ── 接口 ──────────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(body: AuthIn) -> Any:
    """
    邮箱 + 密码注册。
    Supabase 默认会发确认邮件；如果项目关闭了邮件确认，注册后可直接登录。
    """
    if not body.email or not body.password:
        raise HTTPException(status_code=422, detail="email 和 password 不能为空")
    try:
        return await auth_sign_up(body.email, body.password)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login")
async def login(body: AuthIn) -> Any:
    """
    邮箱 + 密码登录。
    成功返回 {access_token, token_type, expires_in, refresh_token, user}。
    前端保存 access_token，后续请求放入 Authorization: Bearer <token>。
    """
    if not body.email or not body.password:
        raise HTTPException(status_code=422, detail="email 和 password 不能为空")
    try:
        return await auth_sign_in(body.email, body.password)
    except httpx.HTTPStatusError as e:
        code = e.response.status_code
        # 400 通常是密码错误或用户不存在
        detail = "邮箱或密码错误" if code == 400 else str(e)
        raise HTTPException(status_code=code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RefreshIn(BaseModel):
    refresh_token: str = ""


@router.post("/refresh")
async def refresh(body: RefreshIn) -> Any:
    """用 refresh_token 换取新的 access_token。"""
    if not body.refresh_token:
        raise HTTPException(status_code=422, detail="refresh_token 不能为空")
    try:
        return await auth_refresh(body.refresh_token)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None, alias="authorization"),
) -> Any:
    """使当前 token 失效。需要在 Header 里带 Authorization: Bearer <token>。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization header")
    token = authorization[7:]
    try:
        await auth_sign_out(token)
        return {"message": "已退出登录"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me")
async def me(
    authorization: Optional[str] = Header(None, alias="authorization"),
) -> Any:
    """返回当前登录用户的信息（id、email、created_at 等）。"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="缺少 Authorization header")
    token = authorization[7:]
    try:
        return await auth_get_user(token)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
