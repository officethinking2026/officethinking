from flask import Flask, request, redirect, url_for, session
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

    hoy = datetime.now().date()
    prox_7 = hoy + timedelta(days=7)
    ant_7 = hoy - timedelta(days=7)

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

    # 📊 CONTADORES
    hoy_list = []
    futuro_list = []
    pasado_list = []

    for c in data:

        try:
            fecha = datetime.strptime(c.get("fecha",""), "%Y-%m-%d").date()
        except:
            continue

        if fecha == hoy:
            hoy_list.append(c)
        elif hoy < fecha <= prox_7:
            futuro_list.append(c)
        elif ant_7 <= fecha < hoy:
            pasado_list.append(c)

    # 🎨 UI
    html = f"""
    <style>
        body {{
            font-family: Arial;
            margin:0;
            background:#f5f5f5;
        }}

        header {{
            background:#c0392b;
            color:white;
            padding:15px;
            display:flex;
            justify-content:space-between;
        }}

        .grid {{
            display:grid;
            grid-template-columns:repeat(3,1fr);
            gap:10px;
            padding:10px;
        }}

        .box {{
            background:white;
            padding:10px;
            border-radius:10px;
            text-align:center;
        }}

        .card {{
            background:white;
            margin:10px;
            padding:10px;
            border-radius:10px;
        }}

        input,select,textarea {{
            padding:6px;
            margin:3px;
            width:90%;
        }}

        button {{
            padding:8px;
            background:#c0392b;
            color:white;
            border:none;
            border-radius:5px;
        }}

        a {{ margin-left:10px; }}
    </style>

    <header>
        <div>🏢 Office Thinking CRM</div>
        <div>
            Usuario: {session.get("user")} |
            <a href="/logout" style="color:white;">🚪 Salir</a>
        </div>
    </header>

    <div class="grid">
        <div class="box">📅 Hoy<br><b>{len(hoy_list)}</b></div>
        <div class="box">➡️ Próximos<br><b>{len(futuro_list)}</b></div>
        <div class="box">⬅️ Pasados<br><b>{len(pasado_list)}</b></div>
    </div>

    <div class="card">
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

            <textarea name="notas" placeholder="Notas"></textarea><br>

            <button>Guardar</button>
        </form>
    </div>

    <h3 style="margin-left:10px;">📋 Clientes</h3>
    """

    for i, c in enumerate(data):

        html += f"""
        <div class="card">
            <b>{c.get('codigo')}</b> - {c.get('nombre')}<br>
            📅 {c.get('fecha')} | 💰 {c.get('monto')}<br>
            📱 {c.get('celular')} | 📧 {c.get('email')}<br>

            <a href="/edit/{i}">✏️ Editar</a>
            <a href="/delete/{i}">🗑️ Eliminar</a>
        </div>
        """

    html += "</div>"
    return html

# ✏️ EDITAR (FIX DEFINITIVO)
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