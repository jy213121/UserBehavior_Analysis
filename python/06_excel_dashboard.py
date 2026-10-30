# 06_excel_dashboard.py — 生成 Excel 简单看板（BI 能力佐证）
# 数据从 MySQL 实时取数（经 db_query），用 openpyxl 写表 + 图表。零安装（Anaconda 自带 openpyxl）。
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query import query
from openpyxl import Workbook
from openpyxl.chart import BarChart, PieChart, LineChart, Reference
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from pathlib import Path

IMG = Path(__file__).resolve().parents[1]
OUT = IMG / "results" / "电商看板.xlsx"

# ---------- 取数 ----------
f = query("""
SELECT
  COUNT(DISTINCT CASE WHEN behavior_type='pv'   THEN user_id END) pv,
  COUNT(DISTINCT CASE WHEN behavior_type='cart' THEN user_id END) cart,
  COUNT(DISTINCT CASE WHEN behavior_type='buy'  THEN user_id END) buy,
  COUNT(DISTINCT CASE WHEN behavior_type='fav'  THEN user_id END) fav
FROM user_behavior
""")
pv, cart, buy, fav = [int(f.iloc[0][c]) for c in ["pv", "cart", "buy", "fav"]]

fb = query("""
SELECT
  COUNT(DISTINCT CASE WHEN behavior_type='fav' AND user_id IN
     (SELECT user_id FROM user_behavior WHERE behavior_type='buy') THEN user_id END) fav_and_buy,
  (SELECT COUNT(DISTINCT a.user_id) FROM
     (SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='fav') a
     LEFT JOIN (SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='cart') b
     ON a.user_id=b.user_id WHERE b.user_id IS NULL) only_fav_no_cart
FROM user_behavior
""")
fav_and_buy = int(fb.iloc[0]["fav_and_buy"])
only_fav_no_cart = int(fb.iloc[0]["only_fav_no_cart"])

rfm = query("""
WITH base AS (
  SELECT user_id,
    DATEDIFF((SELECT DATE(FROM_UNIXTIME(MAX(ts))) FROM user_behavior), DATE(FROM_UNIXTIME(MAX(ts)))) rd,
    SUM(behavior_type='buy') buy_cnt
  FROM user_behavior GROUP BY user_id
),
scored AS (SELECT *, NTILE(3) OVER (ORDER BY rd ASC) r_t, NTILE(3) OVER (ORDER BY buy_cnt DESC) f_t FROM base)
SELECT CASE WHEN r_t=1 AND f_t=1 THEN '高价值' WHEN r_t=3 THEN '流失' ELSE '一般' END seg,
       COUNT(*) n, ROUND(AVG(buy_cnt),1) avg_buy
FROM scored GROUP BY seg
""")
rfm["n"] = rfm["n"].astype(int)
rfm["avg_buy"] = rfm["avg_buy"].astype(float)
rfm["pct"] = (rfm["n"] / rfm["n"].sum() * 100).round(2)

ret = query("""
WITH fd AS (SELECT user_id, DATE(FROM_UNIXTIME(MIN(ts))) d FROM user_behavior GROUP BY user_id),
rd AS (SELECT DISTINCT user_id, DATE(FROM_UNIXTIME(ts)) d FROM user_behavior),
co AS (SELECT f.user_id, f.d,
  MAX(CASE WHEN r.d=DATE_ADD(f.d,INTERVAL 1 DAY) THEN 1 ELSE 0 END) r1,
  MAX(CASE WHEN r.d=DATE_ADD(f.d,INTERVAL 7 DAY) THEN 1 ELSE 0 END) r7
  FROM fd f LEFT JOIN rd r ON f.user_id=r.user_id GROUP BY f.user_id)
SELECT ROUND(AVG(r1)*100,2) d1, ROUND(AVG(r7)*100,2) d7
FROM co WHERE d BETWEEN '2017-11-25' AND '2017-12-02'
""")
d1, d7 = float(ret.iloc[0]["d1"]), float(ret.iloc[0]["d7"])

