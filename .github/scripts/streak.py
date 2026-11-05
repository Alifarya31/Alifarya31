import json
import os
import urllib.request
from datetime import date

USER = os.environ.get("GH_USER", "Alifarya31")
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def fetch_days():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    days.sort(key=lambda d: d["date"])
    return cal["totalContributions"], days


def streaks(days):
    today = date.today().isoformat()
    # longest
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] > 0 else 0
        longest = max(longest, run)
    # current (hari ini yang masih 0 tidak memutus streak)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"] > 0:
            current += 1
        elif i == 0 and d["date"] == today:
            continue
        else:
            break
    return current, longest


def build_svg(total, current, longest):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="495" height="160" viewBox="0 0 495 160">
  <rect x="0.5" y="0.5" width="494" height="159" rx="16" fill="#0F0B1A" stroke="#2A2340"/>
  <g font-family="Segoe UI, Ubuntu, sans-serif" text-anchor="middle">
    <line x1="165" y1="35" x2="165" y2="125" stroke="#3B2350"/>
    <line x1="330" y1="35" x2="330" y2="125" stroke="#3B2350"/>

    <text x="82" y="85" font-size="30" font-weight="700" fill="#FFFFFF">{total}</text>
    <text x="82" y="112" font-size="13" fill="#C9BFE0">Total Contributions</text>
    <text x="82" y="130" font-size="10" fill="#8F84A8">last 12 months</text>

    <circle cx="247" cy="75" r="38" fill="none" stroke="#F75C7E" stroke-width="5"/>
    <text x="247" y="85" font-size="28" font-weight="700" fill="#FFFFFF">{current}</text>
    <text x="247" y="140" font-size="13" font-weight="600" fill="#F75C7E">Current Streak</text>

    <text x="412" y="85" font-size="30" font-weight="700" fill="#FFFFFF">{longest}</text>
    <text x="412" y="112" font-size="13" fill="#C9BFE0">Longest Streak</text>
    <text x="412" y="130" font-size="10" fill="#8F84A8">last 12 months</text>
  </g>
</svg>
"""


if __name__ == "__main__":
    total, days = fetch_days()
    current, longest = streaks(days)
    os.makedirs("assets", exist_ok=True)
    with open("assets/streak.svg", "w", encoding="utf-8") as f:
        f.write(build_svg(total, current, longest))
    print(f"total={total} current={current} longest={longest}")
