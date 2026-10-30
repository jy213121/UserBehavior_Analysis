# -*- coding: utf-8 -*-
"""
01_import_via_python.py  —— 用 Python「触发」SQL 导入（零安装版）
------------------------------------------------------------------
核心思路：
  Python 标准库不能直接说 MySQL 的网络协议，但可以用 subprocess 调用
  本机已经装好的 mysql.exe，把 LOAD DATA 那条 SQL 喂给它。
  => 底层干活的还是那条 SQL，Python 只是「调度员」。
  => 不需要 pip install 任何包，符合「不擅自装依赖」的约束。

真正的「驱动版」写法（pymysql / sqlalchemy，见下方讲解）需要装包，
那种才像生产环境；本脚本是当下你不用装包就能跑通的等价做法。
"""
import subprocess
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MYSQL = r"D:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"   # 本机 MySQL 客户端
CNF = os.path.join(BASE, "db.cnf")                                 # 凭据（已 gitignore）
SQL = os.path.join(BASE, "sql", "01_load.sql")                    # 里面是 DROP/CREATE/LOAD DATA

cmd = [MYSQL, f"--defaults-extra-file={CNF}", "--local-infile=1"]
with open(SQL, "r", encoding="utf-8") as f:
    proc = subprocess.run(cmd, stdin=f, capture_output=True, text=True)

print(proc.stdout)
if proc.returncode != 0:
    print("STDERR:", proc.stderr)
else:
    print("returncode:", proc.returncode, "(0 = 导入成功)")