trend = query("""
SELECT DATE(FROM_UNIXTIME(ts)) dt, COUNT(DISTINCT user_id) dau
FROM user_behavior WHERE ts >= UNIX_TIMESTAMP('2017-11-25')
GROUP BY DATE(FROM_UNIXTIME(ts)) ORDER BY dt
""")
trend["dt"] = trend["dt"].astype(str)
trend["dau"] = trend["dau"].astype(int)

# ---------- 写表 ----------
wb = Workbook()
HEAD = Font(bold=True, color="FFFFFF", size=11)
HFILL = PatternFill("solid", fgColor="4C72B0")
TITLE = Font(bold=True, size=14, color="2c3e50")
thin = Side(style="thin", color="DDDDDD")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEAD
        cell.fill = HFILL
        cell.alignment = Alignment(horizontal="center")


# Sheet1 概览
ws = wb.active
ws.title = "概览"
ws["A1"] = "UserBehavior 电商分析看板（关键指标）"
ws["A1"].font = TITLE
rows = [
    ["指标", "数值", "说明"],
    ["整体 浏览→购买（用户口径）", f"{buy/pv*100:.2f}%", f"购买 {buy} / 浏览 {pv}"],
    ["主漏点 浏览→加购", f"{cart/pv*100:.2f}%", f"约 {pv-cart} 人看了就走"],
    ["加购→购买", f"{buy/cart*100:.2f}%", "购物车环节健康"],
    ["收藏兑现率", f"{fav_and_buy/fav*100:.2f}%", f"收藏 {fav} 人中 {fav_and_buy} 人购买"],
    ["仅收藏未加购（精准人群）", only_fav_no_cart, "可做定向券"],
    ["次日留存（密集窗口）", f"{d1:.2f}%", "高频样本偏高"],
    ["7日留存（密集窗口）", f"{d7:.2f}%", "高频样本偏高"],
    ["高价值用户占比", f"{rfm.loc[rfm.seg=='高价值','pct'].iloc[0]:.2f}%", "应优先维系"],
    ["峰值 DAU", 965, "2017-12-03（周日）"],
]
for i, r in enumerate(rows, start=3):
    for j, v in enumerate(r, start=1):
        ws.cell(row=i, column=j, value=v).border = BORDER
style_header(ws, 3, 3)
ws.column_dimensions["A"].width = 28
ws.column_dimensions["B"].width = 14
ws.column_dimensions["C"].width = 40

# Sheet2 转化漏斗
ws2 = wb.create_sheet("转化漏斗")
ws2["A1"] = "转化漏斗（修正版：pv→cart→buy 主路径）"
ws2["A1"].font = TITLE
hdr = ["环节", "独立用户数", "占浏览比", "逐段转化"]
data = [
    ["浏览 pv", pv, "100%", "—"],
    ["加购 cart", cart, f"{cart/pv*100:.2f}%", f"浏览→加购 {cart/pv*100:.2f}%"],
    ["购买 buy", buy, f"{buy/pv*100:.2f}%", f"加购→购买 {buy/cart*100:.2f}%"],
    ["收藏 fav（并行旁路）", fav, f"{fav/pv*100:.2f}%", f"收藏兑现 {fav_and_buy/fav*100:.2f}%"],
]
ws2.append([])
for j, h in enumerate(hdr, 1):
    ws2.cell(row=3, column=j, value=h)
style_header(ws2, 3, 4)
for i, r in enumerate(data, start=4):
    for j, v in enumerate(r, 1):
        ws2.cell(row=i, column=j, value=v).border = BORDER
for col, w in zip("ABCD", [22, 14, 12, 26]):
    ws2.column_dimensions[col].width = w
