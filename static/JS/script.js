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
        
        if (Array.isArray(listaTelefones) && listaTelefones.length > 0) {
          listaTelefones.forEach(tel => adicionarTelefone(tel));
        } else if (['edit', 'novo', 'new'].includes(modo)) {
          adicionarTelefone(); 
        }
      } catch (e) {
        console.error("Erro ao analisar a string JSON de telefones:", e);
        if (['edit', 'novo', 'new'].includes(modo)) adicionarTelefone();
      }
    } else if (['edit', 'novo', 'new'].includes(modo)) {
      adicionarTelefone();
    }
  }
}

function abrirNovoPaciente() {
  document.querySelectorAll("#modalPaciente input, #modalPaciente select, #modalPaciente textarea")
    .forEach(el => el.value = "");

  document.getElementById('prontuario').value = 'Automático';

  const elModo = document.getElementById("modo");
  if (elModo) elModo.value = "novo";

  const container = document.getElementById('container-telefones');
  if (container) {
      container.innerHTML = '';
      adicionarTelefone(); 
  }

  document.getElementById('modalPaciente').style.display = 'block';
  abrirAba('identificacao', document.querySelector('#modalPaciente .nav-link'));
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
  document.querySelectorAll('#container-telefones .linha-telefone').forEach(linha => {
    const ddd = linha.querySelector('input[name="ddd[]"]')?.value || '';
    const numero = linha.querySelector('input[name="numero_telefone[]"]')?.value || '';
    const tipo = linha.querySelector('select[name="tipo_telefone[]"]')?.value || 'Paciente';
    const nome_familiar = linha.querySelector('input[name="nome_familiar[]"]')?.value || '';
    const parentesco_familiar = linha.querySelector('input[name="parentesco_familiar[]"]')?.value || '';

    if (ddd && numero) {
      listaTelefones.push({ ddd, numero, tipo, nome_familiar, parentesco_familiar });
    }
  });

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
    telefones: listaTelefones,
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

function adicionarLinhaConsulta() {
  const container = document.getElementById('lista_consultas_futuras');
  if (!container) return;

  const novaLinha = document.createElement('div');
  novaLinha.className = 'row g-2 mb-2 align-items-center linha-dinamica';
  
  novaLinha.innerHTML = `
    <div class="col-md-3"><input type="date" name="data_proxima_consulta[]" required class="form-control form-control-sm"></div>
    <div class="col-md-2"><input type="time" name="hora_proxima_consulta[]" required class="form-control form-control-sm"></div>
    <div class="col-md-5">
      <select name="profissional_proxima_consulta[]" required class="form-select form-control-sm">
        <option value="">Selecione...</option>
        <option value="Profissional Atual">Mesmo profissional atual</option>
      </select>
    </div>
    <div class="col-md-2">
      <button type="button" class="btn btn-sm btn-outline-danger w-100" onclick="removerLinhaDinamica(this)">Remover</button>
    </div>
  `;
  container.appendChild(novaLinha);
}

function adicionarLinhaGrupo() {
  const container = document.getElementById('lista_grupos_futuros');
  if (!container) return;

  const novaLinha = document.createElement('div');
  novaLinha.className = 'linha-dinamica mb-3 p-2 border rounded bg-light'; 
  
  novaLinha.innerHTML = `
    <div class="row g-2 align-items-center">
      <div class="col-md-3">
        <select name="tipo_pactuacao_periodo[]" required class="form-select form-control-sm" onchange="atualizarInterfaceGrupo(this)">
          <option value="Grupo Terapeutico">Grupo Terapêutico</option>
          <option value="Acolhimento Diurno">Acolhimento Diurno</option>
        </select>
      </div>
      <div class="col-md-3"><input type="date" name="data_inicio_pactuacao[]" required class="form-control form-control-sm"></div>
      <div class="col-md-3"><input type="date" name="data_fim_pactuacao[]" required class="form-control form-control-sm"></div>
      <div class="col-md-3">
        <button type="button" class="btn btn-sm btn-outline-danger w-100" onclick="removerLinhaDinamica(this)">Remover</button>
      </div>
    </div>
    
    <input type="hidden" name="dias_semana_acolhimento[]" class="input-dias-string" value="">

    <div class="secao-dias border-top mt-2 pt-2" style="display: none;">
      <small class="text-muted d-block mb-1">Dias específicos da semana (Se nenhum for marcado, assume-se todos os dias):</small>
      <div class="d-flex flex-wrap gap-3">
        <label class="d-flex align-items-center gap-1" style="font-size: 13px; cursor:pointer; font-weight: normal;">
          <input type="checkbox" value="Seg" onchange="atualizarDiasString(this)" style="width:15px; height:15px; margin:0;"> Seg
        </label>
        <label class="d-flex align-items-center gap-1" style="font-size: 13px; cursor:pointer; font-weight: normal;">
          <input type="checkbox" value="Ter" onchange="atualizarDiasString(this)" style="width:15px; height:15px; margin:0;"> Ter
        </label>
        <label class="d-flex align-items-center gap-1" style="font-size: 13px; cursor:pointer; font-weight: normal;">
          <input type="checkbox" value="Qua" onchange="atualizarDiasString(this)" style="width:15px; height:15px; margin:0;"> Qua
        </label>
        <label class="d-flex align-items-center gap-1" style="font-size: 13px; cursor:pointer; font-weight: normal;">
          <input type="checkbox" value="Qui" onchange="atualizarDiasString(this)" style="width:15px; height:15px; margin:0;"> Qui
        </label>
        <label class="d-flex align-items-center gap-1" style="font-size: 13px; cursor:pointer; font-weight: normal;">
          <input type="checkbox" value="Sex" onchange="atualizarDiasString(this)" style="width:15px; height:15px; margin:0;"> Sex
        </label>
      </div>
    </div>
  `;
  container.appendChild(novaLinha);
}

function atualizarInterfaceGrupo(select) {
  const linha = select.closest('.linha-dinamica');
  const secaoDias = linha.querySelector('.secao-dias');
  const hiddenInput = linha.querySelector('.input-dias-string');
  
  if (select.value === 'Acolhimento Diurno') {
    secaoDias.style.display = 'block';
  } else {
    secaoDias.style.display = 'none';
    hiddenInput.value = '';
    secaoDias.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
  }
}

function atualizarDiasString(checkbox) {
  const linha = checkbox.closest('.linha-dinamica');
  const hiddenInput = linha.querySelector('.input-dias-string');
  const checkboxesMarcados = linha.querySelectorAll('.secao-dias input[type="checkbox"]:checked');
  
  const diasArray = Array.from(checkboxesMarcados).map(cb => cb.value);
  hiddenInput.value = diasArray.join(','); 
}

function removerLinhaDinamica(botao) {
  const linha = botao.closest('.linha-dinamica');
  if (!linha) return;
  
  const listaContainer = linha.parentElement;
  linha.remove();
  
  // REGRA DE OURO: Se a lista ficou vazia, desmarca o checkbox principal e esconde o bloco
  if (listaContainer.children.length === 0) {
    if (listaContainer.id === 'lista_consultas_futuras') {
      document.getElementById('marcar_consulta_futura').checked = false;
      document.getElementById('container_consultas_lista').style.display = 'none';
    } else if (listaContainer.id === 'lista_grupos_futuros') {
      document.getElementById('marcar_grupo_futuro').checked = false;
      document.getElementById('container_grupos_lista').style.display = 'none';
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

function salvarAtendimento() {
  const valor = (id) => document.getElementById(id)?.value || '';
  const modo = valor('modo_atendimento') || 'novo';
  
  // Captura os procedimentos selecionados como string separada por vírgula
  const procedimentos = Array.from(document.querySelectorAll('input[name="procedimentos_atendimento"]:checked'))
    .map(input => input.value)
    .join(', ');

  // Validações básicas obrigatórias
  const prontuario = valor('prontuario_atendimento');
  const data_atendimento = valor('data_atendimento');

  if (!prontuario.trim()) {
    alert("Informe o prontuário.");
    document.getElementById('prontuario_atendimento')?.focus();
    return;
  }

  if (!data_atendimento) {
    alert("Informe a data do atendimento.");
    document.getElementById('data_atendimento')?.focus();
    return;
  }

  if (!procedimentos) {
    alert("Selecione ao menos um procedimento.");
    return;
  }

  // Montagem do payload estruturado com as listas dinâmicas capturadas
  const dadosFormulario = {
    id: valor('atendimento_id'),
    prontuario: prontuario,
    data_atendimento: data_atendimento,
    observacoes: valor('observacoes_atendimento'),
    acolhimento_24h: valor('acolhimento_24h'),
    paciente_aceitou: valor('paciente_aceitou'),
    procedimentos: procedimentos,

    // Captura da lista dinâmica: Consultas Individuais
    data_proxima_consulta: Array.from(document.querySelectorAll('input[name="data_proxima_consulta[]"]')).map(el => el.value),
    hora_proxima_consulta: Array.from(document.querySelectorAll('input[name="hora_proxima_consulta[]"]')).map(el => el.value),
    profissional_proxima_consulta: Array.from(document.querySelectorAll('select[name="profissional_proxima_consulta[]"]')).map(el => el.value),

    // Captura da lista dinâmica: Grupos / Acolhimento por Período
    tipo_pactuacao_periodo: Array.from(document.querySelectorAll('select[name="tipo_pactuacao_periodo[]"]')).map(el => el.value),
    data_inicio_pactuacao: Array.from(document.querySelectorAll('input[name="data_inicio_pactuacao[]"]')).map(el => el.value),
    data_fim_pactuacao: Array.from(document.querySelectorAll('input[name="data_fim_pactuacao[]"]')).map(el => el.value),
    dias_semana_acolhimento: Array.from(document.querySelectorAll('input[name="dias_semana_acolhimento[]"]')).map(el => el.value)
  };

  const url = (modo === 'editar' || modo === 'edit') ? '/atualizar_atendimento' : '/novo_atendimento';

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(dadosFormulario)
  })
  .then(res => res.json())
  .then(data => {
    alert(data.mensagem || 'Atendimento salvo com sucesso!');
    fecharModalAtendimento();
    location.reload();
  })
  .catch(err => {
    console.error('Erro ao salvar atendimento:', err);
    alert('Erro ao salvar o atendimento no servidor.');
  });
}