import glob
import subprocess
import json
import os
from datetime import datetime, timezone, timedelta

TW_TZ = timezone(timedelta(hours=8))
TIMESTAMP_FILE = "scripts/timestamps.json"

# 載入已記錄的時間
if os.path.exists(TIMESTAMP_FILE):
    with open(TIMESTAMP_FILE, "r", encoding="utf-8") as f:
        timestamps = json.load(f)
else:
    timestamps = {}

all_files = [f for f in glob.glob("*.html") if f != "index.html"]

def get_first_commit_time(filename):
    result = subprocess.run(
        ["git", "log", "--follow", "--diff-filter=A", "--format=%ct", filename],
        capture_output=True, text=True, encoding="utf-8"
    )
    lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
    # 取最舊那筆（最後一行）
    return int(lines[-1]) if lines else 0

# 只對新檔案記錄時間，舊的不動
changed = False
for f in all_files:
    if f not in timestamps:
        ts = get_first_commit_time(f)
        if ts:
            timestamps[f] = ts
            changed = True

# 儲存更新的時間記錄
if changed:
    with open(TIMESTAMP_FILE, "w", encoding="utf-8") as f:
        json.dump(timestamps, f, ensure_ascii=False, indent=2)

# 生成列表
files_with_time = []
for f in all_files:
    ts = timestamps.get(f, 0)
    dt = datetime.fromtimestamp(ts, tz=TW_TZ) if ts else datetime.min.replace(tzinfo=TW_TZ)
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