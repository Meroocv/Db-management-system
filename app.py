import os
import re
import sqlite3

from flask import Flask, jsonify, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'um_segredo_bem_forte_123456'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'perfis')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

CBO_OPCOES = {
    "411010": "Assistente em Administracao",
    "251605": "Assistente Social",
    "322230": "Auxiliar em Enfermagem",
    "223405": "Farmaceutico",
    "223505": "Enfermeiro",
    "224140": "Profissional de Educacao Fisica",
    "251510": "Psicologo Clinico",
    "223905": "Terapeuta Ocupacional",
    "322205": "Tecnico em Enfermagem",
    "225125": "Medico Clinico",
    "225133": "Medico Psiquiatra",
    "223710": "Nutricionista",
}
EXTENSOES_FOTO = {"png", "jpg", "jpeg", "webp"}


def conectar():
    return sqlite3.connect('database.db', timeout=10)


def conectar_rh():
    conn = sqlite3.connect('rh.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def foto_permitida(nome_arquivo):
    return (
        '.' in nome_arquivo and
        nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_FOTO
    )


def init_rh_database():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    conn = conectar_rh()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS servidores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cnes TEXT NOT NULL,
            name TEXT NOT NULL,
            cbo TEXT NOT NULL,
            cpf TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL,
            senha TEXT NOT NULL,
            foto_perfil TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS solicitacoes_cbo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servidor_id INTEGER NOT NULL,
            cbo_atual TEXT NOT NULL,
            cbo_solicitado TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pendente',
            aprovado_por INTEGER,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            analisado_em DATETIME,
            FOREIGN KEY (servidor_id) REFERENCES servidores (id),
            FOREIGN KEY (aprovado_por) REFERENCES servidores (id)
        )
    """)

    try:
        legado = conectar()
        legado_cursor = legado.cursor()
        legado_cursor.execute("SELECT cnes, name, cbo, cpf, email, senha FROM usuarios")
        for usuario in legado_cursor.fetchall():
            cursor.execute("""
                INSERT OR IGNORE INTO servidores (cnes, name, cbo, cpf, email, senha)
                VALUES (?, ?, ?, ?, ?, ?)
            """, usuario)
        legado.close()
    except sqlite3.Error:
        pass

    conn.commit()
    conn.close()


def servidor_logado():
    if 'usuario_id' not in session:
        return None

    conn = conectar_rh()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servidores WHERE id=?", (session['usuario_id'],))
    servidor = cursor.fetchone()
    conn.close()
    return servidor


def pode_aprovar_rh():
    return session.get('usuario_cbo') == '411010'


def contexto_usuario():
    servidor = servidor_logado()
    return {
        'usuario': session.get('usuario'),
        'usuario_foto': session.get('usuario_foto'),
        'servidor': servidor,
        'cbo_opcoes': CBO_OPCOES,
        'pode_aprovar_rh': pode_aprovar_rh(),
    }


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/logar', methods=['POST'])
def logar():
    user = request.form.get('cpf')
    senha = request.form.get('senha')

    conn = conectar_rh()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM servidores WHERE cpf=?", (user,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario and check_password_hash(usuario['senha'], senha):
        session['usuario_id'] = usuario['id']
        session['usuario'] = usuario['name']
        session['usuario_cbo'] = usuario['cbo']
        session['usuario_foto'] = usuario['foto_perfil']
        return redirect('/dashboard')

    return render_template('login.html', erro="CPF ou senha invalidos")


@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')

    solicitacoes_cbo = []
    if pode_aprovar_rh():
        conn = conectar_rh()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sc.id, s.name, s.cpf, sc.cbo_atual, sc.cbo_solicitado, sc.criado_em
            FROM solicitacoes_cbo sc
            JOIN servidores s ON s.id = sc.servidor_id
            WHERE sc.status = 'pendente'
            ORDER BY sc.criado_em ASC
        """)
        solicitacoes_cbo = cursor.fetchall()
        conn.close()

    contexto = contexto_usuario()
    contexto['solicitacoes_cbo'] = solicitacoes_cbo
    return render_template('dashboard.html', **contexto)


