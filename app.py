import os
import re
from datetime import datetime, timedelta

from flask import Flask, jsonify, redirect, render_template, request, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import func, case, and_
from wtforms import StringField, SubmitField
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from docxtpl import DocxTemplate
import io

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.secret_key = 'um_segredo_bem_forte_123456'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads', 'perfis')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# MODELOS ALCHEMY (TABELAS)
# ==========================================

class Paciente(db.Model):
    __tablename__ = 'pacientes'

    id = db.Column(db.Integer, primary_key=True)
    prontuario = db.Column(db.String(20), unique=True, nullable=False)
    nome_paciente = db.Column(db.String(100), nullable=False)
    nome_social = db.Column(db.String(100))
    cpf = db.Column(db.String(14))
    rg = db.Column(db.String(20))
    cns_paciente = db.Column(db.String(20))
    data_nascimento = db.Column(db.String(10))
    sexo = db.Column(db.String(10))
    naturalidade = db.Column(db.String(50))
    raca_cor = db.Column(db.String(50))
    escolaridade = db.Column(db.String(50))
    etnia = db.Column(db.String(50))
    orientacao_religiosa = db.Column(db.String(50))
    nome_mae = db.Column(db.String(100))
    nome_pai = db.Column(db.String(100))
    nome_responsavel = db.Column(db.String(100))
    grau_parentesco_responsavel = db.Column(db.String(50))
    telefone_responsavel = db.Column(db.String(20))
    municipio = db.Column(db.String(50))
    uf = db.Column(db.String(2))
    zona = db.Column(db.String(20))
    cep = db.Column(db.String(10))
    bairro = db.Column(db.String(50))
    logradouro = db.Column(db.String(100))
    numero = db.Column(db.String(10))
    complemento = db.Column(db.String(50))
    statusPaciente = db.Column(db.String(20))
    terapeuta_referencia = db.Column(db.String(100))
    cid = db.Column(db.String(20))
    data_admissao = db.Column(db.String(10))
    data_conclusao = db.Column(db.String(10))
    
    # Campos adicionais identificados nas rotas de atualização
    tipo = db.Column(db.String(50))
    ddd = db.Column(db.String(5))
    telefone = db.Column(db.String(20))
    origem_paciente = db.Column(db.String(100))
    especificacao_origem = db.Column(db.String(100))
    cnes_usf = db.Column(db.String(20))
    
    telefones = db.relationship('TelefonePaciente', backref='paciente', cascade="all, delete-orphan", lazy=True)

    def __repr__(self):
        return f"<Paciente {self.nome_paciente} (Prontuario: {self.prontuario})>"

class TelefonePaciente(db.Model):
    __tablename__ = 'telefones_paciente'
    
    id = db.Column(db.Integer, primary_key=True)
    prontuario_paciente = db.Column(db.String(50), db.ForeignKey('pacientes.prontuario', ondelete='CASCADE'), nullable=False)
    ddd = db.Column(db.String(2), nullable=False)
    numero = db.Column(db.String(15), nullable=False)
    tipo = db.Column(db.String(20), nullable=False) # 'Paciente' ou 'Familiar'
    nome_familiar = db.Column(db.String(100), nullable=True)
    parentesco_familiar = db.Column(db.String(50), nullable=True)

class Servidor(db.Model):
    __tablename__ = 'servidores'

    id = db.Column(db.Integer, primary_key=True)
    cnes = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    cbo = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())


class SolicitacaoCBO(db.Model):
    __tablename__ = 'solicitacoes_cbo'

    id = db.Column(db.Integer, primary_key=True)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidores.id'), nullable=False)
    cbo_atual = db.Column(db.String(20), nullable=False)
    cbo_solicitado = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pendente', nullable=False)
    aprovado_por = db.Column(db.Integer, db.ForeignKey('servidores.id'))
    criado_em = db.Column(db.DateTime, default=func.current_timestamp())
    analisado_em = db.Column(db.DateTime)


class Atendimento(db.Model):
    __tablename__ = 'atendimentos'

    id = db.Column(db.Integer, primary_key=True)
    prontuario = db.Column(db.String(20), nullable=False)
    data_atendimento = db.Column(db.String(10))
    profissional = db.Column(db.String(100))
    procedimentos = db.Column(db.Text)
    acolhimento_24h = db.Column(db.String(20))
    paciente_aceitou = db.Column(db.String(20))
    observacoes = db.Column(db.Text)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidores.id'))
    created_at = db.Column(db.DateTime, default=func.current_timestamp())


