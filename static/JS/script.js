// ==========================================
// MÓDULO: AUXILIARES E COMPORTAMENTO GERAL
// ==========================================

function calcularIdade(data) {
  if (!data) return "";

  const hoje = new Date();
  const nascimento = new Date(data);

  if (Number.isNaN(nascimento.getTime())) return "";

  let idade = hoje.getFullYear() - nascimento.getFullYear();
  const m = hoje.getMonth() - nascimento.getMonth();

  if (m < 0 || (m === 0 && hoje.getDate() < nascimento.getDate())) {
    idade--;
  }

  return idade;
}

// Inicializa o cálculo de idade nas listagens
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll(".idade").forEach(td => {
    const data = td.dataset.nascimento;
    const idade = calcularIdade(data);
    td.innerText = idade ? idade + " anos" : "";
  });
});

function toggleSidebar() {
  document.body.classList.toggle('sidebar-expanded');
}

function setValue(id, value) {
    let el = document.getElementById(id);
    if (el) {
      // Se o valor for null, undefined, ou a string "none"/"null", limpa o campo
      if (value === null || value === undefined || value === "none" || value === "null") {
        el.value = "";
      } else {
        el.value = value;
      }
    }
  }
// ==========================================
// MÓDULO: INTERFACE E GRID DOS MODAIS
// ==========================================

function organizarCamposDosModais() {
  const classesPorCampo = {
    prontuario: 'campo-curto',
    cpf: 'campo-curto',
    rg: 'campo-curto',
    cns_paciente: 'campo-medio',
    data_nascimento: 'campo-curto',
    sexo: 'campo-curto',
    naturalidade: 'campo-medio',
    raca_cor: 'campo-curto',
    escolaridade: 'campo-medio',
    etnia: 'campo-curto',
    orientacao_religiosa: 'campo-medio',
    grau_parentesco_responsavel: 'campo-medio',
    telefone_responsavel: 'campo-curto',
    telefone: 'campo-curto',
    municipio: 'campo-medio',
    uf: 'campo-minimo',
    zona: 'campo-curto',
    cep: 'campo-curto',
    numero: 'campo-minimo',
    statusPaciente: 'campo-curto',
    cid: 'campo-curto',
    data_admissao: 'campo-curto',
    data_conclusao: 'campo-curto',
    
    // Mapeamentos do módulo de atendimento
    prontuario_atendimento: 'campo-curto',
    data_atendimento: 'campo-curto',
    acolhimento_24h: 'campo-curto',
    paciente_aceitou: 'campo-curto',
    pactuado_retorno: 'campo-curto',
    data_retorno: 'campo-curto',
    atendimento_id: 'campo-curto',
    tipo_agendamento: 'campo-medio',
    data_proxima_consulta: 'campo-curto',
    hora_proxima_consulta: 'campo-curto',
    profissional_proxima_consulta: 'campo-medio',
    grupo_procedimentos: 'campo-largo'
  };

  document.querySelectorAll('.form-grid').forEach(grid => {
    if (grid.dataset.camposOrganizados === 'true') return;

    Array.from(grid.querySelectorAll(':scope > label')).forEach(label => {
      const control = label.nextElementSibling;
      if (!control || !control.matches('input, select, textarea, .checkbox-group')) return;

      const wrapper = document.createElement('div');
      const controlId = control.id || '';
      wrapper.className = classesPorCampo[controlId] || (control.tagName === 'TEXTAREA' || control.classList.contains('checkbox-group') ? 'campo-largo' : 'campo-medio');

      grid.insertBefore(wrapper, label);
      wrapper.appendChild(label);
      wrapper.appendChild(control);
    });

    grid.dataset.camposOrganizados = 'true';
  });
}

document.addEventListener('DOMContentLoaded', organizarCamposDosModais);

// ==========================================
// MÓDULO: PACIENTES (MODAL & FLUXOS)
// ==========================================

