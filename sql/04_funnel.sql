-- ============================================================
-- 04_funnel.sql  模块①：转化漏斗 (pv → fav → cart → buy)
-- ============================================================
-- 口径说明（务必先读，这是面试追问的素材）：
--   1.「每一步的用户数」= 至少发生过该行为的【独立用户数】(COUNT DISTINCT user_id)。
--   2.电商里用户不一定严格按 pv→fav→cart→buy 顺序走，可能「看了直接买」「加购不收藏」。
--     因此逐段转化率(fav→cart、cart→buy)是"做过上一步的人里有多少也做了下一步"，
--     不是严格互斥的因果漏斗，解读时要加这句 caveat（见 本周笔记）。
--   3.本数据集是按 user_id 排序取的前段，仅覆盖约 983 名高频用户，非随机样本。
-- ============================================================

USE user_behavior;

-- ① 漏斗主体：各行为环节独立用户数 + 逐段/整体转化率
WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN behavior_type = 'pv'   THEN user_id END) AS uv_pv,
        COUNT(DISTINCT CASE WHEN behavior_type = 'fav'  THEN user_id END) AS uv_fav,
        COUNT(DISTINCT CASE WHEN behavior_type = 'cart' THEN user_id END) AS uv_cart,
        COUNT(DISTINCT CASE WHEN behavior_type = 'buy'  THEN user_id END) AS uv_buy
    FROM user_behavior
)
SELECT
    uv_pv  AS pv浏览用户数,
    uv_fav AS fav收藏用户数,
    uv_cart AS cart加购用户数,
    uv_buy AS buy购买用户数,
    ROUND(uv_fav  / uv_pv  * 100, 2) AS 浏览到收藏_pct,
    ROUND(uv_cart / uv_fav * 100, 2) AS 收藏到加购_pct,
    ROUND(uv_buy  / uv_cart * 100, 2) AS 加购到购买_pct,
    ROUND(uv_buy  / uv_pv  * 100, 2) AS 整体_浏览到购买_pct
FROM funnel;

-- ② 行为次数漏斗（参考用：看总事件量，而非去重人数）
SELECT
    SUM(behavior_type = 'pv')   AS pv次数,
    SUM(behavior_type = 'fav')  AS fav次数,
    SUM(behavior_type = 'cart') AS cart次数,
    SUM(behavior_type = 'buy')  AS buy次数
FROM user_behavior;
