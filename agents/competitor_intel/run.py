#!/usr/bin/env python3
"""
Agent 3 — Competitor Intel runner.

Takes the value propositions Agent 2 produced, searches the Meta (Facebook/
Instagram) Ad Library via the Apify actor `curious_coder/facebook-ads-library-scraper`,
keeps the long-running "winning" ads, downloads a still for each, and
**vision-classifies every downloaded creative** (real visual_style from the image,
plus hook/offer/cta/niche-relevance). Aggregates the winning patterns and writes
an Agent-4-ready report.

Market: US only (Canada intentionally left out for now).

Pipeline:
  marketing_<slug>.json → search seeds → Apify Ad Library (US) → winners (>N days)
  → download stills → OpenAI vision classify → patterns → data + report

Usage:
  python agents/competitor_intel/run.py outputs/analysis/marketing_100plus...json
  python agents/competitor_intel/run.py <marketing.json> --count 40 --max-queries 6 --top 20
  python agents/competitor_intel/run.py <marketing.json> --dry-run     # show plan + projected charge

Env: APIFY_TOKEN (or APIFY_API_TOKEN), OPENAI_API_KEY  (read from .env)
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# macOS framework Python ships without usable system CAs → use certifi's bundle.
try:
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:  # noqa: BLE001
    _SSL_CTX = ssl.create_default_context()

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = REPO_ROOT / "outputs" / "competitor_intel"
ACTOR_ID = "curious_coder~facebook-ads-library-scraper"
WINNER_DAYS = 14
DEFAULT_VISION_MODEL = "gpt-4o-mini"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"


# ---------------------------------------------------------------------------
# env / http
# ---------------------------------------------------------------------------
def load_env() -> None:
    envp = REPO_ROOT / ".env"
    if envp.exists():
        for line in envp.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def _http_json(method: str, url: str, payload: Optional[dict] = None, timeout: int = 60) -> Any:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
        return json.loads(r.read().decode())


# ---------------------------------------------------------------------------
# Apify
# ---------------------------------------------------------------------------
def build_ads_url(query: str, country: str = "US") -> str:
    params = {
        "active_status": "active",
        "ad_type": "all",
        "country": country,
        "q": query,
        "search_type": "keyword_unordered",
        "media_type": "all",
    }
    return "https://www.facebook.com/ads/library/?" + urllib.parse.urlencode(params)


def apify_collect(token: str, urls: List[str], count: int, max_wait: int = 420) -> List[Dict]:
    """Start the actor (async), poll, return dataset items. Aborts if it overruns."""
    body = {
        "urls": [{"url": u} for u in urls],
        "count": count,
        "scrapeAdDetails": True,
    }
    run = _http_json("POST", f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs?token={token}", body)
    run_id = run["data"]["id"]
    ds_id = run["data"]["defaultDatasetId"]
    print(f"  apify run {run_id} started (count={count}, urls={len(urls)})")
    deadline = time.time() + max_wait
    while time.time() < deadline:
        time.sleep(6)
        st = _http_json("GET", f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}")
        status = st["data"]["status"]
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            print(f"  apify run {status}")
            break
    else:
        print("  ⏹ apify run overran budget → aborting")
        try:
            _http_json("POST", f"https://api.apify.com/v2/actor-runs/{run_id}/abort?token={token}")
        except Exception:
            pass
    items = _http_json(
        "GET", f"https://api.apify.com/v2/datasets/{ds_id}/items?token={token}&clean=true", timeout=120
    )
    return items if isinstance(items, list) else []


# ---------------------------------------------------------------------------
# normalize / filter
# ---------------------------------------------------------------------------
def _text(v: Any) -> str:
    if isinstance(v, dict):
        return str(v.get("text") or "")
    if v in (None, "None"):
        return ""
    return str(v)


def normalize_ad(item: Dict) -> Optional[Dict]:
    sn = item.get("snapshot") or {}
    ad_id = str(item.get("ad_archive_id") or item.get("ad_id") or "")
    if not ad_id:
        return None
    start = item.get("start_date")
    days = None
    if isinstance(start, (int, float)) and start > 0:
        days = int((time.time() - start) / 86400)

    # representative still + media type
    still = ""
    media_type = "image"
    imgs = sn.get("images") or []
    vids = sn.get("videos") or []
    cards = sn.get("cards") or []
    if imgs:
        still = imgs[0].get("original_image_url") or imgs[0].get("resized_image_url") or ""
        media_type = "image"
    elif vids:
        still = vids[0].get("video_preview_image_url") or ""
        media_type = "video"
    elif cards:
        c = cards[0]
        still = c.get("original_image_url") or c.get("video_preview_image_url") or ""
        media_type = "carousel"

    body = _text(sn.get("body")) or _text(sn.get("caption")) or _text(sn.get("link_description"))
    return {
        "ad_id": ad_id,
        "page_name": sn.get("page_name") or item.get("page_name") or "",
        "page_id": str(item.get("page_id") or ""),
        "is_active": bool(item.get("is_active")),
        "start_date": start,
        "days_active": days,
        "ad_copy": body[:600],
        "headline": _text(sn.get("title")),
        "cta_text": sn.get("cta_text") or "",
        "cta_type": sn.get("cta_type") or "",
        "media_type": media_type,
        "still_url": still,
        "ad_library_url": item.get("ad_library_url") or item.get("url") or f"https://www.facebook.com/ads/library/?id={ad_id}",
        "is_template": "{{product" in body,
    }


def select_winners(ads: List[Dict], top: int, exclude_brands: Optional[List[str]] = None) -> List[Dict]:
    # dedup by ad_id
    seen: Dict[str, Dict] = {}
    for a in ads:
        if a["ad_id"] not in seen:
            seen[a["ad_id"]] = a
    uniq = list(seen.values())
    # drop our own brand's ads (don't scrape ourselves)
    brands = [b.lower() for b in (exclude_brands or [])]
    if brands:
        uniq = [a for a in uniq if not any(b in (a.get("page_name", "").lower()) for b in brands)]
    # winners: active, has a still to classify, ranked by days_active
    cand = [a for a in uniq if a["is_active"] and a["still_url"]]
    cand.sort(key=lambda a: (a["days_active"] is not None, a["days_active"] or 0), reverse=True)
    winners = [a for a in cand if (a["days_active"] or 0) >= WINNER_DAYS]
    if len(winners) < top:  # backfill with the longest-running of the rest
        extra = [a for a in cand if a not in winners]
        winners += extra[: top - len(winners)]
    for a in winners:
        d = a["days_active"] or 0
        a["tier"] = ("Strong Winner" if d > 30 else "Winner" if d >= 14 else "Testing" if d >= 7 else "New")
    return winners[:top]


# ---------------------------------------------------------------------------
# download + vision
# ---------------------------------------------------------------------------
def download(url: str, dest: Path) -> bool:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40, context=_SSL_CTX) as r:
            dest.write_bytes(r.read())
        return dest.stat().st_size > 1000
    except Exception:
        return False


VISION_PROMPT = """Classify this competitor ad creative. Use the image (visual) and the ad copy.
Return ONLY JSON:
{
  "hook_type": "pain|curiosity|benefit|social_proof|urgency",
  "offer_type": "lead_magnet|discount|trial|webinar|quiz|demo|subscription|other",
  "visual_style": "minimalist|bold|testimonial|ugc|professional|product_shot|text_heavy|lifestyle",
  "cta_type": "learn_more|sign_up|download|book_call|shop_now|other",
  "primary_message": "one-line gist of the ad",
  "niche_relevant": true|false   // true if relevant to restaurant/local-business customer acquisition & marketing
}"""


def vision_classify(client, model: str, img_path: Path, ad_copy: str) -> Dict[str, Any]:
    import base64

    try:
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        ext = img_path.suffix.lstrip(".") or "jpeg"
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an ad-creative analyst. Output strict JSON."},
                {"role": "user", "content": [
                    {"type": "text", "text": f"{VISION_PROMPT}\n\nAD COPY:\n{ad_copy[:500]}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/{ext};base64,{b64}", "detail": "low"}},
                ]},
            ],
            response_format={"type": "json_object"},
            temperature=0,
            max_tokens=250,
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def make_openai():
    from openai import OpenAI

    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("ERROR: OPENAI_API_KEY missing (needed for vision classification).")
    return OpenAI(api_key=key, timeout=90, max_retries=2)


# ---------------------------------------------------------------------------
# seeds / patterns
# ---------------------------------------------------------------------------
ROLE_STOP = {"owner", "owners", "co-owner", "co-owners", "manager", "managers",
             "general", "marketer", "marketers", "director", "directors", "founder",
             "founders", "ceo", "operator", "operators", "professional", "professionals"}
WORD_STOP = {"the", "a", "an", "your", "you", "for", "with", "and", "to", "of", "in",
             "new", "get", "more", "best", "top", "free", "how", "what", "why", "into",
             "automated", "exclusive", "personalized", "guaranteed", "instantly"}


def detect_niche(marketing: Dict[str, Any]) -> str:
    """Infer the industry anchor (e.g. 'restaurant'). Prefer Agent 2's explicit niche."""
    # 0) Agent 2 market_targeting.niche (source of truth)
    mt_niche = (marketing.get("market_targeting", {}) or {}).get("niche", "")
    if mt_niche:
        w = mt_niche.strip().split()[0].lower().rstrip(",.")
        return w.rstrip("s") if w.endswith("s") and w != "business" else w
    # 1) audience segments minus role words
    for a in marketing.get("audiences", []):
        for w in (a.get("segment") or "").split():
            lw = w.strip(",.").lower()
            if lw and lw not in ROLE_STOP and len(lw) > 3:
                return lw.rstrip("s") if lw.endswith("s") and lw != "business" else lw
    # 2) headline: word after "your" / before "owners"
    hl = (marketing.get("landing_analysis", {}).get("headline") or "").lower().split()
    for i, w in enumerate(hl):
        if w == "your" and i + 1 < len(hl):
            cand = hl[i + 1].strip(",.?")
            if cand and cand not in WORD_STOP:
                return cand.rstrip("s") if cand.endswith("s") else cand
    return ""


