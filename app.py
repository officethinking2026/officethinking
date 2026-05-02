from flask import Flask, request, redirect, session
import json, os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

# 👥 USUARIOS
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
            return redirect("/")

    return """
    <style>
        body{
            font-family:Arial;
            background:#f4f6f9;
            display:flex;
            justify-content:center;
            align-items:center;
            height:100vh;
        }
        .box{
            background:white;
            padding:30px;
            border-radius:12px;
            box-shadow:0 2px 10px rgba(0,0,0,0.1);
        }
        input,button{
            padding:10px;
            margin:5px 0;
            width:100%;
        }
        button{
            background:#2563eb;
            color:white;
            border:none;
            border-radius:6px;
        }
    </style>

    <div class="box">
        <h2>🏢 Office Thinking</h2>
        <form method="POST">
            <input name="user" placeholder="Usuario">
            <input type="password" name="password" placeholder="Contraseña">
            <button>Entrar</button>
        </form>
    </div>
    """

# 🏠 HOME
@app.route("/", methods=["GET","POST"])
def home():

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    hoy = datetime.now().date()
    prox_7 = hoy + timedelta(days=7)

    # ➕ CREAR CLIENTE
    if request.method == "POST":
        data.append({
            "codigo": generate_code(data),
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "celular": request.form.get("celular"),
            "email": request.form.get("email"),
            "fecha": request.form.get("fecha"),
            "monto": request.form.get("monto"),
            "estado_pago": request.form.get("estado_pago"),
            "notas": request.form.get("notas")
        })
        save_data(data)

    # 📊 ESTADÍSTICAS
    total = len(data)
    pagados = sum(1 for c in data if c.get("estado_pago") == "Pagado")
    pendientes = sum(1 for c in data if c.get("estado_pago") != "Pagado")
    hoy_count = sum(1 for c in data if c.get("fecha") == hoy.strftime("%Y-%m-%d"))

    # 🎨 UI
    html = f"""
    <style>
        body {{
            margin:0;
            font-family:Arial;
            background:#f4f6f9;
        }}

        .sidebar {{
            position:fixed;
            width:220px;
            height:100%;
            background:#111827;
            color:white;
            padding:20px;
        }}

        .sidebar a {{
            display:block;
            color:white;
            text-decoration:none;
            padding:10px;
            border-radius:6px;
        }}

        .sidebar a:hover {{
            background:#374151;
        }}

        .main {{
            margin-left:240px;
            padding:20px;
        }}

        .grid {{
            display:grid;
            grid-template-columns:repeat(4,1fr);
            gap:10px;
        }}

        .card {{
            background:white;
            padding:15px;
            border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
        }}

        .client {{
            background:white;
            padding:15px;
            margin-top:10px;
            border-radius:12px;
            box-shadow:0 2px 8px rgba(0,0,0,0.08);
        }}

        input,select,textarea {{
            width:100%;
            padding:8px;
            margin:5px 0;
            border-radius:6px;
            border:1px solid #ddd;
        }}

        button {{
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
        <a href="#">👥 Clientes</a>
        <a href="/logout">🚪 Salir</a>
    </div>

    <div class="main">

        <h2>📊 Dashboard</h2>

        <div class="grid">
            <div class="card">👥 Total<br><b>{total}</b></div>
            <div class="card">💰 Pagados<br><b>{pagados}</b></div>
            <div class="card">⚠️ Pendientes<br><b>{pendientes}</b></div>
            <div class="card">📅 Hoy<br><b>{hoy_count}</b></div>
        </div>

        <div class="card" style="margin-top:20px;">
            <h3>➕ Nuevo cliente</h3>

            <form method="POST">
                <input name="nombre" placeholder="Nombre">
                <input name="servicio" placeholder="Servicio">
                <input name="celular" placeholder="Celular">
                <input name="email" placeholder="Email">
                <input type="date" name="fecha">
                <input name="monto" placeholder="Monto">

                <select name="estado_pago">
                    <option>Pendiente</option>
                    <option>Pagado</option>
                    <option>Vencido</option>
                </select>

                <textarea name="notas" placeholder="Notas"></textarea>

                <button>Guardar</button>
            </form>
        </div>

        <h3>📋 Clientes</h3>
    """

    for i, c in enumerate(data):

        estado = c.get("estado_pago")

        color = "🟢"
        if estado == "Vencido":
            color = "🔴"
        elif estado == "Pendiente":
            color = "🟡"

        html += f"""
        <div class="client">
            <b>{c.get('codigo')}</b> - {c.get('nombre')} {color}<br>
            📅 {c.get('fecha')} | 💰 {c.get('monto')}<br>
            📱 {c.get('celular')} | 📧 {c.get('email')}<br>

            <a href="/edit/{i}">✏️ Editar</a> |
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

    if index < 0 or index >= len(data):
        return redirect("/")

    c = data[index]

    if request.method == "POST":

        campos = ["nombre","servicio","celular","email","fecha","monto","estado_pago","notas"]

        for k in campos:
            c[k] = request.form.get(k,"")

        data[index] = c
        save_data(data)

        return redirect("/")

    return f"""
    <h2>✏️ Editar cliente</h2>

    <form method="POST">
        <input name="nombre" value="{c.get('nombre','')}"><br>
        <input name="servicio" value="{c.get('servicio','')}"><br>
        <input name="celular" value="{c.get('celular','')}"><br>
        <input name="email" value="{c.get('email','')}"><br>
        <input name="fecha" value="{c.get('fecha','')}"><br>
        <input name="monto" value="{c.get('monto','')}"><br>

        <select name="estado_pago">
            <option>{c.get('estado_pago','Pendiente')}</option>
            <option>Pendiente</option>
            <option>Pagado</option>
            <option>Vencido</option>
        </select><br>

        <textarea name="notas">{c.get('notas','')}</textarea><br>

        <button>Guardar cambios</button>
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