import re
from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'um_segredo_bem_forte_123456'

def conectar():
    return sqlite3.connect('database.db', timeout=10)


# 🔐 LOGIN
@app.route('/')
def login():
    return render_template('login.html')


@app.route('/logar', methods=['POST'])
def logar():
    user = request.form.get('cpf')
    senha = request.form.get('senha')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE cpf=?", (user,))
    usuario = cursor.fetchone()

    conn.close()  # ✅ FECHA CONEXÃO

    if usuario and check_password_hash(usuario[4], senha):
        session['usuario'] = usuario[1]  # nome do usuário
        return redirect('/dashboard')
    else:
        return render_template('login.html', erro="CPF ou senha inválidos")


# 🔒 DASHBOARD PROTEGIDO
@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()

    return render_template('dashboard.html', pacientes=pacientes, usuario=session['usuario'])

# 👤 PACIENTES
@app.route('/pacientes')
def pacientes():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('pacientes.html')


@app.route('/salvar_paciente', methods=['POST'])
def salvar_paciente():
    if 'usuario' not in session:
        return redirect('/')

    prontuario = request.form.get('prontuario')
    nome = request.form.get('nome')
    cns = request.form.get('cns')
    data_nascimento = request.form.get('data_nascimento')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pacientes (prontuario, nome, cns, data_nascimento)
        VALUES (?, ?, ?, ?)
    """, (prontuario, nome, cns, data_nascimento))

    conn.commit()
    conn.close()

    return redirect('/pacientes')


# 📝 CADASTRO
@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    name = request.form.get('name')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar = request.form.get('confirmar_senha')
    cnes = request.form.get('cnes')

    # ✅ Senhas iguais
    if senha != confirmar:
        return render_template('cadastro.html', erro="As senhas não coincidem")

    # ✅ Regras de senha
    if len(senha) < 6:
        return render_template('cadastro.html', erro="Mínimo 6 caracteres")

    if not re.search(r'[A-Z]', senha):
        return render_template('cadastro.html', erro="Precisa de letra maiúscula")

    if not re.search(r'[a-z]', senha):
        return render_template('cadastro.html', erro="Precisa de letra minúscula")

    if not re.search(r'[0-9]', senha):
        return render_template('cadastro.html', erro="Precisa de número")

    conn = conectar()
    cursor = conn.cursor()

    # ✅ Verificar CPF duplicado
    cursor.execute("SELECT * FROM usuarios WHERE cpf=?", (cpf,))
    if cursor.fetchone():
        conn.close()
        return render_template('cadastro.html', erro="CPF já cadastrado")

    # 🔐 Criptografar senha
    senha_hash = generate_password_hash(senha)

    cursor.execute("""
        INSERT INTO usuarios (name, cpf, email, senha, cnes)
        VALUES (?, ?, ?, ?, ?)
    """, (name, cpf, email, senha_hash, cnes))

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/atendimentos')
def atendimentos():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('atendimentos.html')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/teste')
def teste():
    return "funcionando"


app.run(debug=True)