import streamlit as st
import sqlite3
from datetime import date
from pathlib import Path

st.set_page_config(page_title="A股 T+0 辅助计算器", layout="wide")

# ── 样式 ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stMetricDelta"] > div[style*="color: rgb(9, 171, 59)"],
[data-testid="stMetricDelta"] > div[style*="color: rgb(14, 203, 129)"] { color:#ff4b4b !important; }
[data-testid="stMetricDelta"] > div[style*="color: rgb(255, 43, 43)"],
[data-testid="stMetricDelta"] > div[style*="color: rgb(255, 75, 75)"]  { color:#21c55d !important; }

.pnl-card  { background:rgba(255,255,255,0.04); border-radius:8px; padding:12px 16px; margin-bottom:4px; }
.pnl-label { font-size:0.82rem; color:rgba(250,250,250,0.55); margin:0 0 3px 0; }
.pnl-value { font-size:1.55rem; font-weight:700; margin:0; }
.pnl-red   { color:#ff4b4b; }
.pnl-green { color:#21c55d; }
.pnl-gray  { color:rgba(250,250,250,0.7); }

.be-box     { border:2px solid #ff4b4b; border-radius:8px; padding:14px 18px; margin:10px 0; }
.be-box-buy { border:2px solid #21c55d; border-radius:8px; padding:14px 18px; margin:10px 0; }
.be-title         { font-size:0.82rem; color:rgba(250,250,250,0.55); margin:0 0 3px 0; }
.be-price-red     { font-size:1.8rem; font-weight:800; color:#ff4b4b; margin:0; }
.be-price-green   { font-size:1.8rem; font-weight:800; color:#21c55d; margin:0; }
.be-note          { font-size:0.78rem; color:rgba(250,250,250,0.45); margin:4px 0 0 0; }

.save-bar { background:rgba(255,255,255,0.03); border-radius:8px; padding:14px 16px; margin-top:12px; }

@media (max-width:640px) {
    [data-testid="column"] { min-width:100% !important; flex:1 1 100% !important; }
    .stTabs [data-baseweb="tab"] { font-size:13px !important; padding:6px 10px !important; }
    [data-testid="stMetricValue"] { font-size:1.3rem !important; }
    .pnl-value { font-size:1.25rem !important; }
    .be-price-red, .be-price-green { font-size:1.4rem !important; }
    h1 { font-size:1.35rem !important; }
}
</style>
""", unsafe_allow_html=True)

st.title("📊 A股 T+0 辅助计算器")


# ══════════════════════════════════════════════════════════════════════════════
# SQLite 本地存储
# ══════════════════════════════════════════════════════════════════════════════
DB_PATH = Path(__file__).parent / "trading.db"

def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row   # 让结果可按列名访问
    return conn

def _init_db():
    with _conn() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS trade_records (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                trade_type   TEXT,
                stock_name   TEXT,
                buy_price    REAL,
                sell_price   REAL,
                quantity     INTEGER,
                gross_profit REAL,
                total_fee    REAL,
                net_profit   REAL,
                new_avg_cost REAL,
                notes        TEXT
            )
        """)
        c.commit()

_init_db()   # 启动时建表，已存在则跳过


def db_insert(row: dict) -> tuple[bool, str]:
    """写入 trade_records，返回 (成功, 错误信息)"""
    try:
        cols   = ", ".join(row.keys())
        marks  = ", ".join("?" * len(row))
        with _conn() as c:
            c.execute(f"INSERT INTO trade_records ({cols}) VALUES ({marks})",
                      list(row.values()))
            c.commit()
        return True, ""
    except Exception as e:
        return False, str(e)


def db_load_all() -> tuple[list, str]:
    """读取全部记录（按时间倒序），返回 (records, 错误信息)"""
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT * FROM trade_records ORDER BY created_at DESC"
            ).fetchall()
        return [dict(r) for r in rows], ""
    except Exception as e:
        return [], str(e)


# ══════════════════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════════════════
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
    sc1, sc2, sc3 = st.columns([2, 2, 1])
    with sc1:
        stock = st.text_input("股票名称",    placeholder="如：宁德时代",
                              key=f"{key_prefix}_stock")
    with sc2:
        notes = st.text_input("备注（可选）", placeholder="如：早盘高开，快进快出",
                              key=f"{key_prefix}_notes")
    with sc3:
        st.markdown("<br>", unsafe_allow_html=True)
        clicked = st.button("📌 保存本次记录", key=f"{key_prefix}_save",
                            use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        row = {
            "trade_type":  trade_type,
            "stock_name":  stock.strip() or "未填写",
            "notes":       notes.strip(),
            **base_row,
        }
        ok, err = db_insert(row)
        if ok:
            st.toast("✅ 已保存到本地数据库", icon="📌")
            # 同步侧边栏计数
            st.session_state.setdefault("today_count", 0)
            st.session_state["today_count"] += 1
        else:
            st.error(f"保存失败：{err}")


# ── 侧边栏 ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("📋 操作记录")
    today_count = st.session_state.get("today_count", 0)
    if today_count == 0:
        st.caption("今天还没有记录。\n计算完成后点击「📌 保存本次记录」。")
    else:
        st.success(f"今日已保存 **{today_count}** 次记录")
    st.divider()
    st.caption("完整历史请查看「历史记录」Tab。")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab3, tab1, tab2, tab4 = st.tabs(["正T", "反T", "反向计算", "📋 历史记录"])


# ══════════════════════════════════════════════════════════════════════════════
# 正T（机动仓做T：先买后卖）
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("输入区")
    c1, c2, c3 = st.columns(3)
    with c1:
        jd_holding  = st.number_input("原有持仓数量（股）",     min_value=0,    value=10000, step=100,   key="jd_h")
        jd_avg_cost = st.number_input("原有持仓均价/成本（元）", min_value=0.01, value=10.00, step=0.01,  format="%.3f", key="jd_a")
    with c2:
        jd_funds  = st.number_input("机动仓可用资金（元）", min_value=0.0,  value=50000.0, step=1000.0, format="%.2f", key="jd_f")
        jd_buy_px = st.number_input("计划买入价格（元）",   min_value=0.01, value=9.70,   step=0.01,   format="%.3f", key="jd_bp")
    with c3:
        jd_sell_px  = st.number_input("计划卖出价格（元）", min_value=0.01, value=10.00, step=0.01, format="%.3f", key="jd_sp")
        max_by_fund = int(jd_funds // jd_buy_px // 100) * 100
        jd_buy_qty  = st.number_input(
            f"买入数量（股，资金上限 {max_by_fund:,} 股）",
            min_value=0, max_value=max(max_by_fund, 0),
            value=min(1000, max_by_fund), step=100, key="jd_q")

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
        holding_qty = st.number_input("当前持仓数量（股）", min_value=0, value=10000, step=100)
        avg_cost    = st.number_input("持仓均价/成本（元）", min_value=0.0, value=10.00, step=0.01, format="%.3f")
        sell_qty    = st.number_input("计划卖出数量（股）",  min_value=0, value=1000, step=100)
    with col2:
        sell_price       = st.number_input("卖出价格（元）",           min_value=0.0, value=10.50, step=0.01, format="%.3f")
        target_rebuy     = st.number_input("目标回补价格（元，可选）", min_value=0.0, value=10.00, step=0.01, format="%.3f")
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
        res2.metric("若不回补：持仓均价",
                    f"{avg_cost:.3f}" if remaining_qty > 0 else "—（全部卖出）")
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
            cost_up = sell_qty * (sell_price - avg_cost) / remaining_qty
            ca, cb  = st.columns(2)
            ca.metric("失去的筹码（股）", f"{sell_qty:,}")
            cb.metric("剩余持仓成本抬高（元/股）", f"{cost_up:.3f}",
                      delta=f"{cost_up:+.3f}", delta_color="inverse")

        if use_target_rebuy:
            st.divider()
            st.markdown("#### ✅ 回补后综合成本")
            new_avg_t1 = (target_rebuy if remaining_qty == 0
                          else (remaining_qty * avg_cost + sell_qty * target_rebuy) / holding_qty)
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
            rv_h = st.number_input("当前持仓（股）", min_value=1,    value=10000, step=100,  key="rv_h")
            rv_a = st.number_input("当前均价（元）", min_value=0.01, value=10.00, step=0.01, format="%.3f", key="rv_a")
        with c2:
            rv_r = st.number_input("目标降低成本（元/股）", min_value=0.001, value=0.10, step=0.01, format="%.3f", key="rv_r")
            rv_b = st.number_input("计划回补价格（元）",    min_value=0.01,  value=9.80, step=0.01, format="%.3f", key="rv_b")
        with c3:
            rv_sp = st.number_input("卖出价格（元）", min_value=0.01, value=10.50, step=0.01, format="%.3f", key="rv_sp")

        st.divider()
        gap = rv_a - rv_b
        if gap <= 0:
            st.error("回补价格必须低于当前均价，否则操作会抬高成本。")
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
            bi_h = st.number_input("当前持仓数量（股）", min_value=1,    value=10000, step=100,  key="bi_h")
            bi_a = st.number_input("当前持仓均价（元）", min_value=0.01, value=10.00, step=0.01, format="%.3f", key="bi_a")
        with c2:
            bi_r  = st.number_input("目标成本降低幅度（元/股）", min_value=0.001, value=0.20, step=0.01, format="%.3f", key="bi_r")
            bi_bp = st.number_input("计划买入价格（元）",        min_value=0.01,  value=9.50, step=0.01, format="%.3f", key="bi_bp")

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

    h_col, r_col = st.columns([5, 1])
    with r_col:
        refresh = st.button("🔄 刷新", use_container_width=True)

    records, err = db_load_all()

    if err:
        st.error(f"读取数据失败：{err}")
        st.info(f"数据库路径：{DB_PATH}")
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
            ts        = (r.get("created_at") or "")[:16].replace("T", " ")
            ttype     = r.get("trade_type", "—")
            stock     = r.get("stock_name", "—")
            net       = r.get("net_profit", 0) or 0
            net_color = "#ff4b4b" if net > 0 else ("#21c55d" if net < 0 else "#aaa")
            net_sign  = "+" if net > 0 else ""

            with st.container():
                hd1, hd2, hd3, hd4 = st.columns([2, 1, 1, 1])
                hd1.markdown(f"**{ts}**　`{ttype}`　**{stock}**")
                hd2.markdown(f"买入 **{r.get('buy_price',0):.3f}** 元")
                hd3.markdown(f"卖出 **{r.get('sell_price',0):.3f}** 元")
                hd4.markdown(
                    f'税后盈利：<span style="color:{net_color};font-weight:700">'
                    f'{net_sign}{net:.2f} 元</span>',
                    unsafe_allow_html=True)

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