def _angle_words(text: str, n: int = 2) -> str:
    words = [w.strip(",.?!").lower() for w in text.split()]
    kept = [w for w in words if w and not w.isdigit() and w not in WORD_STOP and w not in ROLE_STOP]
    return " ".join(kept[:n])


def load_seeds(marketing_path: Path, max_queries: int, niche_override: str = "",
               queries_override: Optional[List[str]] = None) -> List[str]:
    if queries_override:
        return queries_override[:max_queries]
    d = json.loads(marketing_path.read_text())
    # Agent 2 (competitor_research.search_queries) is the source of truth when present.
    cr_queries = (d.get("competitor_research", {}) or {}).get("search_queries") or []
    if cr_queries and not niche_override:
        out: List[str] = []
        for s in cr_queries:
            s = " ".join(str(s).split()[:4]).strip()
            if s and s.lower() not in {x.lower() for x in out}:
                out.append(s)
        return out[:max_queries]
    niche = niche_override or detect_niche(d)

    angles: List[str] = []
    for vp in d.get("value_propositions", []):
        for key in ("unique_mechanism", "headline"):
            a = _angle_words(vp.get(key) or "")
            if a:
                angles.append(a)
    for p in (d.get("landing_analysis", {}).get("pain_points") or [])[:3]:
        a = _angle_words(p)
        if a:
            angles.append(a)
    # niche-anchor every query so the Ad Library returns same-industry competitors
    seeds: List[str] = []
    if niche:
        # strong category queries first
        seeds += [f"{niche} marketing", f"{niche} customers", f"{niche} advertising"]
        for a in angles:
            seeds.append(a if niche in a else f"{niche} {a}")
    else:
        seeds = angles or ["small business marketing"]
    # dedup preserve order
    out: List[str] = []
    for s in seeds:
        s = " ".join(s.split()[:4]).strip()
        if s and s.lower() not in {x.lower() for x in out}:
            out.append(s)
    return out[:max_queries]


