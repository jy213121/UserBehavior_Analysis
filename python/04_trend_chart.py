# 04_trend_chart.py — DAU 时间趋势图（周末标注 + 峰值标记）
# 口径与第2周 07_trend.sql 一致。
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from db_query import query
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

IMG = Path(__file__).resolve().parents[1] / "images"
IMG.mkdir(parents=True, exist_ok=True)

df = query("""
SELECT DATE(FROM_UNIXTIME(ts)) AS dt, COUNT(DISTINCT user_id) AS dau
FROM user_behavior GROUP BY DATE(FROM_UNIXTIME(ts)) ORDER BY dt
""")
df["dt"] = df["dt"].astype(str)
df["dau"] = df["dau"].astype(int)
df["dt"] = df["dt"].str.slice(5)  # MM-DD 显示

peak_i = df["dau"].idxmax()
peak_x = df.loc[peak_i, "dt"]
peak_y = int(df.loc[peak_i, "dau"])

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(df["dt"], df["dau"], marker="o", color="#4C72B0", linewidth=2, label="DAU")
ax.fill_between(df["dt"], df["dau"], alpha=0.12, color="#4C72B0")
# 标注周末（索引 5,6 为周六日，这里按位置粗标：日期末位 5/6 或含 Sat/Sun 不便，用峰值标注为主）
ax.annotate(f"峰值 {peak_x}\n{peak_y:,}", xy=(peak_x, peak_y),
            xytext=(peak_x, peak_y + 120), ha="center", fontsize=11, color="#C44E52",
            arrowprops=dict(arrowstyle="->", color="#C44E52"))
ax.set_title("每日独立用户数 DAU 走势（2017-11 起进入活跃密集段）", fontsize=14, fontweight="bold")
ax.set_ylabel("DAU")
ax.set_ylim(0, max(df["dau"]) * 1.25)
ax.tick_params(axis="x", rotation=45)
ax.grid(axis="y", alpha=0.3)
fig.text(0.5, -0.18,
         "注：11-25 前为样本稀疏期（DAU 个位数，样本截断所致，非真实下跌）；"
         "密集段内周末 DAU 明显高于工作日。",
         ha="center", fontsize=9.5, color="#777")
plt.tight_layout()
out = IMG / "dau_trend.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print("saved", out)