class ConsultaFutura(db.Model):
    __tablename__ = 'consultas_futuras'

    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.String(10))
    hora = db.Column(db.String(5))
    profissional = db.Column(db.String(100))

class PactuacaoGrupo(db.Model):
    __tablename__ = 'pactuacoes_grupos'

    id = db.Column(db.Integer, primary_key=True)
    atendimento_id = db.Column(db.Integer, db.ForeignKey('atendimentos.id', ondelete='CASCADE'), nullable=False)
    tipo = db.Column(db.String(50)) # 'Grupo Terapeutico' ou 'Acolhimento Diurno'
    data_inicio = db.Column(db.String(10))
    data_fim = db.Column(db.String(10))
    dias_semana = db.Column(db.String(100)) # Guardará "Seg,Ter" ou None


# 1. Tabela para controlar quais CBOs têm direito a agenda
class ConfigCbo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cbo_codigo = db.Column(db.String(10), unique=True, nullable=False)
    nome_cbo = db.Column(db.String(100), nullable=False)
    agenda_ativa = db.Column(db.Boolean, default=True)

# 2. Tabela para bloquear dias por profissional
class Afastamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profissional = db.Column(db.String(100), nullable=False) # Nome ou ID do profissional
    data_inicio = db.Column(db.String(10), nullable=False)   # Formato YYYY-MM-DD
    data_fim = db.Column(db.String(10), nullable=False)      # Formato YYYY-MM-DD
    motivo = db.Column(db.String(100), nullable=False)       # Férias, Licença Médica, etc.

# ==========================================
# CONFIGURAÇÕES E AUXILIARES
# ==========================================

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

def foto_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_FOTO

def servidor_logado():
    if 'usuario_id' not in session:
        return None
    return Servidor.query.get(session['usuario_id'])

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


# ==========================================
# ROTAS DA APLICAÇÃO
# ==========================================

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/logar', methods=['POST'])
def logar():
    user = request.form.get('cpf')
    senha = request.form.get('senha')

    usuario = Servidor.query.filter_by(cpf=user).first()

    if usuario and check_password_hash(usuario.senha, senha):
        session['usuario_id'] = usuario.id
        session['usuario'] = usuario.name
        session['usuario_cbo'] = usuario.cbo
        session['usuario_foto'] = usuario.foto_perfil
        return redirect('/dashboard')

    return render_template('login.html', erro="CPF ou senha invalidos")


@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')

    solicitacoes_pendentes = []
    if pode_aprovar_rh():
        solicitacoes_pendentes = db.session.query(
            SolicitacaoCBO.id, Servidor.name, Servidor.cpf,
            SolicitacaoCBO.cbo_atual, SolicitacaoCBO.cbo_solicitado, SolicitacaoCBO.criado_em
        ).join(Servidor, Servidor.id == SolicitacaoCBO.servidor_id)\
         .filter(SolicitacaoCBO.status == 'pendente')\
         .order_by(SolicitacaoCBO.criado_em.asc()).all()

    contexto = contexto_usuario()
    contexto['solicitacoes_cbo'] = solicitacoes_pendentes
    return render_template('dashboard.html', **contexto)


@app.route('/pacientes')
def pacientes():
    if 'usuario' not in session:
        return redirect('/')
    
    # 1. Captura os parâmetros do filtro dinâmico enviados pelo formulário HTML
    tipo_busca = request.args.get('tipo_busca')
    termo = request.args.get('termo', '').strip()
    
    # Iniciamos a query base
    query = Paciente.query
    
    # 2. Se houver um termo digitado, aplica o filtro na coluna selecionada
    if termo:
        if tipo_busca == 'nome_paciente':
            # Busca por partes do nome (LIKE), ignorando maiúsculas e minúsculas
            query = query.filter(Paciente.nome_paciente.ilike(f"%{termo}%"))
        elif tipo_busca == 'prontuario':
            # Busca pelo início ou valor exato do prontuário
            query = query.filter(Paciente.prontuario.like(f"%{termo}%"))
        elif tipo_busca == 'cpf':
            # Busca por partes do CPF
            query = query.filter(Paciente.cpf.like(f"%{termo}%"))

        elif tipo_busca == 'raca_cor':
            # Busca por partes da raça/cor
            query = query.filter(Paciente.raca_cor.ilike(f"%{termo}%"))

    if query is None:
        return render_template('pacientes.html', **contexto_usuario(), pacientes=["Nenhum paciente encontrado."])
            
    # Executa a query filtrada ou traz todos (.all()) se o filtro estiver vazio
    lista_pacientes = query.all()
    
    # 3. Monta o contexto padrão do sistema (dados do usuário logado, foto, etc.)
    contexto = contexto_usuario()
    contexto['pacientes'] = lista_pacientes
    
    return render_template('pacientes.html', **contexto)