function abrirPaciente(btn, modo) {
  let dados = {
    prontuario: btn.dataset.prontuario,
    nome_paciente: btn.dataset.nomePaciente,
    nome_social: btn.dataset.nomeSocial,
    cpf: btn.dataset.cpf,
    rg: btn.dataset.rg,
    cns_paciente: btn.dataset.cnsPaciente,
    data_nascimento: btn.dataset.dataNascimento,
    sexo: btn.dataset.sexo,
    naturalidade: btn.dataset.naturalidade,
    raca_cor: btn.dataset.racaCor,
    escolaridade: btn.dataset.escolaridade,
    etnia: btn.dataset.etnia,
    orientacao_religiosa: btn.dataset.orientacaoReligiosa,
    nome_mae: btn.dataset.nomeMae,
    nome_pai: btn.dataset.nomePai,
    nome_responsavel: btn.dataset.nomeResponsavel,
    grau_parentesco_responsavel: btn.dataset.grauParentescoResponsavel,
    telefone_responsavel: btn.dataset.telefoneResponsavel,
    telefone: btn.dataset.telefone,
    municipio: btn.dataset.municipio,
    uf: btn.dataset.uf,
    zona: btn.dataset.zona,
    cep: btn.dataset.cep,
    bairro: btn.dataset.bairro,
    tp_logradouro: btn.dataset.tpLogradouro, 
    logradouro: btn.dataset.logradouro,
    numero: btn.dataset.numero,
    complemento: btn.dataset.complemento,
    statusPaciente: btn.dataset.statusPaciente,
    terapeuta_referencia: btn.dataset.terapeutaReferencia,
    cid: btn.dataset.cid,
    data_admissao: btn.dataset.dataAdmissao,
    data_conclusao: btn.dataset.dataConclusao
  };

  function setValue(id, value) {
    let el = document.getElementById(id);
    if (el) el.value = value || "";
  }

  // Preencher campos estruturados
  Object.keys(dados).forEach(key => setValue(key, dados[key]));

  let elModo = document.getElementById("modo");
  if (elModo) elModo.value = modo;

  document.getElementById('modalPaciente').style.display = 'block';
  abrirAba('identificacao', document.querySelector('#modalPaciente .nav-link'));

  let ehEditavel = (modo !== 'view');
  setModoPaciente(ehEditavel);

  // Renderizar telefones dinâmicos com segurança
  const container = document.getElementById('container-telefones');
  if (container) {
    container.innerHTML = ''; 
    let dadosTelefonesRaw = btn.getAttribute('data-telefones'); 
    
    if (dadosTelefonesRaw) {
      try {
        dadosTelefonesRaw = dadosTelefonesRaw.replace(/\r?\n|\r/g, " ").trim();
        const listaTelefones = JSON.parse(dadosTelefonesRaw);
        
        // Se houver telefones cadastrados, exibe todos eles
        if (Array.isArray(listaTelefones) && listaTelefones.length > 0) {
          listaTelefones.forEach(tel => adicionarTelefone(tel));
        }
        // *Nota: Removemos o else/else if que chamava o adicionarTelefone() sozinho.*
        
      } catch (e) {
        console.error("Erro ao analisar a string JSON de telefones:", e);
      }
    }
  
  }
}

function adicionarTelefone(telData = {}) {
  const container = document.getElementById('container-telefones');
  if (!container) return;

  const div = document.createElement('div');
  div.classList.add('linha-telefone', 'mb-2', 'd-flex', 'gap-2', 'align-items-center');

  // Extrai os valores caso venham preenchidos (modo edição)
  const dddVal = telData.ddd || '';
  const numVal = telData.numero || '';
  const tipoVal = telData.tipo || 'Paciente';

  div.innerHTML = `
    <!-- O name="ddd[]" precisa ser exatamente este -->
    <input type="text" name="ddd[]" class="form-control" style="width: 80px;" placeholder="DDD" value="${dddVal}" maxlength="2">
    
    <!-- O name="numero_telefone[]" precisa ser exatamente este -->
    <input type="text" name="numero_telefone[]" class="form-control" placeholder="Número" value="${numVal}">
    
    <!-- O name="tipo_telefone[]" precisa ser exatamente este -->
    <select name="tipo_telefone[]" class="form-select" style="width: 140px;">
      <option value="Paciente" ${tipoVal === 'Paciente' ? 'selected' : ''}>Paciente</option>
      <option value="Responsável" ${tipoVal === 'Responsável' ? 'selected' : ''}>Responsável</option>
      <option value="Familiar" ${tipoVal === 'Familiar' ? 'selected' : ''}>Familiar</option>
    </select>

    <button type="button" class="btn btn-danger btn-sm" onclick="this.closest('.linha-telefone').remove()">X</button>
  `;

  container.appendChild(div);
}

