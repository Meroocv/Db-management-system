import sqlite3

# Cria (ou conecta) ao banco
conn = sqlite3.connect('database.db')

# Cria o cursor
cursor = conn.cursor()

# Cria a tabela de pacientes com os campos usados pelo app
cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes (
    prontuario INTEGER PRIMARY KEY AUTOINCREMENT,
    terapeuta_referencia TEXT,
    nome_paciente TEXT NOT NULL,
    nome_social TEXT,
    cns_paciente TEXT,
    rg TEXT,
    cpf TEXT,
    naturalidade TEXT,
    sexo TEXT,
    data_nascimento TEXT,
    raca_cor TEXT,
    etnia TEXT,
    orientacao_religiosa TEXT,
    escolaridade TEXT,
    nome_mae TEXT,
    nome_pai TEXT,
    nome_responsavel TEXT,
    grau_parentesco_responsavel TEXT,
    telefone_responsavel TEXT,
    municipio TEXT,
    uf TEXT,
    zona TEXT,
    cep TEXT,
    bairro TEXT,
    tipo TEXT,
    logradouro TEXT,
    numero TEXT,
    complemento TEXT,
    telefone TEXT,
    ddd TEXT,
    data_admissao TEXT,
    origem_paciente TEXT,
    especificacao_origem TEXT,
    cnes_usf TEXT,
    cid TEXT,
    statusPaciente TEXT,
    data_conclusao TEXT,
    status TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS atendimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prontuario INTEGER NOT NULL,
    data_atendimento TEXT NOT NULL,
    profissional TEXT NOT NULL,
    servidor_id INTEGER,
    procedimentos TEXT NOT NULL,
    acolhimento_24h TEXT,
    paciente_aceitou TEXT,
    observacoes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prontuario) REFERENCES pacientes (prontuario)
);
""")

# Salva e fecha
conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")
