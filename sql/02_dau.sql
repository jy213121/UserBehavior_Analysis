-- 02_dau.sql  —— 第1周业务问题①：每天有多少独立用户（DAU）
-- ----------------------------------------------------------
-- DAU = Daily Active Users = 每个自然日去重的 user_id 数量
-- 时间戳 ts 是 Unix 秒，用 FROM_UNIXTIME(ts) 转成时间，再 DATE() 取日期
-- 知识点：SELECT / GROUP BY / COUNT(DISTINCT ...) / 日期函数 FROM_UNIXTIME
-- ----------------------------------------------------------

USE user_behavior;

SELECT
    DATE(FROM_UNIXTIME(ts))     AS dt,
    COUNT(DISTINCT user_id)     AS dau
FROM user_behavior
GROUP BY DATE(FROM_UNIXTIME(ts))
ORDER BY dt;
