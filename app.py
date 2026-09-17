import os
import re
from datetime import datetime, timedelta, date

from flask import Flask, jsonify, redirect, render_template, request, session, send_file, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_mail import Mail, Message  # ADICIONADO
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature  # ADICIONADO
from sqlalchemy import func, case, and_, inspect
from wtforms import StringField, SubmitField
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from docxtpl import DocxTemplate
import io
import sqlite3

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
    __tablename__ = 'servidores_autorizados'

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
    confirmado = db.Column(db.Boolean, default=False, nullable=False)  # NOVO CAMPO
    created_at = db.Column(db.DateTime, default=func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())



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





with app.app_context():
    db.create_all()


# ==========================================
# CONFIGURAÇÕES E AUXILIARES
# ==========================================







EXTENSOES_FOTO = {"png", "jpg", "jpeg", "webp"}

def foto_permitida(nome_arquivo):
    return '.' in nome_arquivo and nome_arquivo.rsplit('.', 1)[1].lower() in EXTENSOES_FOTO

def servidor_logado():
    if 'usuario_id' not in session:
        return None
    return db.session.get(Servidor, session['usuario_id'])


@app.context_processor
def contexto_usuario():
    # Tenta buscar o objeto completo do servidor logado (se houver ID na sessão)
    servidor_id = session.get('usuario_id')
    servidor = Servidor.query.get(servidor_id) if servidor_id else None
    
    return {
        'usuario': session.get('usuario'),
        'usuario_foto': session.get('usuario_foto'),
        'servidor': servidor,
        'usuario_cbo': session.get('usuario_cbo'),
    }

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


    contexto = contexto_usuario()
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

@app.route('/gerenciar_servidores')
def gerenciar_servidores():
    # Consulta todos os servidores usando o SQLAlchemy
    servidores = BaseServidores.query.all()
    return render_template('servidores.html', servidores=servidores)

@app.route('/cadastrar_servidor_autorizado', methods=['POST'])
def cadastrar_servidor_autorizado():
    try:
        dados = request.get_json()
        cpf = dados.get('cpf', '').strip()
        nome = dados.get('nome', '').strip()
        cbo = dados.get('cbo', '').strip()

        if not cpf or not nome:
            return jsonify({'mensagem': 'CPF e Nome são obrigatórios.'}), 400

        # Verifica se o CPF já existe
        existente = BaseServidores.query.filter_by(cpf=cpf).first()
        if existente:
            return jsonify({'mensagem': 'Este CPF já possui um pré-cadastro no sistema.'}), 400

        # Cria o novo objeto usando o modelo
        novo_servidor = BaseServidores(cpf=cpf, nome=nome, cbo=cbo)
        db.session.add(novo_servidor)
        db.session.commit()

        return jsonify({
            'sucesso': True, 
            'mensagem': 'Servidor pré-cadastrado com sucesso!'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao pré-cadastrar servidor: {str(e)}")
        return jsonify({
            'sucesso': False, 
            'mensagem': f'Erro interno ao salvar: {str(e)}'
        }), 500

@app.route('/excluir_servidor/<int:id>', methods=['POST'])
def excluir_servidor(id):
    try:
        servidor = BaseServidores.query.get_or_404(id)
        db.session.delete(servidor)
        db.session.commit()
        
        return jsonify({'sucesso': True, 'mensagem': 'Servidor removido com sucesso!'})
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir servidor: {str(e)}")
        return jsonify({'sucesso': False, 'mensagem': f'Erro ao excluir: {str(e)}'}), 500

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
    return render_template('cadastro.html')


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

    # MODIFICAÇÃO: Adicionado .label('data') em Atendimento.data_atendimento para casar com o seu HTML
    lista_atendimentos = db.session.query(
        Atendimento.id, Atendimento.prontuario, Paciente.nome_paciente,
        Atendimento.data_atendimento.label('data'), Atendimento.profissional, Atendimento.procedimentos,
        Atendimento.acolhimento_24h, Atendimento.paciente_aceitou, Atendimento.observacoes,
        Atendimento.servidor_id, pode_editar_condicao.label('pode_editar'), Atendimento.created_at
    ).join(Paciente, Paciente.prontuario == Atendimento.prontuario, isouter=True)\
     .order_by(Atendimento.data_atendimento.desc(), Atendimento.id.desc()).all()

    prontuarios_atendidos = len({atend.prontuario for atend in lista_atendimentos})
    

    contexto = contexto_usuario()
    contexto['atendimentos'] = lista_atendimentos
    contexto['prontuarios_atendidos'] = prontuarios_atendidos
    
    return render_template('atendimentos.html', **contexto) # (Garanta que o nome do arquivo seja exatamente o seu, atendimentos.html ou atendimento.html)


@app.route('/novo_atendimento', methods=['POST'])
def novo_atendimento():
    try:
        # Pega os dados JSON enviados pelo Fetch do JavaScript
        dados = request.get_json()
        
        if not dados:
            return jsonify({'mensagem': 'Nenhum dado foi enviado.'}), 400

        # Extraindo os campos principais
        prontuario = dados.get('prontuario')
        data_atendimento = dados.get('data_atendimento')
        procedimentos = dados.get('procedimentos', []) # Vem como uma lista de strings

        # Validações básicas no backend
        if not prontuario or not data_atendimento:
            return jsonify({'mensagem': 'Prontuário e Data do Atendimento são obrigatórios.'}), 400
            
        if not procedimentos or len(procedimentos) == 0:
            return jsonify({'mensagem': 'Selecione pelo menos um procedimento.'}), 400

        # Transforma a lista de procedimentos em uma string separada por vírgula para salvar no banco
        procedimentos_str = ", ".join(procedimentos)

        # -------------------------------------------------------------
        # SALVANDO DE FATO NO BANCO DE DADOS (SQLite)
        # -------------------------------------------------------------
        conexao = sqlite3.connect('seu_banco.db') # Substitua pelo nome do seu arquivo de banco de dados
        cursor = conexao.cursor()
        
        cursor.execute("""
            INSERT INTO atendimentos (prontuario, data_atendimento, procedimentos) 
            VALUES (?, ?, ?)
        """, (prontuario, data_atendimento, procedimentos_str))
        
        conexao.commit()
        conexao.close()
        # -------------------------------------------------------------

        return jsonify({
            'sucesso': True, 
            'mensagem': 'Atendimento registrado com sucesso!'
        }), 200

    except Exception as e:
        print(f"Erro ao registrar atendimento: {str(e)}")
        return jsonify({
            'sucesso': False, 
            'mensagem': f'Erro interno ao salvar: {str(e)}'
        }), 500
    
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


    db.session.commit()

    session['usuario'] = nome
    session['usuario_foto'] = servidor.foto_perfil
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




if __name__ == '__main__':
    app.run(debug=True)
