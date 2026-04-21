from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Optional

import httpx
import pandas as pd
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


@router.get("/stocks")
async def api_stocks() -> Any:
    """返回A股全部股票代码和名称（公开数据，无需登录）"""
    import akshare as ak
    try:
        df = await asyncio.wait_for(
            asyncio.to_thread(ak.stock_info_a_code_name),
            timeout=60,
        )
        codes = df.iloc[:, 0].astype(str).str.strip().tolist()
        names = df.iloc[:, 1].astype(str).str.strip().tolist()
        return {"stocks": [{"code": c, "name": n} for c, n in zip(codes, names)], "error": ""}
    except Exception as e:
        return {"stocks": [], "error": f"股票列表暂时无法加载：{e}"}


@router.get("/lhb/{stock_code}")
async def api_lhb(
    stock_code: str,
    user: dict = Depends(require_auth),
) -> Any:
    """查询该股票近30天龙虎榜记录（最多5条）"""
    import akshare as ak
    end_date   = datetime.today().strftime("%Y%m%d")
    start_date = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d")
    try:
        df = await asyncio.to_thread(
            ak.stock_lhb_detail_em, start_date=start_date, end_date=end_date
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AKShare 请求失败：{e}")

    if df is None or df.empty:
        return []

    filtered = df[df.iloc[:, 1].astype(str).str.strip() == str(stock_code).strip()]
    if filtered.empty:
        return []

    filtered = filtered.sort_values(by=filtered.columns[3], ascending=False).head(5)

    def _safe(val):
        try:
            return None if pd.isna(val) else float(val)
        except Exception:
            return None

    result = []
    for _, row in filtered.iterrows():
        result.append({
            "date":        str(row.iloc[3])[:10],
            "reason":      str(row.iloc[4]),
            "buy_amount":  _safe(row.iloc[8]),
            "sell_amount": _safe(row.iloc[9]),
            "net_buy":     _safe(row.iloc[7]),
        })
    return result


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
