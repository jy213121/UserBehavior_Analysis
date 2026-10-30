-- ============================================================
-- 04b_funnel_refined.sql  修正版漏斗：承认 fav/cart 是并行意向行为
-- ============================================================
-- 上文发现 cart(723) > fav(363)，说明用户不按 pv→fav→cart→buy 严格顺序走。
-- 因此把漏斗拆成两条合理的路径：
--   主路径  pv → cart → buy   （加购是主流购买前置动作）
--   支路径  pv → fav → buy     （收藏是低量级旁路）
-- 并交叉统计「只收藏不加购」的群体，作为后续运营建议的精准人群。
-- ============================================================

USE user_behavior;

-- ① 修正主路径漏斗 pv → cart → buy
WITH u AS (
    SELECT
        COUNT(DISTINCT CASE WHEN behavior_type='pv'   THEN user_id END) AS pv,
        COUNT(DISTINCT CASE WHEN behavior_type='cart' THEN user_id END) AS cart,
        COUNT(DISTINCT CASE WHEN behavior_type='buy'  THEN user_id END) AS buy
    FROM user_behavior
)
SELECT
    pv  AS 浏览用户数,
    cart AS 加购用户数,
    buy  AS 购买用户数,
    ROUND(cart/pv*100, 2)   AS 浏览到加购_pct,
    ROUND(buy /cart*100, 2) AS 加购到购买_pct,
    ROUND(buy /pv *100, 2)  AS 整体浏览到购买_pct
FROM u;

-- ② 支路径 pv → fav → buy（收藏人群的真实购买兑现率）
WITH f AS (
    SELECT
        COUNT(DISTINCT CASE WHEN behavior_type='fav' THEN user_id END) AS fav_users,
        COUNT(DISTINCT CASE WHEN behavior_type='fav' AND user_id IN
              (SELECT user_id FROM user_behavior WHERE behavior_type='buy')
              THEN user_id END) AS fav_and_buy
    FROM user_behavior
)
SELECT
    fav_users AS 收藏用户数,
    fav_and_buy AS 收藏且购买用户数,
    ROUND(fav_and_buy/fav_users*100, 2) AS 收藏到购买兑现_pct
FROM f;

-- ③ 精准人群：「只收藏、从未加购」的用户（后续定向优惠券的候选池）
SELECT
    COUNT(DISTINCT a.user_id) AS 只收藏未加购_user数
FROM (
    SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='fav'
) a
LEFT JOIN (
    SELECT DISTINCT user_id FROM user_behavior WHERE behavior_type='cart'
) b ON a.user_id = b.user_id
WHERE b.user_id IS NULL;
