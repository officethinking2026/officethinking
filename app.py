from flask import Flask, request, redirect, url_for, session
import json
import os

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

USER = "admin"
PASS = "1234"

def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# LOGIN
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
        body { font-family: Arial; background:#eef1f5; text-align:center; padding-top:100px; }
        .box { background:white; padding:25px; width:300px; margin:auto; border-radius:10px; }
        input { width:90%; padding:10px; margin:5px 0; }
        button { padding:10px; background:#2c3e50; color:white; border:none; border-radius:5px; }
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

# HOME
@app.route("/", methods=["GET", "POST"])
def home():

    if not session.get("logged"):
        return redirect(url_for("login"))

    data = load_data()

    if request.method == "POST":
        nombre = request.form.get("nombre")
        servicio = request.form.get("servicio")
        telefono = request.form.get("telefono")
        email = request.form.get("email")

        if nombre and servicio:
            data.append({
                "nombre": nombre,
                "servicio": servicio,
                "telefono": telefono,
                "email": email
            })
            save_data(data)

    search = request.args.get("search")

    html = """
    <style>
        body { font-family: Arial; background:#eef1f5; margin:0; }
        header { background:#2c3e50; color:white; padding:15px; }
        .container { padding:20px; }
        .card { background:white; padding:15px; margin:10px 0; border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.1); }
        input { padding:8px; margin:5px; }
        button { padding:8px 12px; }
        a { text-decoration:none; padding:5px 8px; border-radius:5px; margin-left:5px; }
        .del { background:#e74c3c; color:white; }
        .edit { background:#f39c12; color:white; }
        .logout { float:right; color:white; }
    </style>

    <header>
        <h2>🏢 Office Thinking</h2>
        <a class="logout" href="/logout">Cerrar sesión</a>
    </header>

    <div class="container">

    <h3>➕ Nuevo cliente</h3>
    <form method="POST">
        <input name="nombre" placeholder="Nombre">
        <input name="servicio" placeholder="Servicio">
        <input name="telefono" placeholder="Teléfono">
        <input name="email" placeholder="Email">
        <button>Guardar</button>
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
            <b>{c['nombre']}</b><br>
            Servicio: {c['servicio']}<br>
            Teléfono: {c.get('telefono','')}<br>
            Email: {c.get('email','')}<br><br>

            <a class="del" href="/delete/{i}">Eliminar</a>
            <a class="edit" href="/edit/{i}">Editar</a>
        </div>
        """

    html += "</div>"
    return html

# DELETE
@app.route("/delete/<int:index>")
def delete(index):
    if session.get("logged"):
        data = load_data()
        if 0 <= index < len(data):
            data.pop(index)
            save_data(data)
    return redirect(url_for("home"))

# EDIT
@app.route("/edit/<int:index>", methods=["GET", "POST"])
def edit(index):

    if not session.get("logged"):
        return redirect(url_for("login"))

    data = load_data()

    if request.method == "POST":
        data[index] = {
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "telefono": request.form.get("telefono"),
            "email": request.form.get("email")
        }
        save_data(data)
        return redirect(url_for("home"))

    c = data[index]

    return f"""
    <h2>Editar cliente</h2>
    <form method="POST">
        Nombre: <input name="nombre" value="{c['nombre']}"><br><br>
        Servicio: <input name="servicio" value="{c['servicio']}"><br><br>
        Teléfono: <input name="telefono" value="{c.get('telefono','')}"><br><br>
        Email: <input name="email" value="{c.get('email','')}"><br><br>
        <button>Guardar</button>
    </form>
    """

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)