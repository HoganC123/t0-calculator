import akshare as ak
try:
    df = ak.stock_lhb_detail_em(symbol="近一月")
    print("成功！数据行数：", len(df))
    print(df.head(3))
except Exception as e:
    print("失败：", e)
