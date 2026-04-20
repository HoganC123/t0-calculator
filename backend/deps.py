"""
FastAPI 依赖项

require_auth：从 Authorization: Bearer <token> 验证用户身份，
              返回 Supabase 用户对象 {"id": "...", "email": "...", ...}
              token 无效或缺失时自动返回 401。
"""
from __future__ import annotations

from typing import Optional

import httpx
from fastapi import Header, HTTPException

from database import auth_get_user


async def require_auth(
    authorization: Optional[str] = Header(None, alias="authorization"),
) -> dict:
    """
    用法：
        @router.get("/list")
        async def api_list(user: dict = Depends(require_auth)):
            user_id = user["id"]
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="请先登录（缺少 Authorization header）")

    token = authorization[7:]

    try:
        user = await auth_get_user(token)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"认证服务异常：{e}")

    if not user.get("id"):
        raise HTTPException(status_code=401, detail="无效的用户信息")

    # 注入原始 token，供需要 RLS 的接口（journal 等）使用
    user["_token"] = token
    return user
