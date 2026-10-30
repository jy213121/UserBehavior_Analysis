-- ============================================================
-- 06_rfm.sql  模块③：RFM 用户分层（高价值 / 一般 / 流失）
-- ============================================================
-- 数据无金额(price/amount)字段，故只做 R(近度) + F(频度)，不做 M。
--   R：最近一次行为距数据最大日的天数（越小越近 → 越好）
--   F：购买次数 buy_cnt（越大 → 越好）
-- 用 NTILE(3) 把 R、F 各分成 3 档(1=最优,3=最差)。
-- 分层规则（可解释、非均分硬切）：
--   高价值 = R 最近档 且 F 最高档（既活跃又爱买）
--   流失   = R 最久档（长期没来）
--   一般   = 其余
-- 注意：GROUP BY 必须用英文别名（MySQL 对中文别名做 GROUP BY 会报 1064）。
-- ============================================================

USE user_behavior;

WITH base AS (
    SELECT
        user_id,
        DATEDIFF(
            (SELECT DATE(FROM_UNIXTIME(MAX(ts))) FROM user_behavior),
            DATE(FROM_UNIXTIME(MAX(ts)))
        ) AS recency_days,
        COUNT(*) AS total_behaviors,
        SUM(behavior_type = 'buy') AS buy_cnt
    FROM user_behavior
    GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(3) OVER (ORDER BY recency_days ASC)  AS r_tier,  -- 1=最近
        NTILE(3) OVER (ORDER BY buy_cnt DESC)      AS f_tier   -- 1=购买最多
    FROM base
)
SELECT
    CASE
        WHEN r_tier = 1 AND f_tier = 1 THEN '高价值'
        WHEN r_tier = 3 THEN '流失'
        ELSE '一般'
    END AS segment,
    COUNT(*) AS user_cnt,
    ROUND(AVG(recency_days), 1) AS avg_recency_days,
    ROUND(AVG(buy_cnt), 1) AS avg_buy_cnt
FROM scored
GROUP BY segment
ORDER BY FIELD(segment, '高价值', '一般', '流失');

-- 补充：各层在总用户中的占比与人均行为量，供报告用
WITH base AS (
    SELECT user_id,
        DATEDIFF((SELECT DATE(FROM_UNIXTIME(MAX(ts))) FROM user_behavior),
                 DATE(FROM_UNIXTIME(MAX(ts)))) AS recency_days,
        COUNT(*) AS total_behaviors,
        SUM(behavior_type = 'buy') AS buy_cnt
    FROM user_behavior GROUP BY user_id
),
scored AS (
    SELECT *,
        NTILE(3) OVER (ORDER BY recency_days ASC) AS r_tier,
        NTILE(3) OVER (ORDER BY buy_cnt DESC)     AS f_tier
    FROM base
)
SELECT
    CASE
        WHEN r_tier = 1 AND f_tier = 1 THEN '高价值'
        WHEN r_tier = 3 THEN '流失'
        ELSE '一般'
    END AS segment,
    COUNT(*) AS user_cnt,
    ROUND(COUNT(*)/SUM(COUNT(*)) OVER()*100, 2) AS pct,
    ROUND(AVG(total_behaviors), 1) AS avg_total_behaviors
FROM scored
GROUP BY segment
ORDER BY FIELD(segment, '高价值', '一般', '流失');