@app.route('/pacientes')
def pacientes():
    if 'usuario' not in session:
        return redirect('/')
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()

    conn.close()

    contexto = contexto_usuario()
    contexto['pacientes'] = pacientes
    return render_template('pacientes.html', **contexto)


@app.route('/novo_paciente', methods=['POST'])
def novo_paciente():
    dados = request.json

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pacientes (
            nome_paciente, nome_social, cpf, rg, cns_paciente,
            data_nascimento, sexo, naturalidade, raca_cor,
            escolaridade, etnia, orientacao_religiosa,
            nome_mae, nome_pai, nome_responsavel,
            grau_parentesco_responsavel, telefone_responsavel,
            telefone, municipio, uf, zona, cep, bairro,
            logradouro, numero, complemento,
            statusPaciente, terapeuta_referencia,
            cid, data_admissao, data_conclusao
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        dados.get('nome_paciente'),
        dados.get('nome_social'),
        dados.get('cpf'),
        dados.get('rg'),
        dados.get('cns_paciente'),
        dados.get('data_nascimento'),
        dados.get('sexo'),
        dados.get('naturalidade'),
        dados.get('raca_cor'),
        dados.get('escolaridade'),
        dados.get('etnia'),
        dados.get('orientacao_religiosa'),
        dados.get('nome_mae'),
        dados.get('nome_pai'),
        dados.get('nome_responsavel'),
        dados.get('grau_parentesco_responsavel'),
        dados.get('telefone_responsavel'),
        dados.get('telefone'),
        dados.get('municipio'),
        dados.get('uf'),
        dados.get('zona'),
        dados.get('cep'),
        dados.get('bairro'),
        dados.get('logradouro'),
        dados.get('numero'),
        dados.get('complemento'),
        dados.get('statusPaciente'),
        dados.get('terapeuta_referencia'),
        dados.get('cid'),
        dados.get('data_admissao'),
        dados.get('data_conclusao')
    ))

    conn.commit()
    conn.close()

    return {"mensagem": "Paciente cadastrado com sucesso!"}


@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', cbo_opcoes=CBO_OPCOES)


@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    name = request.form.get('name')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar = request.form.get('confirmar_senha')
    cnes = request.form.get('cnes')
    cbo = request.form.get('cbo')
    if not cbo:
        return render_template('cadastro.html', erro="CBO e obrigatorio", cbo_opcoes=CBO_OPCOES)

    if senha != confirmar:
        return render_template('cadastro.html', erro="As senhas nao coincidem", cbo_opcoes=CBO_OPCOES)

    if len(senha) < 6:
        return render_template('cadastro.html', erro="Minimo 6 caracteres", cbo_opcoes=CBO_OPCOES)

    if not re.search(r'[A-Z]', senha):
        return render_template('cadastro.html', erro="Precisa de letra maiuscula", cbo_opcoes=CBO_OPCOES)

    if not re.search(r'[a-z]', senha):
        return render_template('cadastro.html', erro="Precisa de letra minuscula", cbo_opcoes=CBO_OPCOES)

    if not re.search(r'[0-9]', senha):
        return render_template('cadastro.html', erro="Precisa de numero", cbo_opcoes=CBO_OPCOES)

    conn = conectar_rh()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM servidores WHERE cpf=?", (cpf,))
    if cursor.fetchone():
        conn.close()
        return render_template('cadastro.html', erro="CPF ja cadastrado", cbo_opcoes=CBO_OPCOES)

    senha_hash = generate_password_hash(senha)

    cursor.execute("""
        INSERT INTO servidores (name, cpf, email, senha, cnes, cbo)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, cpf, email, senha_hash, cnes, cbo))

    conn.commit()
    conn.close()

    return redirect('/')


@app.route('/atendimentos')
def atendimentos():
    if 'usuario' not in session:
        return redirect('/')
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            a.id,
            a.prontuario,
            p.nome_paciente,
            a.data_atendimento,
            a.profissional,
            a.procedimentos,
            a.acolhimento_24h,
            a.paciente_aceitou,
            a.observacoes
        FROM atendimentos a
        LEFT JOIN pacientes p ON p.prontuario = a.prontuario
        ORDER BY a.data_atendimento DESC, a.id DESC
    """)
    atendimentos = cursor.fetchall()
    prontuarios_atendidos = len({atendimento[1] for atendimento in atendimentos})

    conn.close()

    contexto = contexto_usuario()
    contexto['atendimentos'] = atendimentos
    contexto['prontuarios_atendidos'] = prontuarios_atendidos
    return render_template('atendimentos.html', **contexto)


