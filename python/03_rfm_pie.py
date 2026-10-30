# 03_rfm_pie.py — RFM 用户分层饼图（高价值 / 一般 / 流失）
# 口径与第2周 06_rfm.sql 一致（R近度+F频度，无金额字段故不做 M）。
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

df = query("""
WITH base AS (
  SELECT user_id,
    DATEDIFF((SELECT DATE(FROM_UNIXTIME(MAX(ts))) FROM user_behavior),
             DATE(FROM_UNIXTIME(MAX(ts)))) AS recency_days,
    SUM(behavior_type='buy') AS buy_cnt
  FROM user_behavior GROUP BY user_id
),
scored AS (
  SELECT *, NTILE(3) OVER (ORDER BY recency_days ASC) r_tier,
            NTILE(3) OVER (ORDER BY buy_cnt DESC) f_tier
  FROM base
)
SELECT CASE WHEN r_tier=1 AND f_tier=1 THEN '高价值'
            WHEN r_tier=3 THEN '流失' ELSE '一般' END AS segment,
       COUNT(*) AS user_cnt
FROM scored GROUP BY segment
""")
df["user_cnt"] = df["user_cnt"].astype(int)
order = ["高价值", "一般", "流失"]
df["segment"] = df["segment"].astype("category")
df["segment"] = df["segment"].cat.set_categories(order)
df = df.sort_values("segment")

sizes = df["user_cnt"].tolist()
labels = [f"{s}\n{n:,}人" for s, n in zip(df["segment"], sizes)]
colors = ["#C44E52", "#4C72B0", "#8C8C8C"]
total = sum(sizes)

fig, ax = plt.subplots(figsize=(8, 6))
wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                   counterclock=False, wedgeprops=dict(width=0.42, edgecolor="white"))
ax.legend(wedges, [f"{s}：{n:,}人（{n/total*100:.1f}%）" for s, n in zip(df["segment"], sizes)],
          loc="center", fontsize=11, frameon=False)
ax.set_title("RFM 用户分层（按购买频次 F 的价值梯度）\n"
             "高价值 13.5% 贡献绝大多数购买行为", fontsize=14, fontweight="bold")
ax.text(0, -1.35,
        "口径提醒：样本为高频用户且窗口仅约9天，recency 近零方差，\n"
        "「流失」层为活跃人群内的相对后排，非真实流失用户。",
        ha="center", va="top", fontsize=10, color="#C0392B")
plt.tight_layout()
out = IMG / "rfm_pie.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out)
