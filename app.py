from flask import Flask, request, redirect, session
import json, os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

USERS = {
    "paula": "paula1",
    "alfredo": "alfredo1"
}

# ---------- DATA ----------
def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

def generate_code(data):
    return f"C{len(data)+1:04d}"

# ---------- LAYOUT PRO ----------
def layout(content):

    return f"""
    <style>
    body {{
        margin:0;
        font-family:Arial;
        background:linear-gradient(rgba(255,255,255,0.92),rgba(255,255,255,0.92)),
        url('https://upload.wikimedia.org/wikipedia/commons/c/cf/Flag_of_Canada.svg');
        background-size:cover;
    }}

    .sidebar {{
        position:fixed;
        width:230px;
        height:100%;
        background:#0f172a;
        color:white;
        padding:20px;
    }}

    .logo {{
        font-size:20px;
        font-weight:bold;
        cursor:pointer;
        margin-bottom:20px;
    }}

    .sidebar a {{
        display:block;
        padding:10px;
        margin-top:5px;
        color:white;
        text-decoration:none;
        border-radius:6px;
    }}

    .sidebar a:hover {{
        background:#1e293b;
    }}

    .main {{
        margin-left:250px;
        padding:20px;
    }}

    .card {{
        background:white;
        padding:15px;
        border-radius:12px;
        box-shadow:0 4px 12px rgba(0,0,0,0.1);
        margin-top:10px;
    }}

    button {{
        background:#2563eb;
        color:white;
        border:none;
        padding:10px;
        border-radius:8px;
        cursor:pointer;
        transition:0.2s;
    }}

    button:hover {{
        background:#1d4ed8;
        transform:scale(1.05);
    }}

    input,select,textarea {{
        width:100%;
        padding:8px;
        margin:5px 0;
        border-radius:6px;
        border:1px solid #ccc;
    }}

    .back {{
        display:inline-block;
        margin-bottom:10px;
        text-decoration:none;
        color:#2563eb;
        font-weight:bold;
    }}

    .calendar {{
        display:grid;
        grid-template-columns:repeat(7,1fr);
        gap:5px;
    }}

    .day {{
        background:white;
        padding:10px;
        border-radius:8px;
        min-height:80px;
        font-size:12px;
    }}

    .event {{
        background:#2563eb;
        color:white;
        padding:2px;
        margin-top:5px;
        border-radius:4px;
    }}
    </style>

    <div class="sidebar">
        <div class="logo" onclick="window.location.href='/'">🏢 Office Thinking</div>
        <a href="/">📊 Dashboard</a>
        <a href="/clients">👥 Clientes</a>
        <a href="/calendar">📅 Calendario</a>
        <a href="/reports">📈 Reportes</a>
        <a href="/logout">🚪 Salir</a>
    </div>

    <div class="main">
        {content}
    </div>
    """

# ---------- LOGIN ----------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if USERS.get(request.form.get("user")) == request.form.get("password"):
            session["logged"] = True
            return redirect("/")

    return """
    <div style="display:flex;justify-content:center;align-items:center;height:100vh">
        <form method="POST">
            <h2>Office Thinking 🇨🇦</h2>
            <input name="user"><br>
            <input type="password" name="password"><br>
            <button>Entrar</button>
        </form>
    </div>
    """

# ---------- DASHBOARD ----------
@app.route("/")
def home():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    content = f"""
    <h2>📊 Dashboard</h2>
    <div class="card">Clientes: {len(data)}</div>
    """

    return layout(content)

# ---------- CLIENTES ----------
@app.route("/clients", methods=["GET","POST"])
def clients():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":
        data.append({
            "codigo": generate_code(data),
            "nombre": request.form.get("nombre"),
            "fecha": request.form.get("fecha"),
            "mensaje": request.form.get("mensaje","")
        })
        save_data(data)

    content = "<h2>👥 Clientes</h2><a class='back' href='/'>⬅ Volver</a>"

    content += """
    <form method="POST" class="card">
        <input name="nombre" placeholder="Nombre">
        <input type="date" name="fecha">
        <textarea name="mensaje" placeholder="Mensaje para el cliente"></textarea>
        <button>Guardar</button>
    </form>
    """

    for i,c in enumerate(data):
        content += f"""
        <div class="card">
            {c.get('nombre')}<br>
            📅 {c.get('fecha')}<br>
            💬 {c.get('mensaje')}<br>

            <a href="/edit/{i}">Editar</a> |
            <a href="/delete/{i}">Eliminar</a>
        </div>
        """

    return layout(content)

# ---------- CALENDARIO VISUAL ----------
@app.route("/calendar")
def calendar():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()
    today = datetime.now()

    days = []
    for i in range(30):
        d = today + timedelta(days=i)
        events = ""

        for c in data:
            if c.get("fecha") == d.strftime("%Y-%m-%d"):
                events += f"<div class='event'>{c.get('nombre')}</div>"

        days.append(f"<div class='day'>{d.day}{events}</div>")

    content = "<h2>📅 Calendario</h2><a class='back' href='/'>⬅ Volver</a>"
    content += f"<div class='calendar'>{''.join(days)}</div>"

    return layout(content)

# ---------- REPORTES ----------
@app.route("/reports")
def reports():
    if not session.get("logged"):
        return redirect("/login")

    content = """
    <h2>📈 Reportes</h2>
    <a class='back' href='/'>⬅ Volver</a>

    <div class="card">
        ✉️ Aquí podrás definir:
        <br>- mensajes personalizados
        <br>- horarios de envío
        <br>- automatización futura
    </div>
    """

    return layout(content)

# ---------- EDIT ----------
@app.route("/edit/<int:index>", methods=["GET","POST"])
def edit(index):
    data = load_data()
    c = data[index]

    if request.method == "POST":
        c["nombre"] = request.form.get("nombre")
        c["fecha"] = request.form.get("fecha")
        c["mensaje"] = request.form.get("mensaje")
        save_data(data)
        return redirect("/clients")

    content = f"""
    <h2>Editar</h2>
    <a class='back' href='/clients'>⬅ Volver</a>

    <form method="POST" class="card">
        <input name="nombre" value="{c.get('nombre')}">
        <input name="fecha" value="{c.get('fecha')}">
        <textarea name="mensaje">{c.get('mensaje')}</textarea>
        <button>Guardar</button>
    </form>
    """

    return layout(content)

# ---------- DELETE ----------
@app.route("/delete/<int:index>")
def delete(index):
    data = load_data()
    data.pop(index)
    save_data(data)
    return redirect("/clients")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)