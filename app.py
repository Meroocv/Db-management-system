import os
import re
import calendar
from datetime import datetime, timedelta, date

from flask import Flask, jsonify, redirect, render_template, request, session, send_file, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_mail import Mail, Message  # ADICIONADO
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature  # ADICIONADO
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

# CONFIGURAÇÕES DO SERVIDOR DE E-MAIL (SMTP) - GMAIL REAL (PORTA DE CONTINGÊNCIA)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 25           # 🚨 Porta alternativa para furar bloqueios de rede
app.config['MAIL_USE_TLS'] = True     # Ativa a segurança necessária do Google
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'capsadafraniosoares.adm@gmail.com'
app.config['MAIL_PASSWORD'] = 'mdbvxtfvrfphonsf'  # Sua senha de app que está correta
app.config['MAIL_DEFAULT_SENDER'] = ('Sistema Interno', 'capsadafraniosoares.adm@gmail.com')

db = SQLAlchemy(app)
mail = Mail(app)  # Inicializa o gerenciador de e-mails
ts = URLSafeTimedSerializer(app.secret_key)  # Inicializa o gerador de tokens seguros

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
    tipo = db.Column(db.String(20), nullable=False) 
    nome_familiar = db.Column(db.String(100), nullable=True)
    parentesco_familiar = db.Column(db.String(50), nullable=True)

# NOVA TABELA: Carga e dados oficiais pré-existentes dos Servidores
class BaseServidores(db.Model):
    __tablename__ = 'base_servidores'

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
    nome = db.Column(db.String(100), nullable=False)
    cbo = db.Column(db.String(20), nullable=False)

# MODIFICADO: Tabela de Servidores ativos com coluna "confirmado" integrada
class Servidor(db.Model):
    __tablename__ = 'servidores'

    id = db.Column(db.Integer, primary_key=True)
    cnes = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(100), nullable=False)  
    cbo = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    foto_perfil = db.Column(db.String(255))
    regime = db.Column(db.String(20), default="plantonista") 
    confirmado = db.Column(db.Boolean, default=False, nullable=False)  # NOVO CAMPO
    
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
    tipo = db.Column(db.String(50)) 
    data_inicio = db.Column(db.String(10))
    data_fim = db.Column(db.String(10))
    dias_semana = db.Column(db.String(100)) 


class Escala(db.Model):
    __tablename__ = 'escalas'

    id = db.Column(db.Integer, primary_key=True)
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidores.id'), nullable=False)
    dia = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(5), nullable=False)

