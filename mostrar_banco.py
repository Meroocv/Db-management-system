import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pacientes (
    prontuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_paciente TEXT,
    cpf TEXT,
    data_nascimento TEXT
)
""")

conn.commit()
conn.close()