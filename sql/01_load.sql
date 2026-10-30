-- 01_load.sql  —— 第1周 · 用 SQL 把 CSV 导入数据库
-- ----------------------------------------------------------
-- LOAD DATA LOCAL INFILE 是 MySQL 原生的「用 SQL 导入文件」方式：
--   - FIELDS TERMINATED BY ','   字段以逗号分隔
--   - LINES TERMINATED BY '\n'   行以换行分隔（本文件是 LF）
--   - 末尾 (...) 显式指定列顺序（CSV 无表头，所以不 IGNORE 1 LINES）
-- 注意：客户端连接时必须带 --local-infile=1
-- ----------------------------------------------------------

USE user_behavior;

DROP TABLE IF EXISTS user_behavior;
CREATE TABLE user_behavior (
    user_id       BIGINT,
    item_id       BIGINT,
    category_id   BIGINT,
    behavior_type VARCHAR(10),
    ts            INT,
    KEY (ts)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

LOAD DATA LOCAL INFILE 'D:/UserBehavior_Analysis/data/UserBehavior_top100k.csv'
INTO TABLE user_behavior
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
(user_id, item_id, category_id, behavior_type, ts);

-- ---------- 自检（sanity check）----------
SELECT COUNT(*) AS total_rows FROM user_behavior;

SELECT behavior_type, COUNT(*) AS cnt
FROM user_behavior
GROUP BY behavior_type
ORDER BY cnt DESC;

SELECT
    MIN(FROM_UNIXTIME(ts)) AS min_ts,
    MAX(FROM_UNIXTIME(ts)) AS max_ts
FROM user_behavior;
