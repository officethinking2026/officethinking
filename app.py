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

def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# LOGIN
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
    <h2>Login</h2>
    <form method="POST">
        <input name="user">
        <input type="password" name="password">
        <button>Entrar</button>
    </form>
    """

# HOME
@app.route("/", methods=["GET","POST"])
def home():

    if not session.get("logged"):
        return redirect("/login")

    data = load_data()

    if request.method == "POST":
        data.append({
            "nombre": request.form.get("nombre"),
            "servicio": request.form.get("servicio"),
            "fecha": request.form.get("fecha"),
            "accion": request.form.get("accion"),
            "notas": request.form.get("notas"),
            "user": session.get("user")
        })
        save_data(data)

    html = f"""
    <h2>Office Thinking</h2>
    Usuario: {session.get("user")} <br><br>

    <h3>Nuevo seguimiento</h3>
    <form method="POST">
        Nombre: <input name="nombre"><br>
        Servicio: <input name="servicio"><br>
        Fecha: <input type="date" name="fecha"><br>

        Acción:
        <select name="accion">
            <option>Llamar</option>
            <option>Enviar correo</option>
        </select><br>

        Notas:<br>
        <textarea name="notas"></textarea><br>

        <button>Guardar</button>
    </form>

    <h3>📅 Pendientes</h3>
    """

    hoy = datetime.now().strftime("%Y-%m-%d")

    for i, c in enumerate(data):

        estado = "⏳"
        if c.get("fecha") == hoy:
            estado = "🔥 HOY"
        elif c.get("fecha") < hoy:
            estado = "⚠️ ATRASADO"

        html += f"""
        <div style="border:1px solid #ccc; margin:10px; padding:10px;">
            <b>{c['nombre']}</b> - {c['servicio']}<br>
            📅 {c.get('fecha')} | {estado}<br>
            📞 {c.get('accion')}<br>
            📝 {c.get('notas')}<br>
            👤 {c.get('user')}<br>
        </div>
        """

    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)