function abrirNovoPaciente() {
  // Limpa todos os inputs, selects e textareas do modal
  document.querySelectorAll("#modalPaciente input, #modalPaciente select, #modalPaciente textarea")
    .forEach(el => el.value = "");

  // Define o prontuário como automático
  document.getElementById('prontuario').value = 'Automático';

  // Configura o modo para 'novo'
  const elModo = document.getElementById("modo");
  if (elModo) elModo.value = "novo";

  // Prepara o container de telefones: limpa e já adiciona 1 campo obrigatório
  const container = document.getElementById('container-telefones');
  if (container) {
      container.innerHTML = '';
      adicionarTelefone(); // Cria o primeiro campo em branco obrigatoriamente
  }

  // Abre o modal e define a aba inicial
  document.getElementById('modalPaciente').style.display = 'block';
  abrirAba('identificacao', document.querySelector('#modalPaciente .nav-link'));
  
  // Habilita os campos para edição
  setModoPaciente(true);
}

function setModoPaciente(editavel) {
  const inputs = document.querySelectorAll('#modalPaciente input, #modalPaciente select, #modalPaciente textarea');

  inputs.forEach(el => {
    if (el.tagName === 'SELECT') {
      el.disabled = !editavel;
    } else {
      el.readOnly = !editavel;
    }
  });

  const prontuario = document.getElementById('prontuario');
  if (prontuario) prontuario.readOnly = true;

  document.getElementById('btnSalvar').style.display = editavel ? 'inline-block' : 'none';

  let btnAdicionar = document.getElementById('btn-adicionar-telefone');
  if (btnAdicionar) {
    btnAdicionar.style.setProperty('display', editavel ? 'block' : 'none', 'important');
    btnAdicionar.disabled = !editavel;
  }

  document.querySelectorAll('#container-telefones .btn-remover-telefone').forEach(btnRemover => {
    btnRemover.style.setProperty('display', editavel ? 'inline-block' : 'none', 'important');
    btnRemover.disabled = !editavel;
  });
}

function abrirAba(aba, link) {
  document.querySelectorAll('.aba').forEach(div => div.style.display = 'none');

  const abaSelecionada = document.getElementById(aba);
  if (abaSelecionada) {
    abaSelecionada.style.display = abaSelecionada.classList.contains('form-grid') ? 'grid' : 'block';
  }

  document.querySelectorAll('#modalPaciente .nav-link').forEach(nav => {
    nav.classList.remove('active');
    nav.removeAttribute('aria-current');
  });

  if (link) {
    link.classList.add('active');
    link.setAttribute('aria-current', 'page');
  }
}

function fecharModal() {
  document.getElementById('modalPaciente').style.display = 'none';
  document.querySelectorAll('.aba').forEach(div => div.style.display = 'none');
  document.getElementById('identificacao').style.display = 'grid';

  document.querySelectorAll('#modalPaciente .nav-link').forEach(link => {
    link.classList.remove('active');
    link.removeAttribute('aria-current');
  });

  const primeira = document.querySelector('#modalPaciente .nav-link');
  if (primeira) {
    primeira.classList.add('active');
    primeira.setAttribute('aria-current', 'page');
  }
}

