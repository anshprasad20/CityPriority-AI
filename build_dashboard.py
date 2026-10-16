"""Inline dashboard/dash_data.json into the template -> dashboard/citypriority_dashboard.html"""
from datetime import date
from pathlib import Path

VERSION = "1.0.0"   # bump this when you ship a new version

d = Path(__file__).resolve().parent / "dashboard"
html = (d / "dashboard_template.html").read_text(encoding="utf-8")
officer = "data:image/webp;base64," + (d / "officer.b64").read_text().strip()
logo = "data:image/webp;base64," + (d / "logo.b64").read_text().strip()
fav = "data:image/png;base64," + (d / "favicon.b64").read_text().strip()
car = "data:image/webp;base64," + (d / "car.b64").read_text().strip()
chars = (d / "chars.json").read_text().strip()
data = (d / "dash_data.json").read_text(encoding="utf-8").replace("</", "<\\/")
html = html.replace("__LOGO__", logo).replace("__FAVICON__", fav).replace("__CHARS__", chars).replace("__OFFICER__", officer).replace("__CAR__", car).replace("__BUILD_DATE__", date.today().isoformat()).replace("__VERSION__", VERSION)
out = d / "citypriority_dashboard.html"
out.write_text(html.replace("__DATA__", data), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size/1024:.0f} KB) | v{VERSION} | built {date.today().isoformat()}")
