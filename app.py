from flask import Flask, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

USER = "admin"
PASS = "1234"

# 📦 cargar datos
def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        user = request.form.get("user")
        password = request.form.get("password")

        if user == USER and password == PASS:
            session["logged"] = True
            return redirect(url_for("home"))

        return "<h3>❌ Login incorrecto</h3>"

    return """
    <style>
        body { font-family: Arial; background:#f4f6f8; text-align:center; padding-top:100px; }
        .box { background:white; padding:20px; width:300px; margin:auto; border-radius:10px; box-shadow:0 2px 10px rgba(0,0,0,0.1); }
        input { width:90%; padding:8px; margin:5px 0; }
        button { padding:8px 15px; background:#2c3e50; color:white; border:none; border-radius:5px; }
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

# 🏠 PANEL PRINCIPAL
@app.route("/", methods=["GET", "POST"])
def home():

    if not session.get("logged"):
        return redirect(url_for("login"))

    data = load_data()

    # ➕ agregar cliente
    if request.method == "POST":
        nombre = request.form.get("nombre")
        servicio = request.form.get("servicio")

        if nombre and servicio:
            data.append({"nombre": nombre, "servicio": servicio})
            save_data(data)

    search = request.args.get("search")

    html = """
    <style>
        body { font-family: Arial; background:#eef1f5; margin:0; padding:0; }
        header { background:#2c3e50; color:white; padding:15px; }
        .container { padding:20px; }
        .card { background:white; padding:12px; margin:10px 0; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
        input { padding:6px; margin:3px; }
        button { padding:6px 10px; }
        a { text-decoration:none; padding:4px 8px; border-radius:4px; margin-left:5px; }
        .del { background:#e74c3c; color:white; }
        .edit { background:#f39c12; color:white; }
        .logout { float:right; color:white; }
    </style>

    <header>
        <h2>🏢 Office Thinking</h2>
        <a class="logout" href="/logout">Cerrar sesión</a>
    </header>

    <div class="container">

    <h3>➕ Agregar cliente</h3>
    <form method="POST">
        <input name="nombre" placeholder="Nombre">
        <input name="servicio" placeholder="Servicio">
        <button>Agregar</button>
    </form>

    <h3>🔍 Buscar</h3>
    <form method="GET">
        <input name="search" placeholder="Buscar cliente">
        <button>Buscar</button>
    </form>

    <hr>
    <h3>📋 Clientes</h3>
    """

    for i, c in enumerate(data):

        if search and search.lower() not in c["nombre"].lower():
            continue

        html += f"""
        <div class="card">
            <b>{c['nombre']}</b> - {c['servicio']}<br><br>
            <a class="del" href="/delete/{i}">Eliminar</a>
            <a class="edit" href="/edit/{i}">Editar</a>
        </div>
        """

    html += "</div>"
    return html

# ❌ eliminar
@app.route("/delete/<int:index>")
def delete(index):
    if session.get("logged"):
        data = load_data()
        if 0 <= index < len(data):
            data.pop(index)
            save_data(data)
    return redirect(url_for("home"))

# ✏️ editar
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):

    if not session.get("logged"):
        return redirect(url_for("login"))

    data = load_data()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        servicio = request.form.get("servicio")

        data[index] = {"nombre": nombre, "servicio": servicio}
        save_data(data)
        return redirect(url_for("home"))

    c = data[index]

    return f"""
    <h2>Editar cliente</h2>
    <form method="POST">
        <input name="nombre" value="{c['nombre']}"><br><br>
        <input name="servicio" value="{c['servicio']}"><br><br>
        <button>Guardar</button>
    </form>
    """

# 🚪 logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)