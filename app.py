from flask import Flask, request, redirect, url_for, session, Response
import json, os, csv
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "office_thinking_key"

FILE = "data.json"

# 👥 USUARIOS
USERS = {
    "paula": "paula1",
    "alfredo": "alfredo1"
}

# 📩 EMAIL (CONFIG SEGURO)
EMAIL_SENDER = "TU_CORREO_GMAIL"
EMAIL_PASSWORD = "TU_APP_PASSWORD"  # ⚠️ NO poner contraseña real aquí

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

# 📩 EMAIL REAL
def enviar_email(destinatario, asunto, mensaje):
    try:
        msg = MIMEText(mensaje)
        msg["Subject"] = asunto
        msg["From"] = EMAIL_SENDER
        msg["To"] = destinatario

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, destinatario, msg.as_string())
        server.quit()

        print("📩 Email enviado a", destinatario)

    except Exception as e:
        print("❌ Error email:", e)

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
        body {font-family:Arial;text-align:center;padding-top:100px;background:#f4f4f4;}
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

        # 🔔 EMAIL AUTOMÁTICO SI ESTÁ VENCIDO
        if cliente["estado_pago"] == "Vencido" and cliente["email"]:
            enviar_email(
                cliente["email"],
                "⚠️ Pago vencido - Office Thinking",
                f"Hola {cliente['nombre']}, tienes un pago vencido de ${cliente['monto']}."
            )

    hoy = datetime.now().strftime("%Y-%m-%d")

    total = len(data)
    hoy_count = 0
    atrasados = 0
    futuros = 0

    total_pagado = 0
    total_pendiente = 0
    total_vencido = 0

    for c in data:
        fecha = c.get("fecha")
        estado = c.get("estado_pago","Pendiente")
        monto = float(c.get("monto") or 0)

        if fecha == hoy:
            hoy_count += 1
        elif fecha and fecha < hoy:
            atrasados += 1
        else:
            futuros += 1

        if estado == "Pagado":
            total_pagado += monto
        elif estado == "Vencido":
            total_vencido += monto
        else:
            total_pendiente += monto

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
            display:flex;
            justify-content:space-between;
        }}

        .container {{ padding:20px; }}

        .dashboard {{
            display:grid;
            grid-template-columns: repeat(4,1fr);
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

        a {{ margin-left:10px; text-decoration:none; }}
    </style>

    <header>
        <div>🏢 Office Thinking CRM</div>
        <div>
            Usuario: {session.get("user")} |
            <a href="/logout" style="color:white;">🚪 Cerrar sesión</a>
        </div>
    </header>

    <div class="container">

    <h3>📊 Dashboard</h3>

    <div class="dashboard">
        <div class="box">📁 Total<br><b>{total}</b></div>
        <div class="box">🔥 Hoy<br><b>{hoy_count}</b></div>
        <div class="box">⚠️ Atrasados<br><b>{atrasados}</b></div>
        <div class="box">📅 Futuros<br><b>{futuros}</b></div>
    </div>

    <h3>💰 Finanzas</h3>

    <div class="dashboard">
        <div class="box">💵 Pagado<br><b>${total_pagado}</b></div>
        <div class="box">🟡 Pendiente<br><b>${total_pendiente}</b></div>
        <div class="box">🔴 Vencido<br><b>${total_vencido}</b></div>
        <div class="box">📊 Neto<br><b>${total_pagado - total_vencido}</b></div>
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

    <h3>📋 Clientes</h3>
    """

    for i, c in enumerate(data):

        estado = c.get("estado_pago","Pendiente")

        color = "🟢"
        if estado == "Vencido":
            color = "🔴"
        elif estado == "Pendiente":
            color = "🟡"

        html += f"""
        <div class="card">
            <b>{c['codigo']}</b> - {c['nombre']} {color}<br>
            💰 {c.get('monto')} | 📅 {c.get('fecha')}<br>
            📱 {c.get('celular')} | 📧 {c.get('email')}<br>

            <a href="/edit/{i}">✏️ Editar</a>
            <a href="/delete/{i}">🗑️ Eliminar</a>
        </div>
        """

    html += "</div>"
    return html

# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# 🗑️ DELETE
@app.route("/delete/<int:index>")
def delete(index):
    if session.get("logged"):
        data = load_data()
        data.pop(index)
        save_data(data)
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)