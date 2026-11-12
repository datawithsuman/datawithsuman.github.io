"""Collect AI/ML job postings in India from company job boards, for the /jobs/ page.

Reads companies.csv, keeps rows marked Automatic, asks each company's public job-board
API for its postings, keeps India roles with AI/ML titles posted in the last 7 days,
and writes jobs.json next to this file. build.py copies it into the site, and the
daily GitHub Action also writes it straight into docs/jobs/.

Run: python3 new-site/jobs/fetch_jobs.py
"""
import csv, datetime as dt, html, json, re, sys, time, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
DAYS = 7
NOW = dt.datetime.now(dt.timezone.utc)
UA = {"User-Agent": "aimlrounds-jobs/1.0 (+https://aimlrounds.com/jobs/)", "Accept": "application/json"}

INDIA = re.compile(r"\bindia\b|bengaluru|bangalore|hyderabad|pune|mumbai|gurgaon|gurugram|noida|new delhi|\bdelhi\b|chennai|kolkata|ahmedabad|jaipur|kochi|thiruvananthapuram|trivandrum|coimbatore|indore|chandigarh|vadodara|mysore|mysuru", re.I)
# A title must name one of the agreed role types. "AI" added to a normal software title does not count.
ROLE_NOUN = r"(?:engineers?|developers?|architects?|scientists?|researchers?|specialists?|leads?)"
FAMILIES = {
    # AI, GenAI and LLM engineers, applied AI engineers, AI architects: the AI words sit right before the role.
    "AI Engineering": re.compile(r"\b(?:gen ?ai|generative ai|applied ai|agentic ai|conversational ai|ai/ml|ml/ai|ai agents?|ai|llms?)\b(?:[\s/&,-]+[\w.]+){0,3}?[\s/,-]+" + ROLE_NOUN + r"\b", re.I),
    # ML engineers, MLOps, ML platform and infrastructure ("AI/ML" in a list of skills does not count).
    "ML Engineering": re.compile(r"machine[- ]learning|deep learning|(?<!AI/)\bML\b|\bMLE\b|\bMLOps\b|\bLLMOps\b|model (?:serving|inference|training|optimi[sz]ation)", re.I),
    "Data Science": re.compile(r"data scien", re.I),
    "Research": re.compile(r"research scien|applied scien|research engineer|(?:ai|ml|machine learning) research", re.I),
    "Specialist ML": re.compile(r"computer vision|\bNLP\b|natural language|speech|\bASR\b|recommend|recsys|personali[sz]ation|perception", re.I),
}
NEEDS_ROLE = {"ML Engineering", "Specialist ML"}  # these subjects also need an engineer/scientist-type word in the title
ROLE = re.compile(r"engineer|scientist|researcher|architect|developer|\bSDE\b|\bMLE\b|\bMLOps\b|\bLLMOps\b", re.I)
EXCLUDE = re.compile(r"\bintern(ship)?\b|apprentice|trainee|new grad|graduate|fresher|campus|analyst|\bBI\b|business intelligence|sales|pre-?sales|marketing|account (manager|executive)|customer success|success (manager|architect)|product manager|program manager|project manager|product design|designer|recruit|talent|business development|counsel|legal|solutions? (engineer|architect|consultant)|support engineer|customer engineer|technical writer|\bQA\b|test engineer|annotat|labell?ing|content|tutor|trainer|writer|freelance|consultant|automation|procurement|operational excellence", re.I)


def family(title):
    if EXCLUDE.search(title):
        return None
    for name, pat in FAMILIES.items():
        if pat.search(title) and (name not in NEEDS_ROLE or ROLE.search(title)):
            return name
    return None


def is_ai_ml(title):
    return family(title) is not None


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
            if not j.get("title") or not j.get("externalPath"):
                continue  # Workday sometimes returns a stub row with no title
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
    host = host if "." in host else f"{host}.fa.oraclecloud.com"  # some tenants live on a regional host such as x.fa.em2.oraclecloud.com
    out, offset = [], 0
    while offset < 2000:
        d = get(f"https://{host}/hcmRestApi/resources/latest/recruitingCEJobRequisitions?onlyData=true&expand=requisitionList"
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
                           f"https://{host}/hcmUI/CandidateExperience/en/sites/{site}/job/{j['Id']}"))
        if oldest and (NOW - oldest).days > DAYS:
            break
        offset += 200
    return out


# Big tech: their own careers sites. Each has a search, so ask for the AI/ML role words and
# filter the answers the same way as everyone else. Requests are spaced out to be polite.
QUERIES = ["machine learning", "data scientist", "applied scientist", "research scientist", "AI engineer",
           "LLM", "generative AI", "deep learning", "computer vision", "MLOps", "NLP", "speech", "recommendation"]


