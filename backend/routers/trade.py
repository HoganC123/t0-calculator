from __future__ import annotations

from typing import Any, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from database import clear_trades, list_trades, save_trade

router = APIRouter(prefix="/trade", tags=["trade"])


# ── 数据模型 ──────────────────────────────────────────────────────────────────

class TradeIn(BaseModel):
    """保存交易记录时的请求体"""
    trade_type:   str           = Field(...,    description="操作类型，如：正T / 反T")
    stock_name:   str           = Field("未填写", description="股票名称")
    buy_price:    float         = Field(0.0,    description="买入价（元）")
    sell_price:   float         = Field(0.0,    description="卖出价（元）")
    quantity:     int           = Field(0,      description="数量（股）")
    gross_profit: float         = Field(0.0,    description="毛利润（元）")
    total_fee:    float         = Field(0.0,    description="合计手续费（元）")
    net_profit:   float         = Field(0.0,    description="税后实际盈利（元）")
    new_avg_cost: float         = Field(0.0,    description="操作后新均价（元）")
    notes:        Optional[str] = Field("",     description="备注")


# ── 接口 ──────────────────────────────────────────────────────────────────────

@router.post("/save", status_code=201)
async def api_save(body: TradeIn) -> Any:
    """保存一条交易记录到 Supabase"""
    try:
        return await save_trade(body.model_dump())
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def api_list() -> Any:
    """获取所有记录，按时间倒序"""
    try:
        return await list_trades()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def api_clear() -> Any:
    """清空所有记录"""
    try:
        count = await clear_trades()
        return {"deleted": count, "message": "记录已清空"}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