@app.route('/novo_paciente', methods=['POST'])
def novo_paciente():
    dados = request.get_json(silent=True) 

    if not dados:
        return jsonify({"erro": "Os dados não foram enviados no formato JSON correto."}), 400

    if not dados.get('nome_paciente'):
        return jsonify({"erro": "O Nome do Paciente é um campo obrigatório."}), 400

    try:
        novo = Paciente()
        
        # Preenche os campos vindos do front-end (exceto chaves/relacionamentos)
        for campo, valor in dados.items():
            if hasattr(novo, campo) and campo not in ['prontuario', 'telefones']:
                setattr(novo, campo, valor)

        # Lógica de geração do prontuário
        if not dados.get('prontuario'):
            ultimo_paciente = db.session.query(Paciente.prontuario)\
                .order_by(func.cast(Paciente.prontuario, db.Integer).desc())\
                .first()
            
            if ultimo_paciente and ultimo_paciente[0] and ultimo_paciente[0].isdigit():
                proximo_numero = int(ultimo_paciente[0]) + 1
                novo.prontuario = str(proximo_numero).zfill(6)
            else:
                novo.prontuario = "000001"
        else:
            novo.prontuario = str(dados.get('prontuario')).strip()

        db.session.add(novo)

        # 🌟 SALVA MULTIPLOS TELEFONES
        telefones_recebidos = dados.get('telefones', [])
        for tel in telefones_recebidos:
            novo_tel = TelefonePaciente(
                prontuario_paciente=novo.prontuario,
                ddd=tel.get('ddd'),
                numero=tel.get('numero'),
                tipo=tel.get('tipo'),
                nome_familiar=tel.get('nome_familiar') if tel.get('tipo') == 'Familiar' else None,
                parentesco_familiar=tel.get('parentesco_familiar') if tel.get('tipo') == 'Familiar' else None
            )
            db.session.add(novo_tel)

        db.session.commit()
        
        return jsonify({
            "mensagem": "Paciente e telefones cadastrados com sucesso!",
            "prontuario": novo.prontuario
        })

    except Exception as e:
        db.session.rollback()
        print(f"\n=== ERRO EM NOVO_PACIENTE: {str(e)} ===\n")
        return jsonify({"erro": f"Erro interno ao salvar no banco: {str(e)}"}), 500
    

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
    if not re.search(r'[A-Z]', senha) or not re.search(r'[a-z]', senha) or not re.search(r'[0-9]', senha):
        return render_template('cadastro.html', erro="Senha requer letra maiúscula, minúscula e número", cbo_opcoes=CBO_OPCOES)

    if Servidor.query.filter_by(cpf=cpf).first():
        return render_template('cadastro.html', erro="CPF ja cadastrado", cbo_opcoes=CBO_OPCOES)

    senha_hash = generate_password_hash(senha)
    novo_servidor = Servidor(name=name, cpf=cpf, email=email, senha=senha_hash, cnes=cnes, cbo=cbo)
    
    db.session.add(novo_servidor)
    db.session.commit()
    return redirect('/')

@app.route('/paciente/<prontuario>/ficha_word')
def gerar_ficha_word(prontuario):
    paciente = db.session.query(Paciente).filter_by(prontuario=prontuario).first()
    
    # Abre o seu modelo do Word
    doc = DocxTemplate("FICHA DE ACOLHIMENTO 5.docx")
    
    # Passa os dados do banco para dentro do arquivo
    context = { 'p': paciente }
    doc.render(context)
    
    # Salva o arquivo na memória para enviar para o navegador
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    return send_file(
        file_stream, 
        as_attachment=True, 
        download_name=f"Ficha_{paciente.nome_paciente}.docx"
    )