def aggregate_patterns(winners: List[Dict]) -> Dict[str, Any]:
    def dist(key: str) -> Dict[str, int]:
        return dict(Counter(w["classification"].get(key) for w in winners if w.get("classification") and not w["classification"].get("error")))
    return {
        "hook_distribution": dist("hook_type"),
        "visual_styles": dist("visual_style"),
        "offer_types": dist("offer_type"),
        "cta_types": dist("cta_type"),
        "format_distribution": dict(Counter(w["media_type"] for w in winners)),
        "niche_relevant_count": sum(1 for w in winners if (w.get("classification") or {}).get("niche_relevant")),
        "total_analyzed": len(winners),
    }


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def run(args: argparse.Namespace) -> int:
    mp = Path(args.marketing)
    if not mp.is_absolute():
        mp = (Path.cwd() / mp).resolve()
    if not mp.exists():
        sys.exit(f"ERROR: marketing file not found: {mp}")
    slug = json.loads(mp.read_text()).get("source", {}).get("slug", mp.stem)

    marketing = json.loads(mp.read_text())
    mt = marketing.get("market_targeting", {}) or {}
    cr = marketing.get("competitor_research", {}) or {}
    geo = (args.geo or (mt.get("geo", {}) or {}).get("primary") or "US").upper()
    if geo != "US":
        print(f"  (note: Agent 2 geo='{geo}', but this agent is pinned to US for now)")
        geo = "US"
    exclude_brands = cr.get("exclude_brand_terms") or []

    q_override = [q.strip() for q in args.queries.split(";") if q.strip()] if args.queries else None
    seeds = load_seeds(mp, args.max_queries, niche_override=args.niche, queries_override=q_override)
    if not seeds:
        sys.exit("ERROR: no value propositions / pain points to search with.")
    urls = [build_ads_url(s, geo) for s in seeds]

    niche_lbl = args.niche or detect_niche(marketing) or "(none)"
    vert = mt.get("vertical", "")
    src = "Agent2.search_queries" if (cr.get("search_queries") and not args.niche and not q_override) else "derived"
    print(f"▶ Agent 3 · {slug} · market {geo} · vertical='{vert}' niche='{niche_lbl}' · "
          f"{len(seeds)} queries [{src}], count={args.count}, vision={args.vision_model}")
    if exclude_brands:
        print(f"    excluding own brand: {exclude_brands}")
    for s in seeds:
        print(f"    • {s}")
    if args.dry_run:
        print(f"\n[dry-run] would charge up to {args.count} Apify results + ~{args.top} vision calls. No run.")
        return 0

    token = os.environ.get("APIFY_TOKEN") or os.environ.get("APIFY_API_TOKEN")
    if not token:
        sys.exit("ERROR: APIFY_TOKEN missing.")

    raw = apify_collect(token, urls, args.count)
    print(f"  fetched {len(raw)} ads")
    ads = [a for a in (normalize_ad(it) for it in raw) if a]
    winners = select_winners(ads, args.top, exclude_brands=exclude_brands)
    print(f"  → {len(winners)} winners selected (>= {WINNER_DAYS}d or longest-running)")

    creatives_dir = OUT_DIR / "creatives"
    creatives_dir.mkdir(parents=True, exist_ok=True)
    client = make_openai()

    for i, w in enumerate(winners, 1):
        ext = ".jpg"
        local = creatives_dir / f"ad_{w['ad_id']}{ext}"
        ok = download(w["still_url"], local) if w["still_url"] else False
        w["local_path"] = str(local.relative_to(REPO_ROOT)) if ok else None
        if ok:
            w["classification"] = vision_classify(client, args.vision_model, local, w["ad_copy"])
        else:
            w["classification"] = {"error": "download_failed"}
        c = w["classification"]
        tag = c.get("visual_style", c.get("error", "?")) if isinstance(c, dict) else "?"
        print(f"  [{i:02d}/{len(winners)}] {w['page_name'][:20]:<20} {w['days_active']}d {w['media_type']:<8} → {tag}")

    patterns = aggregate_patterns(winners)
    competitors = [
        {"page_name": pn, "ad_count": cnt}
        for pn, cnt in Counter(w["page_name"] for w in winners).most_common()
    ]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    data = {
        "meta": {
            "slug": slug, "market": "US", "generated_at": datetime.now().isoformat(),
            "queries": seeds, "ads_fetched": len(raw), "winners": len(winners),
            "vision_model": args.vision_model, "winner_threshold_days": WINNER_DAYS,
        },
        "competitors": competitors,
        "winning_creatives": winners,
        "patterns": patterns,
    }
    data_path = OUT_DIR / f"data_{slug}_{ts}.json"
    data_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    md = [
        f"# Competitor Intelligence — {slug}",
        f"\n- Market: US · Queries: {len(seeds)} · Ads fetched: {len(raw)} · Winners: {len(winners)}",
        f"- Niche-relevant winners: {patterns['niche_relevant_count']}/{len(winners)}",
        f"\n## Patterns",
        f"- Hooks: {patterns['hook_distribution']}",
        f"- Visual styles: {patterns['visual_styles']}",
        f"- Offers: {patterns['offer_types']}",
        f"- Formats: {patterns['format_distribution']}",
        f"\n## Top competitors",
        *[f"- {c['page_name']} ({c['ad_count']} ads)" for c in competitors[:10]],
        f"\n## Winning creatives",
        "| # | Page | Days | Format | Hook | Visual | Niche | Message |",
        "|---|------|------|--------|------|--------|-------|---------|",
    ]
    for i, w in enumerate(winners, 1):
        c = w.get("classification") or {}
        md.append(
            f"| {i} | {w['page_name'][:18]} | {w['days_active']} | {w['media_type']} | "
            f"{c.get('hook_type','?')} | {c.get('visual_style','?')} | "
            f"{'✓' if c.get('niche_relevant') else '·'} | {str(c.get('primary_message',''))[:40]} |"
        )
    (OUT_DIR / f"report_{slug}_{ts}.md").write_text("\n".join(md))

    print(f"\n✔ {len(winners)} winners · patterns done → {data_path.relative_to(REPO_ROOT)}")
    return 0


def main() -> None:
    load_env()
    ap = argparse.ArgumentParser(description="Agent 3 — competitor intel (Meta Ad Library + vision)")
    ap.add_argument("marketing", help="path to outputs/analysis/marketing_<slug>.json")
    ap.add_argument("--count", type=int, default=40, help="total Apify results to fetch (min 10, pay-per-result)")
    ap.add_argument("--max-queries", type=int, default=6, help="max search queries from the VPs/pains")
    ap.add_argument("--niche", default="", help="industry anchor for queries (e.g. 'restaurant'); from Agent 2 if omitted")
    ap.add_argument("--geo", default="", help="market country code (default: Agent 2 geo / US; agent pinned to US for now)")
    ap.add_argument("--queries", default="", help="override: ';'-separated search queries to use verbatim")
    ap.add_argument("--top", type=int, default=20, help="winners to download + vision-classify")
    ap.add_argument("--vision-model", default=DEFAULT_VISION_MODEL)
    ap.add_argument("--dry-run", action="store_true", help="print plan + projected charge, no run")
    args = ap.parse_args()
    if args.count < 10:
        args.count = 10  # actor minimum
    sys.exit(run(args))


if __name__ == "__main__":
    main()
