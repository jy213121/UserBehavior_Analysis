#!/usr/bin/env bash
# run_mysql.sh —— 一键按顺序执行第1周全部 SQL（建库 -> 导入 -> 两个业务查询）
# 使用前：在项目根目录放一个 db.cnf（已被 .gitignore 忽略），内容：
#   [client]
#   host=127.0.0.1
#   port=3306
#   user=你的账号
#   password=你的密码
MYSQL="/d/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"

"$MYSQL" --defaults-extra-file=db.cnf --local-infile=1 < sql/00_setup.sql
"$MYSQL" --defaults-extra-file=db.cnf --local-infile=1 < sql/01_load.sql
"$MYSQL" --defaults-extra-file=db.cnf --local-infile=1 < sql/02_dau.sql
"$MYSQL" --defaults-extra-file=db.cnf --local-infile=1 < sql/03_conversion_rate.sql
