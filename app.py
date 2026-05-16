from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'segredo'

def conectar():
    return sqlite3.connect('database.db')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/logar', methods=['POST'])
def logar():
    user = request.form['username']
    senha = request.form['senha']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE username=? AND senha=?", (user, senha))
    usuario = cursor.fetchone()

    if usuario:
        session['usuario'] = user
        return redirect('/dashboard')
    else:
        return "Login inválido"

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('dashboard.html')


@app.route('/pacientes')
def pacientes():
    if 'usuario' not in session:
        return redirect('/')
    return render_template('pacientes.html')


@app.route('/salvar_paciente', methods=['POST'])
def salvar_paciente():
    prontuario = request.form['prontuario']
    nome = request.form['nome']
    cns = request.form['cns']
    data_nascimento = request.form['data_nascimento']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pacientes (prontuario, nome, cns, data_nascimento)
        VALUES (?, ?, ?, ?)
    """, (prontuario, nome, cns, data_nascimento))

    conn.commit()
    conn.close()

    return redirect('/pacientes')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')


@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    name = request.form['name']
    cpf = request.form['cpf']
    email = request.form['e-mail']
    senha = request.form['senha']
    cnes = request.form['cnes']

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO usuarios (name, cpf, email, senha, cnes)
        VALUES (?, ?)
    """, (name, cpf, email, senha, cnes))

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/teste')
def teste():
    return "funcionando"

app.run(debug=True)