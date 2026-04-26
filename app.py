import os
for _k in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'all_proxy']:
    os.environ.pop(_k, None)

import streamlit as st
import requests as _req
from datetime import date
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="筹码本", layout="wide")

# ── PWA meta 标签（base64 内嵌图标，兼容 Streamlit Cloud）─────────────────────
_ICON_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAYAAABS3GwHAAADd0lEQVR4nO3dT2oTUQDA4al0"
    "HVzrpkvRC4hLr9AjuBI8TsGVR/AKLsULKF12Y9fiBSot9o8hbUNtkpn5fR8EEpJFCu+XmXnv"
    "Jd1bLBZnA0Q92fUbgF0SAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECa"
    "AEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmA"
    "NAGQJgDSBECaAEgTAGkCIE0ApO35P8G7dTkzcvL20zB1Bw+c5dnl3+4IQJoASBMAaQIIOn71"
    "+uKGAIhzBCBNAKQJgLT9Xb+BgnUWiFa95n8WiNa5yD1e8ZoX378NJY4ApAmANAGQJgDSBEDa"
    "KGeB5rRFuOzrj1//PH7z8ukwNqMMgOk4PTq8fjCBAb9MAKw/wFd49uHz1f0x/uzJfQSwtChU"
    "WwgKt3j/fLh0OhzeOsDnSADBQb7s98efV/drHwACiJyu3BzkXBPATM/HfeFlPQIY89ThUet8"
    "PBfAfbMGtz2/yV2Stz3/2OfGy3Pkq6YOrYNsniPAlkxhUahIAFtaIDLgx0kAG7o4nfoCUYUA"
    "HmHAuzidLgGsuYh0c4XUgJ8PAayxanq+iFRbIa3IB7Bqi8AcVk3vCnZT+55O7pieHusW9/36"
    "xeocBjsPt1+bmbFFgFkGYGaGTAD3zbvDbAJYtWfGYJ+ek5Fd/I46gJuD3haCx2dKd+QBGPSk"
    "A9jFp98mvxM8xfnxCj+MRZoASBMAablrgLFx7r9bjgCkCYA0p0B/WRxqcgQgTQCkCYC0vcVi"
    "cTaMjO0BbIsjAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkC"
    "IE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDS"
    "BECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0A"
    "pAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECaAEgTAGkCIE0ApAmANAGQJgDSBECa"
    "AEgTAGkCIE0ApAmANAEwlP0B5A+Y8bkkQTMAAAAASUVORK5CYII="
)
st.markdown(f"""
<link rel="apple-touch-icon" href="data:image/png;base64,{_ICON_B64}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="筹码本">
<meta name="theme-color" content="#e63946">
""", unsafe_allow_html=True)

