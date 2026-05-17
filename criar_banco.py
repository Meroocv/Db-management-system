import sqlite3

# Cria (ou conecta) ao banco
conn = sqlite3.connect('database.db')

# Cria o cursor
cursor = conn.cursor()

# Cria a tabela de usuários
cursor.execute("""
CREATE TABLE IF NOT EXISTS Pacientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cpf TEXT NOT NULL,
    nascimento DATE NOT NULL,
    telefone NUMBER NOT NULL,
    admissao DATE NOT NULL
)
""")

# Salva e fecha
conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")