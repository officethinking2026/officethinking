from flask import Flask, request, redirect, url_for, session
import json, os
from datetime import datetime, timedelta

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

# 🔐 LOGIN
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

        if user in USERS and USERS[user] == password:
            session["logged"] = True
            session["user"] = user
            return redirect(url_for("home"))

    return """
    <style>
        body{font-family:Arial;text-align:center;padding-top:100px;background:#f4f4f4;}
        input,button{padding:10px;margin:5px;}
    </style>

    <h2>🏢 Office Thinking CRM</h2>
    <form method="POST">
        <input name="user" placeholder="Usuario"><br>
        <input type="password" name="password" placeholder="Contraseña"><br>
        <button>Entrar</button>
    </form>
    """

# 🏠 HOME
@app.route("/", methods=["GET","POST"])
def home():

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    hoy = datetime.now().strftime("%Y-%m-%d")

    # ➕ CLIENTE
    if request.method == "POST":
        cliente = {
            "codigo": generate_code(data),
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "celular": request.form.get("celular"),
            "email": request.form.get("email"),
            "fecha": request.form.get("fecha"),
            "accion": request.form.get("accion"),
            "notas": request.form.get("notas"),
            "monto": request.form.get("monto"),
            "estado_pago": request.form.get("estado_pago"),
            "user": session.get("user")
        }

        data.append(cliente)
        save_data(data)

    # 📅 CALENDARIO
    hoy_tareas = []
    proximos = []
    vencidos = []

    total = len(data)

    for c in data:

        fecha = c.get("fecha")

        if fecha == hoy:
            hoy_tareas.append(c)

        elif fecha and fecha > hoy:
            proximos.append(c)

        elif fecha and fecha < hoy:
            vencidos.append(c)

    html = f"""
    <style>
        body {{
            font-family: Arial;
            margin:0;
            background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)),
            url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Canada.svg/1280px-Flag_of_Canada.svg.png');
            background-size: cover;
        }}

        header {{
            background:#c0392b;
            color:white;
            padding:15px;
            display:flex;
            justify-content:space-between;
        }}

        .container {{ padding:20px; }}

        .grid {{
            display:grid;
            grid-template-columns: repeat(3,1fr);
            gap:10px;
        }}

        .box {{
            background:white;
            padding:10px;
            border-radius:10px;
            text-align:center;
        }}

        .card {{
            background:white;
            padding:15px;
            margin:10px 0;
            border-radius:10px;
        }}

        button {{
            padding:8px;
            background:#c0392b;
            color:white;
            border:none;
            border-radius:5px;
        }}
    </style>

    <header>
        <div>🏢 Office Thinking CRM</div>
        <div>
            Usuario: {session.get("user")} |
            <a href="/logout" style="color:white;">🚪 Salir</a>
        </div>
    </header>

    <div class="container">

    <h3>📅 Calendario inteligente</h3>

    <div class="grid">
        <div class="box">🔥 Hoy<br><b>{len(hoy_tareas)}</b></div>
        <div class="box">📅 Próximos<br><b>{len(proximos)}</b></div>
        <div class="box">⚠️ Vencidos<br><b>{len(vencidos)}</b></div>
    </div>

    <h3>➕ Nuevo cliente</h3>

    <form method="POST">
        <input name="nombre" placeholder="Nombre"><br>
        <input name="servicio" placeholder="Servicio"><br>
        <input name="celular" placeholder="Celular"><br>
        <input name="email" placeholder="Email"><br>
        <input type="date" name="fecha"><br>
        <input name="monto" placeholder="Monto"><br>

        <select name="estado_pago">
            <option>Pendiente</option>
            <option>Pagado</option>
            <option>Vencido</option>
        </select><br>

        <select name="accion">
            <option>Llamar</option>
            <option>Enviar correo</option>
        </select><br>

        <textarea name="notas"></textarea><br>

        <button>Guardar</button>
    </form>

    <h3>📋 Agenda de hoy</h3>
    """

    for c in hoy_tareas:
        html += f"""
        <div class="card">
            🟢 <b>{c['nombre']}</b><br>
            📅 Hoy<br>
            💰 {c.get('monto')}<br>
            📱 {c.get('celular')}<br>
        </div>
        """

    html += "</div>"
    return html

# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)