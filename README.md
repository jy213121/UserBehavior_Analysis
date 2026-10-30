# 电商用户行为分析报告（UserBehavior）

> 以「产出一份电商分析报告」为唯一轴心的 8 周学习计划 · 作品集底座
> 数据：阿里天池 UserBehavior 数据集 **前 10 万行**
> 数据库：本地 **MySQL 8.0**，库名 `user_behavior`

## 三句话读懂这个项目
1. **用了什么数据**：阿里天池 UserBehavior 前 10 万行行为数据（浏览/收藏/加购/购买），经 `LOAD DATA` 入库 MySQL，用 SQL + Python 完成分析。
2. **解决了什么问题**：定位了「浏览→加购」才是转化主漏点（而非收藏），并用 RFM 识别出 13.5% 的高价值核心用户、刻画了周末活跃峰值。
3. **得出了什么可执行的结论**：对「浏览未加购」人群做 48h 加购挽回券、重点维系高价值用户、对 118 名「收藏未购」人群精准发券、大促排期周四~周六——均可 A/B 验证。

## 目录结构
```
UserBehavior_Analysis/
├─ data/UserBehavior_top100k.csv      # 原始数据（已从源目录拷入，作品集自包含）
├─ sql/
│  ├─ 00_setup.sql                    # 建库 + 开启 local_infile
│  ├─ 01_load.sql                     # LOAD DATA 用 SQL 导入（删表/建表/导入/自检）
│  ├─ 02_dau.sql                      # 业务问题①：DAU
│  ├─ 03_conversion_rate.sql          # 业务问题②：浏览→购买转化率
│  ├─ 04_funnel.sql                   # 模块①：原始 4 步漏斗
│  ├─ 04b_funnel_refined.sql          # 模块①：修正版并行路径漏斗
│  ├─ 05_retention.sql                # 模块②：次日/7日留存（cohort）
│  ├─ 06_rfm.sql                      # 模块③：RFM 三层（NTILE）
│  └─ 07_trend.sql                    # 模块④：DAU 时间趋势/星期规律/异常日
├─ week1_notes/指标拆解练习.md         # 前3天任务：支付转化率拆解框架
├─ week1_notes/本周发现与口径提示.md   # 第1周口径坑
├─ week2_notes/
│  ├─ 01_转化漏斗分析.md              # 模块①：收藏非主漏点，真漏点在浏览→加购
│  ├─ 02_留存分析.md                  # 模块②
│  ├─ 03_RFM分析.md                   # 模块③：recency 无方差，「流失」非真流失
│  └─ 04_时间趋势分析.md              # 模块④：周末峰、看密集段
├─ results/                           # 查询结果 CSV（dau/conversion/funnel/retention/rfm/trend）
├─ python/                            # 取数工具 + 三张图脚本 + 报告转HTML
├─ images/                            # funnel.png / rfm_pie.png / dau_trend.png
├─ report/                            # 分析报告.md（2000-3000字）+ 分析报告.html
├─ week4_notes/可视化说明.md          # 第4周：Python 可视化说明
├─ run_mysql.sh                       # 一键跑全部 SQL
├─ db.cnf                             # 本地凭据（已被 .gitignore 忽略，勿提交）
└─ .gitignore
```

## 第1周交付物（已完成）
- ✅ 指标拆解练习：支付转化率掉了 5% 该怎么拆（用户分层 / 渠道 / 时间 / 品类）
- ✅ 用 SQL 把 CSV 导入 MySQL（`LOAD DATA LOCAL INFILE`）
- ✅ 业务问题①：每日独立用户数 DAU
- ✅ 业务问题②：浏览→购买整体转化率（用户口径）

## 第2–3周交付物（SQL 四模块，已完成）
- ✅ 模块①转化漏斗：发现原 4 步顺序不成立（cart 723 > fav 363），拆成
  `pv→cart→buy`(主, 加购→购买 92.81%) 与 `pv→fav→buy`(支, 收藏兑现 73.55%)；
  **真漏点在 浏览→加购(仅 73.78%)**，推翻计划预设的「收藏是主要流失点」。
