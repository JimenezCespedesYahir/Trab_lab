# ============================================================
# capture_payloads_v18.py
# ============================================================
#
# Production-oriented Power BI embedded pipeline.
#
# Key changes vs v17:
# - no long-lived nth() locators after a rerender
# - filter containers are rediscovered and tagged
# - dropdown ownership is scored from the click anchor, not by area only
# - overlay/options are snapshotted from the live DOM before every action
# - virtualized scrolling uses the real scroll root when possible
# - waits are based on DOM/network quiet plus validation
# - /querydata requests and responses are persisted with correlation metadata
# - structured JSONL logging keeps the Power BI state trail auditable
#
# ============================================================

import hashlib
import json
import os
import re
import threading
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple
from uuid import uuid4

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


# ============================================================
# CONFIG
# ============================================================

POWERBI_URL = (
    "https://app.powerbi.com/view?"
    "r=eyJrIjoiOGQ4ZWJkMWQtNjk2OS00ZmM0LWFhMGUt"
    "MGUyNTY2ZTY3OGE0IiwidCI6IjExMzgxOTYwLWVk"
    "YWMtNGRkNC1hZTQ0LWViZGRmNGE3OTVjYyJ9"
    "&pageName=ReportSection"
)

HEADLESS = os.getenv("HEADLESS", "0").strip() == "1"
KEEP_BROWSER_OPEN = os.getenv("KEEP_BROWSER_OPEN", "1").strip() == "1"
SLOW_MO_MS = int(os.getenv("SLOW_MO_MS", "80"))

SESSION_ID = os.getenv("SESSION_ID") or (
    "pbi-"
    + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    + "-"
    + uuid4().hex[:8]
)

OUTPUT_DIR = Path("capture_payloads_v18_outputs")
RUN_DIR = OUTPUT_DIR / SESSION_ID
REQUEST_DIR = RUN_DIR / "querydata_requests"
RESPONSE_DIR = RUN_DIR / "querydata_responses"
DEBUG_DIR = RUN_DIR / "debug"
EVENT_LOG = RUN_DIR / "events.jsonl"

for directory in (OUTPUT_DIR, RUN_DIR, REQUEST_DIR, RESPONSE_DIR, DEBUG_DIR):
    directory.mkdir(exist_ok=True)

FILTER_LABELS = (
    "MACROREGION",
    "Institucion",
    "Unidad ejecutora",
    "Grupo Producto",
)

QUERYDATA_PATH = "/querydata"

DEFAULT_TIMEOUT_MS = 30000
SHORT_TIMEOUT_MS = 5000


# ============================================================
# STATE
# ============================================================

querydata_request_counter = 0
querydata_response_counter = 0
querydata_event_counter = 0
last_querydata_at = 0.0

state_lock = threading.RLock()
current_filters: Dict[str, str] = {}
active_action: Dict[str, Any] = {}
request_registry: Dict[str, Dict[str, Any]] = {}


# ============================================================
# LOGGING AND RUN CONTEXT
# ============================================================

def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def context_snapshot() -> Dict[str, Any]:
    with state_lock:
        return {
            "session_id": SESSION_ID,
            "filters_applied": dict(current_filters),
            "active_action": dict(active_action),
        }