class Afastamento(db.Model):
    __tablename__ = 'afastamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # SE O SEU __tablename__ na classe Servidor for 'servidores':
    servidor_id = db.Column(db.Integer, db.ForeignKey('servidores.id'), nullable=False)
    
    # SE O SEU __tablename__ na classe Servidor for 'Servidor' (com S maiúsculo):
    # servidor_id = db.Column(db.Integer, db.ForeignKey('Servidor.id'), nullable=False)

    tipo = db.Column(db.String(50), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Pendente')
    
    servidor = db.relationship('Servidor', backref=db.backref('afastamentos', lazy=True))


with app.app_context():
    db.create_all()


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

CBOS_MEDICOS = {'225125', '225133'}




EXTENSOES_FOTO = {"png", "jpg", "jpeg", "webp"}

def foto_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_FOTO

def servidor_logado():
    if 'usuario_id' not in session:
        return None
    return db.session.get(Servidor, session['usuario_id'])

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

# NOVA FUNÇÃO AUXILIAR: Envio do token por e-mail
# MODIFICADO: Envio do token com logs para o terminal
def enviar_email_confirmacao(usuario_email, usuario_nome):
    print(f"📬 [MAILPIT] Iniciando montagem do e-mail para: {usuario_email}")
    try:
        token = ts.dumps(usuario_email, salt='confirmacao-email-sal')
        link_confirmacao = url_for('confirmar_email', token=token, _external=True)
        
        mensagem = Message("Confirmação de Cadastro - Sistema de Escalas", recipients=[usuario_email])
        mensagem.body = f"Olá, {usuario_nome}!\n\nClique no link para ativar sua conta: {link_confirmacao}"
        
        mensagem.html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 5px;">
            <h2 style="color: #333;">Olá, {usuario_nome}!</h2>
            <p>Sua conta no <strong>Sistema de Escalas</strong> foi pré-cadastrada com sucesso.</p>
            <p>Para ativar seu acesso e utilizar o sistema, clique no botão abaixo:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{link_confirmacao}" style="background-color: #28a745; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Ativar Minha Conta</a>
            </div>
            <p style="font-size: 12px; color: #777;">Este link é válido por 24 horas.</p>
        </div>
        """
        
        print("🔄 [MAILPIT] Disparando comando mail.send(mensagem)...")
        mail.send(mensagem)
        print("🚀 [MAILPIT] comando mail.send executado SEM ERROS pelo Flask!")
        
    except Exception as e:
        print(f"❌ [ERRO INTERNO NO FLASK-MAIL]: Erro exato ao tentar falar com o Mailpit: {e}")
        raise e  # Repassa o erro para a rota capturar na tela

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

    if not user or not senha:
        return render_template('login.html', erro="Preencha todos os campos.")

    # 🔍 Limpa o CPF digitado no login (remove pontos e traços)
    cpf_digitado_limpo = re.sub(r'\D', '', user)

    # 🔍 Busca todos os servidores e compara o CPF de forma limpa
    usuario = None
    todos_servidores = Servidor.query.all()
    for s in todos_servidores:
        if re.sub(r'\D', '', s.cpf) == cpf_digitado_limpo:
            usuario = s
            break

    # Se achou o usuário, valida a senha e o e-mail
    if usuario and check_password_hash(usuario.senha, senha):
        if not usuario.confirmado:
            return render_template('login.html', erro="Sua conta ainda não foi ativada. Verifique seu e-mail para confirmar o cadastro.")

        # Cria a sessão do usuário
        session['usuario_id'] = usuario.id
        session['usuario'] = usuario.nome
        session['usuario_cbo'] = usuario.cbo
        session['usuario_foto'] = usuario.foto_perfil
        
        print(f"🎉 [LOGIN] {usuario.nome} logou com sucesso!")
        return redirect('/dashboard')

    return render_template('login.html', erro="CPF ou senha inválidos.")

@app.route('/dashboard')
def dashboard():
    if 'usuario' not in session:
        return redirect('/')

    solicitacoes_pendentes = []
    if pode_aprovar_rh():
        solicitacoes_pendentes = db.session.query(
            SolicitacaoCBO.id, Servidor.nome, Servidor.cpf,
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
    
    tipo_busca = request.args.get('tipo_busca')
    termo = request.args.get('termo', '').strip()
    
    query = Paciente.query
    
    if termo:
        if tipo_busca == 'nome_paciente':
            query = query.filter(Paciente.nome_paciente.ilike(f"%{termo}%"))
        elif tipo_busca == 'prontuario':
            query = query.filter(Paciente.prontuario.like(f"%{termo}%"))
        elif tipo_busca == 'cpf':
            query = query.filter(Paciente.cpf.like(f"%{termo}%"))
        elif tipo_busca == 'raca_cor':
            query = query.filter(Paciente.raca_cor.ilike(f"%{termo}%"))

    lista_pacientes = query.all()
    
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
        for campo, valor in dados.items():
            if hasattr(novo, campo) and campo not in ['prontuario', 'telefones']:
                setattr(novo, campo, valor)

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
        return jsonify({"erro": f"Erro interno ao salvar no banco: {str(e)}"}), 500
    

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html', cbo_opcoes=CBO_OPCOES)


# =====================================================================
# MODIFICADO: Rota de Verificação para Ajax usando comparação limpa
# =====================================================================
@app.route('/api/verificar_cpf/<cpf>')
def verificar_cpf(cpf):
    # Remove qualquer caractere que não seja número do CPF recebido via URL
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    # Busca todos os servidores na base e compara ignorando pontuações
    servidor_base = None
    todos_base = BaseServidores.query.all()
    for s in todos_base:
        if re.sub(r'\D', '', s.cpf) == cpf_limpo:
            servidor_base = s
            break
            
    if servidor_base:
        return jsonify({
            "existe": True, 
            "nome": servidor_base.nome,
            "cbo": servidor_base.cbo  # ADICIONADO: envia o CBO para preencher a tela automaticamente!
        })
    return jsonify({"existe": False}), 404


# =====================================================================
# MODIFICADO: Rota de Cadastro Final corrigida para aceitar os campos da tela
# =====================================================================
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    cpf_enviado = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    # 🔍 1. Remove pontuações do CPF para busca segura
    cpf_limpo = re.sub(r'\D', '', cpf_enviado) if cpf_enviado else ""

    # 🔍 2. Busca o profissional autorizado na base do RH
    servidor_oficial = None
    todos_base = BaseServidores.query.all()
    for s in todos_base:
        if re.sub(r'\D', '', s.cpf) == cpf_limpo:
            servidor_oficial = s
            break

    if not servidor_oficial:
        return "❌ ERRO: CPF não encontrado na base de dados do RH!"

    # 🔍 3. SALVAMENTO DIRETO (Sem travas de validação para teste)
    senha_hash = generate_password_hash(senha)
    
    novo_servidor = Servidor(
        nome=servidor_oficial.nome, 
        cpf=servidor_oficial.cpf, 
        email=email, 
        senha=senha_hash, 
        cnes="Não Informado", 
        cbo=servidor_oficial.cbo, # Pega o CBO direto do banco do RH
        confirmado=False
    )
    
    try:
        db.session.add(novo_servidor)
        db.session.commit()
        print("✅ [DEBUG] Usuário salvo no banco com sucesso!")
        
        # 🚨 DISPARO DO E-MAIL FORÇADO
        print(f"🔄 [DEBUG] Tentando enviar e-mail para {email}...")
        enviar_email_confirmacao(email, servidor_oficial.nome)
        print("✅ [DEBUG] O Flask-Mail enviou o e-mail com sucesso!")
        
        return "🎉 CADASTRO REALIZADO! Verifique sua caixa de entrada (e a pasta de Spam/Lixo Eletrônico)."
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ [ERRO CRÍTICO NO ENVIO/BANCO]: {e}")
        return f"Falha no processo: {e}"
    
@app.route('/confirmar/<token>')
def confirmar_email(token):
    try:
        # Token expira em 24 horas (86400 segundos)
        email = ts.loads(token, salt='confirmacao-email-sal', max_age=86400)
        print(f"🔍 [Token Válido] E-mail extraído com sucesso: {email}")
    except SignatureExpired:
        print("❌ [Erro Token] O token expirou por tempo (max_age).")
        return render_template('login.html', erro="O link de confirmação expirou (mais de 24h).")
    except BadTimeSignature as e:
        print(f"❌ [Erro Token] Assinatura corrompida ou inválida. Detalhes: {e}")
        return render_template('login.html', erro="Link de ativação inválido ou corrompido.")
    except Exception as e:
        print(f"❌ [Erro Token] Erro genérico ao decodificar: {e}")
        return render_template('login.html', erro="Falha ao processar o link de ativação.")

    servidor = Servidor.query.filter_by(email=email).first()
    if servidor:
        if servidor.confirmado:
            return render_template('login.html', mensagem_sucesso="Esta conta já está ativada. Pode efetuar seu login.")
        
        servidor.confirmado = True
        db.session.commit()
        print(f"✅ [Sucesso] Servidor com e-mail {email} foi confirmado!")
        return render_template('login.html', mensagem_sucesso="E-mail verificado com sucesso! Conta ativa.")
    
    print(f"⚠️ [Aviso] E-mail {email} decodificado mas não encontrado na tabela Servidor.")
    return render_template('login.html', erro="Usuário não encontrado.")

@app.route('/paciente/<prontuario>/ficha_word')
def gerar_ficha_word(prontuario):
    paciente = db.session.query(Paciente).filter_by(prontuario=prontuario).first()
    doc = DocxTemplate("FICHA DE ACOLHIMENTO 5.docx")
    context = { 'p': paciente }
    doc.render(context)
    
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
    
    pode_editar_condicao = case(
        (and_(Atendimento.servidor_id == usuario_id, 
              Atendimento.created_at >= datetime.utcnow() - timedelta(days=10)), 1),
        else_=0
    )

    lista_atendimentos = db.session.query(
        Atendimento.id, Atendimento.prontuario, Paciente.nome_paciente,
        Atendimento.data_atendimento, Atendimento.profissional, Atendimento.procedimentos,
        Atendimento.acolhimento_24h, Atendimento.paciente_aceitou, Atendimento.observacoes,
        Atendimento.servidor_id, pode_editar_condicao.label('pode_editar'), Atendimento.created_at
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

    paciente = Paciente.query.filter(func.ltrim(Paciente.prontuario, '0') == prontuario.lstrip('0')).first()
    if not paciente:
        return jsonify({'erro': 'Paciente nao encontrado'}), 404

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
    db.session.flush() 

    datas_con = dados.get('data_proxima_consulta', [])
    horas_con = dados.get('hora_proxima_consulta', [])
    prof_con = dados.get('profissional_proxima_consulta', [])

    for i in range(len(datas_con)):
        if datas_con[i]: 
            nova_con = ConsultaFutura(
                atendimento_id=novo.id,
                data=datas_con[i],
                hora=horas_con[i] if i < len(horas_con) else '',
                profissional=prof_con[i] if i < len(prof_con) else ''
            )
            db.session.add(nova_con)

    tipos_pac = dados.get('tipo_pactuacao_periodo', [])
    dt_inicio_pac = dados.get('data_inicio_pactuacao', [])
    dt_fim_pac = dados.get('data_fim_pactuacao', [])
    dias_esp = dados.get('dias_semana_acolhimento', [])

    for i in range(len(tipos_pac)):
        if tipos_pac[i]:
            tipo = tipos_pac[i]
            dias = dias_esp[i] if (tipo == 'Acolhimento Diurno' and i < len(dias_esp)) else None
            
            nova_pac = PactuacaoGrupo(
                atendimento_id=novo.id,
                tipo=tipo,
                data_inicio=dt_inicio_pac[i] if i < len(dt_inicio_pac) else '',
                data_fim=dt_fim_pac[i] if i < len(dt_fim_pac) else '',
                dias_semana=dias
            )
            db.session.add(nova_pac)

    db.session.commit() 
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

    atendimento = db.session.get(Atendimento, atendimento_id)
    if not atendimento:
        return jsonify({'erro': 'Atendimento nao encontrado'}), 404

    if atendimento.servidor_id != session.get('usuario_id'):
        return jsonify({'erro': 'Voce so pode editar atendimentos criados por voce'}), 403

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
    return jsonify({'mensagem': 'Atendimento updated!'})


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

    servidor.nome = nome
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
            servidor = db.session.get(Servidor, solicitacao.servidor_id)
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
        for campo, valor in dados.items():
            if hasattr(paciente, campo) and campo not in ['prontuario', 'telefones']:
                setattr(paciente, campo, valor)

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

    agendas = [
        {"data": "2024-07-01", "hora": "10:00", "profissional": "Dr. Silva", "tipo": "Consulta"},
        {"data": "2024-07-02", "hora": "14:00", "profissional": "Dra. Souza", "tipo": "Acolhimento Diurno"},
    ]

    contexto = contexto_usuario()
    contexto['agendas'] = agendas
    return render_template('agendas.html', **contexto)

@app.route('/servidores')
def servidores():
    if 'usuario' not in session:
        return redirect('/')

    agora = datetime.now()
    ano = request.args.get('ano', agora.year, type=int)
    mes = request.args.get('mes', agora.month, type=int)
    
    _, ultimo_dia = calendar.monthrange(ano, mes)
    dias_da_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    lista_dias = []
    for dia in range(1, ultimo_dia + 1):
        dia_semana_num = datetime(ano, mes, dia).weekday()
        lista_dias.append({
            "numero": dia, 
            "nome_semana": dias_da_semana[dia_semana_num],
            "is_util": dia_semana_num < 5
        })
        
    todos_servidores = Servidor.query.filter(Servidor.cbo.in_(CBO_OPCOES.keys())).all()
    
    # 1. BUSCA AFASTAMENTOS QUE REBATEM NO MÊS/ANO VISUALIZADO
    primeiro_dia_mes = date(ano, mes, 1)
    ultimo_dia_mes = date(ano, mes, ultimo_dia)
    
    afastamentos_mes = Afastamento.query.filter(
        Afastamento.data_inicio <= ultimo_dia_mes,
        Afastamento.data_fim >= primeiro_dia_mes,
        Afastamento.status == 'Autorizado'
    ).all()
    
    turnos_salvos = Escala.query.filter_by(mes=mes, ano=ano).all()
    mapa_escala = {(t.servidor_id, t.dia): t.turno for t in turnos_salvos}

    escala_por_cargo = {}
    for s in todos_servidores:
        nome_aba = CBO_OPCOES.get(s.cbo, "outros")
        if nome_aba not in escala_por_cargo:
            escala_por_cargo[nome_aba] = []
            
        # Filtra os afastamentos deste servidor específico neste mês
        afastamentos_servidor = [a for a in afastamentos_mes if a.servidor_id == s.id]
        
        turnos_mes = []
        for d in lista_dias:
            dia_num = d['numero']
            data_corrente = date(ano, mes, dia_num)
            
            # 2. VERIFICA SE O SERVIDOR ESTÁ AFASTADO NESSE DIA
            afastamento_ativo = None
            for afast in \
                    afastamentos_servidor:
                if afast.data_inicio <= data_corrente <= \
                        afast.data_fim:
                    afastamento_ativo = afast
                    break
            
            if afastamento_ativo:
                # Aplica a sigla correspondente do afastamento
                if 'férias' in afastamento_ativo.tipo.lower():
                    turno_dia = 'F'
                elif 'licença' in \
                        afastamento_ativo.tipo.lower():
                    turno_dia = 'LM'
                else:
                    turno_dia = 'F'  # Folga/Afastamento padrão
            else:
                # 3. SE NÃO HOUVER AFASTAMENTO, SEGUE A LOGA NORMAL DE TURNOS
                turno_dia = mapa_escala.get((s.id, dia_num))
                
                if turno_dia is None:
                    if s.cbo in CBOS_MEDICOS:
                        # Fallback dinâmico para os novos regimes de médicos diaristas
                        if d['is_util'] and s.regime in ['m', 't', 'mt', 'i']:
                            turno_dia = s.regime.upper()
                        elif d['is_util'] and (s.regime == 'plantonista' or not s.regime):
                            turno_dia = '-'  # Plantonista começa vazio na semana
                        else:
                            turno_dia = '-'
                    elif d['is_util'] and s.regime in ['diarista_40h', 'diarista_integral', 'mt']:
                        turno_dia = 'MT'
                    elif d['is_util'] and s.regime in ['diarista_manha', 'm']:
                        turno_dia = 'M'
                    elif d['is_util'] and s.regime in ['diarista_tarde', 't']:
                        turno_dia = 'T'
                    elif d['is_util'] and s.regime in ['diarista_intermediario', 'i']:
                        turno_dia = 'I'
                    else:
                        turno_dia = '-'
                        
            turnos_mes.append(turno_dia)

        escala_por_cargo[nome_aba].append({
            "id": s.id,
            "nome": s.nome,  
            "turnos": turnos_mes 
        })
        
    meses_ano = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"), (5, "Maio"), (6, "Junho"),
        (7, "Julho"), (8, "Agosto"), (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]

    contexto = contexto_usuario()
    contexto.update({
        'escala_por_cargo': escala_por_cargo,
        'lista_dias': lista_dias,
        'mes_atual': mes,
        'ano_atual': ano,
        'meses_ano': meses_ano,
        'cargo_usuario': session.get('usuario_cbo'),
        'servidores_lista': todos_servidores  # <-- ADICIONE ESSA LINHA AQUI
    })
    return render_template('servidores.html', **contexto)

@app.context_processor
def injetar_servidores():
    # Substitua pela forma como você busca os servidores no seu banco de dados
    # Exemplo se usar SQLAlchemy: servidores = Servidor.query.all()
    # Exemplo se usar banco normal: servidores = buscar_todos_servidores_do_banco()
    
    servidores = Servidor.query.order_by(Servidor.nome).all() 
    
    # O nome da chave aqui deve ser EXATAMENTE o que está no seu loop do modal
    return dict(servidores_lista=servidores)


@app.route('/configurar-escala', methods=['GET', 'POST'])
def configurar_escala():
    if 'usuario' not in session or session.get('usuario_cbo') != '411010':
        return redirect('/')

    agora = datetime.now()
    mes = request.args.get('mes', agora.month, type=int)
    ano = request.args.get('ano', agora.year, type=int)

    if request.method == 'POST':
        dados = request.form
        mes_salvar = int(dados.get('mes'))
        ano_salvar = int(dados.get('ano'))

        for chave, valor in dados.items():
            if chave.startswith('regime_'):
                servidor_id = int(chave.split('_')[1])
                servidor = db.session.get(Servidor, servidor_id)
                if servidor:  # <-- CORRIGIDO: Agora salva o regime para TODOS, incluindo médicos
                    servidor.regime = valor

        for chave, valor in dados.items():
            if chave.startswith('turno_'):
                partes = chave.split('_')
                servidor_id = int(partes[1])
                dia_num = int(partes[2])

                registro_existente = Escala.query.filter_by(
                    servidor_id=servidor_id, dia=dia_num, mes=mes_salvar, ano=ano_salvar
                ).first()

                if registro_existente:
                    registro_existente.turno = valor
                else:
                    novo_turn = Escala(
                        servidor_id=servidor_id, dia=dia_num, mes=mes_salvar, ano=ano_salvar, turno=valor
                    )
                    db.session.add(novo_turn)

        db.session.commit()
        flash('Escala salva com sucesso!', 'success')
        return redirect(url_for('servidores', mes=mes, ano=ano))

    _, ultimo_dia = calendar.monthrange(ano, mes)
    dias_da_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    
    lista_dias = []
    for dia in range(1, ultimo_dia + 1):
        dia_semana_num = datetime(ano, mes, dia).weekday()
        lista_dias.append({"numero": dia, "nome_semana": dias_da_semana[dia_semana_num], "is_util": dia_semana_num < 5})

    todos_servidores = Servidor.query.filter(Servidor.cbo.in_(CBO_OPCOES.keys())).all()
    turnos_salvos = Escala.query.filter_by(mes=mes, ano=ano).all()

    escala_por_cargo = {}
    for s in todos_servidores:
        nome_aba = CBO_OPCOES.get(s.cbo, "outros")
        if nome_aba not in escala_por_cargo:
            escala_por_cargo[nome_aba] = []
            
        servidor_dados = {
            "id": s.id,
            "nome": s.nome,  
            "cbo": s.cbo,
            "regime": s.regime,
            "turnos_existentes": {t.dia: t.turno for t in turnos_salvos if t.servidor_id == s.id}
        }
        escala_por_cargo[nome_aba].append(servidor_dados)

    meses_ano = [
        (1, "Janeiro"), (2, "Fevereiro"), (3, "Março"), (4, "Abril"), (5, "Maio"), (6, "Junho"),
        (7, "Julho"), (8, "Agosto"), (9, "Setembro"), (10, "Outubro"), (11, "Novembro"), (12, "Dezembro")
    ]

    afastamentos_lista = Afastamento.query.order_by(Afastamento.data_inicio.desc()).all()

    contexto = contexto_usuario()
    contexto.update({
        'escala_por_cargo': escala_por_cargo,
        'lista_dias': lista_dias,
        'mes_config': mes,
        'ano_config': ano,
        'afastamentos_lista': afastamentos_lista,
        'meses_ano': meses_ano
    })
    return render_template('configurar_escala.html', **contexto)


@app.route('/cadastrar-afastamento', methods=['POST'])
def cadastrar_afastamento():
    if 'usuario' not in session or session.get('usuario_cbo') != '411010':
        return redirect('/')

    servidor_id = request.form.get('servidor_id', type=int)
    tipo = request.form.get('tipo')
    data_inicio_str = request.form.get('data_inicio')
    data_fim_str = request.form.get('data_fim')

    if not servidor_id or not tipo or not data_inicio_str or not data_fim_str:
        flash('Todos os campos são obrigatórios!', 'danger')
        return redirect(url_for('servidores'))

    try:
        # Converte as strings de data que vêm do HTML (formato YYYY-MM-DD) para objetos date do Python
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()

        if data_fim < data_inicio:
            flash('A data de fim não pode ser menor que a data de início!', 'danger')
            return redirect(url_for('servidores'))

        # Cria o registro do afastamento
        novo_afastamento = Afastamento(
            servidor_id=servidor_id,
            tipo=tipo,
            data_inicio=data_inicio,
            data_fim=data_fim,
            status='Pendente'
        )
        
        db.session.add(novo_afastamento)
        db.session.commit()
        flash('Afastamento cadastrado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao cadastrar afastamento: {str(e)}', 'danger')

    # Retorna para a mesma página mantendo o mês e ano visualizados
    mes = request.form.get('mes_retorno', datetime.now().month, type=int)
    ano = request.form.get('ano_retorno', datetime.now().year, type=int)
    return redirect(url_for('servidores', mes=mes, ano=ano))

# 1. ROTA PARA AUTORIZAR O AFASTAMENTO
@app.route('/autorizar_afastamento/<int:id>', methods=['POST'])
def autorizar_afastamento(id):
    afastamento = Afastamento.query.get_or_404(id)
    afastamento.status = 'Autorizado'
    
    # [DICA]: Se você quiser que o "F" apareça automaticamente na tabela ao autorizar,
    # você pode varrer os dias entre afastamento.data_inicio e data_fim aqui 
    # e salvar o turno deles como 'F' no banco de dados.
    
    db.session.commit()
    flash('Afastamento autorizado com sucesso!', 'success')
    return redirect(request.referrer) # Volta para a página onde o gestor estava

# 2. ROTA PARA EDITAR OS DIAS DO AFASTAMENTO
@app.route('/editar_afastamento/<int:id>', methods=['POST'])
def editar_afastamento(id):
    afastamento = Afastamento.query.get_or_404(id)
    
    # Coleta as novas datas enviadas pelo modal de edição
    data_inicio_str = request.form.get('data_inicio')
    data_fim_str = request.form.get('data_fim')
    
    # Converte strings do input date para objetos date do Python
    from datetime import datetime
    afastamento.data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    afastamento.data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    
    db.session.commit()
    flash('Período de afastamento atualizado!', 'success')
    return redirect(request.referrer)

# 3. ROTA PARA CANCELAR / DELETAR O AFASTAMENTO
@app.route('/cancelar_afastamento/<int:id>', methods=['POST'])
def cancelar_afastamento(id):
    afastamento = Afastamento.query.get_or_404(id)
    
    db.session.delete(afastamento)
    db.session.commit()
    
    flash('Afastamento cancelado e removido do sistema.', 'warning')
    return redirect(request.referrer)


if __name__ == '__main__':
    app.run(debug=True)