# ── 样式（金融科技极简风 v2）─────────────────────────────────────────────────
st.markdown("""
<style>
/* ── 全局基础 ── */
html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                 "Helvetica Neue", Arial, sans-serif;
    letter-spacing: 0.01em;
}
h1,h2,h3 { font-weight: 300 !important; letter-spacing: -0.02em; }

/* ── 全局背景 ── */
.stApp { background: #0a0a0a; }
[data-testid="stSidebar"] > div:first-child { background: #0d0d0d; }

/* ── 顶部工具栏隐藏多余元素 ── */
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; border-bottom: 1px solid #1a1a1a; }

/* ── 指标颜色（A股：涨红跌绿）── */
[data-testid="stMetricDelta"] > div[style*="color: rgb(9, 171, 59)"],
[data-testid="stMetricDelta"] > div[style*="color: rgb(14, 203, 129)"] { color:#ff3b30 !important; }
[data-testid="stMetricDelta"] > div[style*="color: rgb(255, 43, 43)"],
[data-testid="stMetricDelta"] > div[style*="color: rgb(255, 75, 75)"]  { color:#2ecc71 !important; }
[data-testid="stMetricValue"] { font-weight: 300 !important; font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { color: #666 !important; font-size: 0.78rem !important; }

/* ── 输入框 ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {
    background: transparent !important;
    border: none !important;
    border-bottom: 1px solid #333 !important;
    border-radius: 0 !important;
    color: #f0f0f0 !important;
    padding: 8px 2px !important;
    font-size: 0.95rem !important;
    transition: border-color 0.2s;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {
    border-bottom-color: #ff3b30 !important;
    box-shadow: none !important;
    outline: none !important;
}

/* ── 按钮 ── */
[data-testid="stButton"] > button {
    border-radius: 4px !important;
    font-weight: 400 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    transition: opacity 0.15s !important;
}
[data-testid="stButton"] > button[kind="primary"] {
    background: #ff3b30 !important;
    border: none !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

/* ── Tab ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid #1e1e1e !important;
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    color: #666 !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #f0f0f0 !important;
    border-bottom-color: #ff3b30 !important;
    background: transparent !important;
}

/* ── 卡片组件 ── */
.pnl-card  {
    background: #141414;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 8px;
}
.pnl-label { font-size: 0.78rem; color: #666; margin: 0 0 6px 0; letter-spacing: 0.04em; text-transform: uppercase; }
.pnl-value { font-size: 1.5rem; font-weight: 300; margin: 0; }
.pnl-red   { color: #ff3b30; }
.pnl-green { color: #2ecc71; }
.pnl-gray  { color: #888; }

.be-box     { border: 1px solid #ff3b30; border-radius: 8px; padding: 16px 20px; margin: 12px 0; background: rgba(255,59,48,0.04); }
.be-box-buy { border: 1px solid #2ecc71; border-radius: 8px; padding: 16px 20px; margin: 12px 0; background: rgba(46,204,113,0.04); }
.be-title       { font-size: 0.75rem; color: #666; margin: 0 0 6px 0; letter-spacing: 0.05em; text-transform: uppercase; }
.be-price-red   { font-size: 1.9rem; font-weight: 300; color: #ff3b30; margin: 0; }
.be-price-green { font-size: 1.9rem; font-weight: 300; color: #2ecc71; margin: 0; }
.be-note        { font-size: 0.78rem; color: #555; margin: 6px 0 0 0; }

.save-bar { background: #141414; border: 1px solid #222; border-radius: 8px; padding: 16px 20px; margin-top: 16px; }
.pct-hint { font-size: 0.78rem; color: #666; margin: -4px 0 8px 0; }

/* ── 侧边栏底部固定用户信息 ── */
[data-testid="stSidebarContent"] {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}
.sidebar-scroll { flex: 1 1 auto; overflow-y: auto; padding-bottom: 0.5rem; }
.sidebar-bottom {
    border-top: 1px solid #1e1e1e;
    padding: 14px 0 6px 0;
    background: #0d0d0d;
}

/* ── select / slider ── */
[data-testid="stSelectbox"] > div > div {
    background: #141414 !important;
    border: 1px solid #222 !important;
    border-radius: 4px !important;
}

/* ── 数据表格 ── */
[data-testid="stDataFrame"] { border: 1px solid #1e1e1e; border-radius: 8px; overflow: hidden; }

/* ── 分割线 ── */
hr { border-color: #1e1e1e !important; }

/* ── 登录页居中卡片 ── */
.auth-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 8px;
    padding: 40px 36px;
    margin-top: 24px;
}
.auth-logo {
    font-size: 1.4rem;
    font-weight: 300;
    color: #f0f0f0;
    margin-bottom: 4px;
}
.auth-sub {
    font-size: 0.82rem;
    color: #555;
    margin-bottom: 32px;
}

/* ── 响应式 ── */
@media (max-width:640px) {
    [data-testid="column"] { min-width:100% !important; flex:1 1 100% !important; }
    .stTabs [data-baseweb="tab"] { font-size:12px !important; padding:8px 12px !important; }
    [data-testid="stMetricValue"] { font-size:1.2rem !important; }
    .pnl-value { font-size:1.2rem !important; }
    .be-price-red, .be-price-green { font-size:1.4rem !important; }
    h1 { font-size:1.3rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<h1 style="margin-bottom:0;font-weight:300;letter-spacing:-0.03em">筹码本</h1>'
    '<p style="color:#555;font-size:0.85rem;margin-top:4px;letter-spacing:0.02em">A 股散户决策工具</p>',
    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# 后端 API 调用
# ══════════════════════════════════════════════════════════════════════════════
_API     = st.secrets.get("BACKEND_URL", "https://t0-calculator-production.up.railway.app")
_TIMEOUT = 8   # 秒


def _warmup_backend() -> None:
    """
    页面加载时同步检测后端是否就绪：
    1. 先做一次快速探测（3 秒超时）
    2. 若失败，显示 spinner，每 5 秒重试，最多 6 次（共等 ≤30 秒）
    3. 成功后调用 st.rerun()，自动刷新页面数据；6 次全失败则静默放行
    同一 session 只执行一次，后续 rerun 直接跳过。
    """
    import time
    import requests as _r

    if st.session_state.get("_backend_ready"):
        return  # 本次 session 已确认就绪，跳过

    # ── 快速探测（不显示 UI，后端已热时用户无感知）─────────────────────────────
    try:
        resp = _r.get(f"{_API}/health", timeout=3)
        if resp.status_code == 200:
            st.session_state["_backend_ready"] = True
            return
    except Exception:
        pass

    # ── 后端未就绪：显示等待提示，每 5 秒重试一次，最多 6 次 ─────────────────
    with st.spinner("服务启动中，预计等待 10–30 秒，请稍候…"):
        for attempt in range(6):
            time.sleep(5)
            try:
                resp = _r.get(f"{_API}/health", timeout=5)
                if resp.status_code == 200:
                    st.session_state["_backend_ready"] = True
                    st.rerun()   # 成功后自动刷新，用户看到正常页面
            except Exception:
                pass

    # 6 次全失败：静默放行，不阻塞页面（后续 API 调用会给出具体错误）
    st.session_state["_backend_ready"] = True


# 每次新 session 打开页面时触发一次预热检测
_warmup_backend()

_ERR_CONN = "服务启动中，请等待10秒后重试"   # 统一连接失败提示（Railway 冷启动）


def _unavailable(e: Exception) -> bool:
    """判断是否为连接类错误"""
    return isinstance(e, (_req.exceptions.ConnectionError,
                          _req.exceptions.Timeout))


def _refresh_token_if_needed() -> None:
    """
    检查 access_token 是否即将过期（剩余 < 60 秒），若是则用 refresh_token 换新。
    刷新失败时清除登录状态，让页面回到登录界面。
    """
    import time
    expires_at = st.session_state.get("token_expires_at", 0)
    if not st.session_state.get("token") or time.time() < expires_at - 60:
        return  # 未登录或尚未过期，无需刷新

    refresh_token = st.session_state.get("refresh_token", "")
    if not refresh_token:
        _handle_expired()
        return

    try:
        resp = _req.post(
            f"{_API}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10,
        )
        if not resp.ok:
            _handle_expired()
            return
        data = resp.json()
        st.session_state["token"]            = data["access_token"]
        st.session_state["refresh_token"]    = data.get("refresh_token", refresh_token)
        st.session_state["token_expires_at"] = time.time() + data.get("expires_in", 3600)
    except Exception:
        _handle_expired()


def _auth_hdr() -> dict:
    """取 token（请求前自动刷新），拼成 Authorization header"""
    _refresh_token_if_needed()
    token = st.session_state.get("token", "")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _handle_expired() -> None:
    """token 过期时清除登录状态并刷新页面"""
    st.session_state.pop("token", None)
    st.session_state.pop("refresh_token", None)
    st.session_state.pop("token_expires_at", None)
    st.session_state.pop("user_email", None)
    st.session_state.pop("today_count", None)
    st.error("登录已过期，请重新登录")
    st.rerun()


def db_insert(row: dict) -> tuple[bool, str]:
    """POST /trade/save，返回 (成功, 错误信息)"""
    try:
        resp = _req.post(f"{_API}/trade/save", json=row,
                         headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


def db_load_all() -> tuple[list, str]:
    """GET /trade/list，返回 (records, 错误信息)"""
    try:
        resp = _req.get(f"{_API}/trade/list",
                        headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return resp.json(), ""
    except Exception as e:
        return [], _ERR_CONN if _unavailable(e) else str(e)


def db_delete_one(record_id) -> tuple[bool, str]:
    """DELETE /trade/delete/{id}，删除单条记录"""
    try:
        resp = _req.delete(f"{_API}/trade/delete/{record_id}",
                           headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


def db_clear_all() -> tuple[bool, str]:
    """DELETE /trade/clear，返回 (成功, 错误信息)"""
    try:
        resp = _req.delete(f"{_API}/trade/clear",
                           headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


# ── 交易日志 API ──────────────────────────────────────────────────────────────

def db_journal_save(data: dict) -> tuple[bool, str]:
    try:
        resp = _req.post(f"{_API}/journal/save", json=data,
                         headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


def db_journal_list() -> tuple[list, str]:
    try:
        resp = _req.get(f"{_API}/journal/list",
                        headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return resp.json(), ""
    except Exception as e:
        return [], _ERR_CONN if _unavailable(e) else str(e)


def db_journal_delete(record_id) -> tuple[bool, str]:
    try:
        resp = _req.delete(f"{_API}/journal/delete/{record_id}",
                           headers=_auth_hdr(), timeout=_TIMEOUT)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


def db_journal_lhb(stock_code: str) -> tuple[list, str]:
    try:
        resp = _req.get(f"{_API}/journal/lhb/{stock_code}",
                        headers=_auth_hdr(), timeout=30)
        if resp.status_code == 401:
            _handle_expired()
        resp.raise_for_status()
        return resp.json(), ""
    except Exception as e:
        return [], _ERR_CONN if _unavailable(e) else str(e)


def _set_proxy() -> None:
    import os
    os.environ["http_proxy"]  = "http://127.0.0.1:7890"
    os.environ["https_proxy"] = "http://127.0.0.1:7890"


@st.cache_data(show_spinner="正在加载A股股票列表…", ttl=3600)
def load_stock_list() -> tuple[list[tuple[str, str]], str]:
    try:
        _set_proxy()
        import akshare as ak
        df = ak.stock_info_a_code_name()
        codes = df.iloc[:, 0].astype(str).str.strip().tolist()
        names = df.iloc[:, 1].astype(str).str.strip().tolist()
        return list(zip(codes, names)), ""
    except ImportError:
        return [], "akshare 未安装，请执行：pip install akshare"
    except Exception as e:
        return [], str(e)


def _disk_cache_path(code: str, start_str: str, end_str: str):
    from pathlib import Path
    cache_dir = Path(__file__).parent / ".stock_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{code}_{start_str}_{end_str}.pkl"


def _fetch_via_akshare(code: str, start_str: str, end_str: str) -> pd.DataFrame:
    """
    不使用 `with` 上下文管理器——with 块的 __exit__ 会调用 shutdown(wait=True)，
    导致 TimeoutError 抛出后仍阻塞等待线程结束。
    改为手动创建 executor，超时后立即 shutdown(wait=False) 跳过等待。
    """
    import concurrent.futures
    _set_proxy()
    import akshare as ak

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(
        ak.stock_zh_a_hist,
        symbol=code, period="daily",
        start_date=start_str, end_date=end_str,
        adjust="qfq",
    )
    try:
        result = future.result(timeout=8)
        executor.shutdown(wait=False)
        return result
    except Exception:
        executor.shutdown(wait=False)  # 超时/异常后不阻塞，线程后台自行结束
        raise


def _fetch_via_baostock(code: str, start_str: str, end_str: str) -> pd.DataFrame:
    import os
    import baostock as bs
    # baostock 股票代码：6 开头=上海，其余=深圳
    prefix = "sh" if code.startswith("6") else "sz"
    bs_code = f"{prefix}.{code}"
    sd = f"{start_str[:4]}-{start_str[4:6]}-{start_str[6:]}"
    ed = f"{end_str[:4]}-{end_str[4:6]}-{end_str[6:]}"

    # baostock 是国内服务，临时清除代理避免路由冲突
    proxy_bak = {}
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        proxy_bak[k] = os.environ.pop(k, None)

    try:
        bs.login()
        rs = bs.query_history_k_data_plus(
            bs_code,
            "date,open,high,low,close,volume,amount,pctChg",
            start_date=sd, end_date=ed,
            frequency="d", adjustflag="2",  # 前复权
        )
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        bs.logout()
    finally:
        for k, v in proxy_bak.items():
            if v is not None:
                os.environ[k] = v

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows, columns=rs.fields)
    df = df.rename(columns={
        "date": "日期", "close": "收盘", "volume": "成交量",
        "pctChg": "涨跌幅", "open": "开盘", "high": "最高",
        "low": "最低", "amount": "成交额",
    })
    for col in ["收盘", "成交量", "涨跌幅", "开盘", "最高", "最低"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["收盘"]).reset_index(drop=True)


@st.cache_data(show_spinner=False, ttl=3600)
def fetch_stock_history(code: str, start_str: str, end_str: str) -> tuple[pd.DataFrame, str, str]:
    """返回 (df, error_msg, source_label)。source_label 非空时前端展示数据来源。"""
    import pickle

    # 1. 磁盘缓存：同股票同日期范围直接复用
    cache_path = _disk_cache_path(code, start_str, end_str)
    if cache_path.exists():
        try:
            with open(cache_path, "rb") as f:
                cached = pickle.load(f)
            # 兼容旧缓存（只存 DataFrame）和新缓存（存 (df, source) 元组）
            if isinstance(cached, tuple):
                df, src = cached
            else:
                df, src = cached, "缓存"
            if isinstance(df, pd.DataFrame) and not df.empty:
                return df, "", f"本地缓存（{src}）"
        except Exception:
            cache_path.unlink(missing_ok=True)

    def _save_cache(df: pd.DataFrame, src: str) -> None:
        try:
            with open(cache_path, "wb") as f:
                pickle.dump((df, src), f)
        except Exception:
            pass

    # 2. 首选 akshare（8 秒强制超时）
    ak_err = ""
    try:
        df = _fetch_via_akshare(code, start_str, end_str)
        if isinstance(df, pd.DataFrame) and not df.empty:
            _save_cache(df, "akshare")
            return df, "", ""
        ak_err = "返回空数据"
    except ImportError:
        ak_err = "akshare 未安装"
    except Exception as e:
        ak_err = str(e)

    # 3. 备选 baostock（国内服务，无需代理，akshare 超时后立即执行）
    bs_err = ""
    try:
        df = _fetch_via_baostock(code, start_str, end_str)
        if isinstance(df, pd.DataFrame) and not df.empty:
            _save_cache(df, "baostock")
            return df, "", "baostock（国内直连）"
        bs_err = "返回空数据"
    except ImportError:
        bs_err = "baostock 未安装，请执行：pip install baostock"
    except Exception as e:
        bs_err = str(e)

    return pd.DataFrame(), (
        f"历史数据获取失败。\n"
        f"akshare：{ak_err}\n"
        f"baostock：{bs_err}\n"
        f"请检查网络，或执行 pip install baostock 后重试。"
    ), ""


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════
def pct_hint(price: float, ref: float, label_up: str, label_dn: str) -> None:
    """在输入框正下方显示相对涨跌幅（涨绿跌红，字号小一号）。
    price / ref 任一为 0 时不渲染。"""
    if price <= 0 or ref <= 0:
        return
    pct   = (price - ref) / ref * 100
    arrow = "▲" if pct >= 0 else "▼"
    color = "#21c55d" if pct >= 0 else "#ff4b4b"
    label = label_up if pct >= 0 else label_dn
    st.markdown(
        f'<p class="pct-hint" style="color:{color}">'
        f'{arrow} {pct:+.2f}%　{label}</p>',
        unsafe_allow_html=True)


def pnl_card(col, label: str, amount: float, unit: str = "元", decimals: int = 2):
    sign = "+" if amount > 0 else ""
    css  = "pnl-red" if amount > 0 else ("pnl-green" if amount < 0 else "pnl-gray")
    col.markdown(
        f'<div class="pnl-card"><p class="pnl-label">{label}</p>'
        f'<p class="pnl-value {css}">{sign}{amount:,.{decimals}f} {unit}</p></div>',
        unsafe_allow_html=True,
    )


def calc_fees(buy_amount: float, sell_amount: float) -> dict:
    buy_comm  = max(buy_amount  * 0.0003, 5.0) if buy_amount  > 0 else 0.0
    sell_comm = max(sell_amount * 0.0003, 5.0) if sell_amount > 0 else 0.0
    stamp_tax = sell_amount * 0.001
    total     = buy_comm + sell_comm + stamp_tax
    return {"buy_comm": buy_comm, "sell_comm": sell_comm,
            "stamp_tax": stamp_tax, "total": total}


def fee_expander(fees: dict, gross_profit: float):
    with st.expander("💰 手续费明细（点击展开）"):
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("买入佣金",   f"{fees['buy_comm']:.2f} 元",  help="买入金额×万分之三（最低5元）")
        f2.metric("卖出佣金",   f"{fees['sell_comm']:.2f} 元", help="卖出金额×万分之三（最低5元）")
        f3.metric("印花税",     f"{fees['stamp_tax']:.2f} 元", help="卖出金额×0.1%，仅卖出时收取")
        f4.metric("合计手续费", f"{fees['total']:.2f} 元")
        net  = gross_profit - fees["total"]
        sign = "+" if net > 0 else ""
        st.caption(f"毛利润 {'+' if gross_profit>0 else ''}{gross_profit:.2f} 元　"
                   f"− 手续费 {fees['total']:.2f} 元　= **税后实际盈利 {sign}{net:.2f} 元**")


def be_box_sell(price: float, label: str, note: str):
    st.markdown(f'<div class="be-box"><p class="be-title">{label}</p>'
                f'<p class="be-price-red">{price:.3f} 元</p>'
                f'<p class="be-note">{note}</p></div>', unsafe_allow_html=True)


def be_box_buy(price: float, label: str, note: str):
    st.markdown(f'<div class="be-box-buy"><p class="be-title">{label}</p>'
                f'<p class="be-price-green">{price:.3f} 元</p>'
                f'<p class="be-note">{note}</p></div>', unsafe_allow_html=True)


def save_section(key_prefix: str, trade_type: str, base_row: dict):
    """
    通用「保存本次记录」区块。
    base_row 须含：buy_price, sell_price, quantity,
                   gross_profit, total_fee, net_profit, new_avg_cost
    """
    st.markdown('<div class="save-bar">', unsafe_allow_html=True)
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        stock = st.text_input("股票名称", placeholder="",
                              key=f"{key_prefix}_stock")
    with sc2:
        st.markdown("<br>", unsafe_allow_html=True)
        clicked = st.button("📌 保存本次记录", key=f"{key_prefix}_save",
                            use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        row = {
            "trade_type":  trade_type,
            "stock_name":  stock.strip() or "未填写",
            "notes":       "",
            **base_row,
        }
        ok, err = db_insert(row)
        if ok:
            st.toast("✅ 已保存到历史记录", icon="📌")
            # 同步侧边栏计数
            st.session_state.setdefault("today_count", 0)
            st.session_state["today_count"] += 1
        else:
            st.error(f"保存失败：{err}")


# ══════════════════════════════════════════════════════════════════════════════
# 仓位与止损计算器
# ══════════════════════════════════════════════════════════════════════════════

def _pos_fees(buy_px: float, exit_px: float, qty: int) -> dict:
    """计算一次完整交易的手续费（买入 + 卖出 + 印花税）"""
    buy_amt  = buy_px  * qty
    sell_amt = exit_px * qty
    buy_comm  = max(buy_amt  * 0.0003, 5.0)
    sell_comm = max(sell_amt * 0.0003, 5.0)
    stamp     = sell_amt * 0.001
    return {"buy_comm": buy_comm, "sell_comm": sell_comm,
            "stamp": stamp, "total": buy_comm + sell_comm + stamp}


def show_position_page():
    st.subheader("📐 仓位与止损计算器")
    st.caption("根据资金规模与风险承受能力，计算合理仓位和止损金额。")

    # ── 输入区 ────────────────────────────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    with c1:
        p_capital  = st.number_input("总资金（元）",
                        min_value=0.0, value=0.0, step=10000.0,
                        format="%.2f", key="p_cap")
        p_max_loss = st.number_input("单笔最大可承受亏损（元）",
                        min_value=0.0, value=0.0, step=100.0,
                        format="%.2f", key="p_loss")
    with c2:
        p_buy  = st.number_input("计划买入价格（元）",
                    min_value=0.0, value=0.0, step=0.01,
                    format="%.3f", key="p_buy")
        p_stop = st.number_input("止损价格（元）",
                    min_value=0.0, value=0.0, step=0.01,
                    format="%.3f", key="p_stop")
    with c3:
        p_target = st.number_input("目标价格（元，可选）",
                       min_value=0.0, value=0.0, step=0.01,
                       format="%.3f", key="p_target")

    st.divider()

    # ── 输入校验 ──────────────────────────────────────────────────────────────
    if p_capital <= 0 or p_max_loss <= 0 or p_buy <= 0 or p_stop <= 0:
        st.info("请填写全部必填项：总资金、最大亏损、买入价、止损价。")
        return
    if p_stop >= p_buy:
        st.error("止损价格必须低于买入价格。")
        return
    if p_target > 0 and p_target <= p_buy:
        st.error("目标价格必须高于买入价格。")
        return

    # ── 核心计算 ──────────────────────────────────────────────────────────────
    risk_per_share = p_buy - p_stop
    shares = int(p_max_loss / risk_per_share // 100) * 100

    if shares == 0:
        st.warning("按当前参数计算，建议仓位不足 100 股。"
                   "请增大最大亏损或缩小止损距离。")
        return

    buy_amount     = shares * p_buy
    capital_ratio  = buy_amount / p_capital * 100
    fees_stop      = _pos_fees(p_buy, p_stop, shares)
    stop_loss_net  = shares * risk_per_share + fees_stop["total"]

    # ── 核心结果 ──────────────────────────────────────────────────────────────
    st.markdown("#### 核心结果")
    r1, r2, r3, r4 = st.columns(4)
    r1.metric("建议买入数量",       f"{shares:,} 股")
    r2.metric("实际动用资金",       f"{buy_amount:,.2f} 元")
    r3.metric("占总资金比例",       f"{capital_ratio:.1f}%")
    r4.metric("止损金额（含手续费）", f"{stop_loss_net:.2f} 元")

    # ── 盈亏比（仅填目标价时显示）──
    if p_target > 0:
        fees_win      = _pos_fees(p_buy, p_target, shares)
        profit_net    = shares * (p_target - p_buy) - fees_win["total"]
        rr            = profit_net / stop_loss_net if stop_loss_net > 0 else 0
        stop_pct      = (p_buy - p_stop) / p_buy * 100
        target_pct    = (p_target - p_buy) / p_buy * 100

        st.divider()
        g1, g2, g3, g4 = st.columns(4)
        pnl_card(g1, "目标盈利（税后）", profit_net)
        g2.metric("盈亏比（收益:风险）", f"{rr:.2f} : 1",
                  delta="良好" if rr >= 2 else ("尚可" if rr >= 1.5 else "偏低"),
                  delta_color="off",
                  help=f"每承担 1 元风险，预期获得 {rr:.2f} 元收益")
        g3.metric("止损距离", f"-{stop_pct:.2f}%")
        g4.metric("目标涨幅", f"+{target_pct:.2f}%")

        if rr < 1.5:
            st.warning(f"盈亏比 {rr:.2f}:1 偏低，建议 ≥ 2:1，"
                       "可考虑上移止损或调低目标价来改善。")

    # ── 风险级别提示 ──────────────────────────────────────────────────────────
    st.divider()
    if capital_ratio < 30:
        st.success(f"✅ 轻仓操作（{capital_ratio:.1f}%）— 风险可控")
    elif capital_ratio < 60:
        st.info(f"ℹ️ 中等仓位（{capital_ratio:.1f}%）— 注意止损执行")
    elif capital_ratio < 80:
        st.warning(f"⚠️ 重仓操作（{capital_ratio:.1f}%）— 严格执行止损")
    else:
        st.error(f"🚨 接近满仓（{capital_ratio:.1f}%）— 风险极高，谨慎操作")

    # ── 手续费明细 ────────────────────────────────────────────────────────────
    with st.expander("💰 手续费明细（止损情景）"):
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("买入佣金",   f"{fees_stop['buy_comm']:.2f} 元")
        f2.metric("卖出佣金",   f"{fees_stop['sell_comm']:.2f} 元")
        f3.metric("印花税",     f"{fees_stop['stamp']:.2f} 元")
        f4.metric("手续费合计", f"{fees_stop['total']:.2f} 元")
        st.caption(f"不含手续费止损额 {shares * risk_per_share:.2f} 元"
                   f"　+　手续费 {fees_stop['total']:.2f} 元"
                   f"　= 实际损失 **{stop_loss_net:.2f} 元**")

    # ── 分批建仓计划 ──────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 分批建仓计划")

    batches = st.slider("计划分几批买入", min_value=2, max_value=5,
                        value=2, key="p_batches")

    # 每批参考价格：在买入价到止损价之间均匀分布（间距为止损距离的15%）
    price_step = risk_per_share * 0.15
    # 每批股数（尽量均等，第一批吸收余数）
    per_batch  = max(100, (shares // batches // 100) * 100)
    allocated  = per_batch * batches
    extra_lots = (shares - allocated) // 100          # 多出的整手
    batch_qtys = [per_batch + (100 if i < extra_lots else 0)
                  for i in range(batches)]

    # 表头
    h0, h1, h2, h3, h4, h5 = st.columns([0.6, 1.2, 1.8, 1.6, 1.4, 1.8])
    for col, txt in zip([h0,h1,h2,h3,h4,h5],
                        ["批次","数量（股）","参考价格（元）",
                         "本批资金（元）","累计股数","累计均价（元）"]):
        col.markdown(f"<span style='font-size:0.82rem;color:rgba(250,250,250,0.5)'>"
                     f"{txt}</span>", unsafe_allow_html=True)

    cum_shares = 0
    cum_cost   = 0.0
    for i, qty in enumerate(batch_qtys):
        ref_px  = max(p_buy - i * price_step, p_stop * 1.02)
        b_cost  = qty * ref_px
        cum_shares += qty
        cum_cost   += b_cost
        avg_cost    = cum_cost / cum_shares

        c0,c1_,c2_,c3_,c4_,c5_ = st.columns([0.6,1.2,1.8,1.6,1.4,1.8])
        c0.markdown(f"第 {i+1} 批")
        c1_.markdown(f"**{qty:,}**")
        c2_.markdown(f"≤ **{ref_px:.3f}**")
        c3_.markdown(f"{b_cost:,.2f}")
        c4_.markdown(f"{cum_shares:,}")
        c5_.markdown(f"**{avg_cost:.3f}**")

    st.caption("每批参考买入价逐步降低，越跌越买以摊薄成本；"
               "无论分几批建仓，触及止损价时的最大亏损始终不超过你设定的上限。")


# ══════════════════════════════════════════════════════════════════════════════
# 交易日志页面
# ══════════════════════════════════════════════════════════════════════════════
_ACTION_TYPES  = ["买入", "卖出", "加仓", "减仓"]
_EMOTIONS      = ["冷静", "冲动", "跟风", "恐慌"]
_EMOTION_COLOR = {"冷静": "#21c55d", "冲动": "#ff4b4b", "跟风": "#f59e0b", "恐慌": "#8b5cf6"}
_EMOTION_ICON  = {"冷静": "🧠", "冲动": "⚡", "跟风": "🐑", "恐慌": "😨"}
_ACTION_COLOR  = {"买入": "#ff4b4b", "卖出": "#21c55d", "加仓": "#f87171", "减仓": "#4ade80"}


def show_journal_page():
    st.subheader("📓 个人交易日志")

    # ── 新增表单 ──────────────────────────────────────────────────────────────
    with st.expander("➕  记录新交易", expanded=not bool(st.session_state.get("jl_saved"))):
        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            _sl, _sl_err = load_stock_list()
            if _sl:
                st.caption(f"已加载 {len(_sl)} 只股票")
                jl_search = st.text_input("🔍 股票搜索", key="jl_search", placeholder="")
                _q = jl_search.strip()
                _matches = [(c, n) for c, n in _sl if _q in c or _q in n][:8] if _q else []
                if _matches:
                    _opts = ["— 请选择 —"] + [f"{c}  {n}" for c, n in _matches]
                    _sel  = st.selectbox("", _opts, key="jl_stock_sel",
                                         label_visibility="collapsed")
                    if _sel and _sel != "— 请选择 —":
                        _parts = _sel.split("  ", 1)
                        jl_code = _parts[0].strip()
                        jl_name = _parts[1].strip() if len(_parts) > 1 else ""
                    else:
                        jl_code = jl_name = ""
                elif _q:
                    st.caption("未找到匹配的A股股票")
                    jl_code = jl_name = ""
                else:
                    jl_code = jl_name = ""
            else:
                st.caption("⚠️ 股票搜索暂时不可用，请手动输入")
                jl_code = st.text_input("股票代码", key="jl_code_fb")
                jl_name = st.text_input("股票名称", key="jl_name_fb")
        with fc2:
            jl_action  = st.selectbox("操作类型", _ACTION_TYPES, key="jl_action")
            jl_emotion = st.selectbox("情绪标签", _EMOTIONS, key="jl_emotion")
        with fc3:
            jl_price = st.number_input("成交价格（元）", min_value=0.0, value=0.0,
                                       step=0.01, format="%.3f", key="jl_price")
            jl_qty   = st.number_input("成交数量（股）", min_value=0, value=0,
                                       step=100, key="jl_qty")

        jl_date   = st.date_input("成交日期", value=date.today(), key="jl_date")
        jl_reason = st.text_area("交易理由（必填）", key="jl_reason", height=90)
        jl_notes  = st.text_input("备注（可选）", key="jl_notes")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾  保存日志", type="primary", key="jl_save"):
            if not jl_code.strip():
                st.error("请搜索并选择股票")
            elif not jl_reason.strip():
                st.error("交易理由不能为空")
            elif jl_price <= 0:
                st.error("请输入有效的成交价格")
            elif jl_qty <= 0:
                st.error("请输入有效的成交数量")
            else:
                ok, err = db_journal_save({
                    "stock_code":  jl_code.strip(),
                    "stock_name":  jl_name.strip(),
                    "action_type": jl_action,
                    "price":       jl_price,
                    "quantity":    jl_qty,
                    "trade_date":  str(jl_date),
                    "reason":      jl_reason.strip(),
                    "emotion":     jl_emotion,
                    "notes":       jl_notes.strip(),
                })
                if ok:
                    st.session_state["jl_saved"] = True
                    st.toast("✅ 日志已保存", icon="📓")
                    st.rerun()
                else:
                    st.error(f"保存失败：{err}")

    # ── 加载日志 ──────────────────────────────────────────────────────────────
    records, err = db_journal_list()
    if err:
        st.error(f"读取失败：{err}")
        return
    if not records:
        st.info("暂无交易日志。点击上方「记录新交易」开始记录。")
        return

    total = len(records)

    # ── 统计面板 ──────────────────────────────────────────────────────────────
    st.divider()
    st.markdown("#### 📊 统计分析")
    stat1, stat2, stat3 = st.columns([3, 2, 1])

    with stat1:
        st.markdown("**情绪分布**")
        em_counts = {}
        for r in records:
            em = r.get("emotion", "冷静")
            em_counts[em] = em_counts.get(em, 0) + 1
        # 只显示有数据的情绪
        pie_labels = [em for em in _EMOTIONS if em_counts.get(em, 0) > 0]
        pie_values = [em_counts[em] for em in pie_labels]
        pie_colors = [_EMOTION_COLOR[em] for em in pie_labels]
        if pie_labels:
            fig = go.Figure(data=[go.Pie(
                labels=pie_labels,
                values=pie_values,
                marker=dict(colors=pie_colors,
                            line=dict(color="#0e1117", width=2)),
                textfont=dict(color="white", size=13),
                textinfo="label+percent",
                hovertemplate="%{label}: %{value} 次 (%{percent})<extra></extra>",
                hole=0.35,
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=0, r=0, t=10, b=10),
                showlegend=False,
                height=220,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with stat2:
        st.markdown("**最常交易 Top 3**")
        stock_counts: dict = {}
        for r in records:
            key = r.get("stock_name") or r.get("stock_code") or "未知"
            stock_counts[key] = stock_counts.get(key, 0) + 1
        top3 = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (name, cnt) in enumerate(top3, 1):
            st.markdown(
                f'<p style="margin:8px 0;font-size:0.9rem">'
                f'<span style="color:rgba(250,250,250,0.4)">#{i}</span>&nbsp;'
                f'<span style="font-weight:600">{name}</span>&nbsp;'
                f'<span style="color:rgba(250,250,250,0.5)">{cnt} 次</span></p>',
                unsafe_allow_html=True)

    with stat3:
        st.metric("总记录数", f"{total} 条")

    # ── 筛选 ──────────────────────────────────────────────────────────────────
    st.divider()
    fl1, fl2, fl3 = st.columns(3)
    with fl1:
        f_stock   = st.text_input("筛选股票名称/代码", key="jl_fs")
    with fl2:
        f_action  = st.selectbox("操作类型", ["全部"] + _ACTION_TYPES, key="jl_fa")
    with fl3:
        f_emotion = st.selectbox("情绪标签", ["全部"] + _EMOTIONS, key="jl_fe")

    filtered = [
        r for r in records
        if (not f_stock or f_stock in (r.get("stock_name","") + r.get("stock_code","")))
        and (f_action  == "全部" or r.get("action_type") == f_action)
        and (f_emotion == "全部" or r.get("emotion")     == f_emotion)
    ]
    st.caption(f"显示 {len(filtered)} / {total} 条记录")
    st.divider()

    # ── 日志列表 ──────────────────────────────────────────────────────────────
    for r in filtered:
        rid     = r.get("id")
        conf_k  = f"jl_conf_{rid}"
        td      = (r.get("trade_date") or "")[:10]
        action  = r.get("action_type", "")
        stock   = r.get("stock_name") or r.get("stock_code") or "—"
        code    = r.get("stock_code", "")
        price   = r.get("price", 0)
        qty     = r.get("quantity", 0)
        emotion = r.get("emotion", "")
        reason  = r.get("reason", "")
        notes   = r.get("notes", "")
        a_color = _ACTION_COLOR.get(action, "#aaa")
        e_icon  = _EMOTION_ICON.get(emotion, "")

        with st.container():
            c1, c2, c3, c_del = st.columns([2.8, 1.8, 1.2, 0.4])
            c1.markdown(
                f'**{td}**&nbsp;&nbsp;'
                f'<span style="color:{a_color};font-weight:700">{action}</span>&nbsp;&nbsp;'
                f'**{stock}**' + (f'&nbsp;<span style="color:rgba(250,250,250,0.4);font-size:0.8rem">({code})</span>' if code else ''),
                unsafe_allow_html=True)
            c2.markdown(f"**{price:.3f}** 元 × **{qty:,}** 股")
            c3.markdown(f"{e_icon} {emotion}")
            with c_del:
                if st.button("🗑️", key=f"jl_delbtn_{rid}", help="删除",
                             use_container_width=True):
                    st.session_state[conf_k] = True

            if st.session_state.get(conf_k):
                st.warning(f"确定删除这条记录吗？（{td} {action} {stock}）")
                yc, nc, _ = st.columns([1, 1, 4])
                with yc:
                    if st.button("✅ 确认删除", type="primary",
                                 use_container_width=True, key=f"jl_dodel_{rid}"):
                        ok2, err2 = db_journal_delete(rid)
                        st.session_state.pop(conf_k, None)
                        if ok2:
                            st.toast("已删除", icon="🗑️")
                        else:
                            st.error(f"删除失败：{err2}")
                        st.rerun()
                with nc:
                    if st.button("❌ 取消", use_container_width=True,
                                 key=f"jl_cancel_{rid}"):
                        st.session_state.pop(conf_k, None)
                        st.rerun()

            with st.expander("查看详情"):
                st.markdown(f"**交易理由：** {reason}")
                if notes:
                    st.caption(f"备注：{notes}")
                dm1, dm2, dm3 = st.columns(3)
                dm1.metric("成交价", f"{price:.3f} 元")
                dm2.metric("数量",   f"{qty:,} 股")
                dm3.metric("成交金额", f"{price * qty:,.2f} 元")

                # ── 龙虎榜记录 ────────────────────────────────────────────────
                st.markdown("---")
                st.markdown("**📋 龙虎榜记录（近30日）**")
                if not code:
                    st.caption("请编辑此记录补充股票代码，以查询龙虎榜")
                else:
                    lhb_key = f"lhb_{rid}"
                    if lhb_key not in st.session_state:
                        with st.spinner("正在查询龙虎榜数据…"):
                            lhb_data, lhb_err = db_journal_lhb(code)
                            st.session_state[lhb_key] = (lhb_data, lhb_err)
                    lhb_data, lhb_err = st.session_state[lhb_key]
                    if lhb_err:
                        st.warning(f"龙虎榜查询失败：{lhb_err}")
                    elif not lhb_data:
                        st.caption("近30日未上龙虎榜")
                    else:
                        rows = []
                        for item in lhb_data:
                            buy  = item.get("buy_amount")
                            sell = item.get("sell_amount")
                            net  = item.get("net_buy")
                            rows.append({
                                "日期":   item.get("date", ""),
                                "上榜原因": item.get("reason", ""),
                                "买入金额（万）": f"{buy/1e4:.1f}" if buy is not None else "—",
                                "卖出金额（万）": f"{sell/1e4:.1f}" if sell is not None else "—",
                                "净买入（万）":  f"{net/1e4:.1f}" if net is not None else "—",
                            })
                        st.dataframe(rows, use_container_width=True, hide_index=True)
            st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# 策略回测
# ══════════════════════════════════════════════════════════════════════════════

def _ind_macd(close_arr):
    s     = pd.Series(close_arr)
    ema12 = s.ewm(span=12, adjust=False).mean()
    ema26 = s.ewm(span=26, adjust=False).mean()
    dif   = ema12 - ema26
    dea   = dif.ewm(span=9, adjust=False).mean()
    return dif.values, dea.values

def _ind_rsi(close_arr, period: int = 14):
    s     = pd.Series(close_arr)
    delta = s.diff()
    avg_g = delta.clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    avg_l = (-delta).clip(lower=0).ewm(alpha=1 / period, adjust=False).mean()
    rs    = avg_g / (avg_l + 1e-10)
    return (100 - 100 / (1 + rs)).values

def _ind_boll(close_arr, period: int = 20, k: float = 2.0):
    s   = pd.Series(close_arr)
    mid = s.rolling(period).mean()
    std = s.rolling(period).std(ddof=1)
    return mid.values, (mid + k * std).values, (mid - k * std).values


def _calc_backtest(df: pd.DataFrame,
                   buy_cfg: list,  buy_logic: str,
                   sell_cfg: dict,
                   initial_capital: float) -> tuple[list, list, dict]:
    """
    回测引擎：T+1 成交（信号日收盘触发，次日开盘价执行），全仓买入，整手（100股）。

    buy_cfg  : 买入条件列表 [{"id": str, "enabled": bool, "x"?: float, "n"?: int}, ...]
    buy_logic: "AND"（全部满足）或 "OR"（任一满足）
    sell_cfg : 卖出条件字典 {"hold": {...}, "tp": {...}, "sl": {...}, ...}
    """
    df = df.copy()
    df["日期"] = pd.to_datetime(df["日期"])
    df = df.sort_values("日期").reset_index(drop=True)
    n = len(df)
    if n < 10:
        return [], [], {}

    close  = df["收盘"].astype(float).values
    volume = df["成交量"].astype(float).values
    pct_ch = df["涨跌幅"].astype(float).values if "涨跌幅" in df.columns else [0.0] * n
    open_p = df["开盘"].astype(float).values if "开盘" in df.columns else close

    # ── 预计算所有技术指标 ────────────────────────────────────────────────────
    close_s = pd.Series(close)
    vol_s   = pd.Series(volume)

    # MA 缓存（按需计算各种周期）
    _ma_cache: dict = {}
    def _ma(p: int):
        if p not in _ma_cache:
            _ma_cache[p] = close_s.rolling(p, min_periods=p).mean().values
        return _ma_cache[p]

    # N 日最高 / 最低 缓存
    _hi_cache: dict = {}
    def _high(p: int):
        if p not in _hi_cache:
            _hi_cache[p] = close_s.rolling(p, min_periods=p).max().values
        return _hi_cache[p]

    _lo_cache: dict = {}
    def _low(p: int):
        if p not in _lo_cache:
            _lo_cache[p] = close_s.rolling(p, min_periods=p).min().values
        return _lo_cache[p]

    dif, dea     = _ind_macd(close)
    rsi14        = _ind_rsi(close, 14)
    _, _, boll_lo = _ind_boll(close, 20)

    vol_ma5  = vol_s.rolling(5, min_periods=5).mean().values
    vol_prev = vol_s.shift(1).values   # 昨日成交量

    # 连续下跌天数
    consec_dn = [0] * n
    for _i in range(1, n):
        consec_dn[_i] = consec_dn[_i-1] + 1 if close[_i] < close[_i-1] else 0

    # ── warmup（所有条件中所需最长回溯 + MACD 35 根稳定期）────────────────────
    warmup = 35
    for cond in buy_cfg:
        if cond.get("enabled"):
            cid = cond["id"]
            if cid in ("ma_cross_up", "above_ma", "below_ma"):
                warmup = max(warmup, int(cond.get("n", 20)) + 1)
            elif cid in ("drawdown", "consec_down"):
                warmup = max(warmup, int(cond.get("n", 20)))
    for scid, scfg in sell_cfg.items():
        if scfg.get("enabled") and scid in ("below_ma", "new_low"):
            warmup = max(warmup, int(scfg.get("n", 20)))
    if n <= warmup:
        return [], [], {}

    # ── 主循环 ────────────────────────────────────────────────────────────────
    capital = float(initial_capital)
    qty = 0;  buy_px = 0.0;  buy_dt = None;  buy_i = -1
    trades: list[dict]     = []
    equity_cur: list[dict] = []
    tick = 0

    for i in range(warmup, n):
        px     = close[i]
        equity = capital + qty * px
        equity_cur.append({"date": str(df["日期"].iloc[i])[:10], "equity": round(equity, 2)})

        # ── 卖出检查 ──────────────────────────────────────────────────────────
        if qty > 0:
            days_h     = i - buy_i
            ret_pct    = (px / buy_px - 1) * 100
            should_sell = False

            sc = sell_cfg.get("hold", {})
            if sc.get("enabled") and days_h >= int(sc.get("days", 20)):
                should_sell = True
            sc = sell_cfg.get("tp", {})
            if sc.get("enabled") and ret_pct >= float(sc.get("pct", 10)):
                should_sell = True
            sc = sell_cfg.get("sl", {})
            if sc.get("enabled") and ret_pct <= -float(sc.get("pct", 5)):
                should_sell = True
            sc = sell_cfg.get("macd_dead", {})
            if sc.get("enabled") and i > 0:
                if dif[i] < dea[i] and dif[i-1] >= dea[i-1]:
                    should_sell = True
            sc = sell_cfg.get("rsi_above", {})
            if sc.get("enabled") and not pd.isna(rsi14[i]):
                if rsi14[i] > float(sc.get("x", 70)):
                    should_sell = True
            sc = sell_cfg.get("below_ma", {})
            if sc.get("enabled"):
                mn = _ma(int(sc.get("n", 20)))
                if not pd.isna(mn[i]) and px < mn[i]:
                    should_sell = True
            sc = sell_cfg.get("new_low", {})
            if sc.get("enabled"):
                lo = _low(int(sc.get("n", 20)))
                if not pd.isna(lo[i]) and px <= lo[i]:
                    should_sell = True

            if should_sell:
                sell_amt   = qty * px
                s_comm     = max(sell_amt * 0.0003, 5.0)
                proceeds   = sell_amt - s_comm - sell_amt * 0.001
                buy_amt    = qty * buy_px
                b_comm     = max(buy_amt * 0.0003, 5.0)
                total_cost = buy_amt + b_comm
                trades.append({
                    "buy_date":   str(buy_dt)[:10],
                    "buy_price":  round(buy_px, 3),
                    "sell_date":  str(df["日期"].iloc[i])[:10],
                    "sell_price": round(px, 3),
                    "hold_days":  days_h,
                    "pnl_pct":    round((proceeds - total_cost) / total_cost * 100, 2),
                })
                capital = proceeds
                qty = 0;  buy_px = 0.0;  buy_dt = None;  buy_i = -1

        # ── 买入信号检查（无持仓） ─────────────────────────────────────────────
        else:
            signals = []
            for cond in buy_cfg:
                if not cond.get("enabled"):
                    continue
                cid = cond["id"]
                sig = False

                if cid == "drop_pct":
                    sig = float(pct_ch[i]) < -float(cond.get("x", 3))
                elif cid == "vol_ma5":
                    vm5 = vol_ma5[i-1] if i > 0 else 0
                    sig = vm5 > 0 and volume[i] > vm5 * float(cond.get("x", 2))
                elif cid == "ma_cross_up":
                    mn = _ma(int(cond.get("n", 20)))
                    sig = (not pd.isna(mn[i]) and not pd.isna(mn[i-1])
                           and close[i] > mn[i] and close[i-1] <= mn[i-1])
                elif cid == "interval":
                    sig = tick % max(int(cond.get("n", 5)), 1) == 0
                elif cid == "above_ma":
                    mn  = _ma(int(cond.get("n", 20)))
                    sig = not pd.isna(mn[i]) and close[i] > mn[i]
                elif cid == "below_ma":
                    mn  = _ma(int(cond.get("n", 20)))
                    sig = not pd.isna(mn[i]) and close[i] < mn[i]
                elif cid == "macd_golden":
                    sig = i > 0 and dif[i] > dea[i] and dif[i-1] <= dea[i-1]
                elif cid == "rsi_below":
                    sig = not pd.isna(rsi14[i]) and rsi14[i] < float(cond.get("x", 30))
                elif cid == "vol_yesterday":
                    vy  = vol_prev[i]
                    sig = vy > 0 and volume[i] > vy * float(cond.get("x", 2))
                elif cid == "consec_down":
                    sig = consec_dn[i] >= int(cond.get("n", 3))
                elif cid == "drawdown":
                    hi  = _high(int(cond.get("n", 60)))
                    sig = (not pd.isna(hi[i]) and hi[i] > 0
                           and (hi[i] - close[i]) / hi[i] * 100 >= float(cond.get("x", 10)))
                elif cid == "boll_lower":
                    sig = not pd.isna(boll_lo[i]) and close[i] < boll_lo[i] * 1.02

                signals.append(sig)

            tick += 1
            fire = (all(signals) if buy_logic == "AND" else any(signals)) if signals else False

            # T+1：次日开盘价执行
            if fire and i + 1 < n:
                exec_px = open_p[i + 1]
                if capital > exec_px * 100:
                    max_qty     = int((capital * 0.9997 - 5) / exec_px / 100) * 100
                    actual_cost = max_qty * exec_px
                    actual_comm = max(actual_cost * 0.0003, 5.0)
                    if max_qty > 0 and actual_cost + actual_comm <= capital:
                        capital -= actual_cost + actual_comm
                        qty    = max_qty;  buy_px = exec_px
                        buy_dt = df["日期"].iloc[i + 1];  buy_i = i + 1

    # ── 末日强制平仓 ──────────────────────────────────────────────────────────
    if qty > 0:
        px         = close[-1]
        sell_amt   = qty * px
        proceeds   = sell_amt - max(sell_amt * 0.0003, 5.0) - sell_amt * 0.001
        buy_amt    = qty * buy_px
        total_cost = buy_amt + max(buy_amt * 0.0003, 5.0)
        trades.append({
            "buy_date":   str(buy_dt)[:10],
            "buy_price":  round(buy_px, 3),
            "sell_date":  str(df["日期"].iloc[-1])[:10],
            "sell_price": round(px, 3),
            "hold_days":  (n - 1) - buy_i,
            "pnl_pct":    round((proceeds - total_cost) / total_cost * 100, 2),
        })
        capital = proceeds
        if equity_cur:
            equity_cur[-1]["equity"] = round(capital, 2)

    final_eq  = capital
    total_ret = (final_eq - initial_capital) / initial_capital * 100
    n_cal = max((pd.to_datetime(equity_cur[-1]["date"]) -
                 pd.to_datetime(equity_cur[0]["date"])).days, 1) if len(equity_cur) > 1 else 1
    ann_ret = ((1 + total_ret / 100) ** (365.0 / n_cal) - 1) * 100

    pnls     = [t["pnl_pct"] for t in trades] or [0.0]
    win_rate = sum(1 for p in pnls if p > 0) / len(pnls) * 100
    avg_ret  = sum(pnls) / len(pnls)
    max_loss = min(pnls)

    peak = 0.0;  max_dd = 0.0
    for e in equity_cur:
        v = e["equity"]
        if v > peak: peak = v
        if peak > 0:
            dd = (peak - v) / peak * 100
            if dd > max_dd: max_dd = dd

    return trades, equity_cur, {
        "total_trades":      len(trades),
        "win_rate":          round(win_rate, 1),
        "avg_return":        round(avg_ret, 2),
        "max_loss":          round(max_loss, 2),
        "max_drawdown":      round(max_dd, 2),
        "total_return":      round(total_ret, 2),
        "annualized_return": round(ann_ret, 2),
        "final_equity":      round(final_eq, 2),
    }


def show_backtest_page():
    st.subheader("📈 策略回测")
    st.warning("⚠️ 回测结果基于历史数据，不代表未来收益，仅供参考", icon="⚠️")

    # ── 参数设置 ──────────────────────────────────────────────────────────────
    st.markdown("#### ⚙️ 参数设置")
    pa, pb, pc = st.columns([1.2, 1, 1])
    with pa:
        st.markdown("**股票**")
        bt_code = st.text_input("股票代码", key="bt_code", placeholder="")
        bt_name = st.text_input("股票名称", key="bt_name", placeholder="")
    with pb:
        st.markdown("**回测区间**")
        bt_start = st.date_input("开始日期", value=date(2023, 1, 1), key="bt_start")
        bt_end   = st.date_input("结束日期", value=date.today(), key="bt_end")
    with pc:
        st.markdown("**资金 & 手续费**")
        bt_capital = st.number_input("初始资金（元）", min_value=10000,
                                     value=100000, step=10000, key="bt_capital")
        st.caption("佣金万分之三（最低5元）· 印花税 0.1%")

    st.divider()

    # ── 买入条件（多选 + AND/OR 逻辑）────────────────────────────────────────
    _hdr_l, _hdr_r = st.columns([3, 1.2])
    with _hdr_l:
        st.markdown("**📥 买入条件**（可多选）")
    with _hdr_r:
        _and_mode = st.toggle("全部满足（AND）", value=True, key="bt_buy_and")
    buy_logic = "AND" if _and_mode else "OR"
    st.caption(f"逻辑：{'需同时满足所有勾选条件' if buy_logic == 'AND' else '满足任一勾选条件即触发'}")

    # 条件定义：(id, 显示文本, [(参数key, 标签, 默认值, step, min)])
    _BUY_DEFS = [
        ("drop_pct",    "单日跌幅超过 X%",              [("x", "跌幅 X%",    3.0, 0.5, 0.1)]),
        ("vol_ma5",     "成交量超过 5 日均量 X 倍",      [("x", "倍数 X",     2.0, 0.5, 0.1)]),
        ("ma_cross_up", "价格上穿 N 日均线（金叉）",     [("n", "N 天",       20,  1,   2  )]),
        ("interval",    "每隔 N 个交易日定投一次",       [("n", "间隔 N 天",  5,   1,   1  )]),
        ("above_ma",    "股价在 N 日均线之上（趋势过滤）",[("n", "N 天",       20,  1,   2  )]),
        ("below_ma",    "股价在 N 日均线之下（超跌过滤）",[("n", "N 天",       20,  1,   2  )]),
        ("macd_golden", "MACD 金叉（DIF 上穿 DEA）",    []),
        ("rsi_below",   "RSI 低于 X（超卖，默认30）",   [("x", "RSI 阈值",   30,  5,   1  )]),
        ("vol_yesterday","成交量比昨日放大 X 倍",        [("x", "倍数 X",     2.0, 0.5, 0.1)]),
        ("consec_down", "连续下跌 N 天后买入",          [("n", "N 天",       3,   1,   1  )]),
        ("drawdown",    "距 N 日最高点回撤超过 X%",     [("n", "N 天",       60,  5,   5  ),
                                                         ("x", "回撤 X%",    10.0,1.0, 1.0)]),
        ("boll_lower",  "布林带下轨附近（20日，下轨×1.02）",[]),
    ]

    buy_cfg = []
    for cid, label, params in _BUY_DEFS:
        n_p = len(params)
        cols = st.columns([2.6] + [0.9] * n_p) if n_p else [st.columns(1)[0]]
        with cols[0]:
            enabled = st.checkbox(label, key=f"bc_{cid}")
        item: dict = {"id": cid, "enabled": enabled}
        for j, (pk, plabel, pdef, pstep, pmin) in enumerate(params):
            with cols[j + 1]:
                is_int = isinstance(pdef, int)
                raw = st.number_input(
                    plabel,
                    min_value=int(pmin) if is_int else float(pmin),
                    value=int(pdef) if is_int else float(pdef),
                    step=int(pstep) if is_int else float(pstep),
                    key=f"bc_{cid}_{pk}",
                    disabled=not enabled,
                    label_visibility="collapsed",
                )
                item[pk] = int(raw) if is_int else float(raw)
        buy_cfg.append(item)

    st.divider()

    # ── 卖出条件（多选）──────────────────────────────────────────────────────
    st.markdown("**📤 卖出条件**（至少选一项）")

    _SELL_DEFS = [
        ("hold",      "持有超过 N 天强制卖出",       [("days","N 天",    20,  1,   1  )]),
        ("tp",        "盈利达到 X% 止盈",            [("pct", "止盈 X%", 10.0,0.5, 0.1)]),
        ("sl",        "亏损达到 X% 止损",            [("pct", "止损 X%", 5.0, 0.5, 0.1)]),
        ("macd_dead", "MACD 死叉（DIF 下穿 DEA）",  []),
        ("rsi_above", "RSI 高于 X（超买，默认70）",  [("x",   "RSI 阈值",70,  5,   1  )]),
        ("below_ma",  "跌破 N 日均线卖出",           [("n",   "N 天",    20,  1,   2  )]),
        ("new_low",   "股价创 N 日新低卖出",         [("n",   "N 天",    20,  1,   2  )]),
    ]

    # 3 列布局排列卖出条件
    sell_cfg: dict = {}
    _sell_items = []
    for scid, slabel, sparams in _SELL_DEFS:
        n_p = len(sparams)
        cols = st.columns([2.6] + [0.9] * n_p) if n_p else [st.columns(1)[0]]
        with cols[0]:
            s_enabled = st.checkbox(slabel, key=f"sc_{scid}")
        s_item: dict = {"enabled": s_enabled}
        for j, (pk, plabel, pdef, pstep, pmin) in enumerate(sparams):
            with cols[j + 1]:
                is_int = isinstance(pdef, int)
                raw = st.number_input(
                    plabel,
                    min_value=int(pmin) if is_int else float(pmin),
                    value=int(pdef) if is_int else float(pdef),
                    step=int(pstep) if is_int else float(pstep),
                    key=f"sc_{scid}_{pk}",
                    disabled=not s_enabled,
                    label_visibility="collapsed",
                )
                s_item[pk] = int(raw) if is_int else float(raw)
        sell_cfg[scid] = s_item

    # ── 运行回测 ──────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("▶️ 开始回测", type="primary", key="bt_run"):
        active_buy  = [c for c in buy_cfg  if c.get("enabled")]
        active_sell = [k for k, v in sell_cfg.items() if v.get("enabled")]
        if not bt_code:
            st.error("请先输入股票代码")
        elif bt_start >= bt_end:
            st.error("开始日期必须早于结束日期")
        elif not active_buy:
            st.error("请至少勾选一个买入条件")
        elif not active_sell:
            st.error("请至少勾选一个卖出条件")
        else:
            _label = f"{bt_code}" + (f" {bt_name}" if bt_name.strip() else "")
            with st.spinner(f"正在获取 {_label} 历史数据，请稍候…"):
                df_hist, hist_err, data_src = fetch_stock_history(
                    bt_code.strip(),
                    bt_start.strftime("%Y%m%d"),
                    bt_end.strftime("%Y%m%d"),
                )
            if hist_err:
                st.error(hist_err)
                st.info("💡 建议先用较短的时间范围测试，例如最近半年（6个月）")
            elif df_hist.empty:
                st.error("未获取到行情数据，请检查股票代码和日期范围")
            else:
                if data_src:
                    st.info(f"数据来源：{data_src}", icon="ℹ️")
                trades, equity_cur, metrics = _calc_backtest(
                    df_hist, buy_cfg, buy_logic, sell_cfg, float(bt_capital),
                )
                st.session_state["bt_result"] = {
                    "trades":     trades,
                    "equity_cur": equity_cur,
                    "metrics":    metrics,
                    "df_hist":    df_hist,
                    "capital":    bt_capital,
                    "stock":      f"{bt_name}（{bt_code}）",
                    "data_src":   data_src,
                }
                st.rerun()

    # ── 回测结果 ──────────────────────────────────────────────────────────────
    res = st.session_state.get("bt_result")
    if not res:
        return

    trades     = res["trades"]
    equity_cur = res["equity_cur"]
    m          = res["metrics"]
    df_hist    = res["df_hist"]
    cap        = res["capital"]
    stk        = res["stock"]
    data_src   = res.get("data_src", "")

    st.divider()
    src_tag = f"　<small style='color:rgba(250,250,250,0.4)'>数据来源：{data_src}</small>" if data_src else ""
    st.markdown(f"#### 📊 回测结果 — {stk}{src_tag}", unsafe_allow_html=True)

    # 核心指标
    r1, r2, r3, r4 = st.columns(4)
    tr  = m["total_return"];  ann = m["annualized_return"]
    clr = "normal" if tr >= 0 else "inverse"
    r1.metric("总收益率",   f"{tr:+.2f}%",
              delta=f"年化 {ann:+.2f}%", delta_color=clr)
    r2.metric("最终资金",   f"{m['final_equity']:,.2f} 元")
    r3.metric("总交易次数", f"{m['total_trades']} 次")
    r4.metric("胜率",       f"{m['win_rate']:.1f}%")

    r5, r6, r7, r8 = st.columns(4)
    r5.metric("平均每笔收益", f"{m['avg_return']:+.2f}%")
    r6.metric("最大单笔亏损", f"{m['max_loss']:.2f}%")
    r7.metric("最大回撤",     f"{m['max_drawdown']:.2f}%")
    r8.metric("初始资金",     f"{cap:,.0f} 元")

    # 图表
    tab_eq, tab_kl = st.tabs(["📈 资金曲线", "📊 交易标注"])

    with tab_eq:
        fig_eq = go.Figure()
        fig_eq.add_trace(go.Scatter(
            x=[e["date"]   for e in equity_cur],
            y=[e["equity"] for e in equity_cur],
            mode="lines", name="账户净值",
            line=dict(color="#4ade80", width=2),
            fill="tozeroy", fillcolor="rgba(74,222,128,0.07)",
        ))
        fig_eq.add_hline(y=cap, line_dash="dot",
                          line_color="rgba(250,250,250,0.3)",
                          annotation_text="初始资金",
                          annotation_font_color="rgba(250,250,250,0.5)")
        fig_eq.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(250,250,250,0.8)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                       tickformat=",.0f"),
            height=360, margin=dict(l=10, r=10, t=30, b=10),
            showlegend=False,
        )
        st.plotly_chart(fig_eq, use_container_width=True)

    with tab_kl:
        _df = df_hist.copy()
        _df["日期"] = pd.to_datetime(_df["日期"]).astype(str)
        fig_kl = go.Figure()
        fig_kl.add_trace(go.Scatter(
            x=_df["日期"], y=_df["收盘"].astype(float),
            mode="lines", name="收盘价",
            line=dict(color="rgba(250,250,250,0.6)", width=1.5),
        ))
        if trades:
            fig_kl.add_trace(go.Scatter(
                x=[t["buy_date"]   for t in trades],
                y=[t["buy_price"]  for t in trades],
                mode="markers", name="买入",
                marker=dict(symbol="triangle-up", size=13, color="#21c55d"),
                hovertemplate="%{x}<br>买入 %{y:.3f}<extra></extra>",
            ))
            fig_kl.add_trace(go.Scatter(
                x=[t["sell_date"]  for t in trades],
                y=[t["sell_price"] for t in trades],
                mode="markers", name="卖出",
                marker=dict(symbol="triangle-down", size=13, color="#ff4b4b"),
                hovertemplate="%{x}<br>卖出 %{y:.3f}<extra></extra>",
            ))
        fig_kl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="rgba(250,250,250,0.8)",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            height=380, margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        st.plotly_chart(fig_kl, use_container_width=True)

    # 交易明细
    if trades:
        st.markdown("#### 📋 交易明细")
        st.dataframe(
            [{
                "买入日期": t["buy_date"],
                "买入价":   f"{t['buy_price']:.3f}",
                "卖出日期": t["sell_date"],
                "卖出价":   f"{t['sell_price']:.3f}",
                "持有天数": t["hold_days"],
                "盈亏%":    f"{t['pnl_pct']:+.2f}%",
            } for t in trades],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("回测期间内未触发任何交易，请适当放宽买入条件或扩大回测区间")


# ══════════════════════════════════════════════════════════════════════════════
# 用户认证
# ══════════════════════════════════════════════════════════════════════════════

def api_login(email: str, password: str,
              max_tries: int = 4, retry_delay: float = 2.0) -> tuple[bool, str]:
    """
    调用 /auth/login，成功后把 token 和邮箱写入 session_state。
    遇到连接类错误（Railway 冷启动）时自动重试，最多 max_tries 次。
    密码错误等业务错误不重试。
    """
    import time
    print(f"[DEBUG] api_login: 使用 API 地址 = {_API}")
    last_err = _ERR_CONN
    for attempt in range(max_tries):
        try:
            print(f"[DEBUG] api_login: 第 {attempt+1}/{max_tries} 次尝试 POST {_API}/auth/login")
            resp = _req.post(f"{_API}/auth/login",
                             json={"email": email, "password": password},
                             timeout=_TIMEOUT)
            print(f"[DEBUG] api_login: HTTP {resp.status_code}，响应体 = {resp.text[:200]}")
            if resp.status_code == 400:
                return False, "邮箱或密码错误"
            if resp.status_code == 401:
                # 旧 session 冲突，等待后重试
                last_err = f"401 session冲突（第{attempt+1}次）"
                if attempt < max_tries - 1:
                    time.sleep(retry_delay)
                continue
            resp.raise_for_status()
            data = resp.json()
            import time as _time
            st.session_state["token"]            = data["access_token"]
            st.session_state["refresh_token"]    = data.get("refresh_token", "")
            st.session_state["token_expires_at"] = _time.time() + data.get("expires_in", 3600)
            st.session_state["user_email"]       = data.get("user", {}).get("email", email)
            return True, ""
        except Exception as e:
            err_detail = f"{type(e).__name__}: {e}"
            print(f"[DEBUG] api_login: 第 {attempt+1} 次异常 → {err_detail}")
            if not _unavailable(e):
                return False, err_detail   # 业务错误，不重试，直接透传真实错误
            last_err = err_detail          # 连接错误也记录真实信息
            if attempt < max_tries - 1:
                time.sleep(retry_delay)
    return False, last_err


def api_register(email: str, password: str) -> tuple[bool, str]:
    """调用 /auth/register，返回 (成功, 错误信息)"""
    try:
        resp = _req.post(f"{_API}/auth/register",
                         json={"email": email, "password": password},
                         timeout=_TIMEOUT)
        if resp.status_code == 422:
            return False, "邮箱格式不正确或密码长度不足"
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        return False, _ERR_CONN if _unavailable(e) else str(e)


def api_logout() -> None:
    """调用 /auth/logout 让 token 失效，然后清除本地状态"""
    token = st.session_state.get("token", "")
    if token:
        try:
            _req.post(f"{_API}/auth/logout",
                      headers={"Authorization": f"Bearer {token}"},
                      timeout=_TIMEOUT)
        except Exception:
            pass  # 网络异常也直接清除本地状态
    st.session_state.pop("token",       None)
    st.session_state.pop("user_email",  None)
    st.session_state.pop("today_count", None)


def _show_auth_page() -> None:
    """未登录时显示的登录 / 注册表单（居中卡片）"""
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, card, _ = st.columns([1, 1.4, 1])
    with card:
        st.markdown(
            '<p class="auth-logo">筹码本</p>'
            '<p class="auth-sub">A 股散户决策工具</p>',
            unsafe_allow_html=True,
        )
        tab_in, tab_up = st.tabs(["登录", "注册"])

        # ── 登录 Tab ──
        with tab_in:
            email_in = st.text_input("邮箱", key="login_email",
                                     placeholder="your@email.com")
            pwd_in   = st.text_input("密码", type="password", key="login_pwd")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("登 录", use_container_width=True,
                         type="primary", key="do_login"):
                if not email_in or not pwd_in:
                    st.warning("请输入邮箱和密码")
                else:
                    with st.spinner("登录中，若服务冷启动将自动重试（最多等待约30秒）…"):
                        ok, err = api_login(email_in, pwd_in)
                    if ok:
                        st.rerun()
                    else:
                        st.error(f"登录失败：{err}")

        # ── 注册 Tab ──
        with tab_up:
            email_up = st.text_input("邮箱", key="reg_email",
                                     placeholder="your@email.com")
            pwd_up   = st.text_input("密码（至少 6 位）", type="password",
                                     key="reg_pwd")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("注 册", use_container_width=True, key="do_register"):
                if not email_up or not pwd_up:
                    st.warning("请输入邮箱和密码")
                elif len(pwd_up) < 6:
                    st.warning("密码长度至少 6 位")
                else:
                    with st.spinner("注册中…"):
                        ok, err = api_register(email_up, pwd_up)
                    if ok:
                        st.success("✅ 注册成功！请检查邮箱确认账号，然后回到「登录」Tab 登录。")
                    else:
                        st.error(f"注册失败：{err}")



# ── 登录拦截：未登录时显示表单，中止后续渲染 ──────────────────────────────────
if "token" not in st.session_state:
    _show_auth_page()
    st.stop()


# ── 侧边栏 ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── 顶部可滚动区域开始 ──
    st.markdown('<div class="sidebar-scroll">', unsafe_allow_html=True)

    # ── 工具导航 ──
    st.radio("", ["📊 T+0 计算器", "📓 交易日志", "📐 仓位计算", "📈 策略回测"],
             key="page", label_visibility="collapsed")

    # ── T+0 计算器专属：今日保存计数 ──
    if st.session_state.get("page", "📊 T+0 计算器") == "📊 T+0 计算器":
        st.divider()
        st.caption("📋 **今日保存记录**")
        today_count = st.session_state.get("today_count", 0)
        if today_count == 0:
            st.caption("还没有记录。计算完成后点击「保存本次记录」。")
        else:
            st.success(f"今日已保存 **{today_count}** 次记录")
        st.caption("完整历史请查看「历史记录」Tab。")

    st.markdown('</div>', unsafe_allow_html=True)

    # ── 底部用户信息（固定在侧边栏底部）──
    user_email = st.session_state.get("user_email", "")
    st.markdown(
        f'<div class="sidebar-bottom">'
        f'<p style="font-size:0.75rem;color:rgba(250,250,250,0.4);margin:0 0 2px 0">当前账号</p>'
        f'<p style="font-size:0.85rem;font-weight:600;margin:0 0 10px 0;'
        f'word-break:break-all">{user_email}</p>'
        f'</div>',
        unsafe_allow_html=True)
    if st.button("退出登录", use_container_width=True, key="logout_btn"):
        api_logout()
        st.rerun()


# ── 页面路由 ──────────────────────────────────────────────────────────────────
if st.session_state.get("page") == "📓 交易日志":
    show_journal_page()
    st.stop()

if st.session_state.get("page") == "📐 仓位计算":
    show_position_page()
    st.stop()

if st.session_state.get("page") == "📈 策略回测":
    show_backtest_page()
    st.stop()


# ── T+0 计算器 Tabs ───────────────────────────────────────────────────────────
tab3, tab1, tab2, tab4 = st.tabs(["正T", "反T", "反向计算", "📋 历史记录"])


# ══════════════════════════════════════════════════════════════════════════════
# 正T（机动仓做T：先买后卖）
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("输入区")
    c1, c2, c3 = st.columns(3)
    with c1:
        jd_holding  = st.number_input("原有持仓数量（股）",     min_value=0,   value=0,   step=100,   key="jd_h")
        jd_avg_cost = st.number_input("原有持仓均价/成本（元）", min_value=0.0, value=0.0, step=0.01,  format="%.3f", key="jd_a")
    with c2:
        jd_funds  = st.number_input("机动仓可用资金（元）", min_value=0.0, value=0.0, step=1000.0, format="%.2f", key="jd_f")
        jd_buy_px = st.number_input("计划买入价格（元）",   min_value=0.0, value=0.0, step=0.01,   format="%.3f", key="jd_bp")
    with c3:
        jd_sell_px  = st.number_input("计划卖出价格（元）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="jd_sp")
        pct_hint(jd_sell_px, jd_buy_px, "高于买入价", "低于买入价，将亏损")
        max_by_fund = int(jd_funds // jd_buy_px // 100) * 100 if jd_buy_px > 0 else 0
        jd_buy_qty  = st.number_input(
            f"买入数量（股，资金上限 {max_by_fund:,} 股）",
            min_value=0, max_value=max(max_by_fund, 0),
            value=min(0, max_by_fund), step=100, key="jd_q")

    jd_n = (jd_buy_qty // 100) * 100

    st.divider()
    st.subheader("计算结果")

    if jd_n == 0:
        st.info("请输入有效的买入数量（至少100股）。")
    else:
        buy_amt  = jd_n * jd_buy_px
        sell_amt = jd_n * jd_sell_px
        fees     = calc_fees(buy_amt, sell_amt)
        gross    = sell_amt - buy_amt
        net      = gross - fees["total"]
        total_old_cost  = jd_holding * jd_avg_cost if jd_holding > 0 else 0
        cost_dilution   = net / jd_holding if jd_holding > 0 else 0
        new_avg_success = jd_avg_cost - cost_dilution if jd_holding > 0 else jd_avg_cost
        be_sell         = (buy_amt + fees["buy_comm"]) / (jd_n * 0.9987)

        st.markdown("#### ✅ 顺利完成T（买入后成功卖出）")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("实际动用资金（元）", f"{buy_amt:,.2f}")
        pnl_card(m2, "本次T净盈利（税后）", net)
        m3.metric("原持仓成本摊薄（元/股）", f"{cost_dilution:+.4f}",
                  delta=f"{cost_dilution:+.4f}", delta_color="inverse")
        m4.metric("操作后综合均价（元）", f"{new_avg_success:.3f}",
                  delta=f"{(new_avg_success-jd_avg_cost):+.3f}", delta_color="inverse")

        fee_expander(fees, gross)

        bx1, bx2 = st.columns(2)
        with bx1:
            be_box_sell(be_sell, "保本卖出价（正T）",
                        f"卖出价至少达到此价格，才能覆盖买入成本及全部手续费（买入佣金{fees['buy_comm']:.2f}元）。")
        with bx2:
            diff = jd_sell_px - be_sell
            ok_color = "pnl-red" if diff >= 0 else "pnl-green"
            st.markdown(
                f'<div class="pnl-card" style="margin-top:10px">'
                f'<p class="pnl-label">计划卖出价 vs 保本价</p>'
                f'<p class="pnl-value {ok_color}">{"▲ 高于保本价" if diff>=0 else "▼ 低于保本价，将亏损"}'
                f'　{abs(diff):.3f} 元</p></div>', unsafe_allow_html=True)

        st.divider()
        total_qty_stuck = jd_holding + jd_n
        new_avg_stuck   = (total_old_cost + buy_amt) / total_qty_stuck if total_qty_stuck > 0 else 0
        st.markdown("#### ⚠️ 风险情景：机动仓被套，卖不掉")
        st.warning(f"若无法卖出，机动仓 **{jd_n:,} 股** 并入原仓，"
                   f"总持仓 **{total_qty_stuck:,} 股**，"
                   f"综合均价 **{jd_avg_cost:.3f}** → **{new_avg_stuck:.3f} 元**。")
        rk1, rk2, rk3 = st.columns(3)
        for col, pct, label in [(rk1,0.03,"跌3%"),(rk2,0.05,"跌5%"),(rk3,0.10,"跌10%")]:
            pnl_card(col, f"较买入价{label}（{jd_buy_px*(1-pct):.3f}元）新增浮亏",
                     (jd_buy_px*(1-pct) - new_avg_stuck) * total_qty_stuck)

        if jd_sell_px <= jd_buy_px:
            st.error("卖出价不高于买入价，扣除手续费后本次T必然亏损！")

        st.divider()
        save_section("jd", "正T", {
            "buy_price":    jd_buy_px,
            "sell_price":   jd_sell_px,
            "quantity":     jd_n,
            "gross_profit": round(gross, 4),
            "total_fee":    round(fees["total"], 4),
            "net_profit":   round(net, 4),
            "new_avg_cost": round(new_avg_success, 4),
        })


# ══════════════════════════════════════════════════════════════════════════════
# 反T（先卖后买）
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader("输入区")
    col1, col2 = st.columns(2)
    with col1:
        holding_qty = st.number_input("当前持仓数量（股）", min_value=0, value=0,   step=100)
        avg_cost    = st.number_input("持仓均价/成本（元）", min_value=0.0, value=0.0, step=0.01, format="%.3f")
        sell_qty    = st.number_input("计划卖出数量（股）",  min_value=0, value=0,   step=100)
    with col2:
        sell_price       = st.number_input("卖出价格（元）",           min_value=0.0, value=0.0, step=0.01, format="%.3f")
        pct_hint(sell_price, avg_cost, "高于成本", "低于成本，卖出亏损")
        target_rebuy     = st.number_input("目标回补价格（元，可选）", min_value=0.0, value=0.0, step=0.01, format="%.3f")
        pct_hint(target_rebuy, sell_price, "高于卖出价，将亏损", "低于卖出价，有利润空间")
        use_target_rebuy = st.checkbox("启用目标回补价格", value=True)

    st.divider()
    st.subheader("计算结果")

    if holding_qty == 0 or sell_qty == 0:
        st.info("请输入有效的持仓和卖出数量。")
    elif sell_qty > holding_qty:
        st.error("卖出数量不能大于持仓数量。")
    else:
        remaining_qty = holding_qty - sell_qty
        sell_amt_t1   = sell_qty * sell_price
        sell_comm_t1  = max(sell_amt_t1 * 0.0003, 5.0)
        stamp_tax_t1  = sell_amt_t1 * 0.001
        net_sell_t1   = sell_amt_t1 - sell_comm_t1 - stamp_tax_t1
        be_rebuy      = net_sell_t1 / (sell_qty * 1.0003)
        gross_t1      = sell_qty * (sell_price - avg_cost)
        # 若不回补：新均价 = (原总成本 - 卖出所得) / 剩余数量
        no_rebuy_avg  = (holding_qty * avg_cost - sell_qty * sell_price) / remaining_qty \
                        if remaining_qty > 0 else 0

        if use_target_rebuy:
            rebuy_amt_t1  = sell_qty * target_rebuy
            rebuy_comm_t1 = max(rebuy_amt_t1 * 0.0003, 5.0)
            fees_t1 = {"buy_comm": rebuy_comm_t1, "sell_comm": sell_comm_t1,
                       "stamp_tax": stamp_tax_t1, "total": rebuy_comm_t1+sell_comm_t1+stamp_tax_t1}
            rt_gross = sell_qty * (sell_price - target_rebuy)
            rt_net   = rt_gross - fees_t1["total"]
        else:
            fees_t1 = {"buy_comm": 0, "sell_comm": sell_comm_t1,
                       "stamp_tax": stamp_tax_t1, "total": sell_comm_t1+stamp_tax_t1}
            rt_gross = gross_t1
            rt_net   = gross_t1 - fees_t1["total"]

        res1, res2, res3 = st.columns(3)
        pnl_card(res1, "T盈利（毛，未回补费用）", gross_t1)
        avg_delta_no_rebuy = no_rebuy_avg - avg_cost if remaining_qty > 0 else 0
        res2.metric("若不回补：持仓均价",
                    f"{no_rebuy_avg:.3f}" if remaining_qty > 0 else "—（全部卖出）",
                    delta=f"{avg_delta_no_rebuy:+.3f}" if remaining_qty > 0 else None,
                    delta_color="inverse")
        res3.metric("剩余持仓数量", f"{remaining_qty:,} 股")

        st.divider()
        fee_expander(fees_t1, rt_gross)

        bx1, bx2 = st.columns(2)
        with bx1:
            be_box_buy(be_rebuy, "保本回补价（反T）",
                       f"回补价不超过此价格，卖出操作至少不亏（已含卖出手续费{sell_comm_t1+stamp_tax_t1:.2f}元）。")
        with bx2:
            if use_target_rebuy:
                diff_t1 = be_rebuy - target_rebuy
                ok_t1   = target_rebuy <= be_rebuy
                st.markdown(
                    f'<div class="pnl-card" style="margin-top:10px">'
                    f'<p class="pnl-label">计划回补价 vs 保本回补价</p>'
                    f'<p class="pnl-value {"pnl-red" if ok_t1 else "pnl-green"}">'
                    f'{"✓ 低于保本价，有利润空间" if ok_t1 else "✗ 高于保本价，将亏损"}'
                    f'　{abs(diff_t1):.3f} 元</p></div>', unsafe_allow_html=True)

        if remaining_qty > 0:
            st.divider()
            st.markdown("#### ⚠️ 若股价继续上涨、无法回补")
            ca, cb  = st.columns(2)
            ca.metric("失去的筹码（股）", f"{sell_qty:,}")
            cb.metric("不回补剩余持仓均价变化（元/股）", f"{avg_delta_no_rebuy:+.3f}",
                      delta=f"{avg_delta_no_rebuy:+.3f}", delta_color="inverse")

        if use_target_rebuy:
            st.divider()
            st.markdown("#### ✅ 回补后综合成本")
            new_avg_t1 = (target_rebuy if remaining_qty == 0
                          else (remaining_qty * no_rebuy_avg + sell_qty * target_rebuy) / holding_qty)
            cost_delta = new_avg_t1 - avg_cost
            c1, c2, c3 = st.columns(3)
            c1.metric("新综合均价（元）", f"{new_avg_t1:.3f}",
                      delta=f"{cost_delta:+.3f}", delta_color="inverse")
            pnl_card(c2, "本次T净盈利（税后）", rt_net)
            c3.metric("成本变化（元/股）", f"{cost_delta:+.3f}",
                      delta=f"{cost_delta:+.3f}", delta_color="inverse")

            if target_rebuy > sell_price:
                st.warning("回补价高于卖出价，本次T+0将亏损！")
            if target_rebuy > be_rebuy:
                st.error(f"计划回补价（{target_rebuy:.3f}）高于保本回补价（{be_rebuy:.3f}），回补后将净亏损！")

            st.divider()
            save_section("t1", "反T", {
                "buy_price":    target_rebuy,
                "sell_price":   sell_price,
                "quantity":     sell_qty,
                "gross_profit": round(rt_gross, 4),
                "total_fee":    round(fees_t1["total"], 4),
                "net_profit":   round(rt_net, 4),
                "new_avg_cost": round(new_avg_t1, 4),
            })


# ══════════════════════════════════════════════════════════════════════════════
# 反向计算（降低成本）
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    mode = st.radio("计算模式",
                    ["卖出降成本（先卖后回补）", "买入摊薄（直接加仓）"],
                    horizontal=True, key="tab2_mode")
    st.divider()

    # ── 子模式 A ──────────────────────────────────────────────────────────────
    if mode == "卖出降成本（先卖后回补）":
        st.subheader("我想卖出一部分再低价回补，让成本降低 X 元")
        c1, c2, c3 = st.columns(3)
        with c1:
            rv_h = st.number_input("当前持仓（股）", min_value=0,   value=0,   step=100,  key="rv_h")
            rv_a = st.number_input("当前均价（元）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="rv_a")
        with c2:
            rv_r = st.number_input("目标降低成本（元/股）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="rv_r")
            rv_b = st.number_input("计划回补价格（元）",    min_value=0.0, value=0.0, step=0.01, format="%.3f", key="rv_b")
        with c3:
            rv_sp = st.number_input("卖出价格（元）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="rv_sp")

        st.divider()
        gap = rv_sp - rv_b          # 每股利润空间 = 卖出价 − 回补价
        if rv_sp <= 0 or rv_b <= 0:
            st.info("请输入卖出价格和回补价格。")
        elif rv_b >= rv_sp:
            st.error("回补价格必须低于卖出价格，否则低买高卖无法盈利。")
        elif rv_r <= 0:
            st.info("请输入正数的降低幅度。")
        else:
            n_s      = round(rv_h * rv_r / gap / 100) * 100
            act_red  = n_s * gap / rv_h if rv_h > 0 else 0
            new_avg  = rv_a - act_red
            sell_rv  = n_s * rv_sp
            rebuy_rv = n_s * rv_b
            fees_rv  = calc_fees(rebuy_rv, sell_rv)
            gross_rv = n_s * (rv_sp - rv_b)
            net_rv   = gross_rv - fees_rv["total"]

            sc_rv    = max(sell_rv * 0.0003, 5.0)
            st_rv    = sell_rv * 0.001
            be_r_rv  = (sell_rv - sc_rv - st_rv) / (n_s * 1.0003) if n_s > 0 else 0

            r1, r2, r3, r4 = st.columns(4)
            r1.metric("需卖出股数（股）", f"{n_s:,.0f}", help="已取整至最近整手")
            r2.metric("实际可降成本（元/股）", f"{act_red:.3f}")
            r3.metric("操作后新均价（元）", f"{new_avg:.3f}",
                      delta=f"{(new_avg-rv_a):+.3f}", delta_color="inverse")
            pnl_card(r4, "T净盈利（税后）", net_rv)

            fee_expander(fees_rv, gross_rv)

            bx1, bx2 = st.columns(2)
            with bx1:
                be_box_buy(be_r_rv, "保本回补价（卖出降成本）",
                           f"回补价不超过此价格时，本次T操作至少保本（卖出手续费{sc_rv+st_rv:.2f}元已含）。")
            with bx2:
                diff_rv = be_r_rv - rv_b
                ok_rv   = rv_b <= be_r_rv
                st.markdown(
                    f'<div class="pnl-card" style="margin-top:10px">'
                    f'<p class="pnl-label">计划回补价 vs 保本回补价</p>'
                    f'<p class="pnl-value {"pnl-red" if ok_rv else "pnl-green"}">'
                    f'{"✓ 低于保本价，有利润空间" if ok_rv else "✗ 高于保本价，将亏损"}'
                    f'　{abs(diff_rv):.3f} 元</p></div>', unsafe_allow_html=True)

            if n_s > rv_h:
                st.error(f"需卖出 {n_s:,.0f} 股，超过持仓！请降低目标降幅或提高回补价格。")
            else:
                st.success(f"卖出 **{n_s:,} 股**（占持仓 {n_s/rv_h*100:.1f}%），"
                           f"在 **{rv_b:.3f} 元** 回补后，"
                           f"均价从 **{rv_a:.3f}** 降至 **{new_avg:.3f} 元**。")
                st.divider()
                save_section("rv_a", "反向计算-卖出降成本", {
                    "buy_price":    rv_b,
                    "sell_price":   rv_sp,
                    "quantity":     n_s,
                    "gross_profit": round(gross_rv, 4),
                    "total_fee":    round(fees_rv["total"], 4),
                    "net_profit":   round(net_rv, 4),
                    "new_avg_cost": round(new_avg, 4),
                })

    # ── 子模式 B ──────────────────────────────────────────────────────────────
    else:
        st.subheader("我想通过额外买入来摊薄成本，降低 X 元/股")
        c1, c2, _ = st.columns(3)
        with c1:
            bi_h = st.number_input("当前持仓数量（股）", min_value=0,   value=0,   step=100,  key="bi_h")
            bi_a = st.number_input("当前持仓均价（元）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="bi_a")
        with c2:
            bi_r  = st.number_input("目标成本降低幅度（元/股）", min_value=0.0, value=0.0, step=0.01, format="%.3f", key="bi_r")
            bi_bp = st.number_input("计划买入价格（元）",        min_value=0.0, value=0.0, step=0.01, format="%.3f", key="bi_bp")

        st.divider()
        gap_bi = bi_a - bi_bp
        if gap_bi <= 0:
            st.error("买入价格必须低于当前均价，否则不能摊薄成本。")
        elif bi_r <= 0:
            st.info("请输入正数的降低幅度。")
        elif bi_r >= gap_bi:
            st.error(f"目标降幅（{bi_r:.3f}）不能超过均价与买入价之差（{gap_bi:.3f}），否则需无限加仓。")
        else:
            n_buy       = int(bi_h * bi_r / (gap_bi - bi_r) // 100 + 1) * 100
            new_avg_bi  = (bi_h * bi_a + n_buy * bi_bp) / (bi_h + n_buy)
            act_red_bi  = bi_a - new_avg_bi
            req_cap     = n_buy * bi_bp
            buy_amt_bi  = req_cap
            fees_bi     = calc_fees(buy_amt_bi, 0)
            be_sell_bi  = (buy_amt_bi + fees_bi["buy_comm"]) / (n_buy * 0.9987)
            new_total   = bi_h + n_buy

            st.markdown("#### ✅ 核心结果")
            r1, r2, r3, r4 = st.columns(4)
            r1.metric("需买入数量（股）", f"{n_buy:,}", help="已向上取整至整手")
            r2.metric("实际可降成本（元/股）", f"{act_red_bi:.3f}")
            r3.metric("操作后新均价（元）", f"{new_avg_bi:.3f}",
                      delta=f"{(new_avg_bi-bi_a):+.3f}", delta_color="inverse")
            r4.metric("需动用资金（元）", f"{req_cap:,.2f}")

            with st.expander("💰 手续费明细（点击展开）"):
                f1, f2 = st.columns(2)
                f1.metric("买入佣金", f"{fees_bi['buy_comm']:.2f} 元", help="买入金额×万分之三（最低5元）")
                f2.metric("印花税", "0.00 元", help="仅卖出时收取，本次无")
                st.caption(f"买入手续费 {fees_bi['buy_comm']:.2f} 元，"
                           f"实际动用资金 {req_cap+fees_bi['buy_comm']:,.2f} 元（含佣金）。")

            bx1, bx2 = st.columns(2)
            with bx1:
                be_box_sell(be_sell_bi, "保本卖出价（新买入部分）",
                            f"若未来需卖出这 {n_buy:,} 股，至少达到此价格才不亏（含买入佣金{fees_bi['buy_comm']:.2f}元及卖出手续费）。")
            with bx2:
                st.markdown(
                    f'<div class="pnl-card" style="margin-top:10px">'
                    f'<p class="pnl-label">摊薄后新均价 vs 保本卖出价</p>'
                    f'<p class="pnl-value pnl-gray">'
                    f'新均价 {new_avg_bi:.3f} 元　保本价 {be_sell_bi:.3f} 元</p></div>',
                    unsafe_allow_html=True)

            st.success(f"买入 **{n_buy:,} 股**（{bi_bp:.3f} 元），"
                       f"均价从 **{bi_a:.3f}** 降至 **{new_avg_bi:.3f} 元**，"
                       f"实际降低 **{act_red_bi:.3f} 元/股**。")

            st.divider()
            st.markdown("#### ⚠️ 风险提示：买入后若股价继续下跌")
            st.warning(f"买入后总持仓 **{new_total:,} 股**，"
                       f"总市值约 **{new_total*new_avg_bi:,.2f} 元**（按新均价计）。")
            rk1, rk2, rk3 = st.columns(3)
            for col, pct, label in [(rk1,0.03,"跌3%"),(rk2,0.05,"跌5%"),(rk3,0.10,"跌10%")]:
                pnl_card(col, f"较买入价{label}（{bi_bp*(1-pct):.3f}元）新增浮亏",
                         (bi_bp*(1-pct) - bi_bp) * n_buy)

            st.divider()
            save_section("rv_b", "反向计算-买入摊薄", {
                "buy_price":    bi_bp,
                "sell_price":   0.0,
                "quantity":     n_buy,
                "gross_profit": 0.0,
                "total_fee":    round(fees_bi["buy_comm"], 4),
                "net_profit":   0.0,
                "new_avg_cost": round(new_avg_bi, 4),
            })


# ══════════════════════════════════════════════════════════════════════════════
# 历史记录 Tab
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("📋 历史操作记录")

    # ── 顶栏：刷新 + 清空按钮
    h_col, r_col, c_col = st.columns([4, 1, 1])
    with r_col:
        st.button("🔄 刷新", use_container_width=True)
    with c_col:
        if st.button("🗑️ 清空记录", use_container_width=True):
            st.session_state["confirm_clear"] = True

    # ── 二次确认区
    if st.session_state.get("confirm_clear"):
        st.warning("⚠️ 确定要清空所有历史记录吗？此操作不可撤销。")
        yes_col, no_col, _ = st.columns([1, 1, 4])
        with yes_col:
            if st.button("✅ 确认清空", type="primary", use_container_width=True,
                         key="do_clear"):
                ok, err2 = db_clear_all()
                st.session_state["confirm_clear"] = False
                st.session_state["today_count"] = 0
                if ok:
                    st.toast("记录已清空", icon="🗑️")
                else:
                    st.error(f"清空失败：{err2}")
                st.rerun()
        with no_col:
            if st.button("❌ 取消", use_container_width=True, key="cancel_clear"):
                st.session_state["confirm_clear"] = False
                st.rerun()

    records, err = db_load_all()

    if err:
        st.error(f"读取数据失败：{err}")
        st.info("后端服务连接中，请稍候...")
    elif not records:
        st.info("暂无历史记录。完成一次计算后点击「📌 保存本次记录」即可保存。")
    else:
        # ── 统计概览
        total_trades = len(records)
        total_pnl    = sum(r.get("net_profit", 0) or 0 for r in records)
        avg_pnl      = total_pnl / total_trades if total_trades else 0

        s1, s2, s3 = st.columns(3)
        s1.metric("总交易次数", f"{total_trades} 次")
        pnl_card(s2, "累计税后盈利", total_pnl)
        pnl_card(s3, "平均每次盈利", avg_pnl)

        st.divider()

        # ── 过滤
        fc1, fc2 = st.columns(2)
        with fc1:
            filter_type = st.selectbox(
                "筛选类型",
                ["全部"] + sorted(set(r.get("trade_type","") for r in records)),
                key="hist_type")
        with fc2:
            filter_stock = st.text_input("筛选股票名称（留空显示全部）", key="hist_stock")

        filtered = [r for r in records
                    if (filter_type == "全部" or r.get("trade_type") == filter_type)
                    and (not filter_stock or filter_stock in (r.get("stock_name") or ""))]

        st.caption(f"显示 {len(filtered)} / {total_trades} 条记录")
        st.divider()

        # ── 表格显示
        for r in filtered:
            rid       = r.get("id")
            ts        = (r.get("created_at") or "")[:16].replace("T", " ")
            ttype     = r.get("trade_type", "—")
            stock     = r.get("stock_name", "—")
            net       = r.get("net_profit", 0) or 0
            net_color = "#ff4b4b" if net > 0 else ("#21c55d" if net < 0 else "#aaa")
            net_sign  = "+" if net > 0 else ""
            confirm_key = f"confirm_del_{rid}"

            with st.container():
                hd1, hd2, hd3, hd4, hd_del = st.columns([2, 1, 1, 1, 0.4])
                hd1.markdown(f"**{ts}**　`{ttype}`　**{stock}**")
                hd2.markdown(f"买入 **{r.get('buy_price',0):.3f}** 元")
                hd3.markdown(f"卖出 **{r.get('sell_price',0):.3f}** 元")
                hd4.markdown(
                    f'税后盈利：<span style="color:{net_color};font-weight:700">'
                    f'{net_sign}{net:.2f} 元</span>',
                    unsafe_allow_html=True)
                with hd_del:
                    if st.button("🗑️", key=f"del_btn_{rid}",
                                 help="删除这条记录",
                                 use_container_width=True):
                        st.session_state[confirm_key] = True

                # ── 单条二次确认
                if st.session_state.get(confirm_key):
                    st.warning(f"确定删除这条记录吗？（{ts}　{ttype}　{stock}）")
                    yes_c, no_c, _ = st.columns([1, 1, 4])
                    with yes_c:
                        if st.button("✅ 确认删除", type="primary",
                                     use_container_width=True,
                                     key=f"do_del_{rid}"):
                            ok, err_d = db_delete_one(rid)
                            st.session_state.pop(confirm_key, None)
                            if ok:
                                st.toast("记录已删除", icon="🗑️")
                            else:
                                st.error(f"删除失败：{err_d}")
                            st.rerun()
                    with no_c:
                        if st.button("❌ 取消", use_container_width=True,
                                     key=f"cancel_del_{rid}"):
                            st.session_state.pop(confirm_key, None)
                            st.rerun()

                with st.expander("展开详情"):
                    d1, d2, d3, d4, d5 = st.columns(5)
                    d1.metric("数量",     f"{r.get('quantity',0):,} 股")
                    d2.metric("手续费",   f"{r.get('total_fee',0):.2f} 元")
                    d3.metric("毛利润",   f"{r.get('gross_profit',0):+.2f} 元")
                    d4.metric("新均价",   f"{r.get('new_avg_cost',0):.3f} 元")
                    d5.metric("税后盈利", f"{net:+.2f} 元")
                    if r.get("notes"):
                        st.caption(f"备注：{r['notes']}")
                st.divider()


st.caption("本工具仅用于辅助计算，不构成投资建议。佣金按万分之三计算，最低5元/笔；印花税0.1%仅卖出时收取。")