@app.route('/atendimentos')
def atendimentos():
    if 'usuario' not in session:
        return redirect('/')

    usuario_id = session.get('usuario_id')
    
    # Define a regra condicional (CASE WHEN do SQL) usando SQLAlchemy expressions
    pode_editar_condicao = case(
        (and_(Atendimento.servidor_id == usuario_id, 
              Atendimento.created_at >= datetime.utcnow() - timedelta(days=10)), 1),
        else_=0
    )

    lista_atendimentos = db.session.query(
        Atendimento.id,
        Atendimento.prontuario,
        Paciente.nome_paciente,
        Atendimento.data_atendimento,
        Atendimento.profissional,
        Atendimento.procedimentos,
        Atendimento.acolhimento_24h,
        Atendimento.paciente_aceitou,
        Atendimento.observacoes,
        Atendimento.servidor_id,
        pode_editar_condicao.label('pode_editar'),
        Atendimento.created_at
    ).join(Paciente, Paciente.prontuario == Atendimento.prontuario, isouter=True)\
     .order_by(Atendimento.data_atendimento.desc(), Atendimento.id.desc()).all()

    prontuarios_atendidos = len({atend.prontuario for atend in lista_atendimentos})

    contexto = contexto_usuario()
    contexto['atendimentos'] = lista_atendimentos
    contexto['prontuarios_atendidos'] = prontuarios_atendidos
    return render_template('atendimentos.html', **contexto)


@app.route('/novo_atendimento', methods=['POST'])
def novo_atendimento():
    if 'usuario' not in session:
        return jsonify({'erro': 'Usuario nao autenticado'}), 401

    dados = request.get_json()
    if not dados:
        return jsonify({'erro': 'Dados não enviados corretamente'}), 400

    prontuario = dados.get('prontuario', '').strip()

    if not prontuario:
        return jsonify({'erro': 'Informe o prontuario do paciente'}), 400

    # Busca o paciente ignorando zeros à esquerda
    paciente = Paciente.query.filter(func.ltrim(Paciente.prontuario, '0') == prontuario.lstrip('0')).first()

    if not paciente:
        return jsonify({'erro': 'Paciente nao encontrado'}), 404

    # 1. Salva o Atendimento Principal
    novo = Atendimento(
        prontuario=paciente.prontuario,
        data_atendimento=dados.get('data_atendimento'),
        profissional=session.get('usuario'),
        procedimentos=dados.get('procedimentos'),
        acolhimento_24h=dados.get('acolhimento_24h'),
        paciente_aceitou=dados.get('paciente_aceitou'),
        observacoes=dados.get('observacoes'),
        servidor_id=session.get('usuario_id')
    )
    
    db.session.add(novo)
    db.session.flush() # Gera o ID do 'novo' atendimento para usarmos logo abaixo

    # 2. Salva as Consultas Individuais Futuras (se houverem no JSON)
    datas_con = dados.get('data_proxima_consulta', [])
    horas_con = dados.get('hora_proxima_consulta', [])
    prof_con = dados.get('profissional_proxima_consulta', [])

    for i in range(len(datas_con)):
        if datas_con[i]: # Só salva se a data foi preenchida
            nova_con = ConsultaFutura(
                atendimento_id=novo.id,
                data=datas_con[i],
                hora=horas_con[i] if i < len(horas_con) else '',
                profissional=prof_con[i] if i < len(prof_con) else ''
            )
            db.session.add(nova_con)

    # 3. Salva as Pactuações de Grupos / Acolhimento Diurno
    tipos_pac = dados.get('tipo_pactuacao_periodo', [])
    dt_inicio_pac = dados.get('data_inicio_pactuacao', [])
    dt_fim_pac = dados.get('data_fim_pactuacao', [])
    dias_esp = dados.get('dias_semana_acolhimento', [])

    for i in range(len(tipos_pac)):
        if tipos_pac[i]:
            tipo = tipos_pac[i]
            # Se for Acolhimento Diurno, captura a string de dias (ex: "Ter,Qui")
            dias = dias_esp[i] if (tipo == 'Acolhimento Diurno' and i < len(dias_esp)) else None
            
            nova_pac = PactuacaoGrupo(
                atendimento_id=novo.id,
                tipo=tipo,
                data_inicio=dt_inicio_pac[i] if i < len(dt_inicio_pac) else '',
                data_fim=dt_fim_pac[i] if i < len(dt_fim_pac) else '',
                dias_semana=dias
            )
            db.session.add(nova_pac)

    db.session.commit() # Grava tudo permanentemente de uma vez só
    return jsonify({'mensagem': 'Atendimento e pactuações cadastrados com sucesso!'})


