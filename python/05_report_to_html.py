# 05_report_to_html.py — 把分析报告.md 转成排版精美的独立 HTML（可浏览器打印为 PDF）
import markdown, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
src = (ROOT / "report" / "分析报告.md").read_text(encoding="utf-8")
body = markdown.markdown(src, extensions=["tables", "fenced_code", "toc"])

CSS = """
* { box-sizing: border-box; }
body { max-width: 880px; margin: 40px auto; padding: 0 28px;
  font-family: "Microsoft YaHei","PingFang SC","Hiragino Sans GB",sans-serif;
  color: #1f2328; line-height: 1.85; font-size: 16px; }
h1 { font-size: 28px; border-bottom: 3px solid #4C72B0; padding-bottom: 10px; }
h2 { font-size: 22px; margin-top: 38px; color: #2c3e50; border-left: 5px solid #4C72B0; padding-left: 12px; }
h3 { font-size: 18px; margin-top: 26px; color: #34495e; }
blockquote { background: #FFF8E1; border-left: 5px solid #F0A500; margin: 18px 0;
  padding: 12px 16px; color: #6b5300; border-radius: 4px; }
table { border-collapse: collapse; width: 100%; margin: 18px 0; font-size: 15px; }
th, td { border: 1px solid #ddd; padding: 9px 12px; text-align: center; }
th { background: #4C72B0; color: #fff; }
tr:nth-child(even) td { background: #f6f8fa; }
strong { color: #c0392b; }
code { background: #f0f0f0; padding: 1px 5px; border-radius: 3px; }
hr { border: none; border-top: 1px solid #eee; margin: 30px 0; }
"""

doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>电商用户行为分析报告</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>"""

out = ROOT / "report" / "分析报告.html"
out.write_text(doc, encoding="utf-8")
print("saved", out)
