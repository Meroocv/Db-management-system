from app import app, db, Atendimento, ConsultaFutura

with app.app_context():
    from app import Atendimento, ConsultaFutura
    
    # Pega o último atendimento e a última consulta futura gravada
    ultimo_atend = Atendimento.query.order_by(Atendimento.id.desc()).first()
    ultima_con = ConsultaFutura.query.order_by(ConsultaFutura.id.desc()).first()
    
    print("--- DADOS DO ATENDIMENTO ---")
    print(f"ID Atendimento: {ultimo_atend.id}")
    print(f"Servidor ID logado: {ultimo_atend.servidor_id}")
    
    print("\n--- DADOS DA CONSULTA AGENDADA ---")
    print(f"Atendimento Vinculado (ID): {ultima_con.atendimento_id}")
    print(f"Data salva no banco: {ultima_con.data} (Olhe o formato!)")
    print(f"Profissional salvo: {ultima_con.profissional}")