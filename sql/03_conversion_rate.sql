-- 03_conversion_rate.sql  —— 第1周业务问题②：浏览 → 购买 整体转化率
-- ----------------------------------------------------------
-- 口径（用户级）：统计周期内「买过的人」 / 「来过的人」
--   分子 = behavior_type='buy'  的去重 user_id
--   分母 = behavior_type='pv'   的去重 user_id
-- 知识点：CTE (WITH ... AS)、CASE WHEN、COUNT(DISTINCT CASE ...)、ROUND
-- ----------------------------------------------------------

USE user_behavior;

WITH uv AS (
    SELECT
        COUNT(DISTINCT CASE WHEN behavior_type = 'pv'  THEN user_id END) AS browse_users,
        COUNT(DISTINCT CASE WHEN behavior_type = 'buy' THEN user_id END) AS buy_users
    FROM user_behavior
)
SELECT
    browse_users,
    buy_users,
    ROUND(buy_users / browse_users, 4) AS conversion_rate
FROM uv;
