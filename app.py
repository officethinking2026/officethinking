from flask import Flask, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

USERS = {
    "paula": "paula1",
    "alfredo": "alfredo1"
}

# 📦 DATA
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

# 🎨 TEMPLATE BASE
def layout(content):

    return f"""
    <style>
        body{{margin:0;font-family:Arial;background:#f4f6f9}}

        .sidebar{{
            position:fixed;
            width:220px;
            height:100%;
            background:#111827;
            color:white;
            padding:20px;
        }}

        .sidebar a{{
            display:block;
            color:white;
            text-decoration:none;
            padding:10px;
            border-radius:6px;
            margin-top:5px;
        }}

        .sidebar a:hover{{background:#374151}}

        .main{{margin-left:240px;padding:20px}}

        .card{{
            background:white;
            padding:15px;
            border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
            margin-top:10px;
        }}

        input,select,textarea{{
            width:100%;
            padding:8px;
            margin:5px 0;
        }}

        button{{
            background:#2563eb;
            color:white;
            border:none;
            padding:10px;
            border-radius:8px;
        }}
    </style>

    <div class="sidebar">
        <h2>🏢 Office Thinking</h2>
        <a href="/">📊 Dashboard</a>
        <a href="/clients">👥 Clientes</a>
        <a href="/agenda">📅 Agenda</a>
        <a href="/reports">📈 Reportes</a>
        <a href="/logout">🚪 Salir</a>
    </div>

    <div class="main">
        {content}
    </div>
    """

# 🔐 LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("user")
        p = request.form.get("password")

        if u in USERS and USERS[u] == p:
            session["logged"] = True
            return redirect("/")

    return """
    <div style="display:flex;justify-content:center;align-items:center;height:100vh">
        <form method="POST">
            <h2>Office Thinking</h2>
            <input name="user"><br>
            <input type="password" name="password"><br>
            <button>Entrar</button>
        </form>
    </div>
    """

# 📊 DASHBOARD
@app.route("/")
def home():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    total = len(data)
    pagados = sum(1 for c in data if c.get("estado_pago") == "Pagado")
    pendientes = total - pagados

    content = f"""
    <h2>Dashboard</h2>

    <div class="card">👥 Total clientes: {total}</div>
    <div class="card">💰 Pagados: {pagados}</div>
    <div class="card">⚠️ Pendientes: {pendientes}</div>
    """

    return layout(content)

# 👥 CLIENTES
@app.route("/clients", methods=["GET","POST"])
def clients():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":
        data.append({
            "codigo": generate_code(data),
            "nombre": request.form.get("nombre"),
            "email": request.form.get("email"),
            "fecha": request.form.get("fecha"),
            "monto": request.form.get("monto"),
            "estado_pago": request.form.get("estado_pago")
        })
        save_data(data)

    content = "<h2>Clientes</h2>"

    content += """
    <form method="POST" class="card">
        <input name="nombre" placeholder="Nombre">
        <input name="email" placeholder="Email">
        <input type="date" name="fecha">
        <input name="monto" placeholder="Monto">
        <select name="estado_pago">
            <option>Pendiente</option>
            <option>Pagado</option>
            <option>Vencido</option>
        </select>
        <button>Guardar</button>
    </form>
    """

    for i, c in enumerate(data):
        content += f"""
        <div class="card">
            <b>{c.get('codigo')}</b> - {c.get('nombre')}<br>
            {c.get('email')} | {c.get('monto')}
            <br>
            <a href="/edit/{i}">Editar</a> |
            <a href="/delete/{i}">Eliminar</a>
        </div>
        """

    return layout(content)

# 📅 AGENDA
@app.route("/agenda")
def agenda():
    if not session.get("logged"):
        return redirect("/login")

    data = load_data()
    hoy = datetime.now().date()

    content = "<h2>Agenda</h2>"

    for c in data:
        try:
            fecha = datetime.strptime(c.get("fecha",""), "%Y-%m-%d").date()
            dias = (fecha - hoy).days
        except:
            continue

        content += f"""
        <div class="card">
            {c.get('nombre')} - {c.get('fecha')} ({dias} días)
        </div>
        """

    return layout(content)

# 📈 REPORTES
@app.route("/reports")
def reports():
    if not session.get("logged"):
        return redirect("/login")

    content = """
    <h2>Reportes</h2>
    <div class="card">
        📩 Próximamente:
        <br>- correos automáticos
        <br>- resumen diario
        <br>- programación de envíos
    </div>
    """

    return layout(content)

# ✏️ EDITAR
@app.route("/edit/<int:index>", methods=["GET","POST"])
def edit(index):

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()
    c = data[index]

    if request.method == "POST":
        c["nombre"] = request.form.get("nombre")
        c["email"] = request.form.get("email")
        c["fecha"] = request.form.get("fecha")
        c["monto"] = request.form.get("monto")
        c["estado_pago"] = request.form.get("estado_pago")

        data[index] = c
        save_data(data)

        return redirect("/clients")

    content = f"""
    <h2>Editar cliente</h2>

    <form method="POST" class="card">
        <input name="nombre" value="{c.get('nombre')}">
        <input name="email" value="{c.get('email')}">
        <input name="fecha" value="{c.get('fecha')}">
        <input name="monto" value="{c.get('monto')}">

        <select name="estado_pago">
            <option>{c.get('estado_pago')}</option>
            <option>Pendiente</option>
            <option>Pagado</option>
            <option>Vencido</option>
        </select>

        <button>Guardar</button>
    </form>
    """

    return layout(content)

# 🗑️ DELETE
@app.route("/delete/<int:index>")
def delete(index):
    if session.get("logged"):
        data = load_data()
        if 0 <= index < len(data):
            data.pop(index)
        save_data(data)

    return redirect("/clients")

# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)