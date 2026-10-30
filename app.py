
import os
import requests
from flask import (
    Flask, request, redirect, session,
    render_template_string, url_for, flash
)
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_THIS_SECRET")

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "")
ADMIN_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")

def db_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def db_ready():
    return bool(SUPABASE_URL and SUPABASE_KEY)

BASE_STYLE = """
<style>
*{box-sizing:border-box}
body{margin:0;background:#080b16;color:#f4f6ff;font-family:Arial,sans-serif}
nav{padding:18px 7%;display:flex;justify-content:space-between;
background:#10162a;border-bottom:1px solid #273253}
.logo{font-size:23px;font-weight:900;color:#00eaff}
.hero{text-align:center;padding:65px 18px 40px;
background:linear-gradient(#080b1688,#080b16cc),url("/static/creators/xyz-banner.png") center/cover no-repeat;min-height:420px}
.hero h1{font-size:clamp(38px,8vw,72px);margin:10px 0;color:#fff}
.hero h1 span{color:#00eaff}
.hero p{color:#aeb8d5}
.tag{color:#ffca4b;letter-spacing:4px;font-weight:bold}
.card{max-width:650px;margin:25px auto;padding:25px;
background:#121a30;border:1px solid #29365b;border-radius:18px}
input,select{width:100%;padding:14px;margin:8px 0 15px;
background:#080e20;color:white;border:1px solid #35436b;border-radius:9px}
label{color:#bdc8e5;font-size:14px}
button,.btn{background:linear-gradient(90deg,#00d9ff,#7657ff);
border:0;color:#050816;padding:14px 20px;border-radius:9px;
font-weight:bold;cursor:pointer;text-decoration:none;display:inline-block}
button{width:100%}
h2{color:#00eaff}
.small{color:#9ba8c8;font-size:13px}
table{width:100%;border-collapse:collapse;font-size:13px}
td,th{padding:12px;border-bottom:1px solid #29365b;text-align:left}
.wrap{overflow-x:auto}
.msg{padding:12px;background:#183b35;border-radius:8px;margin:12px 0}
footer{text-align:center;color:#7d89a9;padding:30px}
.creator-photo{width:100%;height:160px;object-fit:cover;border-radius:12px}\n</style>
"""

TOURNAMENT = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XYZ ESPORTS | Tournament</title>""" + BASE_STYLE + """</head><body>
<nav><div class="logo">⚡ XYZ ESPORTS</div><a class="btn" href="/admin">ADMIN</a></nav>
<section class="hero">
<div class="tag">POWERED BY HIMANSH SINGH</div>
<h1>PLAY <span>•</span> COMPETE <span>•</span> WIN</h1>
<p>YOUR BATTLE. YOUR TEAM. YOUR GLORY.</p>
<a class="btn" href="#register">REGISTER NOW</a>
</section>
<div class="card" id="register">
<h2>🏆 Tournament Registration</h2>
<p class="small">अपनी सही जानकारी भरें। आपकी जानकारी केवल Admin Panel में दिखाई देगी।</p>
{% for message in get_flashed_messages() %}<div class="msg">{{message}}</div>{% endfor %}
<form method="post" action="/register">
<label>Team Name</label><input name="team" maxlength="40" required>
<label>Captain Name</label><input name="captain" maxlength="50" required>
<label>Free Fire UID</label><input name="uid" inputmode="numeric" pattern="[0-9]{5,20}" required>
<label>Contact Number</label><input name="phone" inputmode="numeric" pattern="[0-9]{10}" required>
<label>City / State</label><input name="city" maxlength="80" required>
<label>Match Type</label>
<select name="mode"><option>Squad</option><option>Duo</option><option>Solo</option></select>
<label>Player 2 Name (optional)</label><input name="player2" maxlength="50">
<label>Player 2 UID (optional)</label><input name="uid2" maxlength="20">
<label>Player 3 Name (optional)</label><input name="player3" maxlength="50">
<label>Player 3 UID (optional)</label><input name="uid3" maxlength="20">
<label>Player 4 Name (optional)</label><input name="player4" maxlength="50">
<label>Player 4 UID (optional)</label><input name="uid4" maxlength="20">
<button type="submit">SUBMIT REGISTRATION</button>
</form></div>
<footer>XYZ ESPORTS © 2026 • Fan-run tournament platform</footer>
</body></html>
"""

HOME = """
<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>XYZ ESPORTS | Home</title>
""" + BASE_STYLE + """
</head>
<body>
<nav>
<div class="logo">⚡ XYZ ESPORTS</div>
<a class="btn" href="/tournaments">TOURNAMENT</a>
</nav>

<section class="hero">
<div class="tag">OFFICIAL GAMING COMMUNITY</div>
<h1>XYZ <span>ESPORTS</span></h1>
<p>PLAY • COMPETE • WIN</p>
<a class="btn" href="/tournaments">JOIN TOURNAMENT</a>
</section>