def get_text(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA["User-Agent"]}), timeout=30) as r:
                return r.read().decode("utf8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 3:
                raise
            time.sleep(15 * (i + 1))


def slow_json(url):
    for i in range(4):
        try:
            return get(url, tries=1)
        except urllib.error.HTTPError as e:
            if e.code != 429 or i == 3:
                raise
            time.sleep(15 * (i + 1))


def amazon(company, board):
    out = []
    for q in QUERIES:
        d = slow_json("https://www.amazon.jobs/en/search.json?" + urllib.parse.urlencode(
            {"base_query": q, "country": "IND", "result_limit": 100, "sort": "recent"}))
        for j in d.get("jobs", []):
            posted = dt.datetime.strptime(" ".join(j["posted_date"].split()), "%B %d, %Y").replace(tzinfo=dt.timezone.utc)
            out.append(job(company, j["title"], j.get("normalized_location") or j.get("location") or "India", posted, "https://www.amazon.jobs" + j["job_path"]))
        time.sleep(1)
    return out


def microsoft(company, board):
    out = []
    for q in QUERIES:
        for start in (0, 10, 20):
            try:
                d = slow_json("https://apply.careers.microsoft.com/api/pcsx/search?" + urllib.parse.urlencode(
                    {"domain": "microsoft.com", "query": q, "location": "India", "start": start, "sort_by": "timestamp"}))
            except urllib.error.HTTPError as e:
                if e.code == 429 and out:  # rate-limited late in the run: keep what we already have
                    return out
                raise
            posts = d["data"]["positions"]
            for j in posts:
                posted = dt.datetime.fromtimestamp(j["postedTs"], dt.timezone.utc)
                out.append(job(company, j["name"], " / ".join(j.get("locations") or []), posted, "https://apply.careers.microsoft.com" + j["positionUrl"]))
            time.sleep(5)
            if len(posts) < 10 or (posts and (NOW - dt.datetime.fromtimestamp(posts[-1]["postedTs"], dt.timezone.utc)).days > DAYS):
                break
    return out


def google(company, board):
    out = []
    def strings(o):
        if isinstance(o, str):
            yield o
        elif isinstance(o, list):
            for x in o:
                yield from strings(x)
    for q in QUERIES:
        for page in (1, 2):
            h = get_text("https://www.google.com/about/careers/applications/jobs/results?" + urllib.parse.urlencode(
                {"q": q, "location": "India", "sort_by": "date", "page": page}))
            m = re.search(r"AF_initDataCallback\(\{key: 'ds:1', hash: '\d+', data:(.*?), sideChannel", h, re.S)
            rows = (json.loads(m.group(1))[0] or []) if m else []
            for j in rows:
                ts = [x[0] for x in j if isinstance(x, list) and len(x) == 2 and isinstance(x[0], int) and x[0] > 1.6e9]
                locs = [x for x in strings(j[3:]) if INDIA.search(x) and len(x) < 80]
                if ts and locs:
                    out.append(job(company, j[1], " / ".join(dict.fromkeys(locs)), dt.datetime.fromtimestamp(ts[0], dt.timezone.utc),
                                   f"https://www.google.com/about/careers/applications/jobs/results/{j[0]}"))
            time.sleep(2)
            if len(rows) < 20 or (rows and ts and (NOW - dt.datetime.fromtimestamp(ts[0], dt.timezone.utc)).days > DAYS):
                break
    return out


def apple(company, board):
    """Apple's search ignores keywords from scripts, so read every India posting (about 100) and filter here."""
    out = []
    for page in range(1, 15):
        h = get_text(f"https://jobs.apple.com/en-in/search?sort=newest&location=india-INDC&page={page}")
        m = re.search(r'window.__staticRouterHydrationData = JSON.parse\("(.*?)"\);', h, re.S)
        if not m:
            break
        data = json.loads(json.loads('"' + m.group(1) + '"'))
        def find(o):
            if isinstance(o, dict):
                if "searchResults" in o:
                    return o["searchResults"]
                o = list(o.values())
            if isinstance(o, list):
                for v in o:
                    r = find(v)
                    if r is not None:
                        return r
        rows = find(data) or []
        for j in rows:
            posted = dt.datetime.strptime(j["postingDate"].replace("Sept", "Sep"), "%d %b %Y").replace(tzinfo=dt.timezone.utc)
            locs = " / ".join(l.get("name", "") for l in j.get("locations", [])) or "India"
            out.append(job(company, j["postingTitle"], locs if INDIA.search(locs) else locs + ", India", posted,
                           f"https://jobs.apple.com/en-in/details/{j['positionId']}/{j.get('transformedPostingTitle', '')}"))
        time.sleep(2)
        if len(rows) < 20:
            break
    return out



def eightfold(company, board):
    """Eightfold career sites (board = host/domain). Searches the AI/ML words, India only."""
    host, domain = board.split("/")
    out, seen = [], set()
    for q in QUERIES:
        for start in range(0, 100, 10):
            d = slow_json(f"https://{host}/api/pcsx/search?" + urllib.parse.urlencode({"domain": domain, "query": q, "location": "India", "start": start}))
            pos = (d.get("data") or {}).get("positions") or []
            for j in pos:
                if j["id"] in seen:
                    continue
                seen.add(j["id"])
                ts = j.get("postedTs") or j.get("creationTs")
                out.append(job(company, j["name"], " / ".join(j.get("locations") or []) or "India",
                               dt.datetime.fromtimestamp(ts, dt.timezone.utc) if ts else None, f"https://{host}/careers/job/{j['id']}"))
            if len(pos) < 10:
                break
    return out


def jibe(company, board):
    """Jibe (iCIMS) career sites such as jobs.zs.com, newest first, India only."""
    out = []
    for page in range(1, 11):
        d = get(f"https://{board}/api/jobs?" + urllib.parse.urlencode({"page": page, "limit": 100, "location": "India", "sortBy": "posted_date", "descending": "true", "internal": "false"}))
        rows = d.get("jobs") or []
        for r in rows:
            j = r["data"]
            out.append(job(company, j["title"], j.get("full_location") or j.get("city") or "India", iso(j.get("posted_date")), f"https://{board}/jobs/{j['slug']}"))
        if len(rows) < 100 or (out[-1]["posted"] and (NOW - out[-1]["posted"]).days > DAYS):
            break
    return out


def successfactors(company, board):
    """SuccessFactors career sites (board = host/path, e.g. careers.ey.com/ey). The search list has no dates,
    so it searches the AI/ML words in India and reads the date from each matching job's page."""
    base = "https://" + board.rstrip("/")
    host = "https://" + board.split("/")[0]
    out, seen = [], set()
    for q in QUERIES:
        for start in range(0, 100, 25):
            h = get_text(f"{base}/search/?" + urllib.parse.urlencode({"q": q, "locationsearch": "India", "startrow": start, "sortColumn": "referencedate", "sortDirection": "desc"}))
            rows = re.findall(r'<tr class="data-row">(.*?)</tr>', h, re.S)
            for r in rows:
                m = re.search(r'href="([^"]+)" class="jobTitle-link">([^<]+)<', r)
                loc = re.search(r'class="jobLocation">\s*([^<]+?)\s*<', r)
                if not m or m.group(1) in seen:
                    continue
                seen.add(m.group(1))
                title, loc = html.unescape(m.group(2).strip()), (loc.group(1) if loc else "India")
                loc = loc if INDIA.search(loc) else loc + ", India"
                posted = None
                if is_ai_ml(title):
                    p = re.search(r'itemprop="datePosted" content="([^"]+)"', get_text(host + m.group(1)))
                    if p:
                        posted = dt.datetime.strptime(p.group(1).replace(" UTC", ""), "%a %b %d %H:%M:%S %Y").replace(tzinfo=dt.timezone.utc)
                out.append(job(company, title, loc, posted, host + html.unescape(m.group(1))))
            if len(rows) < 25:
                break
    return out


def radancy(company, board):
    """Radancy (TalentBrew) career sites such as careers.unitedhealthgroup.com. Searches the AI/ML words,
    keeps Indian locations, and reads the posting date from each matching job's page."""
    out, seen = [], set()
    for q in QUERIES:
        d = get(f"https://{board}/search-jobs/results?" + urllib.parse.urlencode({
            "ActiveFacetID": 0, "CurrentPage": 1, "RecordsPerPage": 250, "Distance": 50, "RadiusUnitType": 0, "Keywords": q,
            "Location": "India", "ShowRadius": "False", "IsPagination": "False", "SearchResultsModuleName": "Search Results",
            "SearchFiltersModuleName": "Search Filters", "SortCriteria": 0, "SortDirection": 0, "SearchType": 5}))
        for path, title, loc in re.findall(r'<a href="(/job/[^"]+)"[^>]*>\s*<div>\s*<h2>([^<]+)</h2>.*?job-location[^>]*>([^<]+)<', d.get("results", ""), re.S):
            title, loc = html.unescape(title.strip()), html.unescape(loc.strip())
            if path in seen or not INDIA.search(loc) or not is_ai_ml(title):
                continue
            seen.add(path)
            p = re.search(r'"datePosted"\s*:\s*"(\d{4}-\d{2}-\d{2})', get_text(f"https://{board}{path}"))
            posted = dt.datetime.fromisoformat(p.group(1)).replace(tzinfo=dt.timezone.utc) if p else None
            out.append(job(company, title, loc + ", India", posted, f"https://{board}{path}"))
    return out


def eightfold_v2(company, board):
    """Older Eightfold career sites (board = host/domain), e.g. HSBC. India only, newest first."""
    host, domain = board.split("/")
    out, seen = [], set()
    for q in QUERIES:
        for start in range(0, 100, 10):
            d = slow_json(f"https://{host}/api/apply/v2/jobs?" + urllib.parse.urlencode({"domain": domain, "query": q, "location": "India", "start": start, "num": 10}))
            pos = d.get("positions") or []
            for j in pos:
                if j["id"] in seen:
                    continue
                seen.add(j["id"])
                ts = j.get("t_create") or j.get("t_update")
                out.append(job(company, j["name"], j.get("location") or "India", dt.datetime.fromtimestamp(ts, dt.timezone.utc) if ts else None,
                               j.get("canonicalPositionUrl") or f"https://{host}/careers/job/{j['id']}"))
            if len(pos) < 10:
                break
    return out


def atlassian(company, board):
    """Atlassian publishes every open role as one JSON list."""
    out = []
    for j in get("https://www.atlassian.com/endpoint/careers/listings"):
        loc = " / ".join(l for l in j.get("locations", []) if INDIA.search(l)) or " / ".join(j.get("locations", []))
        upd = (j.get("portalJobPost") or {}).get("updatedDate")
        posted = dt.datetime.strptime(upd, "%Y-%m-%d %I:%M %p").replace(tzinfo=dt.timezone.utc) if upd else None
        out.append(job(company, j["title"], loc, posted, j.get("applyUrl") or (j.get("portalJobPost") or {}).get("portalUrl", "")))
    return out


def bofa(company, board):
    """Bank of America's own job search, India only."""
    out = []
    for start in range(0, 2000, 200):
        d = get("https://careers.bankofamerica.com/services/jobssearchservlet?" + urllib.parse.urlencode({"start": start, "rows": 200, "search": "jobsByLocation", "searchstring": "India"}))
        rows = d.get("jobsList") or []
        for j in rows:
            loc = j.get("location") or j.get("additionalLocationsList") or "India"
            loc = loc if INDIA.search(loc) else loc + ", India"
            posted = dt.datetime.strptime(j["postedDate"], "%m/%d/%Y").replace(tzinfo=dt.timezone.utc) if j.get("postedDate") else None
            out.append(job(company, j["postingTitle"], loc, posted, "https://careers.bankofamerica.com" + j["jcrURL"]))
        if len(rows) < 200:
            break
    return out


def goldman(company, board):
    """Goldman Sachs careers (higher.gs.com) role search, India only."""
    q = "query GetRoles($s: RoleSearchQueryInput!) { roleSearch(searchQueryInput: $s) { totalCount items { roleId jobTitle createdDate locations { city state country } externalSource { sourceId } } } }"
    out = []
    for page in range(0, 20):
        v = {"s": {"page": {"pageSize": 50, "pageNumber": page}, "sort": {"sortStrategy": "POSTED_DATE", "sortOrder": "DESC"},
                   "filters": [{"filterCategoryType": "LOCATION", "filters": [{"filter": "India", "subFilters": []}]}],
                   "experiences": ["EARLY_CAREER", "PROFESSIONAL"], "searchTerm": ""}}
        d = get("https://api-higher.gs.com/gateway/api/v1/graphql", json.dumps({"query": q, "variables": v}).encode())["data"]["roleSearch"]
        for j in d["items"]:
            loc = " / ".join(f'{l["city"]}, {l["country"]}' for l in j["locations"] if l.get("country") == "India" and l.get("city")) or "India"
            out.append(job(company, j["jobTitle"], loc, iso(j.get("createdDate")), f"https://higher.gs.com/roles/{(j.get('externalSource') or {}).get('sourceId') or j['roleId']}"))
        if len(d["items"]) < 50:
            break
    return out


def mercedes(company, board):
    """Mercedes-Benz jobs API, India only (country code 390), newest first."""
    out = []
    for first in range(1, 2001, 100):
        q = {"SearchParameters": {"FirstItem": first, "CountItem": 100, "Sort": [{"Criterion": "PublicationStartDate", "Direction": "DESC"}],
                                  "MatchedObjectDescriptor": ["PositionID", "PositionTitle", "PositionURI", "PositionLocation.CityName", "PositionLocation.CountryName", "PublicationStartDate"]},
             "SearchCriteria": [{"CriterionName": "PositionLocation.Country", "CriterionValue": [390]}], "LanguageCode": "EN"}
        r = get("https://jobs.api.mercedes-benz.com/search?data=" + urllib.parse.quote(json.dumps(q, separators=(",", ":"))))["SearchResult"]
        for it in r["SearchResultItems"]:
            j = it["MatchedObjectDescriptor"]
            loc = ", ".join(dict.fromkeys(l.get("CityName", "") for l in j.get("PositionLocation", []) if l.get("CityName"))) + ", India"
            p = j.get("PublicationStartDate")
            out.append(job(company, j["PositionTitle"], loc.strip(", "), dt.datetime.fromisoformat(p).replace(tzinfo=dt.timezone.utc) if p else None, j["PositionURI"]))
        if len(r["SearchResultItems"]) < 100:
            break
    return out


def juspay(company, board):
    """Juspay's job list. It has no posting dates; main() dates each job by when we first saw it."""
    d = get("https://joinus.juspay.in/api/careerJobOpening?limit=1000")
    return [job(company, j["job_title"], j.get("job_location") or "", None, f"https://juspay.io/careers/{j['job_id']}")
            for j in d.get("allJobs", []) if j.get("opening_status", True)]


def ripplehire(company, board):
    """RippleHire career sites (board = subdomain/token), e.g. Tredence. No posting dates; dated by first sighting."""
    sub, token = board.split("/")
    out = []
    for page in range(0, 20):
        params = json.dumps({"page": page, "search": "*:*", "token": token, "source": "CAREERSITE", "pagesize": 100})
        req = urllib.request.Request(f"https://{sub}.ripplehire.com/candidate/candidatejobsearch",
                                     data=urllib.parse.urlencode({"careerSiteUrlParams": params, "lang": "en"}).encode(),
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded"})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        rows = d.get("jobVoList") or []
        for j in rows:
            out.append(job(company, j["jobTitle"], j.get("locations") or "", None,
                           f"https://{sub}.ripplehire.com/candidate/?token={token}&source=CAREERSITE#detail/job/{j['jobId']}"))
        if len(rows) < 100:
            break
    return out


SOURCES = {"greenhouse": greenhouse, "lever": lever, "ashby": ashby, "smartrecruiters": smartrecruiters,
           "workable": workable, "workday": workday, "oracle": oracle,
           "amazon": amazon, "microsoft": microsoft, "google": google, "apple": apple,
           "eightfold": eightfold, "jibe": jibe, "successfactors": successfactors, "radancy": radancy,
           "eightfold_v2": eightfold_v2, "atlassian": atlassian, "bofa": bofa, "goldman": goldman,
           "mercedes": mercedes, "juspay": juspay, "ripplehire": ripplehire}


def fetch(row):
    try:
        return row, SOURCES[row["source"]](row["company"], row["board_id"]), None
    except Exception as e:
        return row, [], f"{type(e).__name__}: {e}"[:160]


def main():
    rows = [r for r in csv.DictReader(open(HERE / "companies.csv")) if r["how_we_get_jobs"] == "Automatic" and r["source"] in SOURCES]
    with ThreadPoolExecutor(12) as ex:
        results = list(ex.map(fetch, rows))
    # Some boards give no posting date. Date those jobs by the day we first saw them (kept in seen.json);
    # the first time a company is read, its existing jobs count as old so the backlog doesn't flood the page.
    seen_path = HERE / "seen.json"
    first_seen = json.loads(seen_path.read_text()) if seen_path.exists() else {}
    today = NOW.date().isoformat()
    for row, jobs, err in results:
        undated = [j for j in jobs if j["posted"] is None]
        if not undated or err:
            continue
        known = any(k.startswith(row["company"] + "|") for k in first_seen)
        for j in undated:
            key = row["company"] + "|" + j["url"]
            first_seen.setdefault(key, today if known else "2000-01-01")
            j["posted"] = dt.datetime.fromisoformat(first_seen[key]).replace(tzinfo=dt.timezone.utc)
    seen_path.write_text(json.dumps(dict(sorted(first_seen.items())), indent=0))
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
