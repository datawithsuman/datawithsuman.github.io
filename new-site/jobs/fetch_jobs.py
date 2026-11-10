"""Collect AI/ML job postings in India from company job boards, for the /jobs/ page.

Reads companies.csv, keeps rows marked Automatic, asks each company's public job-board
API for its postings, keeps India roles with AI/ML titles posted in the last 7 days,
and writes jobs.json next to this file. build.py copies it into the site, and the
daily GitHub Action also writes it straight into docs/jobs/.

Run: python3 new-site/jobs/fetch_jobs.py
"""
import csv, datetime as dt, json, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAYS = 7
NOW = dt.datetime.now(dt.timezone.utc)
UA = {"User-Agent": "aimlrounds-jobs/1.0 (+https://aimlrounds.com/jobs/)", "Accept": "application/json"}

INDIA = re.compile(r"\bindia\b|bengaluru|bangalore|hyderabad|pune|mumbai|gurgaon|gurugram|noida|new delhi|\bdelhi\b|chennai|kolkata|ahmedabad|jaipur|kochi|thiruvananthapuram|trivandrum|coimbatore|indore|chandigarh|vadodara|mysore|mysuru", re.I)
# A title needs an AI/ML subject and a technical role, or one of the scientist titles on its own.
SUBJECT = re.compile(r"machine[- ]learning|\bML\b|\bMLE\b|\bAI\b|\bA\.I\.|artificial intelligence|\bLLMs?\b|gen ?AI|generative|deep learning|computer vision|\bCV\b|\bNLP\b|natural language|speech|\bASR\b|\bTTS\b|recommend|recsys|ranking|personali[sz]ation|\bMLOps\b|LLMOps|perception|foundation model|inference|agentic|\bRAG\b", re.I)
ROLE = re.compile(r"engineer|engineering|scientist|researcher|research|architect|developer|\bSDE\b|\bMLE\b|\bMLOps\b", re.I)
SCIENTIST = re.compile(r"data scien|applied scien|research scien|machine learning scien|\bML scien", re.I)
EXCLUDE = re.compile(r"\bintern(ship)?\b|apprentice|trainee|new grad|graduate|fresher|campus|analyst|\bBI\b|business intelligence|sales|pre-?sales|marketing|account (manager|executive)|customer success|success manager|product manager|program manager|project manager|product design|designer|recruit|talent|business development|counsel|legal|solutions? (engineer|architect|consultant)|support engineer|technical writer|\bQA\b|test engineer|annotat|labell?ing|content|tutor|trainer|writer|expert\b.*\b(freelance|contract)|freelance", re.I)


def is_ai_ml(title):
    if EXCLUDE.search(title):
        return False
    return bool(SCIENTIST.search(title)) or bool(SUBJECT.search(title) and ROLE.search(title))


def get(url, data=None, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**UA, **({"Content-Type": "application/json"} if data else {})})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:
            err = e
            time.sleep(1 + i)
    raise err


def iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


CITIES = {"bengaluru": "Bengaluru", "bangalore": "Bengaluru", "hyderabad": "Hyderabad", "pune": "Pune", "navi mumbai": "Navi Mumbai", "mumbai": "Mumbai",
          "gurgaon": "Gurugram", "gurugram": "Gurugram", "noida": "Noida", "new delhi": "Delhi", "delhi": "Delhi", "chennai": "Chennai", "kolkata": "Kolkata",
          "ahmedabad": "Ahmedabad", "jaipur": "Jaipur", "kochi": "Kochi", "thiruvananthapuram": "Thiruvananthapuram", "trivandrum": "Thiruvananthapuram",
          "coimbatore": "Coimbatore", "indore": "Indore", "chandigarh": "Chandigarh", "vadodara": "Vadodara", "mysore": "Mysuru", "mysuru": "Mysuru"}


def place(location):
    """Short display text: the Indian cities named, else 'India'; remote kept."""
    low = location.lower()
    found = []
    for k, v in CITIES.items():
        if re.search(r"\b" + k + r"\b", low) and v not in found and not (k == "mumbai" and "Navi Mumbai" in found and low.count("mumbai") == 1):
            found.append(v)
    m = re.search(r"(\d+) locations", low)
    text = ", ".join(found[:3]) + (f" +{len(found) - 3}" if len(found) > 3 else "") if found else (f"{m.group(1)} locations in India" if m else "India")
    return text + (" · Remote" if "remote" in low else "")


def job(company, title, location, posted, url):
    return {"title": " ".join(title.split()), "company": company, "location": location.strip(" ,"), "posted": posted, "url": url}


def greenhouse(company, board):
    out = []
    for j in get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs")["jobs"]:
        out.append(job(company, j["title"], (j.get("location") or {}).get("name", ""), iso(j.get("first_published") or j.get("updated_at")), j["absolute_url"]))
    return out


def lever(company, board):
    out = []
    for j in get(f"https://api.lever.co/v0/postings/{board}?mode=json"):
        c = j.get("categories") or {}
        locs = c.get("allLocations") or [c.get("location") or ""]
        out.append(job(company, j["text"], " / ".join(l for l in locs if l), dt.datetime.fromtimestamp(j["createdAt"] / 1000, dt.timezone.utc), j["hostedUrl"]))
    return out


def ashby(company, board):
    out = []
    for j in get(f"https://api.ashbyhq.com/posting-api/job-board/{board}")["jobs"]:
        if j.get("isListed") is False:
            continue
        locs = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        country = ((j.get("address") or {}).get("postalAddress") or {}).get("addressCountry", "")
        loc = " / ".join(dict.fromkeys(l for l in locs if l))
        if country == "India" and not INDIA.search(loc):
            loc += ", India"
        out.append(job(company, j["title"], loc, iso(j.get("publishedAt")), j["jobUrl"]))
    return out