function salvarEdicao() {
  let listaTelefones = [];
  
  // 1. Varre cada linha de telefone para extrair os dados
  document.querySelectorAll('#container-telefones .linha-telefone').forEach(linha => {
    const ddd = linha.querySelector('input[name="ddd[]"]')?.value.trim() || '';
    const numero = linha.querySelector('input[name="numero_telefone[]"]')?.value.trim() || '';
    const tipo = linha.querySelector('select[name="tipo_telefone[]"]')?.value || 'Paciente';
    const nome_familiar = linha.querySelector('input[name="nome_familiar[]"]')?.value.trim() || '';
    const parentesco_familiar = linha.querySelector('input[name="parentesco_familiar[]"]')?.value.trim() || '';

    // Só adiciona na lista se o DDD e o número estiverem preenchidos
    if (ddd && numero) {
      listaTelefones.push({ ddd, numero, tipo, nome_familiar, parentesco_familiar });
    }
  });

  // 2. VALIDAÇÃO OBRIGATÓRIA: Impede o salvamento se não houver pelo menos um telefone válido
  if (listaTelefones.length === 0) {
    alert("Atenção: É obrigatório cadastrar pelo menos um telefone de contato para o paciente.");
    return; // Para a execução aqui e não envia o fetch
  }

  // 3. Monta o objeto de dados com todas as informações do formulário
  let dados = {
    prontuario: document.getElementById('prontuario').value,
    terapeuta_referencia: document.getElementById('terapeuta_referencia')?.value || '',
    nome_paciente: document.getElementById('nome_paciente').value,
    nome_social: document.getElementById('nome_social')?.value || '',
    cns_paciente: document.getElementById('cns_paciente')?.value || '',
    rg: document.getElementById('rg')?.value || '',
    cpf: document.getElementById('cpf').value,
    nome_mae: document.getElementById('nome_mae')?.value || '',
    nome_pai: document.getElementById('nome_pai')?.value || '',
    nome_responsavel: document.getElementById('nome_responsavel')?.value || '',
    grau_parentesco_responsavel: document.getElementById('grau_parentesco_responsavel')?.value || '',
    telefone_responsavel: document.getElementById('telefone_responsavel')?.value || '',
    data_nascimento: document.getElementById('data_nascimento').value,
    sexo: document.getElementById('sexo')?.value || '',
    naturalidade: document.getElementById('naturalidade')?.value || '',
    raca_cor: document.getElementById('raca_cor')?.value || '',
    escolaridade: document.getElementById('escolaridade')?.value || '',
    etnia: document.getElementById('etnia')?.value || '',
    orientacao_religiosa: document.getElementById('orientacao_religiosa')?.value || '',
    telefones: listaTelefones, // Vai preenchido com os telefones validados
    municipio: document.getElementById('municipio')?.value || '',
    uf: document.getElementById('uf')?.value || '',
    zona: document.getElementById('zona')?.value || '',
    cep: document.getElementById('cep')?.value || '',
    bairro: document.getElementById('bairro')?.value || '',
    logradouro: document.getElementById('logradouro')?.value || '',
    numero: document.getElementById('numero')?.value || '',
    complemento: document.getElementById('complemento')?.value || '',
    statusPaciente: document.getElementById('statusPaciente')?.value || '',
    cid: document.getElementById('cid')?.value || '',
    data_admissao: document.getElementById('data_admissao')?.value || '',
    data_conclusao: document.getElementById('data_conclusao')?.value || ''
  };

  // 4. Envia via Fetch para o backend Python (Flask)
  fetch('/atualizar_paciente', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dados)
  })
  .then(res => res.json())
  .then(data => {
    alert(data.mensagem);
    fecharModal();
    location.reload();
  })
  .catch(err => {
    console.error('Erro ao salvar:', err);
    alert('Erro ao salvar paciente');
  });
}

// ==========================================
// MÓDULO: PERFIL USUÁRIO
// ==========================================

function abrirModalPerfil() {
  const modal = document.getElementById('modalPerfil');
  if (modal) modal.style.display = 'block';
}

function fecharModalPerfil() {
  const modal = document.getElementById('modalPerfil');
  if (modal) modal.style.display = 'none';
}

// ==========================================
// MÓDULO: ATENDIMENTOS & LINHAS DINÂMICAS
// ==========================================

function abrirAbaAtendimento(nomeAba, link) {
  document.querySelectorAll('.aba-conteudo').forEach(el => el.style.display = 'none');
  document.querySelectorAll('#modalAtendimento .nav-link').forEach(el => el.classList.remove('active'));
  
  const abaAlvo = document.getElementById('tab_' + nomeAba) || document.getElementById(nomeAba);
  if (abaAlvo) abaAlvo.style.display = 'block';
  
  if (link) link.classList.add('active');
}

