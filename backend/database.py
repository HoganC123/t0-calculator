"""
Supabase REST API 封装（用 httpx，不依赖 supabase Python 库）

分两大块：
  - Auth：注册 / 登录 / 退出 / 获取当前用户
  - Trade：增删查，全部带 user_id 过滤
"""
from __future__ import annotations

import os

for _k in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(_k, None)

import httpx
from dotenv import load_dotenv

load_dotenv()

_URL     = os.getenv("SUPABASE_URL", "").rstrip("/")
_KEY     = os.getenv("SUPABASE_KEY", "")
_TABLE   = f"{_URL}/rest/v1/trade_records"
_JOURNAL = f"{_URL}/rest/v1/trade_journal"
_AUTH    = f"{_URL}/auth/v1"

# ── 启动时诊断日志 ────────────────────────────────────────────────────────────
print(f"[DEBUG] SUPABASE_URL  前20字符: {_URL[:20]!r}")
print(f"[DEBUG] SUPABASE_KEY  前10字符: {_KEY[:10]!r}  (长度={len(_KEY)})")
print(f"[DEBUG] SUPABASE_KEY  格式: {'sb_secret_/sb_publishable_ (新格式，可能不兼容)' if _KEY.startswith('sb_') else 'eyJ... (旧格式JWT)' if _KEY.startswith('eyJ') else '未知格式或未设置'}")


# ── 公共 Header 构造 ───────────────────────────────────────────────────────────

def _headers(prefer: str = "") -> dict:
    """使用 Service Role Key 访问 PostgREST（绕过 RLS，由应用层做 user_id 过滤）"""
    h = {
        "apikey":        _KEY,
        "Authorization": f"Bearer {_KEY}",
        "Content-Type":  "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _auth_headers(token: str) -> dict:
    """使用用户 JWT 访问 Supabase Auth API"""
    return {
        "apikey":        _KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type":  "application/json",
    }


def _user_headers(user_token: str, prefer: str = "") -> dict:
    """使用用户 JWT 访问 PostgREST（让 RLS 生效）"""
    h = {
        "apikey":        _KEY,
        "Authorization": f"Bearer {user_token}",
        "Content-Type":  "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


# ══════════════════════════════════════════════════════════════════════════════
# Auth 函数
# ══════════════════════════════════════════════════════════════════════════════

async def auth_sign_up(email: str, password: str) -> dict:
    """
    POST /auth/v1/signup
    返回 Supabase 用户对象（含 id、email、created_at）
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_AUTH}/signup",
            json={"email": email, "password": password},
            headers={"apikey": _KEY, "Content-Type": "application/json"},
            timeout=10,
        )
    _raise(resp)
    return resp.json()


async def auth_sign_in(email: str, password: str) -> dict:
    """
    POST /auth/v1/token?grant_type=password
    返回 {access_token, token_type, expires_in, refresh_token, user}
    """
    url = f"{_AUTH}/token?grant_type=password"
    print(f"[DEBUG] auth_sign_in: POST {url}")
    print(f"[DEBUG] auth_sign_in: apikey前10字符={_KEY[:10]!r}")
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            url,
            json={"email": email, "password": password},
            headers={"apikey": _KEY, "Content-Type": "application/json"},
            timeout=10,
        )
    print(f"[DEBUG] Supabase response status: {resp.status_code}")
    print(f"[DEBUG] Supabase response body: {resp.text}")
    _raise(resp)
    return resp.json()


async def auth_refresh(refresh_token: str) -> dict:
    """
    POST /auth/v1/token?grant_type=refresh_token
    返回新的 {access_token, refresh_token, expires_in, ...}
    """
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_AUTH}/token?grant_type=refresh_token",
            json={"refresh_token": refresh_token},
            headers={"apikey": _KEY, "Content-Type": "application/json"},
            timeout=10,
        )
    _raise(resp)
    return resp.json()


async def auth_sign_out(token: str) -> None:
    """POST /auth/v1/logout — 使该 token 失效"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{_AUTH}/logout",
            headers=_auth_headers(token),
            timeout=10,
        )
    # Supabase 退出登录返回 204，不需要 body
    if resp.status_code not in (200, 204):
        _raise(resp)


async def auth_get_user(token: str) -> dict:
    """
    GET /auth/v1/user — 验证 token 并返回用户信息
    token 无效时 Supabase 返回 401，由调用方处理
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{_AUTH}/user",
            headers=_auth_headers(token),
            timeout=10,
        )
    _raise(resp)
    return resp.json()


# ══════════════════════════════════════════════════════════════════════════════
# Trade 函数（全部带 user_id）
# ══════════════════════════════════════════════════════════════════════════════

async def save_trade(data: dict, user_id: str) -> dict:
    """
    POST /rest/v1/trade_records
    自动注入 user_id，返回插入后的完整记录
    """
    payload = {**data, "user_id": user_id}
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _TABLE,
            json=payload,
            headers=_headers("return=representation"),
            timeout=10,
        )
    _raise(resp)
    result = resp.json()
    return result[0] if isinstance(result, list) and result else result


async def list_trades(user_id: str) -> list[dict]:
    """
    GET /rest/v1/trade_records?user_id=eq.<user_id>&order=created_at.desc
    只返回当前用户自己的记录
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _TABLE,
            params={
                "user_id": f"eq.{user_id}",
                "order":   "created_at.desc",
                "limit":   "1000",
            },
            headers=_headers(),
            timeout=10,
        )
    _raise(resp)
    return resp.json()


async def delete_trade(record_id: str, user_id: str) -> None:
    """
    DELETE /rest/v1/trade_records?id=eq.<id>&user_id=eq.<user_id>
    双重过滤：防止越权删除他人记录
    """
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            _TABLE,
            params={"id": f"eq.{record_id}", "user_id": f"eq.{user_id}"},
            headers=_headers(),
            timeout=10,
        )
    _raise(resp)


async def clear_trades(user_id: str) -> int:
    """
    DELETE /rest/v1/trade_records?user_id=eq.<user_id>
    只清空当前用户的记录，返回删除条数
    """
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            _TABLE,
            params={"user_id": f"eq.{user_id}"},
            headers=_headers("return=representation"),
            timeout=10,
        )
    _raise(resp)
    if resp.status_code == 204:
        return 0
    deleted = resp.json()
    return len(deleted) if isinstance(deleted, list) else 0


# ══════════════════════════════════════════════════════════════════════════════
# Journal 函数（使用用户 JWT，RLS 自动过滤）
# ══════════════════════════════════════════════════════════════════════════════

async def save_journal(data: dict, user_token: str) -> dict:
    """POST /rest/v1/trade_journal — 插入一条日志"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            _JOURNAL,
            json=data,
            headers=_user_headers(user_token, "return=representation"),
            timeout=10,
        )
    _raise(resp)
    result = resp.json()
    return result[0] if isinstance(result, list) and result else result


async def list_journal(user_token: str) -> list[dict]:
    """GET /rest/v1/trade_journal — 按日期倒序返回当前用户所有日志"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            _JOURNAL,
            params={"order": "trade_date.desc,created_at.desc", "limit": "1000"},
            headers=_user_headers(user_token),
            timeout=10,
        )
    _raise(resp)
    return resp.json()


async def delete_journal(record_id: str, user_token: str) -> None:
    """DELETE /rest/v1/trade_journal?id=eq.<id> — RLS 保证只能删自己的记录"""
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            _JOURNAL,
            params={"id": f"eq.{record_id}"},
            headers=_user_headers(user_token),
            timeout=10,
        )
    _raise(resp)


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
