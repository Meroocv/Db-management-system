import pandas as pd
from app import app, db, BaseServidores  # Importa o Flask, o DB e o Modelo do seu app.py

def importar_planilha(caminho_arquivo):
    # 1. Ler a planilha (mude para pd.read_csv se for um arquivo CSV)
    print("🔄 Lendo a planilha...")
    if caminho_arquivo.endswith('.csv'):
        df = pd.read_csv(caminho_arquivo, dtype={"cpf": str, "cbo": str})
    else:
        df = pd.read_excel(caminho_arquivo, dtype={"cpf": str, "cbo": str})

    # Garantir que o CPF e CBO mantenham os zeros à esquerda, se houver
    df['cpf'] = df['cpf'].str.strip()
    df['nome'] = df['nome'].str.strip()
    df['cbo'] = df['cbo'].str.strip()

    print(f"📊 Encontrados {len(df)} profissionais para importar.")

    # 2. Abrir o contexto do Flask para interagir com o SQLite
    with app.app_context():
        adicionados = 0
        ignorados = 0

        for _, linha in df.iterrows():
            # Verificar se o CPF já está cadastrado para evitar duplicados
            existe = BaseServidores.query.filter_by(cpf=linha['cpf']).first()
            
            if not existe:
                novo_servidor = BaseServidores(
                    cpf=linha['cpf'],
                    nome=linha['nome'],
                    cbo=linha['cbo']
                )
                db.session.add(novo_servidor)
                adicionados += 1
            else:
                ignorados += 1

        # 3. Salvar as alterações no banco de dados
        if adicionados > 0:
            db.session.commit()
            print(f"✅ Sucesso! {adicionados} novos profissionais cadastrados.")
        else:
            print("⚠️ Nenhum novo registro inserido.")
        
        if ignorados > 0:
            print(f"ℹ️ {ignorados} registros ignorados porque o CPF já existia na base.")

if __name__ == "__main__":
    # Altere aqui para o nome correto do seu arquivo se for diferente
    ARQUIVO = "profissionais.xlsx" 
    
    try:
        importar_planilha(ARQUIVO)
    except Exception as e:
        print(f"❌ Ocorreu um erro durante a importação: {e}")