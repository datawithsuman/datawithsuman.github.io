"""Fetch pending interview experiences and send back clean-up decisions (used by the 7 AM Claude routine).

    python3 bot.py pull                 # prints pending posts as JSON
    python3 bot.py push decisions.json  # sends [{id, action, role?, family?, body?, note?}, ...]

Needs EXP_BOT_TOKEN. EXP_API defaults to https://experiences.aimlrounds.com/.
"""
import json
import os
import sys
import urllib.request

API = os.environ.get("EXP_API", "https://experiences.aimlrounds.com/")
TOKEN = os.environ.get("EXP_BOT_TOKEN", "")


def call(path, data=None):
    req = urllib.request.Request(API + path, method="POST" if data is not None else "GET",
                                 data=json.dumps(data).encode() if data is not None else None,
                                 headers={"authorization": f"Bearer {TOKEN}", "content-type": "application/json",
                                          "user-agent": "aimlrounds-cleanup/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "error": e.read().decode()[:200]}


def main():
    if not TOKEN:
        sys.exit("EXP_BOT_TOKEN is not set")
    if len(sys.argv) >= 2 and sys.argv[1] == "pull":
        print(json.dumps(call("bot/pending"), ensure_ascii=False, indent=1))
    elif len(sys.argv) == 3 and sys.argv[1] == "push":
        decisions = json.load(open(sys.argv[2]))
        done = {"publish": 0, "reject": 0, "hold": 0, "failed": 0}
        for d in decisions:
            res = call("bot/decide", d)
            if res.get("ok"):
                done[d["action"]] += 1
            else:
                done["failed"] += 1
                print(f"post {d.get('id')}: {res}", file=sys.stderr)
        print(json.dumps(done))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