def emit_event(event: str, level: str = "info", message: Optional[str] = None, **fields: Any) -> None:
    entry = {
        "timestamp": utc_timestamp(),
        "session_id": SESSION_ID,
        "level": level,
        "event": event,
        **context_snapshot(),
        **fields,
    }

    if message is not None:
        entry["message"] = message

    with state_lock:
        with open(EVENT_LOG, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def section(title: str) -> None:
    print("\n")
    print("=" * 70)
    print(title)
    print("=" * 70)
    emit_event("section", title=title)


def log(message: str, event: str = "log", level: str = "info", **fields: Any) -> None:
    print(message, flush=True)
    emit_event(event, level=level, message=message, **fields)


def set_active_action(action: str, **fields: Any) -> None:
    with state_lock:
        active_action.clear()
        active_action.update({"action": action, **fields})

    emit_event("active_action_set", action=action, **fields)


def clear_active_action() -> None:
    with state_lock:
        previous = dict(active_action)
        active_action.clear()

    emit_event("active_action_clear", previous=previous)


def mark_filter_applied(label: str, value: str) -> None:
    normalized_label = normalize_text(label)
    with state_lock:
        current_filters[normalized_label] = value

    emit_event("filter_applied", label=label, normalized_label=normalized_label, value=value)


# ============================================================
# TEXT MATCHING
# ============================================================

def normalize_text(text: Any) -> str:
    if text is None:
        return ""

    value = str(text)
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = value.upper()
    value = value.replace("\u00a0", " ")
    value = re.sub(r"[\r\n\t]+", " ", value)
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def compact_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8", errors="ignore")).hexdigest()[:10]


def ordered_tokens_present(needle_tokens: Sequence[str], haystack_tokens: Sequence[str]) -> bool:
    pos = 0
    for token in needle_tokens:
        try:
            pos = haystack_tokens.index(token, pos) + 1
        except ValueError:
            return False
    return True


def text_match_score(candidate: str, target: str) -> float:
    cand = normalize_text(candidate)
    targ = normalize_text(target)

    if not cand or not targ:
        return 0.0

    select_all_aliases = {
        "SELECCIONAR TODO",
        "SELECT ALL",
        "TODOS",
        "ALL",
    }

    if cand in select_all_aliases and targ in select_all_aliases:
        return 100.0

    if cand == targ:
        return 100.0

    if targ in cand:
        length_penalty = min(10.0, max(0.0, (len(cand) - len(targ)) / 10.0))
        return 92.0 - length_penalty

    if cand in targ:
        return 68.0

    cand_tokens = cand.split()
    targ_tokens = targ.split()

    if targ_tokens and all(token in cand_tokens for token in targ_tokens):
        return 86.0

    if targ_tokens and ordered_tokens_present(targ_tokens, cand_tokens):
        return 78.0

    ratio = SequenceMatcher(None, cand, targ).ratio()
    if ratio >= 0.78:
        return 60.0 + (ratio * 15.0)

    return 0.0


# ============================================================
# NETWORK CAPTURE
# ============================================================

def payload_sha256(payload: Optional[str]) -> Optional[str]:
    if payload is None:
        return None
    return hashlib.sha256(payload.encode("utf-8", errors="ignore")).hexdigest()


def request_identity(request) -> str:
    impl = getattr(request, "_impl_obj", None)
    guid = getattr(impl, "_guid", None)
    if guid:
        return str(guid)
    return f"request-object-{id(request)}"


def save_jsonish(directory: Path, prefix: str, counter: int, payload: Optional[str], meta: Dict[str, Any]) -> None:
    filename = directory / f"{prefix}_{counter:03d}.json"

    parsed: Any = None
    if payload:
        try:
            parsed = json.loads(payload)
        except Exception:
            parsed = payload

    envelope = {
        "meta": {
            "timestamp": utc_timestamp(),
            "session_id": SESSION_ID,
            **context_snapshot(),
            **meta,
        },
        "payload": parsed,
    }

    with open(filename, "w", encoding="utf-8") as fh:
        json.dump(envelope, fh, ensure_ascii=False, indent=2)

    log(
        f"SAVED: {filename}",
        event="payload_saved",
        path=str(filename),
        prefix=prefix,
        counter=counter,
        correlation_id=meta.get("correlation_id"),
    )


def handle_request(request) -> None:
    global querydata_request_counter, querydata_event_counter, last_querydata_at

    try:
        url = request.url
        if QUERYDATA_PATH not in url.lower():
            return

        request_key = request_identity(request)
        post_data = request.post_data
        started_monotonic = time.monotonic()

        with state_lock:
            querydata_request_counter += 1
            counter = querydata_request_counter
            querydata_event_counter += 1
            event_counter = querydata_event_counter
            last_querydata_at = started_monotonic
            correlation_id = f"{SESSION_ID}-querydata-{counter:04d}"
            request_registry[request_key] = {
                "correlation_id": correlation_id,
                "request_counter": counter,
                "request_key": request_key,
                "url": url,
                "method": request.method,
                "started_monotonic": started_monotonic,
                "payload_sha256": payload_sha256(post_data),
            }

        save_jsonish(
            REQUEST_DIR,
            "request",
            counter,
            post_data,
            {
                "correlation_id": correlation_id,
                "request_key": request_key,
                "request_counter": counter,
                "url": url,
                "method": request.method,
                "resource_type": request.resource_type,
                "event_counter": event_counter,
                "payload_sha256": payload_sha256(post_data),
            },
        )

    except Exception as exc:
        log(f"REQUEST CAPTURE ERROR: {exc}", event="request_capture_error", level="error")


def handle_response(response) -> None:
    global querydata_response_counter, querydata_event_counter, last_querydata_at

    try:
        url = response.url
        if QUERYDATA_PATH not in url.lower():
            return

        response_seen_monotonic = time.monotonic()
        request = response.request
        request_key = request_identity(request)

        with state_lock:
            querydata_response_counter += 1
            counter = querydata_response_counter
            querydata_event_counter += 1
            event_counter = querydata_event_counter
            last_querydata_at = response_seen_monotonic
            request_meta = dict(request_registry.get(request_key) or {})

        correlation_id = request_meta.get("correlation_id") or f"{SESSION_ID}-orphan-response-{counter:04d}"
        elapsed_ms = None
        if request_meta.get("started_monotonic") is not None:
            elapsed_ms = round((response_seen_monotonic - float(request_meta["started_monotonic"])) * 1000, 1)

        text = None
        try:
            text = response.text()
        except Exception as exc:
            text = json.dumps({"body_error": str(exc)})

        save_jsonish(
            RESPONSE_DIR,
            "response",
            counter,
            text,
            {
                "correlation_id": correlation_id,
                "request_key": request_key,
                "request_counter": request_meta.get("request_counter"),
                "response_counter": counter,
                "url": url,
                "status": response.status,
                "event_counter": event_counter,
                "elapsed_ms": elapsed_ms,
                "correlation_status": "matched" if request_meta else "orphan_response",
                "request_payload_sha256": request_meta.get("payload_sha256"),
                "response_payload_sha256": payload_sha256(text),
            },
        )

    except Exception as exc:
        log(f"RESPONSE CAPTURE ERROR: {exc}", event="response_capture_error", level="error")


# ============================================================
# WAIT HELPERS
# ============================================================

def wait_for_dom_quiet(page: Page, quiet_ms: int = 500, timeout_ms: int = 8000) -> bool:
    try:
        page.evaluate(
            """
            ([quietMs, timeoutMs]) => new Promise((resolve) => {
                let done = false;
                let quietTimer = null;
                const finish = (value) => {
                    if (done) return;
                    done = true;
                    try { observer.disconnect(); } catch (e) {}
                    clearTimeout(quietTimer);
                    clearTimeout(timeoutTimer);
                    resolve(value);
                };
                const armQuiet = () => {
                    clearTimeout(quietTimer);
                    quietTimer = setTimeout(() => finish(true), quietMs);
                };
                const observer = new MutationObserver(armQuiet);
                observer.observe(document.documentElement, {
                    childList: true,
                    subtree: true,
                    attributes: true,
                    characterData: true
                });
                const timeoutTimer = setTimeout(() => finish(false), timeoutMs);
                armQuiet();
            })
            """,
            [quiet_ms, timeout_ms],
        )
        return True
    except Exception:
        return False


def wait_for_querydata_quiet(page: Page, previous_event_count: int, quiet_ms: int = 1200, timeout_ms: int = 20000) -> bool:
    deadline = time.monotonic() + (timeout_ms / 1000)
    saw_new_event = False

    while time.monotonic() < deadline:
        page.wait_for_timeout(150)

        if querydata_event_counter > previous_event_count:
            saw_new_event = True

        if saw_new_event and (time.monotonic() - last_querydata_at) >= (quiet_ms / 1000):
            return True

    return saw_new_event


def wait_powerbi_idle(page: Page, previous_event_count: Optional[int] = None, timeout_ms: int = 20000) -> None:
    if previous_event_count is not None:
        wait_for_querydata_quiet(page, previous_event_count, timeout_ms=timeout_ms)

    wait_for_dom_quiet(page, quiet_ms=500, timeout_ms=7000)


def wait_rerender(page: Optional[Page] = None, previous_event_count: Optional[int] = None, seconds: int = 12) -> None:
    section("WAIT POWER BI IDLE")

    if page is not None:
        wait_powerbi_idle(page, previous_event_count=previous_event_count, timeout_ms=max(5000, seconds * 1000))
    else:
        time.sleep(seconds)


# ============================================================
# DOM SNAPSHOT JAVASCRIPT
# ============================================================

OVERLAY_SNAPSHOT_JS = """
([selectors]) => {
    const visible = (el) => {
        if (!el || !el.isConnected) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        const rect = el.getBoundingClientRect();
        return rect.width >= 12 && rect.height >= 12 && rect.bottom > 0 && rect.right > 0 &&
               rect.top < window.innerHeight && rect.left < window.innerWidth;
    };

    const ensureId = (el, attr, prefix) => {
        let id = el.getAttribute(attr);
        if (!id) {
            id = `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
            el.setAttribute(attr, id);
        }
        return id;
    };

    const unique = [];
    const seen = new Set();

    for (const selector of selectors) {
        for (const el of document.querySelectorAll(selector)) {
            if (!visible(el)) continue;
            if (seen.has(el)) continue;
            seen.add(el);
            unique.push(el);
        }
    }

    const active = document.activeElement;

    return unique.map((el) => {
        const rect = el.getBoundingClientRect();
        const optionCount = el.querySelectorAll('[role="treeitem"], [role="option"]').length;
        const searchCount = el.querySelectorAll('input, textarea, [contenteditable="true"]').length;
        const text = (el.innerText || el.textContent || '').slice(0, 2000);
        const scrollables = [el, ...Array.from(el.querySelectorAll('*'))].filter((node) => {
            try {
                const st = window.getComputedStyle(node);
                const r = node.getBoundingClientRect();
                return r.width > 10 && r.height > 10 &&
                       (node.scrollHeight - node.clientHeight) > 4 &&
                       /(auto|scroll|overlay)/.test(st.overflowY + st.overflow);
            } catch (e) {
                return false;
            }
        });
        const bestScroll = scrollables.sort((a, b) =>
            ((b.scrollHeight - b.clientHeight) * b.clientHeight) -
            ((a.scrollHeight - a.clientHeight) * a.clientHeight)
        )[0] || el;

        return {
            id: ensureId(el, 'data-pbi-overlay-id', 'pbi-overlay'),
            role: el.getAttribute('role') || '',
            className: String(el.className || ''),
            tagName: el.tagName,
            text,
            optionCount,
            searchCount,
            containsActive: active ? el.contains(active) : false,
            rect: {
                x: rect.x,
                y: rect.y,
                left: rect.left,
                top: rect.top,
                right: rect.right,
                bottom: rect.bottom,
                width: rect.width,
                height: rect.height
            },
            scroll: {
                id: ensureId(bestScroll, 'data-pbi-scroll-id', 'pbi-scroll'),
                top: bestScroll.scrollTop,
                clientHeight: bestScroll.clientHeight,
                scrollHeight: bestScroll.scrollHeight
            }
        };
    });
}
"""


CLICK_TARGETS_JS = """
(root) => {
    const visible = (el) => {
        if (!el || !el.isConnected) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        const rect = el.getBoundingClientRect();
        return rect.width >= 4 && rect.height >= 4 && rect.bottom > 0 && rect.right > 0 &&
               rect.top < window.innerHeight && rect.left < window.innerWidth;
    };

    const rectObj = (r) => ({
        x: r.x, y: r.y, left: r.left, top: r.top, right: r.right, bottom: r.bottom,
        width: r.width, height: r.height
    });

    const selectors = [
        '[role="combobox"]',
        '[aria-haspopup]',
        '[aria-expanded]',
        'input[role="combobox"]',
        'button',
        'svg',
        'i',
        '.dropdown',
        '.caret',
        '.chevron'
    ];

    const results = [];
    const seen = new Set();

    for (let selectorIndex = 0; selectorIndex < selectors.length; selectorIndex++) {
        const selector = selectors[selectorIndex];
        for (const el of root.querySelectorAll(selector)) {
            if (!visible(el) || seen.has(el)) continue;
            seen.add(el);
            const r = el.getBoundingClientRect();
            const role = el.getAttribute('role') || '';
            const expanded = el.getAttribute('aria-expanded');
            const reason = `${selector}:${role}:${expanded || ''}`;
            const pointX = role === 'combobox' || selector.includes('aria')
                ? r.right - Math.min(24, Math.max(8, r.width * 0.12))
                : r.left + r.width / 2;
            results.push({
                priority: selectorIndex,
                reason,
                box: rectObj(r),
                x: pointX,
                y: r.top + r.height / 2
            });
        }
    }

    const rootRect = root.getBoundingClientRect();
    const combo = Array.from(root.querySelectorAll('[role="combobox"], [aria-haspopup], input'))
        .filter(visible)
        .map((el) => el.getBoundingClientRect())
        .sort((a, b) => (b.width * b.height) - (a.width * a.height))[0];

    const fallbackRect = combo || rootRect;
    for (const ratio of [0.94, 0.90, 0.86, 0.80]) {
        results.push({
            priority: 100 + ratio,
            reason: `hotspot:${ratio}`,
            box: rectObj(fallbackRect),
            x: fallbackRect.left + fallbackRect.width * ratio,
            y: fallbackRect.top + fallbackRect.height / 2
        });
    }

    return results
        .filter((item) => Number.isFinite(item.x) && Number.isFinite(item.y))
        .sort((a, b) => a.priority - b.priority);
}
"""


OPTIONS_SNAPSHOT_JS = """
(overlay) => {
    const visible = (el) => {
        if (!el || !el.isConnected) return false;
        const style = window.getComputedStyle(el);
        if (style.display === 'none' || style.visibility === 'hidden' || Number(style.opacity) === 0) return false;
        const rect = el.getBoundingClientRect();
        return rect.width >= 5 && rect.height >= 5 && rect.bottom > 0 && rect.right > 0 &&
               rect.top < window.innerHeight && rect.left < window.innerWidth;
    };

    const ensureId = (el) => {
        let id = el.getAttribute('data-pbi-option-id');
        if (!id) {
            id = `pbi-option-${Date.now()}-${Math.random().toString(36).slice(2)}`;
            el.setAttribute('data-pbi-option-id', id);
        }
        return id;
    };

    const rectObj = (r) => ({
        x: r.x, y: r.y, left: r.left, top: r.top, right: r.right, bottom: r.bottom,
        width: r.width, height: r.height
    });

    const roots = Array.from(overlay.querySelectorAll(
        '[role="treeitem"], [role="option"], .slicerItemContainer, .slicerItem, label'
    ));

    const rows = [];
    const seen = new Set();

    for (const node of roots) {
        const row = node.closest('[role="treeitem"], [role="option"], .slicerItemContainer, .slicerItem, li, label') || node;
        if (!visible(row) || seen.has(row)) continue;
        seen.add(row);

        const text = (row.innerText || row.textContent || '').replace(/\\s+/g, ' ').trim();
        if (!text) continue;

        const rect = row.getBoundingClientRect();
        const selected =
            row.getAttribute('aria-selected') === 'true' ||
            row.getAttribute('aria-checked') === 'true' ||
            !!row.querySelector('input:checked') ||
            /selected|checked/i.test(String(row.className || ''));

        rows.push({
            id: ensureId(row),
            text,
            selected,
            role: row.getAttribute('role') || '',
            box: rectObj(rect)
        });
    }

    return rows.sort((a, b) => (a.box.top - b.box.top) || (a.box.left - b.box.left));
}
"""


SCROLL_STATE_JS = """
(overlay) => {
    const visible = (el) => {
        if (!el || !el.isConnected) return false;
        const rect = el.getBoundingClientRect();
        const style = window.getComputedStyle(el);
        return rect.width > 8 && rect.height > 8 &&
               style.display !== 'none' && style.visibility !== 'hidden';
    };

    const ensureId = (el) => {
        let id = el.getAttribute('data-pbi-scroll-id');
        if (!id) {
            id = `pbi-scroll-${Date.now()}-${Math.random().toString(36).slice(2)}`;
            el.setAttribute('data-pbi-scroll-id', id);
        }
        return id;
    };

    const candidates = [overlay, ...Array.from(overlay.querySelectorAll('*'))]
        .filter((el) => {
            try {
                const style = window.getComputedStyle(el);
                return visible(el) &&
                       (el.scrollHeight - el.clientHeight) > 4 &&
                       /(auto|scroll|overlay)/.test(style.overflowY + style.overflow);
            } catch (e) {
                return false;
            }
        });

    const root = candidates.sort((a, b) =>
        ((b.scrollHeight - b.clientHeight) * b.clientHeight) -
        ((a.scrollHeight - a.clientHeight) * a.clientHeight)
    )[0] || overlay;

    const rect = root.getBoundingClientRect();

    return {
        id: ensureId(root),
        top: root.scrollTop,
        clientHeight: root.clientHeight,
        scrollHeight: root.scrollHeight,
        maxTop: Math.max(0, root.scrollHeight - root.clientHeight),
        box: {x: rect.x, y: rect.y, left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom, width: rect.width, height: rect.height}
    };
}
"""


SCROLL_BY_JS = """
(overlay, delta) => {
    const candidates = [overlay, ...Array.from(overlay.querySelectorAll('*'))]
        .filter((el) => {
            try {
                const style = window.getComputedStyle(el);
                return (el.scrollHeight - el.clientHeight) > 4 &&
                       /(auto|scroll|overlay)/.test(style.overflowY + style.overflow);
            } catch (e) {
                return false;
            }
        });

    const root = candidates.sort((a, b) =>
        ((b.scrollHeight - b.clientHeight) * b.clientHeight) -
        ((a.scrollHeight - a.clientHeight) * a.clientHeight)
    )[0] || overlay;

    const before = root.scrollTop;
    const maxTop = Math.max(0, root.scrollHeight - root.clientHeight);
    root.scrollTop = Math.max(0, Math.min(maxTop, before + delta));
    root.dispatchEvent(new Event('scroll', {bubbles: true}));

    return {
        before,
        after: root.scrollTop,
        maxTop,
        clientHeight: root.clientHeight,
        scrollHeight: root.scrollHeight
    };
}
"""


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class FilterContainer:
    page: Page
    label: str
    element_id: str
    text: str
    box: Dict[str, float]

    def locator(self) -> Locator:
        return self.page.locator(f'[data-pbi-filter-id="{self.element_id}"]')


@dataclass
class OverlayRef:
    page: Page
    overlay_id: str
    owner_label: Optional[str]
    owner_box: Optional[Dict[str, float]]
    first_score: float

    def locator(self) -> Locator:
        return self.page.locator(f'[data-pbi-overlay-id="{self.overlay_id}"]')


# ============================================================
# SNAPSHOT HELPERS
# ============================================================

def overlay_snapshot(page: Page) -> List[Dict[str, Any]]:
    selectors = [
        ".slicer-dropdown-menu",
        "[role='listbox']",
        "[role='tree']",
        "[role='menu']",
        "[role='dialog']",
        ".cdk-overlay-pane",
        ".floatingPortal",
    ]
    try:
        return page.evaluate(OVERLAY_SNAPSHOT_JS, [selectors])
    except Exception:
        return []


def rect_area(box: Optional[Dict[str, float]]) -> float:
    if not box:
        return 0.0
    return max(0.0, float(box.get("width", 0))) * max(0.0, float(box.get("height", 0)))


def horizontal_overlap_ratio(a: Dict[str, float], b: Dict[str, float]) -> float:
    left = max(float(a.get("left", a.get("x", 0))), float(b.get("left", b.get("x", 0))))
    right = min(float(a.get("right", a.get("x", 0) + a.get("width", 0))), float(b.get("right", b.get("x", 0) + b.get("width", 0))))
    overlap = max(0.0, right - left)
    denom = max(1.0, min(float(a.get("width", 1)), float(b.get("width", 1))))
    return overlap / denom


def overlay_score(
    candidate: Dict[str, Any],
    owner_box: Optional[Dict[str, float]] = None,
    before_ids: Optional[Set[str]] = None,
    expected_text: Optional[str] = None,
) -> float:
    score = 0.0

    rect = candidate.get("rect") or {}
    area = rect_area(rect)

    role = (candidate.get("role") or "").lower()
    class_name = (candidate.get("className") or "").lower()
    text = candidate.get("text") or ""

    if before_ids:
        if candidate.get("id") not in before_ids:
            score += 32
        else:
            score -= 26

    if role in {"tree", "listbox", "menu", "dialog"}:
        score += 22
    elif role == "combobox":
        score -= 80

    if "slicer" in class_name or "dropdown" in class_name or "overlay" in class_name:
        score += 16

    score += min(28.0, area / 2500.0)
    score += min(20.0, float(candidate.get("optionCount") or 0) * 2.5)
    score += min(12.0, float(candidate.get("searchCount") or 0) * 6)

    if candidate.get("containsActive"):
        score += 25

    if expected_text:
        score += min(45.0, text_match_score(text, expected_text) * 0.45)

    if owner_box:
        overlap = horizontal_overlap_ratio(rect, owner_box)
        score += overlap * 38

        owner_bottom = float(owner_box.get("bottom", owner_box.get("y", 0) + owner_box.get("height", 0)))
        dy = abs(float(rect.get("top", 0)) - owner_bottom)
        if dy < 12:
            score += 28
        elif dy < 80:
            score += 18
        elif dy < 220:
            score += 8

        owner_center_x = float(owner_box.get("left", owner_box.get("x", 0))) + float(owner_box.get("width", 0)) / 2
        rect_center_x = float(rect.get("left", rect.get("x", 0))) + float(rect.get("width", 0)) / 2
        if abs(owner_center_x - rect_center_x) < max(80, float(owner_box.get("width", 0))):
            score += 8

    if not text.strip() and not candidate.get("optionCount") and not candidate.get("searchCount"):
        score -= 45

    if role == "combobox" and not candidate.get("optionCount") and not candidate.get("searchCount"):
        score -= 35

    return score


def overlay_ids(candidates: Iterable[Dict[str, Any]]) -> Set[str]:
    return {str(item.get("id")) for item in candidates if item.get("id")}


def find_active_overlay(
    page: Page,
    owner_box: Optional[Dict[str, float]] = None,
    owner_label: Optional[str] = None,
    before_ids: Optional[Set[str]] = None,
    expected_text: Optional[str] = None,
    timeout_ms: int = 9000,
) -> OverlayRef:
    section("FIND ACTIVE OVERLAY")

    deadline = time.monotonic() + timeout_ms / 1000
    best_ever: Optional[Dict[str, Any]] = None
    best_ever_score = -999.0

    while time.monotonic() < deadline:
        candidates = overlay_snapshot(page)
        best: Optional[Dict[str, Any]] = None
        best_score = -999.0

        for candidate in candidates:
            score = overlay_score(candidate, owner_box=owner_box, before_ids=before_ids, expected_text=expected_text)
            log(
                "OVERLAY "
                f"id={candidate.get('id')} role={candidate.get('role')} "
                f"area={rect_area(candidate.get('rect')):.0f} "
                f"options={candidate.get('optionCount')} search={candidate.get('searchCount')} "
                f"score={score:.1f} text={normalize_text(candidate.get('text', ''))[:80]}",
                event="overlay_candidate",
                overlay_id=candidate.get("id"),
                role=candidate.get("role"),
                score=round(score, 2),
                option_count=candidate.get("optionCount"),
                search_count=candidate.get("searchCount"),
                rect=candidate.get("rect"),
            )

            if score > best_score:
                best_score = score
                best = candidate

            if score > best_ever_score:
                best_ever_score = score
                best_ever = candidate

        if best and best_score >= 45 and (best.get("optionCount") or best.get("searchCount") or best.get("text")):
            log(
                f"ACTIVE OVERLAY SELECTED: {best.get('id')} score={best_score:.1f}",
                event="overlay_selected",
                overlay_id=best.get("id"),
                score=round(best_score, 2),
                owner_label=owner_label,
            )
            return OverlayRef(
                page=page,
                overlay_id=str(best["id"]),
                owner_label=owner_label,
                owner_box=owner_box,
                first_score=best_score,
            )

        page.wait_for_timeout(250)

    if best_ever and best_ever_score >= 30 and (best_ever.get("optionCount") or best_ever.get("searchCount") or best_ever.get("text")):
        log(
            f"FALLBACK OVERLAY SELECTED: {best_ever.get('id')} score={best_ever_score:.1f}",
            event="overlay_selected_fallback",
            level="warning",
            overlay_id=best_ever.get("id"),
            score=round(best_ever_score, 2),
            owner_label=owner_label,
        )
        return OverlayRef(
            page=page,
            overlay_id=str(best_ever["id"]),
            owner_label=owner_label,
            owner_box=owner_box,
            first_score=best_ever_score,
        )

    raise RuntimeError("No active overlay found")


def resolve_overlay(overlay: OverlayRef, expected_text: Optional[str] = None) -> OverlayRef:
    loc = overlay.locator()
    try:
        if loc.count() > 0 and loc.first.is_visible():
            snapshot = overlay_snapshot(overlay.page)
            current = next((item for item in snapshot if item.get("id") == overlay.overlay_id), None)
            if current:
                score = overlay_score(current, owner_box=overlay.owner_box, expected_text=expected_text)
                if score >= 25 and (current.get("optionCount") or current.get("searchCount") or current.get("text")):
                    return overlay
                log(
                    f"OVERLAY REACQUIRE: weak current score={score:.1f} id={overlay.overlay_id}",
                    event="overlay_reacquire_needed",
                    level="warning",
                    overlay_id=overlay.overlay_id,
                    score=round(score, 2),
                )
            else:
                log(
                    f"OVERLAY REACQUIRE: tagged overlay missing id={overlay.overlay_id}",
                    event="overlay_reacquire_needed",
                    level="warning",
                    overlay_id=overlay.overlay_id,
                )
    except Exception:
        pass

    return find_active_overlay(
        overlay.page,
        owner_box=overlay.owner_box,
        owner_label=overlay.owner_label,
        expected_text=expected_text,
        timeout_ms=5000,
    )


# ============================================================
# DASHBOARD AND FILTER PANEL
# ============================================================

def open_dashboard(page: Page) -> None:
    section("OPEN DASHBOARD")

    page.goto(POWERBI_URL, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_load_state("domcontentloaded", timeout=120000)

    section("WAIT INITIAL POWER BI HYDRATION")
    try:
        page.wait_for_selector(".visualContainer", state="visible", timeout=90000)
    except PlaywrightTimeoutError:
        pass

    wait_for_dom_quiet(page, quiet_ms=1200, timeout_ms=25000)


def visible_visual_texts(page: Page, timeout_ms: int = 1200) -> List[str]:
    texts: List[str] = []
    containers = page.locator(".visualContainer")

    try:
        count = containers.count()
    except Exception:
        return texts

    for index in range(count):
        try:
            container = containers.nth(index)
            if not container.is_visible(timeout=timeout_ms):
                continue
            text = container.inner_text(timeout=timeout_ms)
            if text.strip():
                texts.append(text)
        except Exception:
            continue

    return texts


def filters_panel_is_open(page: Page) -> bool:
    normalized_text = "\n".join(normalize_text(text) for text in visible_visual_texts(page, timeout_ms=700))
    hits = sum(1 for label in FILTER_LABELS if normalize_text(label) in normalized_text)
    return hits >= 2


def open_filters_panel(page: Page) -> None:
    section("ENSURE FILTERS PANEL OPEN")

    if filters_panel_is_open(page):
        log("FILTERS PANEL ALREADY OPEN")
        return

    last_count = 0
    deadline = time.monotonic() + 15

    while time.monotonic() < deadline:
        containers = page.locator(".visualContainer")
        count = containers.count()
        last_count = count
        log(f"CONTAINERS: {count}")

        candidates: List[Tuple[float, Locator, str]] = []

        for index in range(count):
            try:
                container = containers.nth(index)
                if not container.is_visible(timeout=1000):
                    continue
                text = container.inner_text(timeout=1500)
                normalized = normalize_text(text)
                if "FILTROS" not in normalized:
                    continue
                box = container.bounding_box(timeout=1000)
                if not box:
                    continue
                combo_count = container.locator("[role='combobox']").count()
                score = 100.0 + float(box.get("x", 0)) / 100.0 - combo_count * 20.0
                candidates.append((score, container, text))
            except Exception as exc:
                log(f"FILTERS CANDIDATE READ FAILED index={index}: {exc}")
                continue

        if not candidates:
            page.wait_for_timeout(500)
            continue

        candidates.sort(key=lambda item: item[0], reverse=True)

        for _, candidate, text in candidates:
            try:
                box = candidate.bounding_box(timeout=1000)
                if not box:
                    continue
                log(f"CLICK FILTERS: {normalize_text(text)[:120]}")
                page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)

                open_deadline = time.monotonic() + 10
                while time.monotonic() < open_deadline:
                    page.wait_for_timeout(300)
                    if filters_panel_is_open(page):
                        log("FILTERS PANEL OPENED")
                        return
            except Exception as exc:
                log(f"FILTER PANEL CLICK FAILED: {exc}")

    raise RuntimeError(f"No se encontro el boton/panel de filtros. Containers={last_count}")


# ============================================================
# FILTER CONTAINER
# ============================================================

def tag_filter_container(container: Locator) -> str:
    return container.evaluate(
        """
        (el) => {
            let id = el.getAttribute('data-pbi-filter-id');
            if (!id) {
                id = `pbi-filter-${Date.now()}-${Math.random().toString(36).slice(2)}`;
                el.setAttribute('data-pbi-filter-id', id);
            }
            return id;
        }
        """
    )


def find_filter_container_stable(page: Page, label: str, timeout_ms: int = 15000) -> FilterContainer:
    section(f"FIND FILTER -> {label}")

    target = normalize_text(label)
    deadline = time.monotonic() + timeout_ms / 1000
    last_signature: Optional[Tuple[str, str]] = None
    stable_seen = 0
    last_candidate: Optional[FilterContainer] = None

    while time.monotonic() < deadline:
        containers = page.locator(".visualContainer")

        try:
            count = containers.count()
        except Exception:
            page.wait_for_timeout(250)
            continue

        scored: List[Tuple[float, FilterContainer]] = []

        for index in range(count):
            try:
                container = containers.nth(index)
                if not container.is_visible(timeout=700):
                    continue

                text = container.inner_text(timeout=1000)
                normalized = normalize_text(text)
                if target not in normalized:
                    continue

                combo_count = container.locator(
                    "[role='combobox'], [aria-haspopup], [aria-expanded], input"
                ).count()
                if combo_count <= 0:
                    continue

                box = container.bounding_box(timeout=1000)
                if not box:
                    continue

                element_id = tag_filter_container(container)
                score = 100.0 + combo_count * 14.0 + float(box.get("x", 0)) / 50.0
                score -= min(20.0, len(normalized) / 200.0)

                scored.append(
                    (
                        score,
                        FilterContainer(
                            page=page,
                            label=label,
                            element_id=element_id,
                            text=text,
                            box=box,
                        ),
                    )
                )
            except Exception:
                continue

        if scored:
            scored.sort(key=lambda item: item[0], reverse=True)
            last_candidate = scored[0][1]
            signature = (
                last_candidate.element_id,
                compact_hash(normalize_text(last_candidate.text)),
            )

            log(
                f"CANDIDATE id={last_candidate.element_id} "
                f"box={last_candidate.box} text={normalize_text(last_candidate.text)[:140]}"
            )

            if signature == last_signature:
                stable_seen += 1
            else:
                last_signature = signature
                stable_seen = 1

            if stable_seen >= 2:
                return last_candidate

        page.wait_for_timeout(300)

    if last_candidate:
        return last_candidate

    raise RuntimeError(f"No se encontro filtro: {label}")


def resolve_filter_container(page: Page, container_or_target: Any) -> FilterContainer:
    if isinstance(container_or_target, FilterContainer):
        loc = container_or_target.locator()
        try:
            if loc.count() > 0 and loc.first.is_visible():
                text = loc.first.inner_text(timeout=1000)
                if normalize_text(container_or_target.label) in normalize_text(text):
                    box = loc.first.bounding_box(timeout=1000)
                    if box:
                        return FilterContainer(
                            page=page,
                            label=container_or_target.label,
                            element_id=container_or_target.element_id,
                            text=text,
                            box=box,
                        )
        except Exception:
            pass

        return find_filter_container_stable(page, container_or_target.label)

    if isinstance(container_or_target, str):
        return find_filter_container_stable(page, container_or_target)

    # Legacy Locator support.
    try:
        text = container_or_target.inner_text(timeout=1000)
        box = container_or_target.bounding_box(timeout=1000)
        element_id = tag_filter_container(container_or_target)
        return FilterContainer(
            page=page,
            label="",
            element_id=element_id,
            text=text,
            box=box or {},
        )
    except Exception as exc:
        raise RuntimeError(f"Cannot resolve filter container: {exc}") from exc


# ============================================================
# DROPDOWN OPENING
# ============================================================

def open_dropdown(page: Page, container: Any, expected_text: Optional[str] = None) -> OverlayRef:
    section("OPEN DROPDOWN")

    last_error: Optional[Exception] = None

    for attempt in range(1, 4):
        target = resolve_filter_container(page, container)
        locator = target.locator().first
        before = overlay_snapshot(page)
        before_ids = overlay_ids(before)

        try:
            click_targets = locator.evaluate(CLICK_TARGETS_JS)
        except Exception as exc:
            last_error = exc
            click_targets = []

        log(f"OPEN ATTEMPT {attempt}: CLICK TARGETS={len(click_targets)}")

        for click_target in click_targets:
            try:
                x = float(click_target["x"])
                y = float(click_target["y"])
                owner_box = click_target.get("box") or target.box

                log(f"CLICK {click_target.get('reason')} X={x:.1f} Y={y:.1f}")
                page.mouse.click(x, y)

                overlay = find_active_overlay(
                    page,
                    owner_box=owner_box,
                    owner_label=target.label,
                    before_ids=before_ids,
                    expected_text=expected_text,
                    timeout_ms=7000,
                )
                return overlay

            except Exception as exc:
                last_error = exc
                log(f"DROPDOWN TARGET FAILED: {exc}")
                close_overlay(page, strict=False)

        page.wait_for_timeout(500)

    raise RuntimeError(f"Could not open dropdown: {last_error}")


# ============================================================
# SEARCH INSIDE OVERLAY
# ============================================================

def search_value(overlay: OverlayRef, value: str, expected_text: Optional[str] = None) -> None:
    section(f"SEARCH -> {value}")

    overlay = resolve_overlay(overlay, expected_text=expected_text or value)
    loc = overlay.locator().first

    search_selectors = [
        "input.searchInput",
        "input[type='text']",
        "input",
        "textarea",
        "[contenteditable='true']",
    ]

    for selector in search_selectors:
        try:
            boxes = loc.locator(selector)
            count = boxes.count()
            log(f"{selector}: {count}")

            for index in range(count):
                sb = boxes.nth(index)
                try:
                    if not sb.is_visible(timeout=1000):
                        continue

                    sb.click(timeout=3000, force=True)
                    page = overlay.page
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    sb.fill(value, timeout=5000)

                    try:
                        actual_value = sb.input_value(timeout=1000)
                        log(f"SEARCHBOX VALUE: {actual_value}")
                    except Exception:
                        pass

                    wait_for_dom_quiet(page, quiet_ms=700, timeout_ms=8000)
                    log("SEARCH APPLIED")
                    return

                except Exception as exc:
                    log(f"SEARCHBOX FAILED: {exc}")
                    continue

        except Exception:
            continue

    log("NO SEARCHBOX FOUND")


# ============================================================
# VIRTUALIZED OPTION SELECTION
# ============================================================

def option_snapshots(overlay: OverlayRef, expected_text: Optional[str] = None) -> List[Dict[str, Any]]:
    overlay = resolve_overlay(overlay, expected_text=expected_text)
    try:
        return overlay.locator().first.evaluate(OPTIONS_SNAPSHOT_JS)
    except Exception:
        refreshed = resolve_overlay(overlay, expected_text=expected_text)
        overlay.overlay_id = refreshed.overlay_id
        return overlay.locator().first.evaluate(OPTIONS_SNAPSHOT_JS)


def option_window_signature(options: Sequence[Dict[str, Any]]) -> str:
    rows = [
        normalize_text(option.get("text") or "")
        for option in options
        if normalize_text(option.get("text") or "")
    ]
    return compact_hash("|".join(rows))


def wait_for_option_window_change(
    overlay: OverlayRef,
    previous_signature: str,
    timeout_ms: int = 1800,
) -> None:
    deadline = time.monotonic() + timeout_ms / 1000

    while time.monotonic() < deadline:
        try:
            current_options = option_snapshots(overlay)
            current_signature = option_window_signature(current_options)
            if current_signature and current_signature != previous_signature:
                log(
                    "VIRTUAL WINDOW UPDATED",
                    event="virtual_window_updated",
                    previous_signature=previous_signature,
                    current_signature=current_signature,
                    option_count=len(current_options),
                )
                return
        except Exception as exc:
            log(f"VIRTUAL WINDOW POLL FAILED: {exc}", event="virtual_window_poll_failed", level="warning")

        overlay.page.wait_for_timeout(100)


def wait_for_scroll_top(overlay: OverlayRef, target_top: float, timeout_ms: int = 2500) -> None:
    deadline = time.monotonic() + timeout_ms / 1000

    while time.monotonic() < deadline:
        try:
            state = overlay.locator().first.evaluate(SCROLL_STATE_JS)
            if abs(float(state.get("top", 0)) - target_top) <= 2:
                return
        except Exception:
            pass

        overlay.page.wait_for_timeout(100)


def reset_overlay_scroll(overlay: OverlayRef) -> None:
    try:
        overlay.locator().first.evaluate(SCROLL_BY_JS, -10_000_000)
        wait_for_scroll_top(overlay, 0)
    except Exception:
        pass


def scroll_overlay(overlay: OverlayRef, delta: int = 220) -> Dict[str, Any]:
    overlay = resolve_overlay(overlay)
    try:
        loc = overlay.locator().first
        state = loc.evaluate(SCROLL_STATE_JS)
        client_height = int(state.get("clientHeight") or 0)
        effective_delta = min(delta, max(80, int(client_height * 0.45))) if client_height else delta

        result = loc.evaluate(SCROLL_BY_JS, effective_delta)

        # Some Power BI virtualized panes only materialize rows from wheel events.
        # Use the wheel as a fallback only when programmatic scroll did not move.
        if abs(float(result.get("after", -1)) - float(result.get("before", -1))) < 2:
            box = state.get("box") or {}
            if box:
                before_wheel = float(result.get("after", result.get("before", state.get("top", 0))))
                overlay.page.mouse.move(box["left"] + box["width"] / 2, box["top"] + box["height"] / 2)
                overlay.page.mouse.wheel(0, effective_delta)
                overlay.page.wait_for_timeout(180)
                after_wheel = loc.evaluate(SCROLL_STATE_JS)
                result = {
                    "before": before_wheel,
                    "after": after_wheel.get("top", before_wheel),
                    "maxTop": after_wheel.get("maxTop", -1),
                    "clientHeight": after_wheel.get("clientHeight", 0),
                    "scrollHeight": after_wheel.get("scrollHeight", 0),
                }

        log(
            "SCROLL STATE "
            f"before={result.get('before')} after={result.get('after', result.get('top'))} "
            f"max={result.get('maxTop')} height={result.get('clientHeight')}",
            event="overlay_scroll",
            before=result.get("before"),
            after=result.get("after", result.get("top")),
            max_top=result.get("maxTop"),
            client_height=result.get("clientHeight"),
        )
        return result
    except Exception as exc:
        log(f"SCROLL FAILED: {exc}", event="overlay_scroll_failed", level="warning")
        overlay.page.mouse.wheel(0, delta)
        return {"before": -1, "after": -1, "maxTop": -1}


def click_option_candidate(page: Page, candidate: Dict[str, Any]) -> None:
    option_id = candidate["id"]
    loc = page.locator(f'[data-pbi-option-id="{option_id}"]').first
    box = loc.bounding_box(timeout=3000)

    if not box:
        raise RuntimeError(f"Option has no bounding box: {candidate.get('text')}")

    # In Power BI slicers the checkbox/hit target is usually near the left edge.
    x = box["x"] + min(max(14.0, box["width"] * 0.08), 34.0)
    y = box["y"] + box["height"] / 2

    page.mouse.click(x, y)


def click_option(overlay: OverlayRef, text: str, max_scrolls: int = 100) -> None:
    section(f"CLICK OPTION -> {text}")

    page = overlay.page
    target_norm = normalize_text(text)

    reset_overlay_scroll(overlay)

    seen_texts: Set[str] = set()
    stagnant_scrolls = 0
    best_seen: Optional[Tuple[float, str]] = None

    for scroll_index in range(max_scrolls):
        overlay = resolve_overlay(overlay, expected_text=text)
        options = option_snapshots(overlay, expected_text=text)
        previous_signature = option_window_signature(options)

        log(
            f"SCROLL ITERATION {scroll_index + 1}: OPTIONS={len(options)}",
            event="option_scan_iteration",
            iteration=scroll_index + 1,
            option_count=len(options),
            signature=previous_signature,
            target=target_norm,
        )

        scored: List[Tuple[float, Dict[str, Any]]] = []
        new_text_this_round = False

        for option in options:
            option_text = option.get("text") or ""
            normalized_option = normalize_text(option_text)
            if not normalized_option:
                continue

            if normalized_option not in seen_texts:
                new_text_this_round = True
                seen_texts.add(normalized_option)

            score = text_match_score(option_text, text)
            if score > 0:
                scored.append((score, option))

            if not best_seen or score > best_seen[0]:
                best_seen = (score, option_text)

            log(
                f"OPTION score={score:.1f} selected={option.get('selected')} text={normalized_option[:120]}",
                event="option_candidate",
                score=round(score, 2),
                selected=option.get("selected"),
                text=normalized_option,
                target=target_norm,
            )

        if scored:
            scored.sort(key=lambda item: (item[0], -len(normalize_text(item[1].get("text", "")))), reverse=True)
            best_score, best = scored[0]

            if best_score >= 78:
                log(
                    f"MATCH FOUND score={best_score:.1f}: {best.get('text')}",
                    event="option_match",
                    score=round(best_score, 2),
                    text=best.get("text"),
                    target=target_norm,
                )
                try:
                    before_events = querydata_event_counter
                    click_option_candidate(page, best)
                    wait_powerbi_idle(page, previous_event_count=before_events, timeout_ms=22000)
                    return
                except Exception as exc:
                    log(
                        f"MATCH CLICK LOST TO RERENDER: {exc}",
                        event="option_click_rerender_retry",
                        level="warning",
                        target=target_norm,
                    )
                    overlay = resolve_overlay(overlay, expected_text=text)
                    continue

        scroll_result = scroll_overlay(overlay, delta=220)
        wait_for_option_window_change(overlay, previous_signature)

        before = float(scroll_result.get("before", -1))
        after = float(scroll_result.get("after", -1))
        max_top = float(scroll_result.get("maxTop", -1))

        if not new_text_this_round and abs(after - before) < 2:
            stagnant_scrolls += 1
        else:
            stagnant_scrolls = 0

        if max_top >= 0 and after >= max_top - 2 and not new_text_this_round:
            stagnant_scrolls += 1

        if stagnant_scrolls >= 6:
            break

    sample = "\n".join(sorted(list(seen_texts))[:40])
    best_msg = f" Best fuzzy candidate: score={best_seen[0]:.1f} text={best_seen[1]}" if best_seen else ""
    raise RuntimeError(f"No se encontro opcion '{target_norm}'.{best_msg}\nSeen sample:\n{sample}")


# ============================================================
# CLOSE AND VALIDATE
# ============================================================

def close_overlay(page: Page, strict: bool = True) -> None:
    section("CLOSE OVERLAY")

    for _ in range(2):
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(350)
        except Exception:
            pass

    if not strict:
        return

    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        active = overlay_snapshot(page)
        if not active:
            return
        try:
            page.mouse.click(8, 8)
        except Exception:
            pass
        page.keyboard.press("Escape")
        page.wait_for_timeout(250)


def validate_filter_selected(page: Page, label: str, expected: str, timeout_ms: int = 18000) -> None:
    section(f"VALIDATE -> {label}")

    expected_norm = normalize_text(expected)
    deadline = time.monotonic() + timeout_ms / 1000
    last_text = ""

    while time.monotonic() < deadline:
        try:
            open_filters_panel(page)
            container = find_filter_container_stable(page, label, timeout_ms=5000)
            text = container.locator().first.inner_text(timeout=1500)
            last_text = text
            normalized = normalize_text(text)
            score = text_match_score(normalized, expected_norm)

            log(f"VALIDATION TEXT: {normalized[:300]}")
            log(f"VALIDATION SCORE: {score:.1f}")

            if expected_norm in normalized or score >= 78:
                log("VALIDATION OK")
                return

        except Exception as exc:
            log(f"VALIDATION RETRY: {exc}")

        page.wait_for_timeout(700)

    raise RuntimeError(
        f"Filtro invalido: {label}. Esperado={expected_norm}. Ultimo texto={normalize_text(last_text)}"
    )


# ============================================================
# APPLY FILTER
# ============================================================

def apply_filter(page: Page, label: str, search_value_text: str, expected_option: str, attempts: int = 3) -> None:
    section(f"APPLY FILTER -> {label}")

    last_error: Optional[Exception] = None

    for attempt in range(1, attempts + 1):
        try:
            set_active_action(
                "apply_filter",
                label=label,
                target=expected_option,
                search=search_value_text,
                attempt=attempt,
                phase="prepare",
            )
            log(
                f"APPLY ATTEMPT {attempt}/{attempts}",
                event="apply_filter_attempt",
                label=label,
                target=expected_option,
                attempt=attempt,
                attempts=attempts,
            )

            close_overlay(page, strict=True)
            open_filters_panel(page)

            set_active_action(
                "apply_filter",
                label=label,
                target=expected_option,
                search=search_value_text,
                attempt=attempt,
                phase="open_dropdown",
            )
            container = find_filter_container_stable(page, label)
            overlay = open_dropdown(page, container, expected_text=expected_option)

            set_active_action(
                "apply_filter",
                label=label,
                target=expected_option,
                search=search_value_text,
                attempt=attempt,
                phase="search",
            )
            search_value(overlay, search_value_text, expected_text=expected_option)

            # Search can rerender the overlay root. Re-own it before clicking.
            set_active_action(
                "apply_filter",
                label=label,
                target=expected_option,
                search=search_value_text,
                attempt=attempt,
                phase="select_option",
            )
            overlay = resolve_overlay(overlay, expected_text=expected_option)
            click_option(overlay, expected_option)

            close_overlay(page, strict=True)
            wait_rerender(page, previous_event_count=None, seconds=8)

            set_active_action(
                "apply_filter",
                label=label,
                target=expected_option,
                search=search_value_text,
                attempt=attempt,
                phase="validate",
            )
            validate_filter_selected(page, label, expected_option)
            mark_filter_applied(label, expected_option)
            clear_active_action()
            return

        except Exception as exc:
            last_error = exc
            log(
                f"APPLY FILTER FAILED: {exc}",
                event="apply_filter_failed",
                level="warning",
                label=label,
                target=expected_option,
                attempt=attempt,
            )
            close_overlay(page, strict=False)
            wait_for_dom_quiet(page, quiet_ms=800, timeout_ms=6000)

            try:
                page.screenshot(path=str(DEBUG_DIR / f"failed_{normalize_text(label)}_{attempt}.png"), full_page=True)
            except Exception:
                pass

    clear_active_action()
    raise RuntimeError(f"Could not apply filter '{label}': {last_error}")


def reset_grupo_producto(page: Page) -> None:
    section("RESET GRUPO PRODUCTO")

    last_error: Optional[Exception] = None

    for attempt in range(1, 4):
        try:
            set_active_action(
                "reset_filter",
                label="Grupo Producto",
                target="Seleccionar todo",
                search="Seleccionar",
                attempt=attempt,
                phase="prepare",
            )
            close_overlay(page, strict=True)
            open_filters_panel(page)

            set_active_action(
                "reset_filter",
                label="Grupo Producto",
                target="Seleccionar todo",
                search="Seleccionar",
                attempt=attempt,
                phase="open_dropdown",
            )
            container = find_filter_container_stable(page, "Grupo Producto")
            overlay = open_dropdown(page, container, expected_text="Seleccionar todo")

            # Some versions show "Seleccionar todo" without a searchbox.
            set_active_action(
                "reset_filter",
                label="Grupo Producto",
                target="Seleccionar todo",
                search="Seleccionar",
                attempt=attempt,
                phase="search",
            )
            search_value(overlay, "Seleccionar", expected_text="Seleccionar todo")
            set_active_action(
                "reset_filter",
                label="Grupo Producto",
                target="Seleccionar todo",
                search="Seleccionar",
                attempt=attempt,
                phase="select_option",
            )
            overlay = resolve_overlay(overlay, expected_text="Seleccionar todo")
            click_option(overlay, "Seleccionar todo", max_scrolls=20)

            close_overlay(page, strict=True)
            wait_rerender(page, previous_event_count=None, seconds=8)
            set_active_action(
                "reset_filter",
                label="Grupo Producto",
                target="ALL",
                search="Seleccionar",
                attempt=attempt,
                phase="validate",
            )
            validate_filter_selected(page, "Grupo Producto", "ALL")
            mark_filter_applied("Grupo Producto", "ALL")
            clear_active_action()
            return

        except Exception as exc:
            last_error = exc
            log(
                f"RESET GRUPO PRODUCTO FAILED attempt={attempt}: {exc}",
                event="reset_filter_failed",
                level="warning",
                label="Grupo Producto",
                attempt=attempt,
            )
            close_overlay(page, strict=False)
            wait_for_dom_quiet(page, quiet_ms=800, timeout_ms=6000)

    clear_active_action()
    raise RuntimeError(f"Could not reset Grupo Producto: {last_error}")


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(DEFAULT_TIMEOUT_MS)

        page.on("request", handle_request)
        page.on("response", handle_response)

        try:
            open_dashboard(page)
            open_filters_panel(page)

            apply_filter(
                page=page,
                label="MACROREGION",
                search_value_text="NORTE",
                expected_option="NORTE",
            )

            apply_filter(
                page=page,
                label="Institucion",
                search_value_text="GOBIERNO",
                expected_option="GOBIERNO REGIONAL",
            )

            apply_filter(
                page=page,
                label="Unidad ejecutora",
                search_value_text="LUCIANO",
                expected_option="SALUD LUCIANO CASTILLO COLONNA",
            )

            reset_grupo_producto(page)

            section("FINAL WAIT")
            wait_for_querydata_quiet(page, querydata_event_counter, quiet_ms=1500, timeout_ms=20000)

            section("SUMMARY")
            log(f"SESSION ID: {SESSION_ID}")
            log(f"QUERYDATA REQUESTS: {querydata_request_counter}")
            log(f"QUERYDATA RESPONSES: {querydata_response_counter}")
            log(f"RUN DIR: {RUN_DIR.resolve()}")

            if KEEP_BROWSER_OPEN:
                input("\nENTER PARA CERRAR...")

        finally:
            browser.close()


if __name__ == "__main__":
    main()
