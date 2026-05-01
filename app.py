from flask import Flask, request, redirect, url_for, session, send_file
import json, os
from datetime import datetime
import csv

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

# 🔢 generar código cliente
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

        return "<h3>❌ Login incorrecto</h3>"

    return """
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)),
            url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Canada.svg/1280px-Flag_of_Canada.svg.png');
            background-size: cover;
            background-position: center;
            text-align:center;
            padding-top:100px;
        }
        .box {
            background:white;
            padding:25px;
            width:300px;
            margin:auto;
            border-radius:10px;
        }
        input {
            width:90%;
            padding:10px;
            margin:5px 0;
        }
        button {
            padding:10px;
            background:#c0392b;
            color:white;
            border:none;
            border-radius:5px;
        }
    </style>

    <div class="box">
        <h2>🏢 Office Thinking</h2>
        <form method="POST">
            <input name="user" placeholder="Usuario"><br>
            <input type="password" name="password" placeholder="Contraseña"><br>
            <button>Entrar</button>
        </form>
    </div>
    """

# 📄 EXPORT CSV
@app.route("/export")
def export():
    data = load_data()
    file = "clientes.csv"

    with open(file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Codigo","Nombre","Servicio","Celular","Email","Fecha","Accion","Notas","Usuario"])

        for c in data:
            writer.writerow([
                c.get("codigo",""),
                c.get("nombre",""),
                c.get("servicio",""),
                c.get("celular",""),
                c.get("email",""),
                c.get("fecha",""),
                c.get("accion",""),
                c.get("notas",""),
                c.get("user","")
            ])

    return send_file(file, as_attachment=True)

# 🏠 HOME
@app.route("/", methods=["GET","POST"])
def home():

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":

        code = generate_code(data)

        data.append({
            "codigo": code,
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "celular": request.form.get("celular"),
            "email": request.form.get("email"),
            "fecha": request.form.get("fecha"),
            "accion": request.form.get("accion"),
            "notas": request.form.get("notas"),
            "user": session.get("user")
        })

        save_data(data)

    hoy = datetime.now().strftime("%Y-%m-%d")

    html = f"""
    <style>
        body {{
            font-family: Arial;
            background: linear-gradient(rgba(255,255,255,0.85), rgba(255,255,255,0.85)),
            url('https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Flag_of_Canada.svg/1280px-Flag_of_Canada.svg.png');
            background-size: cover;
            background-position: center;
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

        .card {{
            background:white;
            padding:15px;
            margin:10px 0;
            border-radius:10px;
        }}

        input, select, textarea {{
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
        <h2>🏢 Office Thinking</h2>
        Usuario: {session.get("user")}
        <a href="/export">📄 Exportar CSV</a>
        <a href="/logout">Cerrar sesión</a>
    </header>

    <div class="container">

    <h3>➕ Nuevo cliente</h3>
    <form method="POST">
        <input name="nombre" placeholder="Nombre"><br>
        <input name="servicio" placeholder="Servicio"><br>
        <input name="celular" placeholder="Celular"><br>
        <input name="email" placeholder="Email"><br>
        <input type="date" name="fecha"><br>

        <select name="accion">
            <option>Llamar</option>
            <option>Enviar correo</option>
        </select><br>

        <textarea name="notas" placeholder="Notas"></textarea><br>

        <button>Guardar</button>
    </form>

    <h3>📋 Clientes</h3>
    """

    for c in data:

        estado = "⏳"
        if c.get("fecha") == hoy:
            estado = "🔥 HOY"
        elif c.get("fecha") and c.get("fecha") < hoy:
            estado = "⚠️ ATRASADO"

        html += f"""
        <div class="card">
            <b>{c.get('codigo')}</b> - {c['nombre']}<br>
            Servicio: {c['servicio']}<br>
            📱 {c.get('celular','')}<br>
            📧 {c.get('email','')}<br>
            📅 {c.get('fecha')} {estado}<br>
            📞 {c.get('accion')}<br>
            📝 {c.get('notas')}<br>
            👤 {c.get('user')}
        </div>
        """

    html += "</div>"
    return html

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)