@app.route('/atualizar_atendimento', methods=['POST'])
def atualizar_atendimento():
    if 'usuario' not in session:
        return jsonify({'erro': 'Usuario nao autenticado'}), 401

    dados = request.get_json()
    atendimento_id = dados.get('id')
    prontuario = dados.get('prontuario', '').strip()

    if not atendimento_id or not prontuario:
        return jsonify({'erro': 'Dados incompletos'}), 400

    atendimento = Atendimento.query.get(atendimento_id)
    if not atendimento:
        return jsonify({'erro': 'Atendimento nao encontrado'}), 404

    if atendimento.servidor_id != session.get('usuario_id'):
        return jsonify({'erro': 'Voce so pode editar atendimentos criados por voce'}), 403

    # Verificação de prazo usando objetos datetime reais gerados pelo Alchemy
    if datetime.utcnow() - atendimento.created_at > timedelta(days=10):
        return jsonify({'erro': 'O prazo de 10 dias para editar este atendimento expirou'}), 403

    paciente = Paciente.query.filter(func.ltrim(Paciente.prontuario, '0') == prontuario.lstrip('0')).first()
    if not paciente:
        return jsonify({'erro': 'Paciente nao encontrado'}), 404

    atendimento.prontuario = paciente.prontuario
    atendimento.data_atendimento = dados.get('data_atendimento')
    atendimento.procedimentos = dados.get('procedimentos')
    atendimento.acolhimento_24h = dados.get('acolhimento_24h')
    atendimento.paciente_aceitou = dados.get('paciente_aceitou')
    atendimento.observacoes = dados.get('observacoes')

    db.session.commit()
    return jsonify({'mensagem': 'Atendimento atualizado com sucesso!'})


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

    if foto and foto.filename and foto_permitida(foto.filename):
        extensao = foto.filename.rsplit('.', 1)[1].lower()
        nome_arquivo = secure_filename(f"servidor_{servidor.id}.{extensao}")
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)
        foto.save(caminho)
        servidor.foto_perfil = f"uploads/perfis/{nome_arquivo}"

    servidor.name = nome
    servidor.email = email
    servidor.cnes = cnes

    if cbo_solicitado and cbo_solicitado != servidor.cbo:
        pendente = SolicitacaoCBO.query.filter_by(servidor_id=servidor.id, status='pendente').first()
        if pendente:
            pendente.cbo_atual = servidor.cbo
            pendente.cbo_solicitado = cbo_solicitado
            pendente.criado_em = func.current_timestamp()
        else:
            nova_solicitacao = SolicitacaoCBO(
                servidor_id=servidor.id,
                cbo_atual=servidor.cbo,
                cbo_solicitado=cbo_solicitado
            )
            db.session.add(nova_solicitacao)

    db.session.commit()

    session['usuario'] = nome
    session['usuario_foto'] = servidor.foto_perfil
    return redirect('/dashboard')


@app.route('/aprovar_cbo/<int:solicitacao_id>', methods=['POST'])
def aprovar_cbo(solicitacao_id):
    if 'usuario_id' not in session or not pode_aprovar_rh():
        return redirect('/dashboard')

    acao = request.form.get('acao')
    solicitacao = SolicitacaoCBO.query.filter_by(id=solicitacao_id, status='pendente').first()

    if solicitacao:
        if acao == 'aprovar':
            servidor = Servidor.query.get(solicitacao.servidor_id)
            if servidor:
                servidor.cbo = solicitacao.cbo_solicitado
            solicitacao.status = 'aprovada'
        else:
            solicitacao.status = 'rejeitada'

        solicitacao.aprovado_por = session['usuario_id']
        solicitacao.analisado_em = func.current_timestamp()
        db.session.commit()

    return redirect('/dashboard')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/atualizar_paciente', methods=['POST'])
