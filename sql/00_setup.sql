-- 00_setup.sql  —— 第1周 · 建库 + 开启本地导入
-- ----------------------------------------------------------
-- 1) 建库（UTF8MB4，中文/emoji 安全）
-- 2) 开启 LOAD DATA LOCAL INFILE（仅拥有 SUPER 权限的账号能 SET GLOBAL）
-- 3) 切换到业务库
-- 知识点：CREATE DATABASE / SET GLOBAL / USE
-- ----------------------------------------------------------

CREATE DATABASE IF NOT EXISTS user_behavior
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

SET GLOBAL local_infile = 1;

USE user_behavior;