<div class="card">
<h2>🔥 FEATURED GAMING CREATORS</h2>
<p class="small">Our featured gaming creators</p>
<div class="grid">
<div class="card"><img src="/static/creators/gyan.jpg" alt="Gyan Gaming" class="creator-photo"><h3>Gyan Gaming</h3></div>
<div class="card"><img src="/static/creators/raistar.jpg" alt="Raistar" class="creator-photo"><h3>Raistar</h3></div>
<div class="card"><img src="/static/creators/lokesh.jpg" alt="Lokesh Gamer" class="creator-photo"><h3>Lokesh Gamer</h3></div>
<div class="card"><img src="/static/creators/total.jpg" alt="Total Gaming" class="creator-photo"><h3>Total Gaming</h3></div>
<div class="card"><img src="/static/creators/skylord.jpg" alt="SKYLORD" class="creator-photo"><h3>SKYLORD</h3></div>
<div class="card"><img src="/static/creators/desi.jpg" alt="Desi Gamers" class="creator-photo"><h3>Desi Gamers</h3></div>
</div>
</div>

<div class="card">
<h2>OWNER</h2>
<h1>HIMANSH SINGH</h1>
<p>POWERED BY HIMANSH SINGH</p>
<p>Contact: himanshs378@gmail.com</p>
</div>

<footer>XYZ ESPORTS © 2026</footer>
</body>
</html>
"""



LOGIN = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Admin Login</title>""" + BASE_STYLE + """</head><body>
<nav><div class="logo">XYZ ESPORTS</div><a href="/" class="btn">HOME</a></nav>
<div class="card"><h2>🔐 Admin Login</h2>
{% for message in get_flashed_messages() %}<div class="msg">{{message}}</div>{% endfor %}
<form method="post">
<label>Admin Email</label><input type="email" name="email" required>
<label>Password</label><input type="password" name="password" required>
<button>LOGIN SECURELY</button></form></div></body></html>
"""

DASH = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>XYZ Admin</title>""" + BASE_STYLE + """</head><body>
<nav><div class="logo">XYZ ADMIN PANEL</div><a class="btn" href="/logout">LOGOUT</a></nav>
<div class="card"><h2>📊 Registrations</h2>
<p>Total registrations: <b>{{rows|length}}</b></p>
<div class="wrap"><table><tr><th>Team</th><th>Captain</th><th>UID</th>
<th>Phone</th><th>City</th><th>Mode</th><th>Date</th></tr>
{% for r in rows %}
<tr><td>{{r.get('team','')}}</td><td>{{r.get('captain','')}}</td>
<td>{{r.get('uid','')}}</td><td>{{r.get('phone','')}}</td>
<td>{{r.get('city','')}}</td><td>{{r.get('mode','')}}</td>
<td>{{r.get('created_at','')}}</td></tr>
{% endfor %}</table></div></div></body></html>
"""

@app.route("/")
def home():
    return render_template_string(HOME)


@app.route("/tournaments")
def tournaments():
    return render_template_string(TOURNAMENT)

@app.route("/register", methods=["POST"])
def register():
    if not db_ready():
        flash("Registration system अभी configure नहीं हुआ है।")
        return redirect(url_for("tournaments") + "#register")

    data = {
        "team": request.form.get("team", "").strip(),
        "captain": request.form.get("captain", "").strip(),
        "uid": request.form.get("uid", "").strip(),
        "phone": request.form.get("phone", "").strip(),
        "city": request.form.get("city", "").strip(),
        "mode": request.form.get("mode", "Squad"),
        "player2": request.form.get("player2", "").strip(),
        "uid2": request.form.get("uid2", "").strip(),
        "player3": request.form.get("player3", "").strip(),
        "uid3": request.form.get("uid3", "").strip(),
        "player4": request.form.get("player4", "").strip(),
        "uid4": request.form.get("uid4", "").strip()
    }
    if not all(data[k] for k in ("team", "captain", "uid", "phone", "city")):
        flash("कृपया जरूरी जानकारी भरें।")
        return redirect(url_for("tournaments") + "#register")
    if not data["uid"].isdigit() or not data["phone"].isdigit() or len(data["phone"]) != 10:
        flash("UID या मोबाइल नंबर सही नहीं है।")
        return redirect(url_for("tournaments") + "#register")

    try:
        res = requests.post(
            SUPABASE_URL + "/rest/v1/registrations",
            headers={**db_headers(), "Prefer": "return=minimal"},
            json=data, timeout=20
        )
        if res.status_code not in (200, 201, 204):
            app.logger.error("Database error: %s", res.text)
            flash("Registration सेव नहीं हुआ। कृपया बाद में कोशिश करें।")
        else:
            flash("Registration सफल! आपकी टीम दर्ज हो गई है।")
    except requests.RequestException:
        flash("Server से संपर्क नहीं हो पाया।")
    return redirect(url_for("tournaments") + "#register")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            if (email == ADMIN_EMAIL.lower() and ADMIN_HASH
                    and check_password_hash(ADMIN_HASH, password)):
                session.clear()
                session["admin"] = True
                return redirect(url_for("admin"))
            flash("गलत Admin ID या Password")
        return render_template_string(LOGIN)

    rows = []
    if db_ready():
        try:
            res = requests.get(
                SUPABASE_URL + "/rest/v1/registrations?select=*&order=created_at.desc",
                headers=db_headers(), timeout=20
            )
            res.raise_for_status()
            rows = res.json()
        except requests.RequestException:
            flash("Database से डेटा नहीं मिल पाया।")
    return render_template_string(DASH, rows=rows)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

