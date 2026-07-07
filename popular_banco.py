import random
from faker import Faker
from datetime import datetime

# AJUSTE AQUI: Importe o seu app, o db e a classe Paciente do seu arquivo principal
# Se o seu arquivo principal se chama 'main.py', mude para: from main import app, db, Paciente
from app import app, db, Paciente 

def gerar_pacientes_teste(quantidade=20):
    fake = Faker('pt_BR')
    
    print(f"Instanciando contexto do banco de dados para gerar {quantidade} registros...")
    
    # Listas de opções para preencher os campos do SUS/Prontuário
    sexos = ['Masculino', 'Feminino', 'Outro']
    racas = ['Branca', 'Preta', 'Parda', 'Amarela', 'Indígena']
    escolaridades = ['Fundamental Incompleto', 'Fundamental Completo', 'Médio Completo', 'Superior Completo']
    zonas = ['Urbana', 'Rural']
    status = ['Ativo', 'Inativo', 'Afastado']
    cids = ['F32.9', 'F41.1', 'F90.0', 'F20.0', 'F10.2']

    # Ativamos o contexto do Flask para que o SQLAlchemy possa acessar o arquivo .db
    with app.app_context():
        for i in range(quantidade):
            # Gera um número de prontuário aleatório único com 6 dígitos
            prontuario_gerado = str(random.randint(100000, 999999))
            
            # Evita tentar inserir o mesmo prontuário se rodar o script mais de uma vez
            if Paciente.query.filter_by(prontuario=prontuario_gerado).first():
                continue

            data_nasc = fake.date_of_birth(minimum_age=5, maximum_age=85).strftime('%d/%m/%Y')
            data_adm = fake.date_between(start_date='-1y', end_date='today').strftime('%d/%m/%Y')

            novo_paciente = Paciente(
                prontuario=prontuario_gerado,
                nome_paciente=fake.name(),
                nome_social=random.choice([fake.name(), "", None]),
                cpf=fake.cpf(),
                rg=f"{random.randint(1000000, 9999999)}-{random.randint(0,9)}",
                cns_paciente=str(random.randint(100000000000000, 999999999999999)), # 15 dígitos do SUS
                data_nascimento=data_nasc,
                sexo=random.choice(sexos),
                naturalidade=fake.city(),
                raca_cor=random.choice(racas),
                escolaridade=random.choice(escolaridades),
                etnia="Não se aplica",
                orientacao_religiosa=random.choice(["Católica", "Evangélica", "Espírita", "Nenhuma"]),
                nome_mae=fake.name_female(),
                nome_pai=fake.name_male(),
                nome_responsavel=fake.name(),
                grau_parentesco_responsavel=random.choice(["Mãe", "Pai", "Irmão(ã)", "Outro"]),
                telefone_responsavel=fake.cellphone_number(),
                municipio=fake.city(),
                uf=fake.state_abbr(),
                zona=random.choice(zonas),
                cep=fake.postcode(),
                bairro="Centro",
                logradouro=fake.street_name(),
                numero=str(random.randint(1, 999)),
                complemento=random.choice(["Casa", "Apto", ""]),
                statusPaciente=random.choice(status),
                terapeuta_referencia=random.choice(["Dr. Silva", "Dra. Souza", ""]),
                cid=random.choice(cids),
                data_admissao=data_adm,
                data_conclusao="",
                
                tipo="Geral",
                # CORREÇÃO AQUI: Sorteia um DDD válido direto de uma lista comum
                ddd=random.choice(["011", "021", "031", "041", "061", "071", "081", "092"]),
                telefone=fake.cellphone_number().replace(" ", "").replace("-", ""),
                origem_paciente="Demanda Espontânea",
                especificacao_origem="Caps",
                cnes_usf=str(random.randint(1000000, 9999999))
            )
            
            db.session.add(novo_paciente)
            
        try:
            db.session.commit()
            print(f"🚀 Sucesso! {quantidade} pacientes adicionados para testes.")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro ao salvar no banco de dados: {e}")

if __name__ == '__main__':
    # Escolha a quantidade de pacientes fictícios que deseja criar aqui:
    gerar_pacientes_teste(quantidade=35)