def smartrecruiters(company, board):
    out, offset = [], 0
    while True:
        d = get(f"https://api.smartrecruiters.com/v1/companies/{board}/postings?country=in&limit=100&offset={offset}")
        for j in d["content"]:
            loc = (j.get("location") or {}).get("fullLocation") or "India"
            loc = loc if INDIA.search(loc) else loc + ", India"
            out.append(job(company, j["name"], loc, iso(j.get("releasedDate")), f"https://jobs.smartrecruiters.com/{board}/{j['id']}"))
        offset += 100
        if offset >= d.get("totalFound", 0) or offset >= 1000:
            return out


def workable(company, board):
    out = []
    for j in get(f"https://apply.workable.com/api/v1/widget/accounts/{board}")["jobs"]:
        loc = ", ".join(x for x in [j.get("city"), j.get("country")] if x)
        posted = iso(j.get("published_on"))
        out.append(job(company, j["title"], loc, posted.replace(tzinfo=dt.timezone.utc) if posted else None, j["url"]))
    return out


def workday_age(text):
    t = (text or "").lower()
    if "today" in t:
        return 0
    if "yesterday" in t:
        return 1
    m = re.search(r"(\d+)\+?\s*day", t)
    return int(m.group(1)) if m else None


def workday(company, board):
    tenant, wd, site = board.split("/")
    host = f"https://{tenant}.{wd}.myworkdayjobs.com"
    api = f"{host}/wday/cxs/{tenant}/{site}/jobs"
    first = get(api, json.dumps({"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}).encode())
    # Location facets differ per company, so pick every value that names India or an Indian city.
    facets = {}
    def walk(items):
        for f in items:
            for v in f.get("values", []):
                if "values" in v:
                    walk([v])
                elif INDIA.search(v.get("descriptor", "")) and "indiana" not in v.get("descriptor", "").lower():
                    facets.setdefault(f["facetParameter"], []).append(v["id"])
    walk(first.get("facets", []))
    if not facets:
        return []
    key = next((k for k in facets if "country" in k.lower()), None)
    applied = {key: facets[key]} if key else {k: v for k, v in facets.items() if "location" in k.lower()} or facets
    out, offset, total = [], 0, None
    while total is None or offset < min(total, 1000):
        d = get(api, json.dumps({"appliedFacets": applied, "limit": 20, "offset": offset, "searchText": ""}).encode())
        total = d.get("total", 0) if total is None else total
        posts = d.get("jobPostings", [])
        if not posts:
            break
        for j in posts:
            age = workday_age(j.get("postedOn"))
            posted = NOW - dt.timedelta(days=age) if age is not None else None
            loc = j.get("locationsText", "")
            if not INDIA.search(loc):
                loc = (loc + ", India").strip(", ")  # "2 Locations" and the like, already filtered to India
            out.append(job(company, j["title"], loc, posted, host + f"/{site}" + j["externalPath"]))
        offset += 20
    return out


def oracle(company, board):
    host, site = board.split("/")
    out, offset = [], 0
    while offset < 2000:
        d = get(f"https://{host}.fa.oraclecloud.com/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList"
                f"&finder=findReqs;siteNumber={site},limit=200,offset={offset},sortBy=POSTING_DATES_DESC")
        reqs = d["items"][0]["requisitionList"]
        if not reqs:
            break
        oldest = None
        for j in reqs:
            posted = iso(j.get("PostedDate"))
            posted = posted.replace(tzinfo=dt.timezone.utc) if posted else None
            oldest = posted
            loc = ", ".join(x for x in [j.get("PrimaryLocation"), j.get("PrimaryLocationCountry")] if x)
            out.append(job(company, j["Title"], j.get("PrimaryLocation") or loc, posted,
                           f"https://{host}.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/{site}/job/{j['Id']}"))
        if oldest and (NOW - oldest).days > DAYS:
            break
        offset += 200
    return out


SOURCES = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "smartrecruiters": smartrecruiters,
           "workable": workable, "workday": workday, "oracle": oracle}


def fetch(row):
    try:
        return row, SOURCES[row["source"]](row["company"], row["board_id"]), None
    except Exception as e:
        return row, [], f"{type(e).__name__}: {e}"[:160]


def main():
    rows = [r for r in csv.DictReader(open(HERE / "companies.csv")) if r["how_we_get_jobs"] == "Automatic" and r["source"] in SOURCES]
    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(fetch, rows))
    keep, seen, report = [], set(), []
    for row, jobs, err in results:
        n = 0
        for j in jobs:
            if not j["posted"] or (NOW - j["posted"]).days > DAYS:
                continue
            if not INDIA.search(j["location"]) or not is_ai_ml(j["title"]):
                continue
            k = (j["company"], j["title"].lower())
            if k in seen:
                continue
            seen.add(k)
            keep.append({**j, "location": place(j["location"]), "posted": j["posted"].date().isoformat()})
            n += 1
        report.append(f'{row["company"]:28} {"ERROR " + err if err else f"{len(jobs):4} postings, {n} kept"}')
    keep.sort(key=lambda j: (j["posted"], j["company"]), reverse=True)
    data = {"updated": NOW.date().isoformat(), "days": DAYS, "count": len(keep), "jobs": keep}
    text = json.dumps(data, ensure_ascii=False, indent=1)
    for out in [HERE / "jobs.json"] + [Path(p) for p in sys.argv[1:]]:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    print("\n".join(report))
    print(f"\n{len(keep)} jobs kept from {len(rows)} companies")
    errors = sum(1 for _, _, e in results if e)
    if errors > len(rows) // 3:
        sys.exit(f"{errors} companies failed, not trusting this run")


if __name__ == "__main__":
    main()