@app.route('/novo_atendimento', methods=['POST'])
def novo_atendimento():
    if 'usuario' not in session:
        return jsonify({'erro': 'Usuario nao autenticado'}), 401

    dados = request.get_json()
    prontuario = dados.get('prontuario', '').strip()

    if not prontuario:
        return jsonify({'erro': 'Informe o prontuario do paciente'}), 400

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT prontuario
            FROM pacientes
            WHERE ltrim(prontuario, '0') = ?
        """, (prontuario.lstrip('0'),))

        paciente = cursor.fetchone()

        if not paciente:
            conn.close()
            return jsonify({'erro': 'Paciente nao encontrado'}), 404

        cursor.execute("""
            INSERT INTO atendimentos (
                prontuario, data_atendimento, profissional, procedimentos,
                acolhimento_24h, paciente_aceitou, observacoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            paciente[0],
            dados.get('data_atendimento'),
            dados.get('profissional'),
            dados.get('procedimentos'),
            dados.get('acolhimento_24h'),
            dados.get('paciente_aceitou'),
            dados.get('observacoes')
        ))

        conn.commit()
        conn.close()

        return jsonify({'mensagem': 'Atendimento cadastrado com sucesso!'})

    except Exception as e:
        print("ERRO INSERT ATENDIMENTO:", e)
        return jsonify({'erro': str(e)}), 500


@app.route('/atualizar_perfil', methods=['POST'])
def atualizar_perfil():
    servidor = servidor_logado()
    if not servidor:
        return redirect('/')

    nome = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    cnes = request.form.get('cnes', '').strip()
    cbo_solicitado = request.form.get('cbo', '').strip()
    foto = request.files.get('foto_perfil')

    if not nome or not email or not cnes:
        return redirect('/dashboard')

    conn = conectar_rh()
    cursor = conn.cursor()
    foto_perfil = servidor['foto_perfil']

    if foto and foto.filename and foto_permitida(foto.filename):
        extensao = foto.filename.rsplit('.', 1)[1].lower()
        nome_arquivo = secure_filename(f"servidor_{servidor['id']}.{extensao}")
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        foto.save(caminho)
        foto_perfil = f"uploads/perfis/{nome_arquivo}"

    cursor.execute("""
        UPDATE servidores
        SET name=?, email=?, cnes=?, foto_perfil=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
    """, (nome, email, cnes, foto_perfil, servidor['id']))

    if cbo_solicitado and cbo_solicitado != servidor['cbo']:
        cursor.execute("""
            SELECT id
            FROM solicitacoes_cbo
            WHERE servidor_id=? AND status='pendente'
        """, (servidor['id'],))
        pendente = cursor.fetchone()

        if pendente:
            cursor.execute("""
                UPDATE solicitacoes_cbo
                SET cbo_atual=?, cbo_solicitado=?, criado_em=CURRENT_TIMESTAMP
                WHERE id=?
            """, (servidor['cbo'], cbo_solicitado, pendente['id']))
        else:
            cursor.execute("""
                INSERT INTO solicitacoes_cbo (servidor_id, cbo_atual, cbo_solicitado)
                VALUES (?, ?, ?)
            """, (servidor['id'], servidor['cbo'], cbo_solicitado))

    conn.commit()
    conn.close()

    session['usuario'] = nome
    session['usuario_foto'] = foto_perfil
    return redirect('/dashboard')


