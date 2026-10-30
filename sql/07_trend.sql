-- ============================================================
-- 07_trend.sql  模块④：时间趋势（DAU 走势 / 星期规律 / 异常日）
-- ============================================================
-- DAU = 当日有行为的独立用户数；按日期聚合，并附星期几与周末标记。
-- 用窗口函数标记峰值(MAX)与低谷(MIN)所在日，便于一眼定位异常。
-- GROUP BY 用英文别名（MySQL 对中文别名做 GROUP BY 会报 1064）。
-- ============================================================

USE user_behavior;

-- ① 每日 DAU + 星期 + 周末标记
WITH daily AS (
    SELECT
        DATE(FROM_UNIXTIME(ts)) AS dt,
        COUNT(DISTINCT user_id) AS dau
    FROM user_behavior
    GROUP BY DATE(FROM_UNIXTIME(ts))
)
SELECT
    dt AS date,
    DAYNAME(dt) AS weekday_en,
    CASE WHEN DAYOFWEEK(dt) IN (1,7) THEN '周末' ELSE '工作日' END AS day_type,
    dau AS dau,
    CASE dau WHEN MAX(dau) OVER() THEN '←峰值' ELSE '' END AS flag
FROM daily
ORDER BY dt;

-- ② 周末 vs 工作日 平均 DAU（看周末是否走高）
WITH daily AS (
    SELECT
        DATE(FROM_UNIXTIME(ts)) AS dt,
        COUNT(DISTINCT user_id) AS dau
    FROM user_behavior GROUP BY DATE(FROM_UNIXTIME(ts))
)
SELECT
    CASE WHEN DAYOFWEEK(dt) IN (1,7) THEN '周末' ELSE '工作日' END AS day_type,
    ROUND(AVG(dau), 1) AS avg_dau,
    COUNT(*) AS n_days
FROM daily
GROUP BY day_type;

-- ③ 峰值日与低谷日（仅密集活跃窗口 11-25~12-03，避免早期稀疏日误导）
WITH daily AS (
    SELECT DATE(FROM_UNIXTIME(ts)) AS dt, COUNT(DISTINCT user_id) AS dau
    FROM user_behavior
    WHERE ts >= UNIX_TIMESTAMP('2017-11-25') AND ts < UNIX_TIMESTAMP('2017-12-04')
    GROUP BY DATE(FROM_UNIXTIME(ts))
)
SELECT
    MAX(CASE WHEN dau = (SELECT MAX(dau) FROM daily) THEN dt END) AS peak_date,
    MAX(CASE WHEN dau = (SELECT MAX(dau) FROM daily) THEN dau END) AS peak_dau,
    MAX(CASE WHEN dau = (SELECT MIN(dau) FROM daily) THEN dt END) AS low_date,
    MAX(CASE WHEN dau = (SELECT MIN(dau) FROM daily) THEN dau END) AS low_dau
FROM daily;
