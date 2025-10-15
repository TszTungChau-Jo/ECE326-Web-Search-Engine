# Lab2_F.py — Google OAuth + Sessions + Anonymous/Signed-In Modes + Per-user History
# ------------------------------------------------------------------------------
# - Anonymous mode: "/" serves Lab1's index.html directly (no history shown).
# - Signed-in mode: "/" renders a query page with user email and per-user history.
# - OAuth flow: /login -> Google -> /redirect (PRG) -> /
# - Sessions: Beaker (file-based), safe to refresh; sign-out does not revoke consent.
# - Persistence:
#     * users.json    : remember if an email has visited before (for "Welcome"/"Welcome back").
#     * history.json  : per-user last 10 search keywords (cross browser/devices).
# - Static assets for Lab1: /lab1, /style.css, /img/<file>
# ------------------------------------------------------------------------------

from bottle import route, run, request, redirect, response, static_file, app as bottle_app
from oauth2client.client import FlowExchangeError, flow_from_clientsecrets, OAuth2WebServerFlow
from googleapiclient.discovery import build
from beaker.middleware import SessionMiddleware
import httplib2, json, os, re

# --- Read OAuth client credentials from the downloaded JSON ---
with open("client_secret.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)["web"]
CLIENT_ID = cfg["client_id"]
CLIENT_SECRET = cfg["client_secret"]

SCOPES  = ['profile', 'email']
REDIRECT = 'http://localhost:8080/redirect'

# ------------------------------------------------------------------------------
# Persistent store: seen users (for Welcome vs Welcome back)
# ------------------------------------------------------------------------------
USER_DB = 'users.json'

def _load_users():
    if not os.path.exists(USER_DB):
        return set()
    try:
        with open(USER_DB, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return set(data.get('emails', []))
    except Exception:
        return set()

def _save_users(emails: set):
    with open(USER_DB, 'w', encoding='utf-8') as f:
        json.dump({'emails': sorted(list(emails))}, f, ensure_ascii=False, indent=2)

def mark_seen(email: str) -> bool:
    """Return True if this is the first time we see this email; otherwise False."""
    emails = _load_users()
    if email in emails:
        return False
    emails.add(email)
    _save_users(emails)
    return True

# ------------------------------------------------------------------------------
# Persistent store: per-user last-10 search keywords
# ------------------------------------------------------------------------------
HIST_DB = 'history.json'

def _load_hist():
    if not os.path.exists(HIST_DB):
        return {}
    try:
        with open(HIST_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def _save_hist(d):
    with open(HIST_DB, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def add_history(email, keyword):
    """Insert the newest keyword at head, keep unique and trim to 10."""
    if not keyword:
        return
    d = _load_hist()
    arr = d.get(email, [])
    arr = [k for k in arr if k != keyword]
    arr.insert(0, keyword)
    d[email] = arr[:10]
    _save_hist(d)

def get_history(email):
    return _load_hist().get(email, [])

# ------------------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------------------
def ensure_session_dir():
    """Create sessions dir for Beaker if not present."""
    os.makedirs('./sessions', exist_ok=True)

def set_no_store():
    """Disable caching so users cannot view protected pages via back/refresh."""
    response.set_header('Cache-Control', 'no-store')

def html_escape(s: str) -> str:
    return (s or "").replace("&","&amp;").replace("<","&lt;") \
                    .replace(">","&gt;").replace('"',"&quot;").replace("'","&#39;")

def header_html():
    """Small header shown on every page."""
    s = request.environ['beaker.session']
    if 'email' in s:
        return f"""
        <div style="display:flex;gap:12px;align-items:center;">
          <span>Signed in as <b>{html_escape(s['email'])}</b></span>
          <a href="/logout">Sign out</a>
        </div><hr/>
        """
    else:
        return "<div><a href='/login'>Sign in with Google</a></div><hr/>"

# server-side rendering of a minimal Lab1-style result table ---
def tokenize_keep_punct(s: str):
    return re.findall(r"\w+|[^\w\s]", s.lower()) if s else []

def lab1_results_html(keywords: str) -> str:
    """Produce a small word-count table similar to Lab1."""
    tokens = tokenize_keep_punct(keywords)
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1
    rows = "".join(f"<tr><td>{html_escape(w)}</td><td>{c}</td></tr>" for w, c in counts.items())
    return (
        f'<p>Search for: "{html_escape(keywords.strip())}"</p>'
        f"<h3>Word Count</h3>"
        f"<p><strong>Total words:</strong> {len(tokens)}</p>"
        f'<table id="results" name="results">{rows}</table>'
    )

# ------------------------------------------------------------------------------
# Sessions (Beaker) — file-based
# ------------------------------------------------------------------------------
ensure_session_dir()
session_opts = {
    'session.type': 'file',
    'session.data_dir': './sessions',
    'session.cookie_expires': 3600,  # 1 hour
    'session.auto': True,
}
app = SessionMiddleware(bottle_app(), session_opts)

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

# Home: Anonymous -> serve Lab1's index.html directly;
#       Signed-in -> show query form + results + per-user history.
@route('/', method='GET')
def home():
    set_no_store()
    s = request.environ['beaker.session']

    # NEW: read Lab1's query param
    keywords = request.query.get('keywords', '').strip()

    # NEW: if signed-in and has a query, add to per-user history (keep 10)
    if 'email' in s and keywords:
        add_history(s['email'], keywords)

    # Always serve index.html for both anonymous and signed-in users
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except FileNotFoundError:
        return "<p>index.html not found.</p>"

    # Insert header (Sign in or Signed in)
    header = header_html()

    if 'email' in s:
        first = s.pop('first_time', False)
        s.save()
        msg = "Welcome" if first else "Welcome back"
        user_info_html = f"<div><h3>{msg}, {s['email']}</h3></div>"
        html = html.replace('<body>', f'<body>\n{header}\n{user_info_html}', 1)
    else:
        html = html.replace('<body>', f'<body>\n{header}', 1)

    response.content_type = 'text/html; charset=utf-8'
    return html


# Start login (only when user clicks the button)
@route('/login')
def login():
    flow = flow_from_clientsecrets("client_secret.json", scope=SCOPES, redirect_uri=REDIRECT)
    uri = flow.step1_get_authorize_url()
    return redirect(str(uri))

# OAuth redirect endpoint (PRG: process, then redirect to "/")
@route('/redirect')
def redirect_page():
    code = request.query.get("code", "")
    if not code:
        return redirect('/')
    try:
        flow = OAuth2WebServerFlow(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPES,
            redirect_uri=REDIRECT
        )
        credentials = flow.step2_exchange(code)  # "code" is single-use
    except FlowExchangeError:
        return redirect('/')

    # Fetch user profile (email)
    http = credentials.authorize(httplib2.Http())
    userinfo = build('oauth2', 'v2', http=http).userinfo().get().execute()
    email = userinfo.get('email', '')

    # Persist and sessionize
    first_time = mark_seen(email)
    s = request.environ['beaker.session']
    s['email'] = email
    s['first_time'] = first_time
    s.save()

    return redirect('/')  # PRG: avoids refresh errors

# Sign-out (session-only; does not revoke Google consent)
@route('/logout')
def logout():
    set_no_store()
    s = request.environ['beaker.session']
    s.delete()
    return "<h3>Logged out.</h3><a href='/'>Home</a>"

# --- Static assets for Lab1 (index.html already sits at project root) ---
@route('/lab1')
def serve_lab1_index():
    return static_file('index.html', root='.')

@route('/style.css')
def serve_css():
    return static_file('style.css', root='.')

@route('/img/<filename:path>')
def serve_img(filename):
    return static_file(filename, root='./img')

@route('/api/history')
def api_history():
    set_no_store()
    response.content_type = 'application/json; charset=utf-8'
    s = request.environ['beaker.session']
    if 'email' not in s:
        return json.dumps({}, ensure_ascii=False)
    return json.dumps({'history': get_history(s['email'])}, ensure_ascii=False)




# ------------------------------------------------------------------------------
# Run server
# ------------------------------------------------------------------------------
run(app=app, host='localhost', port=8080)