chart = BarChart()
chart.type = "bar"
chart.title = "转化漏斗（主路径 pv→cart→buy）"
chart.height = 7
chart.width = 14
dref = Reference(ws2, min_col=2, min_row=4, max_row=6)
cref = Reference(ws2, min_col=1, min_row=4, max_row=6)
chart.add_data(dref, titles_from_data=False)
chart.set_categories(cref)
chart.legend = None
ws2.add_chart(chart, "F3")

# Sheet3 RFM
ws3 = wb.create_sheet("RFM分层")
ws3["A1"] = "RFM 用户分层"
ws3["A1"].font = TITLE
hdr3 = ["分层", "用户数", "占比%", "人均购买"]
for j, h in enumerate(hdr3, 1):
    ws3.cell(row=3, column=j, value=h)
style_header(ws3, 3, 4)
for i, (_, r) in enumerate(rfm.iterrows(), start=4):
    ws3.cell(row=i, column=1, value=r["seg"]).border = BORDER
    ws3.cell(row=i, column=2, value=int(r["n"])).border = BORDER
    ws3.cell(row=i, column=3, value=float(r["pct"])).border = BORDER
    ws3.cell(row=i, column=4, value=float(r["avg_buy"])).border = BORDER
for col, w in zip("ABCD", [14, 12, 12, 12]):
    ws3.column_dimensions[col].width = w
pie = PieChart()
pie.title = "RFM 用户分层占比"
pie.height = 7
pie.width = 11
labels = Reference(ws3, min_col=1, min_row=4, max_row=6)
vals = Reference(ws3, min_col=2, min_row=4, max_row=6)
pie.add_data(vals, titles_from_data=False)
pie.set_categories(labels)
ws3.add_chart(pie, "F3")

# Sheet4 DAU趋势
ws4 = wb.create_sheet("DAU趋势")
ws4["A1"] = "DAU 每日走势（密集窗口 11-25 起）"
ws4["A1"].font = TITLE
ws4.cell(row=3, column=1, value="日期")
ws4.cell(row=3, column=2, value="DAU")
style_header(ws4, 3, 2)
for i, (_, r) in enumerate(trend.iterrows(), start=4):
    ws4.cell(row=i, column=1, value=r["dt"]).border = BORDER
    ws4.cell(row=i, column=2, value=int(r["dau"])).border = BORDER
ws4.column_dimensions["A"].width = 14
ws4.column_dimensions["B"].width = 10
line = LineChart()
line.title = "DAU 走势"
line.height = 7
line.width = 16
ldata = Reference(ws4, min_col=2, min_row=4, max_row=3 + len(trend))
lcats = Reference(ws4, min_col=1, min_row=4, max_row=3 + len(trend))
line.add_data(ldata, titles_from_data=False)
line.set_categories(lcats)
ws4.add_chart(line, "D3")

# Sheet5 口径说明
ws5 = wb.create_sheet("口径说明")
ws5["A1"] = "口径与局限（面试必读）"
ws5["A1"].font = TITLE
notes = [
    "1. 样本为按 user_id 升序前 10 万行，仅约 983 名高频用户，非随机样本；所有率/留存/流失均偏高，不可外推全量。",
    "2. 漏斗顺序已验证：加购(723)>收藏(363)，故拆为 pv→cart→buy 主路径与 pv→fav→buy 旁路，原 4 步顺序不成立。",
    "3. RFM 无金额字段，仅做 R+F；recency 近零方差，「流失」层为活跃人群内相对后排，非真实流失。",
    "4. 留存为高频样本，且 11-27~29 入队 7 日留存=0 是数据截止边界效应，非真实流失。",
    "5. 趋势看密集窗口(11-25 起)；早期个位数 DAU 为样本截断所致。",
]
for i, n in enumerate(notes, start=3):
    ws5.cell(row=i, column=1, value=n)
ws5.column_dimensions["A"].width = 100

wb.save(OUT)
print("saved", OUT)
