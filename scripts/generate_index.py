import glob
import subprocess
from datetime import datetime, timezone, timedelta

TW_TZ = timezone(timedelta(hours=8))

all_files = [f for f in glob.glob("*.html") if f != "index.html"]

def get_first_commit_time(filename):
    # 用 --follow --diff-filter=A 取得檔案「第一次加入」的時間
    result = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%ct", filename],
        capture_output=True, text=True, encoding="utf-8"
    )
    ts = result.stdout.strip()
    return int(ts) if ts else 0

files_with_time = []
for f in all_files:
    ts = get_first_commit_time(f)
    if ts:
        dt = datetime.fromtimestamp(ts, tz=TW_TZ)
    else:
        dt = datetime.min.replace(tzinfo=TW_TZ)
    files_with_time.append((f, dt))

files_with_time.sort(key=lambda x: x[1], reverse=True)

items = ""
for f, dt in files_with_time:
    name = f.replace(".html", "")
    time_display = dt.strftime("%Y-%m-%d %H:%M (台灣)")
    items += f'        <li><a href="{f}"><span class="name">📄 {name}</span><span class="time">{time_display}</span></a></li>\n'

html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Daily Market Analysis</title>
  <style>
    body {{
      font-family: -apple-system, sans-serif;
      max-width: 680px;
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
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 18px;
      text-decoration: none;
      color: #0969da;
      font-size: 1rem;
    }}
    a:hover {{ background: #f0f7ff; border-radius: 8px; }}
    .time {{
      font-size: 0.8rem;
      color: #999;
      white-space: nowrap;
      margin-left: 12px;
    }}
  </style>
</head>
<body>
  <h1>📈 Daily Market Analysis</h1>
  <p class="sub">最新上傳排列在最上方</p>
  <ul>
{items}  </ul>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as out:
    out.write(html)

print(f"Generated index.html with {len(files_with_time)} files.")