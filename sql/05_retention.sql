-- ============================================================
-- 05_retention.sql  模块②：用户留存（次日 / 7日）
-- ============================================================
-- 口径：以「首次活跃日」为队列基准（cohort）。
--   次日留存 = 首次活跃日 D 的用户中，D+1 也活跃的比例
--   7日留存  = 首次活跃日 D 的用户中，D+7 也活跃的比例
-- 用 LEFT JOIN 命中返回日，MAX(CASE...) 标记是否回归，AVG 得留存率。
-- 注意：数据密集段在 11-25~12-03，末段队列(D+1/D+7 超出数据范围)自然记为0，解读时看密集段。
-- ============================================================

USE user_behavior;

WITH first_day AS (
    SELECT user_id, DATE(FROM_UNIXTIME(MIN(ts))) AS fd
    FROM user_behavior GROUP BY user_id
),
return_days AS (
    SELECT DISTINCT user_id, DATE(FROM_UNIXTIME(ts)) AS d
    FROM user_behavior
),
cohort AS (
    SELECT
        f.user_id, f.fd,
        MAX(CASE WHEN r.d = DATE_ADD(f.fd, INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS ret_1,
        MAX(CASE WHEN r.d = DATE_ADD(f.fd, INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS ret_7
    FROM first_day f
    LEFT JOIN return_days r ON f.user_id = r.user_id
    GROUP BY f.user_id, f.fd
)
SELECT
    fd AS 首次活跃日,
    COUNT(*) AS 队列用户数,
    ROUND(AVG(ret_1)*100, 2) AS 次日留存_pct,
    ROUND(AVG(ret_7)*100, 2) AS 七日留存_pct
FROM cohort
GROUP BY fd
ORDER BY fd;

-- 整体口径（只看数据密集窗口 11-25 ~ 12-02 的队列，避免末段无后续数据干扰）
-- 用子查询限定 fd 在密集段内再平均
WITH first_day AS (
    SELECT user_id, DATE(FROM_UNIXTIME(MIN(ts))) AS fd
    FROM user_behavior GROUP BY user_id
),
return_days AS (
    SELECT DISTINCT user_id, DATE(FROM_UNIXTIME(ts)) AS d FROM user_behavior
),
cohort AS (
    SELECT f.user_id, f.fd,
        MAX(CASE WHEN r.d = DATE_ADD(f.fd, INTERVAL 1 DAY) THEN 1 ELSE 0 END) AS ret_1,
        MAX(CASE WHEN r.d = DATE_ADD(f.fd, INTERVAL 7 DAY) THEN 1 ELSE 0 END) AS ret_7
    FROM first_day f LEFT JOIN return_days r ON f.user_id = r.user_id
    GROUP BY f.user_id, f.fd
)
SELECT
    '密集窗口整体(11-25~12-02队列)' AS 口径,
    ROUND(AVG(ret_1)*100, 2) AS 次日留存_pct,
    ROUND(AVG(ret_7)*100, 2) AS 七日留存_pct
FROM cohort
WHERE fd BETWEEN '2017-11-25' AND '2017-12-02';
