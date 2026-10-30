# db_query.py — 用本机 mysql 客户端从 MySQL 取数（零额外依赖，复用 db.cnf）
# 用法：from db_query import query; df = query("SELECT ...")
import subprocess, os
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MYSQL = r"D:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"
CNF = os.path.join(PROJECT_ROOT, "db.cnf")


def query(sql: str) -> pd.DataFrame:
    """执行单条 SELECT，返回 pandas.DataFrame（--batch 输出为制表符分隔）。"""
    cmd = [MYSQL, f"--defaults-extra-file={CNF}", "--local-infile=1",
           "--default-character-set=utf8mb4",
           "--database=user_behavior", "--batch", "-e", sql]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        raise RuntimeError(res.stderr)
    lines = [ln for ln in res.stdout.splitlines() if ln.strip() != ""]
    if len(lines) < 2:
        return pd.DataFrame()
    header = lines[0].split("\t")
    data = [ln.split("\t") for ln in lines[1:]]
    return pd.DataFrame(data, columns=header)