function toggleCamposAgendamento() {
  const checkbox = document.getElementById('marcar_consulta_futura');
  const secaoAgendamento = document.getElementById('secao_agendamento_futuro');
  
  if (checkbox && checkbox.checked) {
    if (secaoAgendamento) secaoAgendamento.style.display = 'block';
  } else {
    if (secaoAgendamento) secaoAgendamento.style.display = 'none';
    if (document.getElementById('data_proxima_consulta')) document.getElementById('data_proxima_consulta').value = '';
    if (document.getElementById('hora_proxima_consulta')) document.getElementById('hora_proxima_consulta').value = '';
    if (document.getElementById('profissional_proxima_consulta')) document.getElementById('profissional_proxima_consulta').value = '';
  }
}

function toggleSecaoPactuacao(containerId, checkbox) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (checkbox.checked) {
    container.style.display = 'block';
    
    if (containerId === 'container_consultas_lista') {
      const lista = document.getElementById('lista_consultas_futuras');
      if (lista && lista.children.length === 0) adicionarLinhaConsulta();
    }
    if (containerId === 'container_grupos_lista') {
      const lista = document.getElementById('lista_grupos_futuros');
      if (lista && lista.children.length === 0) adicionarLinhaGrupo();
    }
  } else {
    container.style.display = 'none';
    if (containerId === 'container_consultas_lista') {
      document.getElementById('lista_consultas_futuras').innerHTML = '';
    } else {
      document.getElementById('lista_grupos_futuros').innerHTML = '';
    }
  }
}

// Evento blur para busca assíncrona de paciente por prontuário no atendimento
document.addEventListener("DOMContentLoaded", function() {
  const campo = document.getElementById("prontuario_atendimento");

  if (campo) {
    campo.addEventListener("blur", function() {
      let prontuario = this.value.trim();

      if (!prontuario || prontuario === "0") return;

      fetch(`/buscar_paciente?prontuario=${prontuario}`)
        .then(res => res.json())
        .then(data => {
          const campoNome = document.getElementById("nome_paciente_atendimento");
          if (!campoNome) return;

          campoNome.value = data.nome_paciente ? data.nome_paciente : "Paciente não encontrado";
        })
        .catch(() => {
          const campoNome = document.getElementById("nome_paciente_atendimento");
          if (campoNome) campoNome.value = "Erro na busca";
        });
    });
  }
});
  
function marcarProcedimentosAtendimento(procedimentos) {
  const selecionados = (procedimentos || '')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean);

  document.querySelectorAll('input[name="procedimentos_atendimento"]')
    .forEach(input => {
      input.checked = selecionados.includes(input.value);
    });
}

function abrirModalAtendimento(botao = null) {
  document.getElementById('modalAtendimento').style.display = 'block';
  
  if (typeof abrirAbaAtendimento === "function") {
    const primeiraAba = document.querySelector('.nav-tabs .nav-link');
    abrirAbaAtendimento('Atendimento', primeiraAba);
  }

  if (!botao) {
    // Modo: Novo Atendimento
    document.getElementById('tituloModalAtendimento').innerText = "Registrar Atendimento";
    document.getElementById('modo_atendimento').value = "novo";
    document.getElementById('atendimento_id').value = "";
    
    if(document.getElementById('prontuario_atendimento')) document.getElementById('prontuario_atendimento').value = '';
    if(document.getElementById('nome_paciente_atendimento')) document.getElementById('nome_paciente_atendimento').value = '';
    if(document.getElementById('data_atendimento')) document.getElementById('data_atendimento').value = '';
    if(document.getElementById('observacoes_atendimento')) document.getElementById('observacoes_atendimento').value = '';

    document.querySelectorAll('input[name="procedimentos_atendimento"]').forEach(cb => cb.checked = false);

    // Reset dos elementos de pactuação futurista
    const chkConsulta = document.getElementById('marcar_consulta_futura');
    const chkGrupo = document.getElementById('marcar_grupo_futuro');
    if(chkConsulta) chkConsulta.checked = false;
    if(chkGrupo) chkGrupo.checked = false;

    const listaConsultas = document.getElementById('lista_consultas_futuras');
    const listaGrupos = document.getElementById('lista_grupos_futuros');
    const containerConsultas = document.getElementById('container_consultas_lista');
    const containerGrupos = document.getElementById('container_grupos_lista');

    if(listaConsultas) listaConsultas.innerHTML = '';
    if(listaGrupos) listaGrupos.innerHTML = '';
    if(containerConsultas) containerConsultas.style.display = 'none';
    if(containerGrupos) containerGrupos.style.display = 'none';

  } else {
    // Modo: Edição
    document.getElementById('tituloModalAtendimento').innerText = "Editar Atendimento";
    document.getElementById('modo_atendimento').value = "editar";
    document.getElementById('atendimento_id').value = botao.getAttribute('data-id') || '';
    // Adicione os preenchimentos extras do botão aqui se necessário...
  }
}