def atualizar_paciente():
    dados = request.get_json()
    prontuario = dados.get('prontuario')

    paciente = Paciente.query.filter_by(prontuario=prontuario).first()
    if not paciente:
        return jsonify({'erro': 'Paciente nao encontrado'}), 404

    try:
        # Atualiza dados nativos do paciente
        for campo, valor in dados.items():
            if hasattr(paciente, campo) and campo not in ['prontuario', 'telefones']:
                setattr(paciente, campo, valor)

        # 🌟 ATUALIZAÇÃO DOS TELEFONES (Delete antigo e insere novo fluxo)
        TelefonePaciente.query.filter_by(prontuario_paciente=prontuario).delete()

        telefones_recebidos = dados.get('telefones', [])
        for tel in telefones_recebidos:
            novo_tel = TelefonePaciente(
                prontuario_paciente=prontuario,
                ddd=tel.get('ddd'),
                numero=tel.get('numero'),
                tipo=tel.get('tipo'),
                nome_familiar=tel.get('nome_familiar') if tel.get('tipo') == 'Familiar' else None,
                parentesco_familiar=tel.get('parentesco_familiar') if tel.get('tipo') == 'Familiar' else None
            )
            db.session.add(novo_tel)

        db.session.commit()
        return jsonify({'mensagem': 'Paciente e lista de telefones atualizados com sucesso!'})

    except Exception as e:
        db.session.rollback()
        print(f"\n=== ERRO EM ATUALIZAR_PACIENTE: {str(e)} ===\n")
        return jsonify({"erro": f"Erro ao atualizar: {str(e)}"}), 500
    
@app.route('/buscar_paciente')
def buscar_paciente():
    prontuario = request.args.get('prontuario', '').strip()
    
    paciente = Paciente.query.filter(func.ltrim(Paciente.prontuario, '0') == prontuario.lstrip('0')).first()

    if paciente:
        return jsonify({
            "prontuario": paciente.prontuario,
            "nome_paciente": paciente.nome_paciente
        })

    return jsonify({"erro": "Paciente nao encontrado"}), 404

@app.route('/agendas')
def agendas():
    if 'usuario' not in session:
        return redirect('/')

    # Exemplo de dados de agenda (substitua com consulta real ao banco)
    agendas = [
        {"data": "2024-07-01", "hora": "10:00", "profissional": "Dr. Silva", "tipo": "Consulta"},
        {"data": "2024-07-02", "hora": "14:00", "profissional": "Dra. Souza", "tipo": "Acolhimento Diurno"},
    ]

    contexto = contexto_usuario()
    contexto['agendas'] = agendas
    return render_template('agendas.html', **contexto)

@app.route('/configurar_agenda')
def tela_configurar_agenda():
    if 'usuario' not in session:
        return redirect('/')
        
    # Puxa os CBOs que já estão ativos no banco
    cbos_ativos_db = ConfigCbo.query.filter_by(agenda_ativa=True).all()
    cbos_configurados_ativos = [c.cbo_codigo for c in cbos_ativos_db]
    
    # Puxa todos os afastamentos agendados
    afastamentos = Afastamento.query.all()

    contexto = contexto_usuario() # Mantém seu contexto da Opção A
    return render_template(
        'configurar_agenda.html', 
        afastamentos=afastamentos, 
        cbos_configurados_ativos=cbos_configurados_ativos,
        **contexto
    )

@app.route('/salvar_config_cbo', methods=['POST'])
def salvar_config_cbo():
    # Pega a lista de CBOs marcados no formulário
    cbos_marcados = request.form.getlist('cbos_ativos')
    
    # Reseta todos para inativos primeiro
    ConfigCbo.query.update({ConfigCbo.agenda_ativa: False})
    
    # Atualiza ou insere os marcados como ativos
    for cbo_cod in cbos_marcados:
        cbo_nome = CBO_OPCOES.get(cbo_cod, "Especialidade")
        config = ConfigCbo.query.filter_by(cbo_codigo=cbo_cod).first()
        if config:
            config.agenda_ativa = True
        else:
            nova_config = ConfigCbo(cbo_codigo=cbo_cod, nome_cbo=cbo_nome, agenda_ativa=True)
            db.session.add(nova_config)
            
    db.session.commit()
    return redirect('/configurar_agenda')

@app.route('/salvar_afastamento', methods=['POST'])
def salvar_afastamento():
    novo_afas = Afastamento(
        profissional=request.form.get('profissional'),
        data_inicio=request.form.get('data_inicio'),
        data_fim=request.form.get('data_fim'),
        motivo=request.form.get('motivo')
    )
    db.session.add(novo_afas)
    db.session.commit()
    return redirect('/configurar_agenda')

@app.route('/deletar_afastamento/<int:id>')
def deletar_afastamento(id):
    afas = Afastamento.query.get(id)
    if afas:
        db.session.delete(afas)
        db.session.commit()
    return redirect('/configurar_agenda')

# ==========================================
# INICIALIZAÇÃO DA BASE DE DADOS
# ==========================================

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)