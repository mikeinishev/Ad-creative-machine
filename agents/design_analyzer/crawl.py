#!/usr/bin/env python3
"""
Agent 1 — URL funnel crawler (Playwright).

Walks a quiz/funnel URL end to end like a real visitor:
  - opens the URL in a mobile browser context
  - dismisses cookie/consent/popup overlays
  - answers every quiz question (deterministic: first valid option)
  - fills and submits the lead form with TEST data
  - follows the funnel to the paywall / checkout, screenshots it, and STOPS
    (never enters card details, never confirms payment)

Every distinct screen is screenshotted into  URLs/<slug>/NN_<type>.png  and logged
to  URLs/<slug>/manifest.json  + summary.md  so the funnel can be re-analysed later
(this is the screenshot set Agent 1's vision step consumes).

Usage:
  python agents/design_analyzer/crawl.py https://example.com/quiz
  python agents/design_analyzer/crawl.py URL1 URL2 --headed --max-steps 50
  python agents/design_analyzer/crawl.py URL --email test.sobaka@gmail.com --phone +13234442211
  python agents/design_analyzer/crawl.py URL --no-submit        # don't fill lead forms
  python agents/design_analyzer/crawl.py URL --desktop          # desktop viewport

Authorisation: only run against funnels you are allowed to submit test leads to.
Uses throwaway test identities; does not pay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[2]


def _rel(p: Path) -> str:
    """Path relative to the repo root when possible, else the absolute path."""
    try:
        return str(Path(p).resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass
class TestLead:
    email: str = "test.sobaka@gmail.com"
    phone: str = "+13234442211"
    first_name: str = "Test"
    last_name: str = "Tester"
    full_name: str = "Test Tester"
    company: str = "QA Test Co"
    zip: str = "10001"
    city: str = "New York"
    generic: str = "Test"


@dataclass
class CrawlConfig:
    out_root: Path = REPO_ROOT / "URLs"
    max_steps: int = 40
    headed: bool = False
    slowmo: int = 0
    device: str = "iPhone 13"   # "" → desktop
    submit_leads: bool = True
    settle_ms: int = 1200
    change_timeout_ms: int = 7000
    nav_timeout_ms: int = 45000
    lead: TestLead = field(default_factory=TestLead)
    llm: bool = False                 # use an LLM to pick actions when heuristics fail/stall
    llm_always: bool = False          # use the LLM on every step
    llm_model: str = "gpt-4o-mini"


# ---------------------------------------------------------------------------
# Keyword/heuristic tables
# ---------------------------------------------------------------------------
CONSENT_RE = re.compile(
    r"\b(accept all|accept|agree|i agree|got it|allow all|allow|ok|okay|consent|"
    r"continue without|reject all|close)\b",
    re.I,
)
CTA_PRIORITY = [
    r"^(get started|let'?s go|start( quiz| now)?|begin|take the quiz)$",
    r"^(see (my )?results?|get (my )?results?|show results?)$",
    r"^(continue|next|next question|proceed|go|submit|done|finish)$",
    r"^(claim|unlock|get (my )?plan|get (my )?offer|view plan)$",
    r"^(sign up|create account|get access|join)$",
    r"^(yes|i'?m ready|i want this)$",
]
PAYWALL_TEXT_RE = re.compile(
    r"(card number|cardholder|cvc|cvv|expiry|expiration|billing address|"
    r"payment (method|details|information)|credit card|complete (your )?(purchase|order|payment)|"
    r"subscribe (now|for|and)|start (my )?(membership|subscription)|"
    r"\$\s?\d[\d,.]*\s*/?\s*(mo|month|yr|year|wk|week|day))",
    re.I,
)
PAY_BUTTON_RE = re.compile(
    r"^(pay( now)?|subscribe|complete (purchase|order|payment)|"
    r"start (membership|subscription|trial)|confirm( payment| & pay)?|place order|checkout)$",
    re.I,
)


# ---------------------------------------------------------------------------
# In-page JS helpers (find + tag an element to act on)
# ---------------------------------------------------------------------------
JS_TAG_OPTION = r"""
() => {
  const TAG = 'data-qc-target';
  document.querySelectorAll('['+TAG+']').forEach(e => e.removeAttribute(TAG));
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 8 && r.height > 8 && s.visibility !== 'hidden' &&
           s.display !== 'none' && s.pointerEvents !== 'none' && el.offsetParent !== null;
  };
  const txt = el => (el.innerText || el.textContent || '').trim();
  // 1) explicit radio/checkbox options → click their label/wrapper
  for (const inp of document.querySelectorAll('input[type=radio], input[type=checkbox]')) {
    let lbl = inp.closest('label') ||
              (inp.id && document.querySelector('label[for="'+inp.id+'"]')) ||
              inp.parentElement;
    const target = lbl && vis(lbl) ? lbl : (vis(inp) ? inp : null);
    if (target) { target.setAttribute(TAG, '1'); return {found:true, type:'option', via:'radio', text:txt(target).slice(0,80)}; }
  }
  // 2) ARIA / role options
  const roleSel = '[role=radio],[role=option],[role=menuitemradio]';
  const roleEls = [...document.querySelectorAll(roleSel)].filter(vis);
  if (roleEls.length) { roleEls[0].setAttribute(TAG,'1'); return {found:true, type:'option', via:'role', text:txt(roleEls[0]).slice(0,80)}; }
  // 3) class/attribute-based answer cards
  const cardSel = [
    '[class*="option" i]','[class*="answer" i]','[class*="choice" i]','[class*="variant" i]',
    '[data-option]','[data-answer]','[data-value] button','button[data-value]',
    '.quiz__option','.quiz-option','.q-option','li[role=button]'
  ].join(',');
  let cards = [...document.querySelectorAll(cardSel)].filter(vis).filter(e => txt(e).length>0);
  // dedup nested (keep outermost clickable)
  cards = cards.filter(e => !cards.some(o => o !== e && o.contains(e)));
  if (cards.length >= 1) { cards[0].setAttribute(TAG,'1'); return {found:true, type:'option', via:'card', text:txt(cards[0]).slice(0,80), count:cards.length}; }
  // 4) groups of >=2 sibling buttons of similar size (likely an answer set)
  const btns = [...document.querySelectorAll('button, a[role=button], [role=button]')].filter(vis).filter(e=>txt(e).length>0);
  const byParent = {};
  for (const b of btns) { const k = b.parentElement; if(!k) continue; (byParent[k.dataset.qck||(k.dataset.qck=Math.random())] ||= []).push(b); }
  for (const k in byParent) {
    const grp = byParent[k];
    if (grp.length >= 2 && grp.length <= 8) {
      // avoid nav bars: skip if any item looks like a CTA word
      grp[0].setAttribute(TAG,'1'); return {found:true, type:'option', via:'siblings', text:txt(grp[0]).slice(0,80), count:grp.length};
    }
  }
  return {found:false};
}
"""

JS_TAG_CTA = r"""
(patterns) => {
  const TAG = 'data-qc-target';
  document.querySelectorAll('['+TAG+']').forEach(e => e.removeAttribute(TAG));
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 8 && r.height > 8 && s.visibility !== 'hidden' &&
           s.display !== 'none' && el.offsetParent !== null;
  };
  const txt = el => (el.innerText || el.textContent || el.value || '').trim();
  const cands = [...document.querySelectorAll(
    "button, a[role=button], [role=button], input[type=submit], input[type=button], a.btn, a[class*='button' i]"
  )].filter(vis).filter(e => txt(e).length > 0 && txt(e).length < 40);
  for (const re of patterns) {
    const rx = new RegExp(re, 'i');
    const hit = cands.find(e => rx.test(txt(e).replace(/\s+/g,' ').trim()));
    if (hit) { hit.setAttribute(TAG,'1'); return {found:true, type:'cta', text:txt(hit).slice(0,60)}; }
  }
  // generic submit fallback
  const sub = document.querySelector("button[type=submit], input[type=submit]");
  if (sub && vis(sub)) { sub.setAttribute(TAG,'1'); return {found:true, type:'cta', via:'submit', text:txt(sub).slice(0,60)}; }
  // primary-button fallback: the funnel often uses creative CTA copy
  // ("Check if my area is open →", "Show me my plan"). Pick the single most
  // prominent actionable button, excluding Back / legal / nav links.
  const EXCLUDE = /^(back|‹|«|<|previous|prev|privacy|terms|menu|skip|log\s?in|sign\s?in|home|close|×|✕|cancel|english|language)\b/i;
  const primary = cands.filter(e => {
    const t = txt(e).replace(/\s+/g,' ').trim();
    return t.length >= 2 && !EXCLUDE.test(t);
  });
  if (primary.length) {
    // prefer a button containing a forward arrow, else the lowest one on screen
    const arrow = primary.find(e => /[→»➜➔➝▶]|->/.test(txt(e)));
    const pick = arrow || primary.sort((a,b) =>
      b.getBoundingClientRect().top - a.getBoundingClientRect().top)[0];
    pick.setAttribute(TAG,'1');
    return {found:true, type:'cta', via:'primary', text:txt(pick).slice(0,60)};
  }
  return {found:false};
}
"""

JS_TAG_CONSENT = r"""
(reSource) => {
  const TAG = 'data-qc-target';
  document.querySelectorAll('['+TAG+']').forEach(e => e.removeAttribute(TAG));
  const rx = new RegExp(reSource, 'i');
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 8 && r.height > 8 && s.visibility !== 'hidden' && s.display !== 'none' && el.offsetParent !== null;
  };
  const txt = el => (el.innerText || el.textContent || el.value || '').trim();
  // only look inside likely banners/modals to avoid clicking the quiz CTA
  const scopes = [...document.querySelectorAll(
    "[id*='cookie' i],[class*='cookie' i],[id*='consent' i],[class*='consent' i]," +
    "[id*='gdpr' i],[class*='gdpr' i],[aria-label*='cookie' i],[class*='banner' i]"
  )];
  const pool = scopes.length ? scopes.flatMap(s => [...s.querySelectorAll('button,a,[role=button]')]) : [];
  const hit = pool.filter(vis).find(e => rx.test(txt(e)));
  if (hit) { hit.setAttribute(TAG,'1'); return {found:true, text:txt(hit).slice(0,40)}; }
  return {found:false};
}
"""

JS_SCAN_INPUTS = r"""
() => {
  const TAG = 'data-qc-input';
  document.querySelectorAll('['+TAG+']').forEach(e => e.removeAttribute(TAG));
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 4 && r.height > 4 && s.visibility !== 'hidden' &&
           s.display !== 'none' && el.offsetParent !== null;
  };
  const ctx = el => {
    let t = '';
    if (el.labels && el.labels[0]) t += ' ' + el.labels[0].innerText;
    if (el.getAttribute('aria-label')) t += ' ' + el.getAttribute('aria-label');
    // nearest preceding heading within the same card/section
    let scope = el.closest('form, section, [class*="step" i], [class*="card" i], main') || document.body;
    const hs = scope.querySelectorAll('h1,h2,h3,label,legend');
    if (hs.length) t += ' ' + hs[hs.length - 1].innerText;
    const h = document.querySelector('h1,h2,h3'); if (h) t += ' ' + h.innerText;
    return t.replace(/\s+/g, ' ').trim();
  };
  const skip = ['hidden','submit','button','checkbox','radio','file','range','image','reset'];
  const out = [];
  let idx = 0;
  for (const el of document.querySelectorAll('input, textarea, select')) {
    const type = (el.type || 'text').toLowerCase();
    if (skip.includes(type)) continue;
    if (!vis(el)) continue;
    el.setAttribute(TAG, String(idx));
    out.push({
      i: idx, tag: el.tagName, type,
      inputmode: el.getAttribute('inputmode') || '',
      name: el.name || '', placeholder: el.placeholder || '',
      aria: el.getAttribute('aria-label') || '',
      context: ctx(el).slice(0, 160),
      hasValue: !!(el.value && String(el.value).trim()),
    });
    idx++;
  }
  return out;
}
"""

JS_PAYWALL = r"""
(reSource) => {
  const rx = new RegExp(reSource, 'i');
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 20 && r.height > 10 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  // VISIBLE Stripe card field only — exclude the hidden __privateStripeFrame
  // control iframes that stripe.js injects on every page (incl. the landing).
  const stripeEls = [...document.querySelectorAll(
    ".StripeElement, iframe[title*='card' i], iframe[title*='secure' i], " +
    "iframe[src*='stripe'][title], iframe[name*='__privateStripeFrame'][title]"
  )].filter(vis);
  const hasStripe = stripeEls.length > 0;
  const cardInput = [...document.querySelectorAll(
    "input[autocomplete='cc-number'],input[name*='cardnumber' i]," +
    "input[name*='card' i]:not([type='checkbox']):not([type='radio']),input[placeholder*='card number' i]"
  )].filter(vis);
  const hasCard = cardInput.length > 0;
  const bodyText = (document.body.innerText || '').slice(0, 8000);
  const textHit = rx.test(bodyText);
  const payRe = /(pay\b|subscribe|get access|complete (purchase|order|payment)|start (membership|subscription|trial)|place order|checkout|enroll)/i;
  const hasPayBtn = [...document.querySelectorAll("button,[role=button],input[type=submit]")]
    .filter(vis).some(b => payRe.test((b.innerText || b.value || '').trim()));
  const url = location.href;
  const onCheckoutHost = /checkout\.stripe\.com|buy\.stripe\.com/i.test(url);
  const paywall = hasStripe || hasCard || onCheckoutHost || (textHit && hasPayBtn);
  return {paywall, signals: {hasStripe, hasCard, onCheckoutHost, textHit, hasPayBtn}};
}
"""

JS_TAG_CANDIDATES = r"""
() => {
  const TAG = 'data-qc-id';
  document.querySelectorAll('['+TAG+']').forEach(e => e.removeAttribute(TAG));
  const vis = el => {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 6 && r.height > 6 && s.visibility !== 'hidden' &&
           s.display !== 'none' && el.offsetParent !== null &&
           r.top < (window.innerHeight + 1200);
  };
  const txt = el => (el.innerText || el.textContent || el.value || '').replace(/\s+/g,' ').trim();
  const out = [];
  let id = 0;
  const seen = new Set();
  const push = (el, kind, extra={}) => {
    if (seen.has(el)) return;
    seen.add(el);
    el.setAttribute(TAG, String(id));
    out.push({id, kind, text: txt(el).slice(0,80), ...extra});
    id++;
  };
  // inputs/selects
  for (const el of document.querySelectorAll('input,textarea,select')) {
    const type = (el.type||'text').toLowerCase();
    if (['hidden','submit','button','checkbox','radio','file','range','image','reset'].includes(type)) continue;
    if (!vis(el)) continue;
    push(el, 'input', {type, placeholder: el.placeholder||'', inputmode: el.getAttribute('inputmode')||''});
  }
  // options
  for (const el of document.querySelectorAll('[role=radio],[role=option],[class*="option" i],[class*="answer" i],[class*="choice" i],label')) {
    if (vis(el) && txt(el)) push(el, 'option');
  }
  // buttons / links
  for (const el of document.querySelectorAll("button,[role=button],a[role=button],input[type=submit],a.btn,a[class*='button' i]")) {
    if (vis(el) && txt(el)) push(el, 'button');
  }
  return out.slice(0, 28);
}
"""


# ---------------------------------------------------------------------------
# Crawler
# ---------------------------------------------------------------------------
class FunnelCrawler:
    def __init__(self, cfg: CrawlConfig):
        self.cfg = cfg

    def _slug(self, url: str) -> str:
        u = urlparse(url)
        raw = (u.netloc + u.path).strip("/") or u.netloc
        slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", raw).strip("_")[:80]
        return slug or "funnel"

    def _signature(self, page) -> str:
        try:
            text = page.inner_text("body", timeout=3000)
        except Exception:
            text = ""
        h = hashlib.sha1(text[:6000].encode("utf-8", "ignore")).hexdigest()[:12]
        return f"{page.url}|{h}"

    def _wait_change(self, page, prev_sig: str) -> bool:
        """Poll until the page signature changes or timeout. Returns True if changed."""
        deadline = time.time() + self.cfg.change_timeout_ms / 1000
        while time.time() < deadline:
            try:
                page.wait_for_timeout(400)
            except Exception:
                pass
            if self._signature(page) != prev_sig:
                try:
                    page.wait_for_load_state("networkidle", timeout=4000)
                except Exception:
                    pass
                return True
        return False

    def _dismiss_overlays(self, page) -> Optional[str]:
        try:
            res = page.evaluate(JS_TAG_CONSENT, CONSENT_RE.pattern)
        except Exception:
            return None
        if res and res.get("found"):
            try:
                page.click("[data-qc-target='1']", timeout=2500)
                page.wait_for_timeout(500)
                return res.get("text", "consent")
            except Exception:
                return None
        return None

    def _value_for(self, meta: Dict[str, Any]) -> str:
        """Pick a test value for an input based on its type/inputmode/name/placeholder/context."""
        L = self.cfg.lead
        t = (meta.get("type") or "").lower()
        im = (meta.get("inputmode") or "").lower()
        blob = " ".join(
            str(meta.get(k, "")) for k in ("type", "inputmode", "name", "placeholder", "aria", "context")
        ).lower()

        if t == "email" or "email" in blob or "e-mail" in blob:
            return L.email
        if t == "tel" or "phone" in blob or "mobile" in blob or "whatsapp" in blob:
            return L.phone
        numeric_words = (
            "how many", "number", "transactions", "count", "revenue", "average",
            "per day", "per month", "customers", "amount", "budget", "spend",
            "sales", "tickets", "covers", "seats", "employees", "age", "$",
        )
        if t == "number" or im in ("numeric", "decimal") or any(w in blob for w in numeric_words):
            return "120"
        if t == "url" or "website" in blob or "url" in blob:
            return "https://example.com"
        if "first name" in blob or ("first" in blob and "name" in blob):
            return L.first_name
        if "last name" in blob or "surname" in blob or ("last" in blob and "name" in blob):
            return L.last_name
        if "company" in blob or "business" in blob or "restaurant" in blob or "venue" in blob:
            return L.company
        if "zip" in blob or "postal" in blob:
            return L.zip
        if "city" in blob:
            return L.city
        if "name" in blob:
            return L.full_name
        return L.generic

    def _scan_and_fill_inputs(self, page) -> List[Dict[str, str]]:
        """Fill all visible empty inputs with contextual test data. Returns what was filled."""
        try:
            metas = page.evaluate(JS_SCAN_INPUTS)
        except Exception:
            return []
        filled: List[Dict[str, str]] = []
        for meta in metas:
            if meta.get("hasValue"):
                continue
            sel = f"[data-qc-input='{meta['i']}']"
            try:
                if meta.get("tag") == "SELECT":
                    page.select_option(sel, index=1, timeout=1500)
                    filled.append({"field": meta.get("name") or "select", "value": "option#1"})
                    continue
                value = self._value_for(meta)
                page.fill(sel, value, timeout=2000)
                filled.append({
                    "field": meta.get("name") or meta.get("placeholder") or meta.get("type") or "input",
                    "value": value,
                })
            except Exception:
                continue
        return filled

    def _is_paywall(self, page) -> Dict[str, Any]:
        try:
            return page.evaluate(JS_PAYWALL, PAYWALL_TEXT_RE.pattern)
        except Exception:
            return {"paywall": False, "signals": {}}

    def _click_tagged(self, page) -> bool:
        try:
            page.click("[data-qc-target='1']", timeout=3000)
            return True
        except Exception:
            # try JS click fallback
            try:
                page.eval_on_selector("[data-qc-target='1']", "el => el.click()")
                return True
            except Exception:
                return False

    def _click_cta(self, page) -> Optional[Dict[str, Any]]:
        cta = page.evaluate(JS_TAG_CTA, CTA_PRIORITY)
        if cta.get("found") and self._click_tagged(page):
            return cta
        return None

    def _decide_and_act(self, page, selected_sig: Optional[str], cur_sig: str) -> Dict[str, Any]:
        """One action per call. Priority: answer options → fill+submit inputs → CTA.

        Options win over inputs so a stray text field on a question screen never
        short-circuits answering. Inputs are filled only when the screen has no
        unanswered options (e.g. numeric quiz questions, lead-capture forms).
        """
        opt = page.evaluate(JS_TAG_OPTION)

        # 1) answer a quiz option (once per screen; CTA advances it afterwards if needed)
        if opt.get("found") and selected_sig != cur_sig:
            page.evaluate(JS_TAG_OPTION)  # re-tag (in case it was cleared)
            if self._click_tagged(page):
                return {"action": "answer", "detail": opt, "selected_sig": cur_sig}

        # 2) typed inputs (numeric questions, name/email/phone lead forms)
        if self.cfg.submit_leads:
            filled = self._scan_and_fill_inputs(page)
            if filled:
                page.wait_for_timeout(450)  # let validation enable the CTA
                cta = self._click_cta(page)
                return {
                    "action": "fill_form",
                    "detail": {"filled": filled, "submit": cta.get("text") if cta else None},
                    "selected_sig": selected_sig,
                }

        # 3) plain CTA (Continue / Next / Get results …)
        cta = self._click_cta(page)
        if cta:
            return {"action": "cta", "detail": cta, "selected_sig": selected_sig}

        # 4) last resort: re-click an option
        if opt.get("found"):
            page.evaluate(JS_TAG_OPTION)
            if self._click_tagged(page):
                return {"action": "answer", "detail": opt, "selected_sig": cur_sig}

        return {"action": "none", "detail": {}, "selected_sig": selected_sig}

    # ---- LLM decider (for non-standard quizzes) ---------------------------
    def _get_llm(self):
        client = getattr(self, "_llm_client", None)
        if client is not None:
            return client
        # load OPENAI_API_KEY from .env if needed
        if not __import__("os").environ.get("OPENAI_API_KEY"):
            envp = REPO_ROOT / ".env"
            if envp.exists():
                for line in envp.read_text().splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        __import__("os").environ.setdefault(k.strip(), v.strip())
        from openai import OpenAI
        key = __import__("os").environ.get("OPENAI_API_KEY")
        if not key:
            print("  ⚠ LLM mode requested but OPENAI_API_KEY missing — skipping", file=sys.stderr)
            self._llm_client = False
            return False
        self._llm_client = OpenAI(api_key=key, timeout=60, max_retries=2)
        return self._llm_client

    def _viewport_dataurl(self, page) -> str:
        import base64 as _b64
        png = page.screenshot()  # viewport only — focused + cheap
        return "data:image/png;base64," + _b64.b64encode(png).decode()

    def _llm_decide(self, page) -> Dict[str, Any]:
        """Ask the model to pick the next action from tagged candidates. Returns action dict."""
        client = self._get_llm()
        if not client:
            return {"action": "none", "detail": {}, "selected_sig": None}
        try:
            cands = page.evaluate(JS_TAG_CANDIDATES)
        except Exception:
            cands = []
        if not cands:
            return {"action": "none", "detail": {}, "selected_sig": None}

        lead = self.cfg.lead
        instr = (
            "You are auto-navigating a quiz/sales funnel toward the checkout/paywall, as a "
            "test visitor. Move FORWARD only (never click Back/close/legal). Goal each step: "
            "answer the question (pick the FIRST sensible option), or fill the input(s), then "
            "click the button that advances (Continue/Next/Get results/Get access/etc).\n"
            f"Test data to use for fields — email: {lead.email}, phone: {lead.phone}, "
            f"name: {lead.full_name}, company: {lead.company}, numeric answers: 120, zip: {lead.zip}.\n"
            "Candidate elements (id, kind, text):\n"
            + "\n".join(
                f"  {c['id']}: [{c['kind']}] {c.get('text','')!r}"
                + (f" type={c.get('type')} ph={c.get('placeholder','')!r}" if c["kind"] == "input" else "")
                for c in cands
            )
            + "\n\nReturn ONLY JSON: {\"reason\":\"...\",\"fills\":[{\"id\":N,\"value\":\"...\"}],\"click_id\":N}. "
            "Use empty fills [] if nothing to type. click_id is the element to click to advance "
            "(an option id is fine if selecting it advances)."
        )
        try:
            resp = client.chat.completions.create(
                model=self.cfg.llm_model,
                messages=[
                    {"role": "system", "content": "You navigate web funnels. Output strict JSON."},
                    {"role": "user", "content": [
                        {"type": "text", "text": instr},
                        {"type": "image_url", "image_url": {"url": self._viewport_dataurl(page), "detail": "low"}},
                    ]},
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=300,
            )
            plan = json.loads(resp.choices[0].message.content)
        except Exception as e:  # noqa: BLE001
            return {"action": "llm_error", "detail": {"error": str(e)}, "selected_sig": None}

        filled = []
        for f in plan.get("fills", []) or []:
            try:
                page.fill(f"[data-qc-id='{int(f['id'])}']", str(f.get("value", "")), timeout=2000)
                filled.append(f)
            except Exception:
                continue
        clicked = None
        cid = plan.get("click_id")
        if cid is not None:
            try:
                page.wait_for_timeout(300)
                page.click(f"[data-qc-id='{int(cid)}']", timeout=3500)
                clicked = cid
            except Exception:
                try:
                    page.eval_on_selector(f"[data-qc-id='{int(cid)}']", "el=>el.click()")
                    clicked = cid
                except Exception:
                    pass
        if filled or clicked is not None:
            return {"action": "llm", "detail": {"reason": plan.get("reason", ""), "fills": filled, "click_id": clicked}, "selected_sig": None}
        return {"action": "none", "detail": {"llm_reason": plan.get("reason", "")}, "selected_sig": None}

    def crawl(self, url: str) -> Dict[str, Any]:
        from playwright.sync_api import sync_playwright

        slug = self._slug(url)
        out_dir = self.cfg.out_root / slug
        shots_dir = out_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "page_text").mkdir(exist_ok=True)

        manifest: Dict[str, Any] = {
            "url": url,
            "slug": slug,
            "started_at": datetime.now().isoformat(),
            "config": {
                "device": self.cfg.device or "desktop",
                "max_steps": self.cfg.max_steps,
                "submit_leads": self.cfg.submit_leads,
                "answer_strategy": "first_option",
            },
            "steps": [],
            "status": "running",
        }
        print(f"\n▶ {url}\n  → {_rel(out_dir)}")

        with sync_playwright() as p:
            launch_kw = {"headless": not self.cfg.headed}
            if self.cfg.slowmo:
                launch_kw["slow_mo"] = self.cfg.slowmo
            browser = p.chromium.launch(**launch_kw)
            ctx_kw: Dict[str, Any] = {"locale": "en-US"}
            if self.cfg.device and self.cfg.device in p.devices:
                ctx_kw.update(p.devices[self.cfg.device])
            else:
                ctx_kw.update({"viewport": {"width": 1280, "height": 900}})
            context = browser.new_context(**ctx_kw)
            context.set_default_timeout(self.cfg.nav_timeout_ms)
            page = context.new_page()

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=self.cfg.nav_timeout_ms)
            except Exception as e:
                manifest["status"] = "error"
                manifest["error"] = f"initial goto failed: {e}"
                self._finalize(manifest, out_dir)
                context.close(); browser.close()
                return manifest

            selected_sig: Optional[str] = None
            seen_sigs: List[str] = []
            stuck = 0
            scrolled = False
            force_llm = False

            for step in range(self.cfg.max_steps):
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                page.wait_for_timeout(self.cfg.settle_ms)

                consent = self._dismiss_overlays(page)
                cur_sig = self._signature(page)
                is_dup = cur_sig in seen_sigs
                seen_sigs.append(cur_sig)

                pw = self._is_paywall(page)
                stype = "paywall" if pw.get("paywall") else ("landing" if step == 0 else "screen")

                shot = shots_dir / f"{step:02d}_{stype}.png"
                try:
                    page.screenshot(path=str(shot), full_page=True)
                except Exception:
                    page.screenshot(path=str(shot))  # viewport fallback
                try:
                    (out_dir / "page_text" / f"{step:02d}.txt").write_text(
                        page.inner_text("body", timeout=3000)[:20000]
                    )
                except Exception:
                    pass

                entry = {
                    "step": step,
                    "url": page.url,
                    "title": (page.title() or "")[:120],
                    "type": stype,
                    "screenshot": shot.name,
                    "consent_dismissed": consent,
                    "duplicate_of_prev": is_dup,
                    "paywall_signals": pw.get("signals"),
                }
                print(f"  [{step:02d}] {stype:<8} {entry['title'][:48]!r}")

                if pw.get("paywall"):
                    entry["action"] = "stop_at_paywall"
                    manifest["steps"].append(entry)
                    manifest["status"] = "reached_paywall"
                    print(f"  ⏹ paywall reached → stop (signals: {pw.get('signals')})")
                    break

                if self.cfg.llm_always or force_llm:
                    act = self._llm_decide(page)
                    if act["action"] in ("none", "llm_error"):
                        act = self._decide_and_act(page, selected_sig, cur_sig)
                else:
                    act = self._decide_and_act(page, selected_sig, cur_sig)
                    if act["action"] == "none" and self.cfg.llm:
                        print("  · heuristics found nothing → LLM decide")
                        act = self._llm_decide(page)
                force_llm = False
                if act.get("selected_sig") is not None:
                    selected_sig = act["selected_sig"]
                entry["action"] = act["action"]
                entry["action_detail"] = act["detail"]
                if act["action"] == "llm":
                    print(f"       llm: {str(act['detail'].get('reason',''))[:70]}")
                manifest["steps"].append(entry)

                if act["action"] in ("none", "llm_error"):
                    if not scrolled:
                        try:
                            page.mouse.wheel(0, 2000)
                        except Exception:
                            pass
                        scrolled = True
                        continue
                    print("  ⏹ no actionable element found → stop")
                    manifest["status"] = "dead_end"
                    break
                scrolled = False

                changed = self._wait_change(page, cur_sig)
                if not changed:
                    stuck += 1
                    if self.cfg.llm and not self.cfg.llm_always:
                        force_llm = True  # let the LLM try a different element next step
                    if stuck >= 3:
                        print("  ⏹ no progress after 3 attempts → stop")
                        manifest["status"] = "stuck"
                        break
                else:
                    stuck = 0
            else:
                manifest["status"] = "max_steps_reached"

            context.close()
            browser.close()

        self._finalize(manifest, out_dir)
        return manifest

    def _finalize(self, manifest: Dict[str, Any], out_dir: Path) -> None:
        manifest["finished_at"] = datetime.now().isoformat()
        manifest["total_screens"] = len(manifest["steps"])
        (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        lines = [
            f"# Funnel crawl — {manifest['slug']}",
            "",
            f"- URL: {manifest['url']}",
            f"- Status: **{manifest['status']}**",
            f"- Screens captured: {manifest['total_screens']}",
            f"- Device: {manifest['config']['device']}",
            "",
            "| # | Type | Action | Title |",
            "|---|------|--------|-------|",
        ]
        for s in manifest["steps"]:
            lines.append(
                f"| {s['step']:02d} | {s['type']} | {s.get('action','')} | {s.get('title','')[:50]} |"
            )
        (out_dir / "summary.md").write_text("\n".join(lines))
        print(f"  ✔ {manifest['status']} · {manifest['total_screens']} screens → {_rel(out_dir / "summary.md")}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Agent 1 — URL funnel crawler")
    ap.add_argument("urls", nargs="+", help="funnel URL(s) to crawl")
    ap.add_argument("--out", default=str(REPO_ROOT / "URLs"), help="output root (default: URLs/)")
    ap.add_argument("--max-steps", type=int, default=40)
    ap.add_argument("--headed", action="store_true", help="show the browser")
    ap.add_argument("--slowmo", type=int, default=0, help="ms delay between actions")
    ap.add_argument("--desktop", action="store_true", help="desktop viewport instead of mobile")
    ap.add_argument("--no-submit", action="store_true", help="do not fill/submit lead forms")
    ap.add_argument("--llm", action="store_true", help="use an LLM to pick actions when heuristics stall (non-standard quizzes)")
    ap.add_argument("--llm-always", action="store_true", help="use the LLM on every step")
    ap.add_argument("--llm-model", default="gpt-4o-mini", help="vision model for LLM mode")
    ap.add_argument("--email", default=TestLead.email)
    ap.add_argument("--phone", default=TestLead.phone)
    ap.add_argument("--name", default=TestLead.full_name)
    args = ap.parse_args()

    fn = args.name.split()
    lead = TestLead(
        email=args.email, phone=args.phone, full_name=args.name,
        first_name=fn[0] if fn else "Test",
        last_name=fn[-1] if len(fn) > 1 else "Tester",
    )
    cfg = CrawlConfig(
        out_root=Path(args.out),
        max_steps=args.max_steps,
        headed=args.headed,
        slowmo=args.slowmo,
        device="" if args.desktop else "iPhone 13",
        submit_leads=not args.no_submit,
        lead=lead,
        llm=args.llm or args.llm_always,
        llm_always=args.llm_always,
        llm_model=args.llm_model,
    )
    crawler = FunnelCrawler(cfg)
    results = []
    for url in args.urls:
        try:
            results.append(crawler.crawl(url))
        except Exception as e:  # noqa: BLE001
            print(f"  ✖ crawl failed for {url}: {e}", file=sys.stderr)
            results.append({"url": url, "status": "crash", "error": str(e)})
    ok = sum(1 for r in results if r.get("status") in ("reached_paywall", "max_steps_reached"))
    print(f"\nDone: {len(results)} funnel(s), {ok} reached paywall/end.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