function fecharModalAtendimento() {
  const modal = document.getElementById('modalAtendimento');
  if (modal) modal.style.display = 'none';
}

function obterProcedimentosMarcados() {
  return Array.from(document.querySelectorAll('input[name="procedimentos_atendimento"]:checked'))
    .map(input => input.value)
    .join(', ');
}

function salvarAtendimento() {
  // 1. Coletar os valores dos campos ocultos e visíveis
  const modo = document.getElementById('modo_atendimento')?.value || 'novo';
  const atendimentoId = document.getElementById('atendimento_id')?.value || '';
  const prontuario = document.getElementById('prontuario_atendimento')?.value.trim();
  const dataAtendimento = document.getElementById('data_atendimento')?.value;

  // 2. Coletar todos os procedimentos selecionados nos checkboxes
  const procedimentosSelecionados = [];
  document.querySelectorAll('input[name="procedimentos_atendimento"]:checked').forEach(checkbox => {
    procedimentosSelecionados.push(checkbox.value);
  });

  // 3. Validações essenciais
  if (!prontuario) {
    alert("Atenção: O campo Prontuário é obrigatório.");
    document.getElementById('prontuario_atendimento').focus();
    return;
  }

  if (!dataAtendimento) {
    alert("Atenção: Selecione a data do atendimento.");
    document.getElementById('data_atendimento').focus();
    return;
  }

  if (procedimentosSelecionados.length === 0) {
    alert("Atenção: Selecione pelo menos um procedimento realizado ou a opção 'Falta'.");
    return;
  }

  // 4. Montar o objeto JSON para enviar ao backend Python (Flask)
  const dadosAtendimento = {
    modo: modo,
    id: atendimentoId,
    prontuario: prontuario,
    data_atendimento: dataAtendimento,
    procedimentos: procedimentosSelecionados
  };

  // 5. Envio via Fetch
  fetch('/novo_atendimento', { // Ajuste a rota se necessário no seu app.py
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dadosAtendimento)
  })
  .then(res => res.json())
  .then(data => {
    alert(data.mensagem || "Atendimento salvo com sucesso!");
    
    // Fecha o modal (certifique-se que o nome da função de fechar confere)
    if (typeof fecharModalAtendimento === 'function') {
      fecharModalAtendimento();
    }
    
    location.reload(); // Atualiza a tela para refletir o registro
  })
  .catch(err => {
    console.error('Erro ao salvar atendimento:', err);
    alert('Erro ao registrar o atendimento no sistema.');
  });
}

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modalCalendario');
    const fecharModal = document.getElementById('fecharModal');
    const inputData = document.getElementById('dataFiltro');
    const listaPacientes = document.getElementById('listaPacientesPopup');
    const tituloMedico = document.getElementById('modalTituloMedico');
    
    let servidorSelecionadoId = null;

    // 1. Monitora o clique nos botões dos cards
    document.querySelectorAll('.btn-abrir-agenda').forEach(botao => {
        botao.addEventListener('click', function() {
            servidorSelecionadoId = this.getAttribute('data-id');
            const nomeMedico = this.getAttribute('data-nome');
            
            tituloMedico.innerText = `Agenda: ${nomeMedico}`;
            listaPacientes.innerHTML = "<p style='color: #94a3b8;'>Selecione um dia no calendário para ver os pacientes...</p>";
            inputData.value = ""; // Limpa a data anterior
            
            modal.style.display = 'flex'; // Exibe o Pop-up/Modal do calendário
        });
    });

    // 2. Fecha o modal
    fecharModal.addEventListener('click', () => modal.style.display = 'none');

    // 3. Quando o usuário escolher/clicar em um dia no calendário
    inputData.addEventListener('change', function() {
        const dataEscolhida = this.value; // Formato YYYY-MM-DD
        
        if(!servidorSelecionadoId || !dataEscolhida) return;

        listaPacientes.innerHTML = "<p>Buscando agendamentos...</p>";

        // Fazemos uma requisição assíncrona (Fetch) para buscar os pacientes reais no banco
        fetch(`/api/agenda/pacientes?servidor_id=${servidorSelecionadoId}&data=${dataEscolhida}`)
            .then(response => response.json())
            .then(pacientes => {
                listaPacientes.innerHTML = ""; // Limpa aviso de carregamento
                
                if(pacientes.length === 0) {
                    listaPacientes.innerHTML = "<p style='color: #64748b;'>Nenhum paciente agendado para este dia.</p>";
                    return;
                }

                // Renderiza a lista de pacientes dentro do pop-up
                pacientes.forEach(p => {
                    const item = document.createElement('div');
                    item.style = "padding: 10px; border-bottom: 1px solid #f1f5f9; display: flex; justify-content: space-between;";
                    item.innerHTML = `
                        <strong>${p.hora}</strong> 
                        <span>${p.paciente_nome} (Prontuário: ${p.prontuario})</span>
                    `;
                    listaPacientes.appendChild(item);
                });
            })
            .catch(err => {
                listaPacientes.innerHTML = "<p style='color: red;'>Erro ao carregar a lista de pacientes.</p>";
            });
    });
});

