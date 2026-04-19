"""
Supabase REST API 封装（用 httpx，不依赖 supabase Python 库）
"""
from __future__ import annotations

import os

import httpx
from dotenv import load_dotenv

load_dotenv()

_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
_KEY = os.getenv("SUPABASE_KEY", "")
_TABLE = f"{_URL}/rest/v1/trade_records"


def _headers(prefer: str = "") -> dict:
    h = {
        "apikey":        _KEY,
        "Authorization": f"Bearer {_KEY}",
        "Content-Type":  "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


# ── 三个核心函数 ───────────────────────────────────────────────────────────────

async def save_trade(data: dict) -> dict:
    """
    POST /rest/v1/trade_records
    返回 Supabase 插入后的完整记录（含 id、created_at）
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _TABLE,
            json=data,
            headers=_headers("return=representation"),
            timeout=10,
        )
    _raise(resp)
    result = resp.json()
    # Supabase 即使单条插入也返回数组
    return result[0] if isinstance(result, list) and result else result


async def list_trades() -> list[dict]:
    """
    GET /rest/v1/trade_records?order=created_at.desc
    返回所有记录，按时间倒序
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _TABLE,
            params={"order": "created_at.desc", "limit": "1000"},
            headers=_headers(),
            timeout=10,
        )
    _raise(resp)
    return resp.json()


async def clear_trades() -> int:
    """
    DELETE /rest/v1/trade_records?id=not.is.null
    删除所有记录，返回删除条数
    """
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            _TABLE,
            params={"id": "not.is.null"},
            headers=_headers("return=representation"),
            timeout=10,
        )
    _raise(resp)
    # 204 No Content 时 body 为空
    if resp.status_code == 204:
        return 0
    deleted = resp.json()
    return len(deleted) if isinstance(deleted, list) else 0


# ── 内部工具 ──────────────────────────────────────────────────────────────────

def _raise(resp: httpx.Response) -> None:
    """统一错误处理：把 Supabase 错误信息透传给调用方"""
    if resp.is_error:
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise httpx.HTTPStatusError(
            message=str(detail),
            request=resp.request,
            response=resp,
        )
