import glob
import re
from datetime import datetime
from collections import defaultdict

# 掃描兩種格式
base_files = glob.glob("[0-9][0-9][A-Z][a-z][a-z][0-9][0-9][0-9][0-9].html")
extra_files = glob.glob("[0-9][0-9][A-Z][a-z][a-z][0-9][0-9][0-9][0-9]-[0-9]*.html")
all_files = base_files + extra_files

# 按日期分組，用 regex 正確提取日期部分
groups = defaultdict(list)
for f in all_files:
    match = re.match(r"(\d{2}[A-Za-z]{3}\d{4})", f)  # 只取開頭日期
    if match:
        date_key = match.group(1)
        groups[date_key].append(f)

# 按日期排序（最新在前）
sorted_dates = sorted(
    groups.keys(),
    key=lambda d: datetime.strptime(d, "%d%b%Y"),
    reverse=True
)

items = ""
for date_key in sorted_dates:
    try:
        dt = datetime.strptime(date_key, "%d%b%Y")
        date_display = dt.strftime("%A, %B %-d, %Y")
    except:
        date_display = date_key

    # 同一天的檔案按名稱排序（確保 07Apr2026.html 在前，-02 在後）
    files_in_day = sorted(groups[date_key])

    if len(files_in_day) == 1:
        f = files_in_day[0]
        items += f'        <li><a href="{f}">📊 {date_display}</a></li>\n'
    else:
        for i, f in enumerate(files_in_day, 1):
            label = f"📊 {date_display}" if i == 1 else f"📊 {date_display} — Update {i}"
            items += f'        <li><a href="{f}">{label}</a></li>\n'

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Market Analysis</title>
  <style>
    body {{
      font-family: -apple-system, sans-serif;
      max-width: 640px;
      margin: 48px auto;
      padding: 0 24px;
      background: #f9f9f9;
      color: #222;
    }}
    h1 {{ font-size: 1.4rem; margin-bottom: 0.5rem; }}
    p.sub {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    ul {{ list-style: none; padding: 0; }}
    li {{
      background: #fff;
      border: 1px solid #e5e5e5;
      border-radius: 8px;
      margin-bottom: 10px;
    }}
    a {{
      display: block;
      padding: 14px 18px;
      text-decoration: none;
      color: #0969da;
      font-size: 1rem;
    }}
    a:hover {{ background: #f0f7ff; border-radius: 8px; }}
  </style>
</head>
<body>
  <h1>📈 Daily Market Analysis</h1>
  <p class="sub">點擊日期查看當天分析報告</p>
  <ul>
{items}  </ul>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated index.html with {len(all_files)} files across {len(sorted_dates)} days.")