- ✅ 模块②留存：密集窗口次日留存 73.78%、7日留存 85.99%（高频样本偏高，非全量）。
- ✅ 模块③RFM：高价值 133(13.53%)/一般 523(53.20%)/流失 327(33.27%)；
  ⚠️ recency 近零方差，「流失」层非真流失，仅反映 F 价值梯度。
- ✅ 模块④时间趋势：DAU 11-25 起稳于 700+，周末冲高至 965(12-03 峰)；
  ⚠️ 工作日均值被早期稀疏日拉低，看趋势以密集段为准。

> ⚠️ 贯穿全项目的口径红线：本数据为 user_id 排序前段、约 983 名高频用户，非随机样本；
> 所有「率/留存/流失」均偏高，结论只作趋势参考，不可外推全量。

## 本周关键发现
- 数据覆盖约 **980 名独立用户**，主活跃段 **2017-11-25 ～ 2017-12-03**
- DAU 主窗口 695～965，**周末（11-25 六、12-02 六、12-03 日）明显走高**
- 浏览→购买整体转化率（用户口径）= **68.47%**（买 671 / 浏 980）
- ⚠️ **样本偏差提示**：10 万行是按 user_id 排序的前段，只覆盖最早约 980 名高频用户，
  不是随机样本。68.47% 是这批样本的特征，不能直接代表全量约百万用户。
  这正是第8周面试追问「是否数据口径 / 样本导致」的现成素材。

## 第4周交付物（Python 可视化，已完成）
- ✅ 环境：本机 Anaconda `D:/Users/258/anaconda3/python.exe`（3.13.9，自带 pandas/numpy/matplotlib/seaborn/scipy）
- ✅ `images/funnel.png`：修正版转化漏斗（pv→cart→buy 主路径 + fav 旁路）
- ✅ `images/rfm_pie.png`：RFM 三层环形饼图（已标注「流失层非真流失」口径提醒）
- ✅ `images/dau_trend.png`：DAU 每日走势 + 峰值标注
- ✅ 取数工具 `python/db_query.py`（mysql 客户端直连，`utf8mb4` 解决中文乱码）；三脚本均从 MySQL 实时取数可复现

## 第5–6周交付物（分析报告，已完成）
- ✅ `report/分析报告.md`（2000-3000 字）：业务背景→分析问题→核心发现(漏斗/留存/RFM)→业务建议→策略验证
- ✅ `report/分析报告.html`：同上，排版精美，可浏览器打开/打印 PDF
- 核心结论：主漏点在**浏览→加购(73.8%)**而非收藏；13.5% 高价值用户贡献绝大多数购买；周末活跃峰值

## 第7周交付物（作品集结构，已完成）
- ✅ 本 README 顶部「三句话项目简介」；目录 `sql/ python/ images/ results/ report/ week*_notes/` 齐全
- ✅ `results/电商看板.xlsx`：Excel 看板（概览/漏斗/RFM/DAU/口径说明 5 sheet + 3 图表），BI 能力佐证
- ✅ `db.cnf` 已被 `.gitignore` 忽略，凭据不进仓库

## 第8周交付物（面试准备，已完成）
- ✅ `week8_notes/模拟面试追问.md`：三个核心追问应答稿 + 深圳投递方向（跨境电商/传统企业数字化）

## 如何复现
1. 在项目根目录放 `db.cnf`（格式见 run_mysql.sh 注释，已在 .gitignore 中）
2. 跑 SQL：`bash run_mysql.sh`（Windows 用 Git Bash）
3. 跑可视化：`D:/Users/258/anaconda3/python.exe python/02_funnel_chart.py`（漏斗/RFM/趋势三图同理）
4. 生成报告 HTML：`D:/Users/258/anaconda3/python.exe python/05_report_to_html.py`
5. 生成 Excel 看板：`D:/Users/258/anaconda3/python.exe python/06_excel_dashboard.py`