// Abrir e Fechar Modal de Configuração (Apenas se o botão existir na tela)
const btnConfig = document.getElementById('btnAbrirConfigPainel');
const modalConfig = document.getElementById('modalConfigAgendas');
const fecharModalConfig = document.getElementById('fecharModalConfig');

if (btnConfig) {
    btnConfig.addEventListener('click', () => modalConfig.style.display = 'flex');
    fecharModalConfig.addEventListener('click', () => {
        modalConfig.style.display = 'none';
        window.location.reload(); // Recarrega para aplicar os cards novos na tela principal
    });
}

// Ouvir cliques nos Checkboxes de permissão de agenda
document.querySelectorAll('.chk-possui-agenda').forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        const servidorId = this.getAttribute('data-id');
        const possuiAgenda = this.checked;

        fetch('/api/servidor/configurar-agenda', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ servidor_id: servidorId, possui_agenda: possuiAgenda })
        })
        .then(response => response.json())
        .then(data => {
            if(!data.sucesso) {
                alert("Erro ao salvar configuração.");
                this.checked = !possuiAgenda; // Reverte se der erro
            }
        })
        .catch(() => {
            alert("Erro de conexão.");
            this.checked = !possuiAgenda;
        });
    });
});

function salvarServidorAutorizado() {
    const nome = document.getElementById('nome_novo_servidor').value.trim();
    const cpf = document.getElementById('cpf_novo_servidor').value.trim();
    const cbo = document.getElementById('cbo_novo_servidor').value.trim();

    // Validação simples no front-end
    if (!nome || !cpf || !cbo) {
        alert("Por favor, preencha todos os campos obrigatórios.");
        return;
    }

    const dados = { nome, cpf, cbo };

    // Envio via Fetch para a rota do Flask
    fetch('/cadastrar_servidor_autorizado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(async res => {
        const respostaJson = await res.json();
        if (!res.ok) {
            throw new Error(respostaJson.mensagem || "Erro ao cadastrar servidor.");
        }
        return respostaJson;
    })
    .then(data => {
        alert(data.mensagem);
        
        // Limpa os campos do formulário
        document.getElementById('formNovoServidor').reset();
        
        // Fecha o modal (usando a API nativa do Bootstrap 5)
        const modalElement = document.getElementById('modalNovoServidor');
        const modalInstance = bootstrap.Modal.getInstance(modalElement);
        if (modalInstance) {
            modalInstance.hide();
        }

        // Recarrega a página para o novo servidor aparecer na tabela
        location.reload();
    })
    .catch(err => {
        console.error('Erro:', err);
        alert(err.message);
    });
}

function abrirModalServidor() {
    const modalElement = document.getElementById('modalNovoServidor');
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
}
