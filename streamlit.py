"""
Student Hub - Streamlit version of student_hub.html
Talks to the same FastAPI backend (default http://127.0.0.1:8000).

Run:
    pip install streamlit requests
    streamlit run app.py

Optional: set a different backend with the env var STUDENT_HUB_API
or on the Settings page.
"""
import html as _html
import math
import os
import re

import requests
import streamlit as st

st.set_page_config(page_title="Student Hub", page_icon="🎓", layout="wide")

DEFAULT_BASE = os.environ.get("STUDENT_HUB_API", "http://127.0.0.1:8000")
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")

# --------------------------------------------------------------------------
# State
# --------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("base", DEFAULT_BASE)
ss.setdefault("page", "Dashboard")
ss.setdefault("cache", None)
ss.setdefault("as_q", "")
ss.setdefault("as_course", "All")
ss.setdefault("as_sort", "Default")
ss.setdefault("as_order", "asc")
ss.setdefault("as_limit", 10)
ss.setdefault("as_page", 1)
ss.setdefault("add_ver", 0)
ss.setdefault("add_msg", None)
ss.setdefault("del_msg", None)
ss.setdefault("set_msg", None)

# --------------------------------------------------------------------------
# Styling (ported from the HTML file)
# --------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{--ink:#0f172a;--mut:#64748b;--line:#e5e7eb;--bg:#f6f7fb;--ind:#4f46e5}
html,body,.stApp,[class*="css"]{font-family:Inter,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.stApp{background:var(--bg);color:var(--ink)}
#MainMenu,footer{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1280px;padding:1.2rem 2rem 3rem}

/* sidebar */
section[data-testid="stSidebar"]{background:#0b1220;border-right:1px solid #172033;width:252px!important}
section[data-testid="stSidebar"] > div{padding-top:0}
section[data-testid="stSidebar"] *{color:#94a3b8}
.brand{display:flex;gap:12px;align-items:center;padding:4px 8px 18px}
.logo{width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6366f1,#4338ca);display:flex;align-items:center;justify-content:center;color:#fff!important;box-shadow:0 4px 12px rgba(79,70,229,.45)}
.logo svg{stroke:#fff}
.bn{color:#fff!important;font-weight:700;font-size:1rem;line-height:1.2}.bs{font-size:.72rem;color:#64748b!important}
.sec{font-size:.68rem;letter-spacing:.9px;text-transform:uppercase;color:#475569!important;font-weight:600;padding:10px 12px 4px}
section[data-testid="stSidebar"] .stButton{margin-bottom:-8px}
section[data-testid="stSidebar"] .stButton button{width:100%;justify-content:flex-start;gap:8px;background:transparent;border:0;color:#94a3b8;font-weight:500;padding:.55rem .75rem;border-radius:9px;box-shadow:none}
section[data-testid="stSidebar"] .stButton button:hover{background:#131c2e;color:#e2e8f0}
section[data-testid="stSidebar"] .stButton button:hover *{color:#e2e8f0}
section[data-testid="stSidebar"] .stButton button[kind="primary"],
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"]{background:rgba(99,102,241,.16);color:#fff;border:0}
section[data-testid="stSidebar"] .stButton button[kind="primary"] *,
section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] *{color:#fff!important}
.foot{margin-top:24px;padding:12px;border:1px solid #172033;border-radius:10px;background:#0e1626;font-size:.75rem}
.foot code{color:#cbd5e1!important;word-break:break-all;background:transparent}

/* top bar */
.topbar{display:flex;align-items:center;justify-content:space-between;background:#fff;border:1px solid var(--line);border-radius:12px;padding:10px 20px;margin-bottom:22px}
.crumb{color:var(--mut)}.crumb b{color:var(--ink);font-weight:600}.tr-r{display:flex;align-items:center;gap:14px}
.pill{display:inline-flex;align-items:center;gap:7px;padding:5px 12px;border-radius:999px;font-size:.78rem;font-weight:600;border:1px solid var(--line);background:#fff;white-space:nowrap}
.pill i{width:8px;height:8px;border-radius:50%;background:#94a3b8}.pill.on i{background:#22c55e;box-shadow:0 0 0 3px #dcfce7}.pill.off i{background:#ef4444;box-shadow:0 0 0 3px #fee2e2}
.me{width:34px;height:34px;border-radius:50%;background:#e0e7ff;color:#4338ca;font-weight:700;display:flex;align-items:center;justify-content:center}

/* headings & cards */
.hd h1{margin:0;font-size:1.6rem;font-weight:700;letter-spacing:-.02em;padding:0}.hd p{margin:4px 0 20px;color:var(--mut)}
h3{font-weight:600;font-size:1.05rem;margin:0 0 10px;padding:0}h4{margin:0 0 12px;font-weight:600;font-size:.95rem;padding:0}
.card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;box-shadow:0 1px 2px rgba(16,24,40,.04);margin-bottom:16px}
.card.p0{padding:0;overflow:hidden}.tw{overflow-x:auto}
.stat{transition:box-shadow .15s,transform .15s}.stat:hover{box-shadow:0 8px 20px rgba(16,24,40,.08);transform:translateY(-1px)}
.chip-i{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.lbl{font-size:.74rem;text-transform:uppercase;letter-spacing:.6px;color:var(--mut);font-weight:600}
.val{font-size:1.85rem;font-weight:700;letter-spacing:-.02em;line-height:1.25}.sub{font-size:.78rem;color:#94a3b8;min-height:1.1em}
.g5{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:16px}
.g3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:16px}
.g5>*,.g3>*{min-width:0}.g5>.card,.g3>.card{margin-bottom:0}
.muted{color:var(--mut);font-size:.9rem}

/* table */
.card table{width:100%;border-collapse:collapse;margin:0}
.card th{background:#f8fafc;font-size:.72rem;text-transform:uppercase;letter-spacing:.5px;color:var(--mut);font-weight:600;text-align:left;padding:12px 16px;border-bottom:1px solid var(--line)}
.card td{padding:12px 16px;border-bottom:1px solid #f1f5f9;vertical-align:middle}
.card tbody tr:last-child td{border:0}.card tbody tr:hover{background:#fafbff}
.who{display:flex;gap:12px;align-items:center}.who small{display:block;color:var(--mut)}
.sm{width:34px;height:34px;border-radius:50%;background:#eef2ff;color:#4338ca;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.mono{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:.82rem;color:#475569}
.chip{background:#f1f5f9;color:#334155;padding:3px 10px;border-radius:6px;font-size:.78rem;font-weight:500;white-space:nowrap}
.mk{display:flex;align-items:center;gap:10px}.mk b{width:28px}.mk .tr{width:70px;flex:none}
.badge{display:inline-flex;align-items:center;gap:6px;padding:3px 10px;border-radius:999px;font-size:.76rem;font-weight:600}
.badge::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.badge.g{background:#dcfce7;color:#15803d}.badge.b{background:#e0e7ff;color:#4338ca}.badge.a{background:#fef3c7;color:#b45309}.badge.r{background:#fee2e2;color:#b91c1c}.badge.n{background:#f1f5f9;color:#475569}

/* profile */
.prof{display:flex;gap:16px;align-items:center}.prof h3{margin:0 0 2px;display:flex;align-items:center;gap:10px}
.av{width:60px;height:60px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#4338ca);color:#fff;display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:700;flex-shrink:0}
.pg{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:18px;padding-top:16px;border-top:1px solid var(--line)}
.pg small{display:block;color:var(--mut);font-size:.72rem;text-transform:uppercase;letter-spacing:.5px}.pg b{font-weight:600}

/* alerts */
.alert{padding:12px 14px;border-radius:10px;border:1px solid;border-left-width:4px;margin-bottom:14px}
.alert.err{background:#fef2f2;border-color:#fca5a5;color:#991b1b}.alert.warn{background:#fffbeb;border-color:#fcd34d;color:#92400e}.alert.ok{background:#f0fdf4;border-color:#86efac;color:#166534}
.fe{color:#dc2626;font-size:.78rem;min-height:1.1em;margin:-8px 0 8px}

/* charts */
.bar{display:flex;align-items:center;gap:10px;margin:9px 0}.bl{width:112px;flex-shrink:0;color:var(--mut);font-size:.8rem;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tr{flex:1;height:8px;background:#eef2f7;border-radius:99px;overflow:hidden}.tr i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#6366f1,#818cf8)}
.bv{width:40px;flex-shrink:0;text-align:right;font-weight:600;font-size:.8rem}
.dn{display:flex;align-items:center;gap:20px;flex-wrap:wrap}.ring{width:120px;height:120px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0}
.ring>div{width:80px;height:80px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center}
.ring b{font-size:1.4rem;line-height:1}.ring small{color:var(--mut);font-size:.7rem}
.dn ul{list-style:none;margin:0;padding:0;flex:1}.dn li{display:flex;align-items:center;gap:8px;padding:3px 0}.dn li i{width:9px;height:9px;border-radius:3px}.dn li b{margin-left:auto}
.empty{text-align:center;padding:44px 20px;color:var(--mut)}.empty h4{color:var(--ink);margin:0 0 4px}
.ei{width:48px;height:48px;border-radius:12px;background:#f1f5f9;display:inline-flex;align-items:center;justify-content:center;margin-bottom:10px}

/* streamlit widgets */
div[data-testid="stForm"]{background:#fff;border:1px solid var(--line);border-radius:12px;padding:20px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
div[data-baseweb="input"],div[data-baseweb="select"]>div,div[data-baseweb="base-input"]{border-radius:9px!important}
.stTextInput label,.stNumberInput label,.stSelectbox label,.stCheckbox label{font-weight:600;font-size:.82rem;color:#334155}
.main .stButton button,div[data-testid="stForm"] button{height:40px;border-radius:9px;font-weight:600;border:1px solid #d5dbe5;background:#fff;color:#334155}
.main .stButton button:hover{background:#f8fafc;border-color:#c3cad6;color:#334155}
.main .stButton button[kind="primary"],div[data-testid="stForm"] button[kind="primary"],
.main .stButton button[data-testid="stBaseButton-primary"],div[data-testid="stForm"] button[data-testid="stBaseButton-primary"],
div[data-testid="stForm"] button[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--ind);border-color:var(--ind);color:#fff}
.main .stButton button[kind="primary"]:hover,.main .stButton button[data-testid="stBaseButton-primary"]:hover{background:#4338ca;color:#fff}
.main .stButton button:disabled{opacity:.5}
.st-key-del_btn button{background:#dc2626!important;border-color:#dc2626!important;color:#fff!important}
.st-key-del_btn button:hover{background:#b91c1c!important}
.st-key-del_btn button:disabled{opacity:.5}

@media(max-width:1100px){.g5{grid-template-columns:repeat(3,1fr)}.g3{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.g5,.g3{grid-template-columns:1fr}.pg{grid-template-columns:1fr 1fr}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def esc(s):
    return _html.escape("" if s is None else str(s), quote=True)


def md(s):
    """Render HTML; collapse indentation so Markdown never treats it as code."""
    st.markdown("".join(line.strip() for line in s.splitlines()), unsafe_allow_html=True)


def head(t, s):
    return f'<div class="hd"><h1>{t}</h1><p>{s}</p></div>'


def alert_box(m, kind="err"):
    return f'<div class="alert {kind}">{esc(m)}</div>'


GRADE_BADGE = {"A+": "g", "A": "g", "B": "b", "C": "a", "Fail": "r"}
GC = {"A+": "#16a34a", "A": "#22c55e", "B": "#6366f1", "C": "#f59e0b", "Fail": "#ef4444"}


def badge(g):
    return f'<span class="badge {GRADE_BADGE.get(g, "n")}">{esc(g)}</span>'


def num(x, default=0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def fmt(n):
    n = round(n, 1)
    return f"{n:g}"


ICO = {
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "pulse": '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    "up": '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>',
    "down": '<polyline points="22 17 13.5 8.5 8.5 13.5 2 7"/><polyline points="16 17 22 17 22 11"/>',
    "book": '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2zM22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
    "cap": '<path d="M22 10 12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/>',
}


def ico(n, z=18):
    return (f'<svg width="{z}" height="{z}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICO[n]}</svg>')


SI = {
    "Total Students": ("users", "#4f46e5", "#eef2ff"),
    "Average Marks": ("pulse", "#059669", "#ecfdf5"),
    "Highest Marks": ("up", "#0284c7", "#f0f9ff"),
    "Lowest Marks": ("down", "#d97706", "#fffbeb"),
    "Total Courses": ("book", "#7c3aed", "#f5f3ff"),
}


def empty_box(t, s):
    return f'<div class="card empty"><div class="ei">{ico("search", 22)}</div><h4>{t}</h4><div>{s}</div></div>'


def profile(s):
    name = s.get("name") or "?"
    return f"""
    <div class="card"><div class="prof"><div class="av">{esc(name[0].upper())}</div>
    <div><h3>{esc(s.get("name"))} {badge(s.get("grade"))}</h3><div class="muted">{esc(s.get("email"))}</div></div></div>
    <div class="pg"><div><small>Student ID</small><b>{esc(s.get("id"))}</b></div>
    <div><small>Course</small><b>{esc(s.get("course"))}</b></div>
    <div><small>Age</small><b>{esc(s.get("age"))}</b></div>
    <div><small>Marks</small><b>{esc(s.get("marks"))}</b></div></div></div>"""


def table(rows):
    body = ""
    for s in rows:
        name = s.get("name") or "?"
        w = max(0, min(100, num(s.get("marks"))))
        body += f"""<tr><td><div class="who"><div class="sm">{esc(name[0].upper())}</div>
        <div><b>{esc(s.get("name"))}</b><small>{esc(s.get("email"))}</small></div></div></td>
        <td class="mono">{esc(s.get("id"))}</td><td><span class="chip">{esc(s.get("course"))}</span></td>
        <td>{esc(s.get("age"))}</td>
        <td><div class="mk"><b>{esc(s.get("marks"))}</b><div class="tr"><i style="width:{w}%"></i></div></div></td>
        <td>{badge(s.get("grade"))}</td></tr>"""
    return ('<div class="card p0 tw"><table><thead><tr><th>Student</th><th>ID</th><th>Course</th>'
            f'<th>Age</th><th>Marks</th><th>Grade</th></tr></thead><tbody>{body}</tbody></table></div>')


def bars(title, items):
    mx = max([1] + [i["v"] for i in items])
    rows = "".join(
        f'<div class="bar"><span class="bl" title="{esc(i["l"])}">{esc(i["l"])}</span>'
        f'<div class="tr"><i style="width:{i["v"] / mx * 100}%"></i></div><span class="bv">{fmt(i["v"])}</span></div>'
        for i in items)
    return f'<div class="card"><h4>{title}</h4>{rows}</div>'


def donut(title, items):
    tot = sum(i["v"] for i in items)
    a, segs = 0.0, []
    for i in items:
        if i["v"]:
            s = a
            a += i["v"] / tot * 100
            segs.append(f'{GC[i["l"]]} {s}% {a}%')
    seg = ",".join(segs) or "#e5e7eb 0 100%"
    lis = "".join(f'<li><i style="background:{GC[i["l"]]}"></i>{i["l"]}<b>{i["v"]}</b></li>' for i in items)
    return (f'<div class="card"><h4>{title}</h4><div class="dn"><div class="ring" style="background:conic-gradient({seg})">'
            f'<div><b>{tot}</b><small>students</small></div></div><ul>{lis}</ul></div></div>')


# --------------------------------------------------------------------------
# API layer (real HTTP calls to FastAPI)
# --------------------------------------------------------------------------
def call(method, path, body=None):
    base = ss.base
    try:
        r = requests.request(method, base + path, json=body, timeout=8)
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "The backend did not respond within 8s."}
    except requests.exceptions.RequestException:
        return {"ok": False, "error": f"Cannot reach the backend at {base}. Is FastAPI running, and is CORS enabled in main.py?"}
    try:
        data = r.json()
    except ValueError:
        data = None
    if r.ok:
        if data is None:
            return {"ok": False, "status": r.status_code, "error": "Backend returned invalid JSON."}
        return {"ok": True, "status": r.status_code, "data": data}
    if r.status_code >= 500:
        return {"ok": False, "status": r.status_code,
                "error": "Server error (500). Check the FastAPI terminal for the traceback."}
    d = data.get("detail") if isinstance(data, dict) else None
    if d:
        if isinstance(d, list):
            msg = "; ".join(
                f'{".".join(str(l) for l in (x.get("loc") or []) if l != "body")}: {x.get("msg")}' for x in d)
        else:
            msg = str(d)
    else:
        msg = f"Unexpected response (HTTP {r.status_code})."
    if r.status_code == 404 and d == "Not Found":
        msg = f"Your backend has no such endpoint: {method} {path.split('?')[0]}"
    return {"ok": False, "status": r.status_code, "error": msg}


def grade_of(m):
    return "A+" if m >= 90 else "A" if m >= 80 else "B" if m >= 70 else "C" if m >= 60 else "Fail"


def norm(p):
    """dict {id:{..}}, list, wrapper or single student -> list of students with id."""
    rows = []
    if isinstance(p, list):
        rows = [dict(x) for x in p if isinstance(x, dict)]
    elif isinstance(p, dict):
        for k in ("students", "data", "items"):
            if isinstance(p.get(k), (dict, list)):
                return norm(p[k])
        v = list(p.values())
        if v and all(isinstance(x, dict) for x in v):
            rows = [{"id": k, **x} for k, x in p.items()]
        elif "name" in p:
            rows = [dict(p)]
    for r in rows:
        if r.get("grade") is None and isinstance(r.get("marks"), int):
            r["grade"] = grade_of(r["marks"])
    return rows


def wrap(r):
    if r["ok"]:
        r["data"] = norm(r["data"])
    return r


def q(v):
    return requests.utils.quote(str(v), safe="")


class A:
    @staticmethod
    def all():
        return wrap(call("GET", "/student"))

    @staticmethod
    def one(sid):
        r = call("GET", "/student/" + q(sid))
        if r["ok"]:
            rows = norm(r["data"])
            if not rows:
                return {"ok": False, "error": "Unexpected response from backend."}
            s = rows[0]
            s["id"] = s.get("id", sid)
            r["data"] = s
        return r

    @staticmethod
    def filter(c):
        return wrap(call("GET", "/filter?course=" + q(c)))

    @staticmethod
    def sort(s, o):
        return wrap(call("GET", f"/sort?sort_by={s}&order={o}"))

    @staticmethod
    def page(p, l):
        r = call("GET", f"/paginate?page={p}&limit={l}")
        if r["ok"]:
            r["total"] = r["data"].get("total_students") if isinstance(r["data"], dict) else None
            r["data"] = norm(r["data"])
        return r

    @staticmethod
    def create(b):
        return call("POST", "/create", b)

    @staticmethod
    def update(sid, b):
        return call("PUT", "/update/" + q(sid), b)  # partial: only changed fields

    @staticmethod
    def delete(sid):
        return call("DELETE", "/delete/" + q(sid))


def students(force=False):
    if force or ss.cache is None:
        r = A.all()
        if not r["ok"]:
            ss.cache = None
            return r
        ss.cache = r["data"]
    return {"ok": True, "data": ss.cache}


@st.cache_data(ttl=5, show_spinner=False)
def ping(base):
    try:
        return requests.get(base + "/openapi.json", timeout=3).ok
    except requests.exceptions.RequestException:
        return False


# --------------------------------------------------------------------------
# Validation (mirrors the backend rules)
# --------------------------------------------------------------------------
def to_int(x):
    if x is None:
        return None
    try:
        return int(x) if float(x).is_integer() else x
    except (TypeError, ValueError):
        return None


def validate(v, need_id=True):
    e = {}
    n = (v.get("name") or "").strip()
    if need_id and not ID_RE.match(v.get("id") or ""):
        e["id"] = "Student ID is required (letters, digits, - or _)."
    if len(n) < 2 or len(n) > 50:
        e["name"] = "Name must be 2-50 characters."
    elif not all(c.isalpha() or c == " " for c in n):
        e["name"] = "Name can contain only letters and spaces."
    age = v.get("age")
    if not (isinstance(age, int) and 0 < age <= 100):
        e["age"] = "Age must be between 1 and 100."
    course = v.get("course")
    if not course or len(course) > 50:
        e["course"] = "Course is required (max 50 characters)."
    marks = v.get("marks")
    if not (isinstance(marks, int) and 0 <= marks <= 100):
        e["marks"] = "Marks must be between 0 and 100."
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v.get("email") or ""):
        e["email"] = "Enter a valid email address."
    return e


def field_errors(placeholders, errors):
    for k, ph in placeholders.items():
        ph.markdown(f'<div class="fe">{esc(errors.get(k, ""))}</div>', unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Navigation
# --------------------------------------------------------------------------
PAGES = {
    "Dashboard": ":material/dashboard:",
    "All Students": ":material/groups:",
    "Add Student": ":material/person_add:",
    "Search Student": ":material/search:",
    "Update Student": ":material/edit:",
    "Delete Student": ":material/delete:",
    "Settings": ":material/tune:",
}
GROUPS = {"Dashboard": "Overview", "All Students": "Manage", "Settings": "System"}


def go(name):
    ss.page = name


with st.sidebar:
    md(f"""<div class="brand"><div class="logo">{ico("cap", 22)}</div>
    <div><div class="bn">Student Hub</div><div class="bs">Management Console</div></div></div>""")
    for name, icon in PAGES.items():
        if name in GROUPS:
            md(f'<div class="sec">{GROUPS[name]}</div>')
        st.button(name, icon=icon, key=f"nav_{name}", on_click=go, args=(name,),
                  type="primary" if ss.page == name else "secondary", use_container_width=True)
    md(f'<div class="foot"><div>API endpoint</div><code>{esc(ss.base)}</code></div>')

connected = ping(ss.base)
md(f"""<div class="topbar"><div class="crumb">Student Hub &nbsp;/&nbsp; <b>{ss.page}</b></div>
<div class="tr-r"><span class="pill {"on" if connected else "off"}"><i></i>{"Backend connected" if connected else "Backend offline"}</span>
<div class="me">A</div></div></div>""")


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------
def p_dash():
    h = head("Dashboard", "Live overview of your student records")
    md(h)
    with st.spinner("Loading…"):
        r = students(force=True)
    if not r["ok"]:
        return md(alert_box(r["error"]))
    s = r["data"]
    if not s:
        md(empty_box("No students yet", "Add your first student to get started."))
        return st.button("Add the first student", type="primary", on_click=go, args=("Add Student",))

    marks = [num(x.get("marks")) for x in s]
    hi = max(s, key=lambda x: num(x.get("marks")))
    lo = min(s, key=lambda x: num(x.get("marks")))

    def stat(label, value, sub=""):
        i, c, b = SI[label]
        return (f'<div class="card stat"><div class="chip-i" style="color:{c};background:{b}">{ico(i, 20)}</div>'
                f'<div class="lbl">{label}</div><div class="val">{esc(value)}</div><div class="sub">{esc(sub)}</div></div>')

    bins = [{"l": l, "v": 0} for l in ["Below 60", "60-69", "70-79", "80-89", "90-100"]]
    for x in marks:
        bins[max(0, min(math.floor(x / 10) - 5, 4))]["v"] += 1
    grades = [{"l": g, "v": sum(1 for x in s if x.get("grade") == g)} for g in ["A+", "A", "B", "C", "Fail"]]
    by_c = {}
    for x in s:
        by_c.setdefault(x.get("course"), []).append(num(x.get("marks")))
    avg_c = sorted(({"l": c, "v": sum(a) / len(a)} for c, a in by_c.items()), key=lambda d: -d["v"])[:6]
    n_courses = len({str(x.get("course")).strip().lower() for x in s})

    md(f"""<div class="g5">{stat("Total Students", len(s), "records in backend")}
    {stat("Average Marks", f"{sum(marks) / len(marks):.1f}", "across all students")}
    {stat("Highest Marks", hi.get("marks"), hi.get("name"))}
    {stat("Lowest Marks", lo.get("marks"), lo.get("name"))}
    {stat("Total Courses", n_courses, "distinct courses")}</div>
    <h3 style="margin:10px 0">Student Performance Analytics</h3>
    <div class="g3">{bars("Marks distribution", bins)}{donut("Grade distribution", grades)}{bars("Average marks by course", avg_c)}</div>""")

    left, right = st.columns([2, 1], gap="large")
    with left:
        md("<h3>Recent Students</h3>")
        md(table(list(reversed(s[-5:]))))
    with right:
        md("<h3>Quick Actions</h3>")
        st.button("Add New Student", type="primary", use_container_width=True, on_click=go, args=("Add Student",), key="qa1")
        st.button("Search Student", use_container_width=True, on_click=go, args=("Search Student",), key="qa2")
        st.button("View All Students", use_container_width=True, on_click=go, args=("All Students",), key="qa3")


def _reset_page():
    ss.as_page = 1


def _clear_filters():
    ss.as_q, ss.as_course, ss.as_sort, ss.as_order, ss.as_limit, ss.as_page = "", "All", "Default", "asc", 10, 1


def _refresh():
    ss.cache = None


def _prev():
    ss.as_page -= 1


def _next():
    ss.as_page += 1


def p_all():
    md(head("All Students", "Search, filter, sort and browse every record"))
    r = students()
    if not r["ok"]:
        return md(alert_box(r["error"]))
    courses = sorted({x.get("course") for x in r["data"] if x.get("course") is not None})
    course_opts = ["All"] + courses
    if ss.as_course not in course_opts:
        ss.as_course = "All"

    with st.container(border=True):
        c = st.columns([2, 1, 1, 1, 1, 0.8, 1], vertical_alignment="bottom")
        c[0].text_input("Search by ID or name", key="as_q", on_change=_reset_page)
        c[1].selectbox("Course", course_opts, key="as_course", on_change=_reset_page)
        c[2].selectbox("Sort by", ["Default", "marks", "age", "name"], key="as_sort", on_change=_reset_page)
        c[3].selectbox("Order", ["asc", "desc"], key="as_order", on_change=_reset_page)
        c[4].selectbox("Rows", [5, 10, 20, 50], key="as_limit", on_change=_reset_page)
        c[5].button("Refresh", on_click=_refresh, use_container_width=True)
        c[6].button("Clear filters", on_click=_clear_filters, use_container_width=True)

    query = ss.as_q.strip().lower()
    server = False
    with st.spinner("Loading…"):
        if ss.as_course != "All":
            res = A.filter(ss.as_course)
            note = f"Filtered by the backend (/filter?course={ss.as_course})."
        elif ss.as_sort != "Default":
            res = A.sort(ss.as_sort, ss.as_order)
            note = f"Sorted by the backend (/sort?sort_by={ss.as_sort}&order={ss.as_order})."
        elif query:
            res = students()
            note = "Search runs in the app over /student data (the backend has no search endpoint)."
        else:
            res = A.page(ss.as_page, ss.as_limit)
            server = True
            note = f"Paginated by the backend (/paginate?page={ss.as_page}&limit={ss.as_limit})."
    if not res["ok"]:
        return md(alert_box(res["error"]))

    rows = res["data"]
    if query:
        rows = [x for x in rows if query in str(x.get("id")).lower() or query in str(x.get("name")).lower()]
    if ss.as_sort != "Default" and ss.as_course != "All":
        k, rev = ss.as_sort, ss.as_order == "desc"
        rows = sorted(rows, key=(lambda x: str(x.get("name")).lower()) if k == "name" else (lambda x: num(x.get(k))),
                      reverse=rev)
        note += " Sorting applied in the app (/filter has no sort option)."

    total = res.get("total") if server else len(rows)
    if total is None:
        total = len(rows)
    pages = max(1, math.ceil(total / ss.as_limit))
    if ss.as_page > pages:
        ss.as_page = pages
    if not server:
        rows = rows[(ss.as_page - 1) * ss.as_limit: ss.as_page * ss.as_limit]

    md(table(rows) if rows else empty_box("No students match", "Try adjusting your search or filters."))
    pc = st.columns([1, 2.6, 1, 5], vertical_alignment="center")
    pc[0].button("← Prev", disabled=ss.as_page <= 1, on_click=_prev, use_container_width=True, key="pv")
    pc[1].markdown(f'<div class="muted" style="text-align:center">Page {ss.as_page} of {pages} · {total} students</div>',
                   unsafe_allow_html=True)
    pc[2].button("Next →", disabled=ss.as_page >= pages, on_click=_next, use_container_width=True, key="nx")
    md(f'<p class="muted">{esc(note)}</p>')


def p_add():
    md(head("Add Student", "Register a new student in the system"))
    v = ss.add_ver
    with st.form("add_form", border=False):
        f_id = st.text_input("Student ID", placeholder="S007", key=f"a_id_{v}")
        ph_id = st.empty()
        f_name = st.text_input("Full name", placeholder="Aarav Sharma", key=f"a_name_{v}")
        ph_name = st.empty()
        c1, c2 = st.columns(2)
        f_age = c1.number_input("Age", value=None, step=1, key=f"a_age_{v}")
        ph_age = c1.empty()
        f_marks = c2.number_input("Marks", value=None, step=1, key=f"a_marks_{v}")
        ph_marks = c2.empty()
        f_course = st.text_input("Course", placeholder="Python", key=f"a_course_{v}")
        ph_course = st.empty()
        f_email = st.text_input("Email", placeholder="name@example.com", key=f"a_email_{v}")
        ph_email = st.empty()
        submitted = st.form_submit_button("Register student", type="primary")
        out = st.empty()

    if ss.add_msg and not submitted:
        out.markdown(alert_box(ss.add_msg, "ok"), unsafe_allow_html=True)
    if submitted:
        ss.add_msg = None
        body = {"name": f_name.strip(), "age": to_int(f_age), "course": f_course.strip(),
                "marks": to_int(f_marks), "email": f_email.strip()}
        data = {"id": f_id.strip(), **body}
        errs = validate(data)
        field_errors({"id": ph_id, "name": ph_name, "age": ph_age, "course": ph_course,
                      "marks": ph_marks, "email": ph_email}, errs)
        if errs:
            return
        with st.spinner("Please wait…"):
            r = A.create(data)
        if r["ok"]:
            ss.cache = None
            msg = r["data"].get("message", "Student created") if isinstance(r["data"], dict) else "Student created"
            ss.add_msg = f"{msg} (HTTP {r['status']})"
            ss.add_ver += 1
            st.toast(f"Student {data['id']} registered", icon="✅")
            st.rerun()
        else:
            prefix = ("Duplicate student ID. " if r.get("status") == 400
                      else "Validation error. " if r.get("status") == 422 else "")
            out.markdown(alert_box(prefix + r["error"]), unsafe_allow_html=True)


def lookup(key, title, sub, btn):
    """Shared 'enter an ID' box. Returns (student, version) or (None, version)."""
    md(head(title, sub))
    ss.setdefault(f"{key}_id", None)
    ss.setdefault(f"{key}_err", None)
    ss.setdefault(f"{key}_ver", 0)
    with st.form(f"{key}_lookup", border=True):
        c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
        sid = c1.text_input("Student ID", placeholder="S001")
        go_btn = c2.form_submit_button(btn, type="primary", use_container_width=True)
    if go_btn:
        sid = sid.strip()
        ss[f"{key}_ver"] += 1
        ss[f"{key}_msg"] = None
        if not ID_RE.match(sid):
            ss[f"{key}_id"] = None
            ss[f"{key}_err"] = "Enter a valid student ID (letters, digits, - or _)."
        else:
            ss[f"{key}_id"], ss[f"{key}_err"] = sid, None
    if ss[f"{key}_err"]:
        md(alert_box(ss[f"{key}_err"], "warn"))
        return None, ss[f"{key}_ver"]
    sid = ss[f"{key}_id"]
    if not sid:
        return None, ss[f"{key}_ver"]
    with st.spinner("Loading…"):
        r = A.one(sid)
    if not r["ok"]:
        not_found = r.get("status") == 404 and "no such endpoint" not in r["error"]
        md(alert_box(f"No student found with ID '{sid}'." if not_found else r["error"],
                     "warn" if r.get("status") == 404 else "err"))
        return None, ss[f"{key}_ver"]
    return r["data"], ss[f"{key}_ver"]


def p_search():
    s, _ = lookup("srch", "Search Student", "Look up a student by ID", "Search")
    if s:
        md(profile(s))


def p_upd():
    s, ver = lookup("upd", "Update Student", "Load a student, edit fields, save only what changed", "Load student")
    if not s:
        return
    md(profile(s))
    md("<h3>Edit details</h3>")
    k = f"{s['id']}_{ver}"
    with st.form("upd_form", border=True):
        u_name = st.text_input("Full name", value=str(s.get("name", "")), key=f"u_name_{k}")
        ph_name = st.empty()
        c1, c2 = st.columns(2)
        u_age = c1.number_input("Age", value=to_int(s.get("age")), step=1, key=f"u_age_{k}")
        ph_age = c1.empty()
        u_marks = c2.number_input("Marks", value=to_int(s.get("marks")), step=1, key=f"u_marks_{k}")
        ph_marks = c2.empty()
        u_course = st.text_input("Course", value=str(s.get("course", "")), key=f"u_course_{k}")
        ph_course = st.empty()
        u_email = st.text_input("Email", value=str(s.get("email", "")), key=f"u_email_{k}")
        ph_email = st.empty()
        submitted = st.form_submit_button("Save changes", type="primary")
        out = st.empty()

    if not submitted:
        return
    v = {"name": u_name.strip(), "age": to_int(u_age), "course": u_course.strip(),
         "marks": to_int(u_marks), "email": u_email.strip()}
    errs = validate(v, need_id=False)
    field_errors({"name": ph_name, "age": ph_age, "course": ph_course, "marks": ph_marks, "email": ph_email}, errs)
    if errs:
        return
    changes = {key: val for key, val in v.items() if val != s.get(key)}  # partial update: changed fields only
    if not changes:
        return out.markdown(alert_box("Nothing changed.", "warn"), unsafe_allow_html=True)
    with st.spinner("Please wait…"):
        r = A.update(s["id"], changes)
    if not r["ok"]:
        return out.markdown(alert_box(r["error"]), unsafe_allow_html=True)
    ss.cache = None
    ss["upd_ver"] += 1  # reload form defaults from the backend
    st.toast(f"Student {s['id']} updated: {', '.join(changes)}", icon="✅")
    st.rerun()


def p_del():
    if ss.del_msg:
        md(head("Delete Student", "Permanently remove a student record"))
        md(alert_box(ss.del_msg, "ok"))
        ss.del_msg = None
        st.button("Delete another student", key="del_again")
        return
    s, ver = lookup("del", "Delete Student", "Permanently remove a student record", "Find student")
    if not s:
        return
    md(profile(s))
    md(alert_box("This cannot be undone. Type the student ID and tick the box to confirm.", "warn"))
    k = f"{s['id']}_{ver}"
    with st.container(border=True):
        typed = st.text_input(f"Type {s['id']} to confirm (then press Enter)", key=f"cf_{k}")
        ticked = st.checkbox("I understand this is permanent", key=f"ck_{k}")
        ready = ticked and typed.strip() == str(s["id"])
        if st.button("Delete student", key="del_btn", disabled=not ready):
            with st.spinner("Please wait…"):
                r = A.delete(s["id"])
            if not r["ok"]:
                return md(alert_box(r["error"]))
            ss.cache = None
            ss.del_id = None
            msg = r["data"].get("message") if isinstance(r["data"], dict) else None
            ss.del_msg = msg or "Deleted."
            st.toast(f"Student {s['id']} deleted", icon="✅")
            st.rerun()


def p_set():
    md(head("Settings", "Backend connection"))
    with st.container(border=True):
        url = st.text_input("API base URL", value=ss.base)
        c1, c2, _ = st.columns([1, 1.4, 4])
        save = c1.button("Save", type="primary")
        test = c2.button("Test connection")
    if save:
        ss.base = url.strip().rstrip("/")
        ss.cache = None
        ping.clear()
        ss.set_msg = "Backend URL updated."
        st.rerun()
    if ss.set_msg:
        md(alert_box(ss.set_msg, "ok"))
        ss.set_msg = None
    if test:
        base = url.strip().rstrip("/")
        old, ss.base = ss.base, base
        r = call("GET", "/openapi.json")
        ss.base = old
        if r["ok"]:
            routes = len((r["data"] or {}).get("paths", {})) if isinstance(r["data"], dict) else 0
            md(alert_box(f"Connected to {base} · {routes} routes available", "ok"))
        else:
            md(alert_box(r["error"]))


ROUTER = {
    "Dashboard": p_dash,
    "All Students": p_all,
    "Add Student": p_add,
    "Search Student": p_search,
    "Update Student": p_upd,
    "Delete Student": p_del,
    "Settings": p_set,
}
ROUTER[ss.page]()
