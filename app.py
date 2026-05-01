from flask import Flask, request, redirect, url_for, session
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
        body {font-family:Arial;text-align:center;padding-top:100px;}
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

    # ➕ CREAR CLIENTE
    if request.method == "POST":
        data.append({
            "codigo": generate_code(data),
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "celular": request.form.get("celular"),
            "email": request.form.get("email"),
            "fecha": request.form.get("fecha"),
            "accion": request.form.get("accion"),
            "notas": request.form.get("notas"),

            # 💰 pagos
            "monto": request.form.get("monto"),
            "estado_pago": request.form.get("estado_pago"),

            "user": session.get("user")
        })
        save_data(data)

    hoy = datetime.now().strftime("%Y-%m-%d")

    # 📊 DASHBOARD GENERAL
    total = len(data)
    hoy_count = 0
    atrasados = 0
    futuros = 0

    # 💰 FINANZAS
    total_pagado = 0
    total_pendiente = 0
    total_vencido = 0

    # 🧠 INTELIGENCIA
    urgentes = 0
    proximos = 0
    normales = 0

    for c in data:

        fecha = c.get("fecha")
        estado = c.get("estado_pago","Pendiente")
        monto = float(c.get("monto") or 0)

        # calendario
        if fecha == hoy:
            hoy_count += 1
        elif fecha and fecha < hoy:
            atrasados += 1
        else:
            futuros += 1

        # finanzas
        if estado == "Pagado":
            total_pagado += monto
        elif estado == "Vencido":
            total_vencido += monto
        else:
            total_pendiente += monto

        # inteligencia
        if estado == "Vencido":
            urgentes += 1
        elif fecha and fecha <= hoy:
            proximos += 1
        else:
            normales += 1

    html = f"""
    <style>
        body {{
            font-family: Arial;
            background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)),
            url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Canada.svg/1280px-Flag_of_Canada.svg.png');
            background-size: cover;
            margin:0;
        }}

        header {{
            background:#c0392b;
            color:white;
            padding:15px;
        }}

        .container {{
            padding:20px;
        }}

        .dashboard {{
            display:grid;
            grid-template-columns: repeat(4,1fr);
            gap:10px;
            margin-bottom:10px;
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

        .urgente {{
            border-left:5px solid red;
            background:#ffe5e5;
        }}

        .proximo {{
            border-left:5px solid orange;
            background:#fff4e5;
        }}

        .normal {{
            border-left:5px solid green;
        }}

        input,select,textarea {{
            padding:8px;
            margin:5px;
        }}

        button {{
            padding:8px 12px;
            background:#c0392b;
            color:white;
            border:none;
            border-radius:5px;
        }}
    </style>

    <header>
        <h2>🏢 Office Thinking CRM</h2>
        Usuario: {session.get("user")}
    </header>

    <div class="container">

    <h3>📊 Dashboard general</h3>

    <div class="dashboard">
        <div class="box">📁 Total<br><b>{total}</b></div>
        <div class="box">🔥 Hoy<br><b>{hoy_count}</b></div>
        <div class="box">⚠️ Atrasados<br><b>{atrasados}</b></div>
        <div class="box">📅 Futuros<br><b>{futuros}</b></div>
    </div>

    <h3>💰 Dashboard financiero</h3>

    <div class="dashboard">
        <div class="box">💵 Pagado<br><b>${total_pagado}</b></div>
        <div class="box">🟡 Pendiente<br><b>${total_pendiente}</b></div>
        <div class="box">🔴 Vencido<br><b>${total_vencido}</b></div>
        <div class="box">📊 Neto<br><b>${total_pagado - total_vencido}</b></div>
    </div>

    <h3>🧠 Panel inteligente</h3>

    <div class="dashboard">
        <div class="box">🔴 Urgentes<br><b>{urgentes}</b></div>
        <div class="box">🟡 Acción pronto<br><b>{proximos}</b></div>
        <div class="box">🟢 Normales<br><b>{normales}</b></div>
        <div class="box">⚡ Sistema activo</div>
    </div>

    <h3>➕ Nuevo cliente</h3>

    <form method="POST">
        <input name="nombre" placeholder="Nombre"><br>
        <input name="servicio" placeholder="Servicio"><br>
        <input name="celular" placeholder="Celular"><br>
        <input name="email" placeholder="Email"><br>
        <input type="date" name="fecha"><br>

        <input name="monto" placeholder="Monto ($)"><br>

        <select name="estado_pago">
            <option>Pendiente</option>
            <option>Pagado</option>
            <option>Vencido</option>
        </select><br>

        <select name="accion">
            <option>Llamar</option>
            <option>Enviar correo</option>
        </select><br>

        <textarea name="notas" placeholder="Notas"></textarea><br>

        <button>Guardar</button>
    </form>

    <h3>📋 Clientes</h3>
    """

    for i, c in enumerate(data):

        estado = c.get("estado_pago","Pendiente")
        fecha = c.get("fecha")

        if estado == "Vencido":
            clase = "urgente"
            etiqueta = "🔴 URGENTE"
        elif fecha and fecha <= hoy:
            clase = "proximo"
            etiqueta = "🟡 ACCIÓN"
        else:
            clase = "normal"
            etiqueta = "🟢 OK"

        html += f"""
        <div class="card {clase}">
            <b>{c.get('codigo')}</b> - {c['nombre']}<br>
            {etiqueta}<br>
            💰 {c.get('monto')}<br>
            📅 {fecha}<br>
            📱 {c.get('celular')}<br>
            📧 {c.get('email')}<br>
            📝 {c.get('notas')}<br>
            👤 {c.get('user')}<br><br>

            <a href="/edit/{i}">✏️ Editar</a>
            <a href="/delete/{i}">🗑️ Eliminar</a>
        </div>
        """

    html += "</div>"
    return html

# ✏️ EDITAR
@app.route("/edit/<int:index>", methods=["GET","POST"])
def edit(index):

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":
        for k in ["nombre","servicio","celular","email","fecha","accion","notas","monto","estado_pago"]:
            data[index][k] = request.form.get(k)

        save_data(data)
        return redirect("/")

    c = data[index]

    return f"""
    <h2>Editar cliente</h2>

    <form method="POST">
        <input name="nombre" value="{c['nombre']}"><br>
        <input name="servicio" value="{c['servicio']}"><br>
        <input name="celular" value="{c.get('celular','')}"><br>
        <input name="email" value="{c.get('email','')}"><br>
        <input name="fecha" value="{c.get('fecha','')}"><br>
        <input name="monto" value="{c.get('monto','')}"><br>

        <select name="estado_pago">
            <option>{c.get('estado_pago','Pendiente')}</option>
            <option>Pagado</option>
            <option>Pendiente</option>
            <option>Vencido</option>
        </select><br>

        <button>Guardar</button>
    </form>
    """

# 🗑️ ELIMINAR
@app.route("/delete/<int:index>")
def delete(index):
    if session.get("logged"):
        data = load_data()
        if 0 <= index < len(data):
            data.pop(index)
            save_data(data)
    return redirect("/")

# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)