@app.route('/aprovar_cbo/<int:solicitacao_id>', methods=['POST'])
def aprovar_cbo(solicitacao_id):
    if 'usuario_id' not in session or not pode_aprovar_rh():
        return redirect('/dashboard')

    acao = request.form.get('acao')
    conn = conectar_rh()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM solicitacoes_cbo
        WHERE id=? AND status='pendente'
    """, (solicitacao_id,))
    solicitacao = cursor.fetchone()

    if solicitacao and acao == 'aprovar':
        cursor.execute("""
            UPDATE servidores
            SET cbo=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (solicitacao['cbo_solicitado'], solicitacao['servidor_id']))
        status = 'aprovada'
    else:
        status = 'rejeitada'

    if solicitacao:
        cursor.execute("""
            UPDATE solicitacoes_cbo
            SET status=?, aprovado_por=?, analisado_em=CURRENT_TIMESTAMP
            WHERE id=?
        """, (status, session['usuario_id'], solicitacao_id))

    conn.commit()
    conn.close()
    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/atualizar_paciente', methods=['POST'])
def atualizar_paciente():
    dados = request.get_json()

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pacientes
            SET
                terapeuta_referencia=?,
                nome_paciente=?,
                nome_social=?,
                cns_paciente=?,
                rg=?,
                cpf=?,
                naturalidade=?,
                sexo=?,
                data_nascimento=?,
                raca_cor=?,
                etnia=?,
                orientacao_religiosa=?,
                escolaridade=?,
                nome_mae=?,
                nome_pai=?,
                nome_responsavel=?,
                grau_parentesco_responsavel=?,
                telefone_responsavel=?,
                municipio=?,
                uf=?,
                zona=?,
                cep=?,
                bairro=?,
                tipo=?,
                logradouro=?,
                numero=?,
                complemento=?,
                ddd=?,
                telefone=?,
                data_admissao=?,
                origem_paciente=?,
                especificacao_origem=?,
                cnes_usf=?,
                cid=?,
                statusPaciente=?,
                data_conclusao=?
            WHERE prontuario=?
        """, (
            dados.get('terapeuta_referencia'),
            dados.get('nome_paciente'),
            dados.get('nome_social'),
            dados.get('cns_paciente'),
            dados.get('rg'),
            dados.get('cpf'),
            dados.get('naturalidade'),
            dados.get('sexo'),
            dados.get('data_nascimento'),
            dados.get('raca_cor'),
            dados.get('etnia'),
            dados.get('orientacao_religiosa'),
            dados.get('escolaridade'),
            dados.get('nome_mae'),
            dados.get('nome_pai'),
            dados.get('nome_responsavel'),
            dados.get('grau_parentesco_responsavel'),
            dados.get('telefone_responsavel'),
            dados.get('municipio'),
            dados.get('uf'),
            dados.get('zona'),
            dados.get('cep'),
            dados.get('bairro'),
            dados.get('tipo'),
            dados.get('logradouro'),
            dados.get('numero'),
            dados.get('complemento'),
            dados.get('ddd'),
            dados.get('telefone'),
            dados.get('data_admissao'),
            dados.get('origem_paciente'),
            dados.get('especificacao_origem'),
            dados.get('cnes_usf'),
            dados.get('cid'),
            dados.get('statusPaciente'),
            dados.get('data_conclusao'),
            dados.get('prontuario')
        ))

        conn.commit()
        conn.close()

        return jsonify({'mensagem': 'Paciente atualizado com sucesso!'})

    except Exception as e:
        print("ERRO UPDATE:", e)
        return jsonify({'erro': str(e)}), 500


@app.route('/buscar_paciente')
def buscar_paciente():
    prontuario = request.args.get('prontuario')
    prontuario = prontuario.lstrip('0')

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT prontuario, nome_paciente
        FROM pacientes
        WHERE ltrim(prontuario, '0') = ?
    """, (prontuario,))

    paciente = cursor.fetchone()
    conn.close()

    if paciente:
        return jsonify({
            "prontuario": paciente[0],
            "nome_paciente": paciente[1]
        })

    return jsonify({"erro": "Paciente nao encontrado"}), 404


init_rh_database()


if __name__ == '__main__':
    app.run(debug=True)
