# 02_funnel_chart.py — 转化漏斗图（修正版：pv→cart→buy 主路径 + fav 并行旁路）
# 数据直接来自 MySQL，与第2周 SQL 口径一致。
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query import query
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

IMG = Path(__file__).resolve().parents[1] / "images"
IMG.mkdir(parents=True, exist_ok=True)

# ---- 主路径 + 收藏分支 ----
df = query("""
SELECT
  COUNT(DISTINCT CASE WHEN behavior_type='pv'   THEN user_id END) AS pv,
  COUNT(DISTINCT CASE WHEN behavior_type='cart' THEN user_id END) AS cart,
  COUNT(DISTINCT CASE WHEN behavior_type='buy'  THEN user_id END) AS buy,
  COUNT(DISTINCT CASE WHEN behavior_type='fav'  THEN user_id END) AS fav
FROM user_behavior
""")
pv, cart, buy, fav = [int(df.iloc[0][c]) for c in ["pv", "cart", "buy", "fav"]]

df2 = query("""
SELECT
  COUNT(DISTINCT CASE WHEN behavior_type='fav' AND user_id IN
     (SELECT user_id FROM user_behavior WHERE behavior_type='buy') THEN user_id END) AS fav_and_buy,
  (SELECT COUNT(DISTINCT a.user_id) FROM
     (SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='fav') a
     LEFT JOIN (SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='cart') b
     ON a.user_id=b.user_id WHERE b.user_id IS NULL) AS only_fav_no_cart
FROM user_behavior
""")
fav_and_buy = int(df2.iloc[0]["fav_and_buy"])
only_fav_no_cart = int(df2.iloc[0]["only_fav_no_cart"])

# ---- 画图 ----
fig, ax = plt.subplots(figsize=(9.5, 5.5))
stages = ["浏览\n(pv)", "加购\n(cart)", "购买\n(buy)"]
vals = [pv, cart, buy]
colors = ["#4C72B0", "#55A868", "#C44E52"]
maxv = max(vals)
y = list(range(len(stages)))[::-1]  # 顶部=浏览

for i, (s, v, c) in enumerate(zip(stages, vals, colors)):
    yy = y[i]
    ax.barh(yy, v, left=-v / 2, height=0.58, color=c, edgecolor="white")
    ax.text(0, yy, f"{s}\n{v:,} 人", ha="center", va="center",
            color="white", fontsize=12, fontweight="bold")
    if i < len(stages) - 1:
        conv = vals[i + 1] / vals[i] * 100
        ax.text(v / 2 + maxv * 0.03, (yy + y[i + 1]) / 2,
                f"{conv:.1f}%", ha="left", va="center", fontsize=12, color="#333")

ax.set_xlim(-maxv * 0.62, maxv * 0.62)
ax.set_ylim(-1.7, 2.6)
ax.set_yticks([])
ax.set_xticks([])
for sp in ["top", "right", "bottom", "left"]:
    ax.spines[sp].set_visible(False)

ax.set_title(f"转化漏斗（修正版：pv→cart→buy 主路径）\n整体浏览→购买转化率 {buy / pv * 100:.1f}%",
             fontsize=14, fontweight="bold", pad=12)

note = (f"收藏(fav)为并行旁路：{fav:,} 人收藏，其中 {fav_and_buy:,} 人最终购买"
        f"（兑现率 {fav_and_buy / fav * 100:.1f}%）；\n"
        f"仅收藏未加购的精准可运营人群：{only_fav_no_cart:,} 人。\n"
        f"真正的大漏点在 浏览→加购：仅 {cart / pv * 100:.1f}%（约 {pv - cart:,} 人看了就走）。")
ax.text(0, -1.45, note, ha="center", va="top", fontsize=10.5, color="#555",
        bbox=dict(boxstyle="round,pad=0.5", fc="#F5F5F5", ec="#DDD"))

plt.tight_layout()
out = IMG / "funnel.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out)
