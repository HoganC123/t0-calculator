from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from database import delete_journal, list_journal, save_journal
from deps import require_auth

router = APIRouter(prefix="/journal", tags=["journal"])


# ── 请求体 ────────────────────────────────────────────────────────────────────

class JournalIn(BaseModel):
    stock_code:  str           = Field("",      description="股票代码")
    stock_name:  str           = Field("",      description="股票名称")
    action_type: str           = Field(...,     description="买入/卖出/加仓/减仓")
    price:       float         = Field(...,     description="成交价格（元）")
    quantity:    int           = Field(...,     description="成交数量（股）")
    trade_date:  str           = Field(...,     description="成交日期 YYYY-MM-DD")
    reason:      str           = Field(...,     description="交易理由（必填）")
    emotion:     str           = Field("冷静",  description="情绪标签")
    notes:       Optional[str] = Field("",      description="备注")


# ── 接口 ──────────────────────────────────────────────────────────────────────

@router.post("/save", status_code=201)
async def api_save(
    body: JournalIn,
    user: dict = Depends(require_auth),
) -> Any:
    """保存一条交易日志，user_id 由 token 自动注入"""
    data = body.model_dump()
    data["user_id"] = user["id"]
    try:
        return await save_journal(data, user_token=user["_token"])
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def api_list(
    user: dict = Depends(require_auth),
) -> Any:
    """获取当前用户所有日志，按 trade_date 倒序"""
    try:
        return await list_journal(user_token=user["_token"])
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{record_id}")
async def api_delete(
    record_id: str,
    user: dict = Depends(require_auth),
) -> Any:
    """删除指定日志（RLS 保证只能删除自己的记录）"""
    try:
        await delete_journal(record_id, user_token=user["_token"])
        return {"deleted": record_id, "message": "日志已删除"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
