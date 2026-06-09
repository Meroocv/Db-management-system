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

document.querySelectorAll(".idade").forEach(td => {
  const data = td.dataset.nascimento;
  const idade = calcularIdade(data);
  td.innerText = idade ? idade + " anos" : "";
});

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
        prontuario_atendimento: 'campo-curto',
        data_atendimento: 'campo-curto',
        acolhimento_24h: 'campo-curto',
        paciente_aceitou: 'campo-curto',
        atendimento_id: 'campo-curto'
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

    // preencher campos
    setValue('prontuario', dados.prontuario);
    setValue('nome_paciente', dados.nome_paciente);
    setValue('nome_social', dados.nome_social);
    setValue('cpf', dados.cpf);
    setValue('rg', dados.rg);
    setValue('cns_paciente', dados.cns_paciente);
    setValue('data_nascimento', dados.data_nascimento);
    setValue('sexo', dados.sexo);
    setValue('naturalidade', dados.naturalidade);
    setValue('raca_cor', dados.raca_cor);
    setValue('escolaridade', dados.escolaridade);
    setValue('etnia', dados.etnia);
    setValue('orientacao_religiosa', dados.orientacao_religiosa);
    setValue('nome_mae', dados.nome_mae);
    setValue('nome_pai', dados.nome_pai);
    setValue('nome_responsavel', dados.nome_responsavel);
    setValue('grau_parentesco_responsavel', dados.grau_parentesco_responsavel);
    setValue('telefone_responsavel', dados.telefone_responsavel);
    setValue('telefone', dados.telefone);
    setValue('municipio', dados.municipio);
    setValue('uf', dados.uf);
    setValue('zona', dados.zona);
    setValue('cep', dados.cep);
    setValue('bairro', dados.bairro);
    setValue('tp_logradouro', dados.tp_logradouro); 
    setValue('logradouro', dados.logradouro);
    setValue('numero', dados.numero);
    setValue('complemento', dados.complemento);
    setValue('statusPaciente', dados.statusPaciente);
    setValue('terapeuta_referencia', dados.terapeuta_referencia);
    setValue('cid', dados.cid);
    setValue('data_admissao', dados.data_admissao);
    setValue('data_conclusao', dados.data_conclusao);

    // Atualiza a flag de modo no input hidden antes de mexer na renderização visual
    let elModo = document.getElementById("modo");
    if (elModo) elModo.value = modo;

    // abrir modal
    document.getElementById('modalPaciente').style.display = 'block';
    abrirAba('identificacao', document.querySelector('#modalPaciente .nav-link'));

    // aplicar modo limpo e direto (Habilita ou desabilita campos do modal)
    let ehEditavel = (modo !== 'view');
    setModoPaciente(ehEditavel);

    // 🌟 RENDERIZAR OS TELEFONES DO BANCO DE FORMA SEGURA:
    const container = document.getElementById('container-telefones');
    if (container) {
        container.innerHTML = ''; // Limpa os telefones do paciente anterior aberto

        let dadosTelefonesRaw = btn.getAttribute('data-telefones'); 
        
        if (dadosTelefonesRaw) {
            try {
                // Remove quebras de linha que o Jinja insere no HTML e que travam o JSON.parse
                dadosTelefonesRaw = dadosTelefonesRaw.replace(/\r?\n|\r/g, " ").trim();
                
                const listaTelefones = JSON.parse(dadosTelefonesRaw);
                
                if (Array.isArray(listaTelefones) && listaTelefones.length > 0) {
                    listaTelefones.forEach(tel => {
                        adicionarTelefone(tel); 
                    });
                } else if (modo === 'edit' || modo === 'novo' || modo === 'new') {
                    adicionarTelefone(); 
                }
            } catch (e) {
                console.error("Erro ao analisar a string JSON de telefones:", e);
                if (modo === 'edit' || modo === 'novo' || modo === 'new') adicionarTelefone();
            }
        } else if (modo === 'edit' || modo === 'novo' || modo === 'new') {
            adicionarTelefone();
        }
    }
}

function abrirNovoPaciente() {
  // limpa TUDO
  document.querySelectorAll("#modalPaciente input, #modalPaciente select, #modalPaciente textarea")
    .forEach(el => el.value = "");

  // define prontuário como automático (visual)
  document.getElementById('prontuario').value = 'Automático';

  // define modo primeiro para que adicionarTelefone() saiba que é editável
  const elModo = document.getElementById("modo");
  if (elModo) elModo.value = "novo";

  // limpa e prepara container de telefones
  const container = document.getElementById('container-telefones');
  if (container) {
      container.innerHTML = '';
      adicionarTelefone(); // Adiciona uma linha limpa padrão
  }

  // abre modal
  document.getElementById('modalPaciente').style.display = 'block';
  abrirAba('identificacao', document.querySelector('#modalPaciente .nav-link'));

  // ativa modo edição
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

    // Manter prontuário travado
    const prontuario = document.getElementById('prontuario');
    if (prontuario) {
        prontuario.readOnly = true;
    }

    // Controlar botão Salvar
    document.getElementById('btnSalvar').style.display = editavel ? 'inline-block' : 'none';

    // Força o botão de adicionar e os botões de remover a aparecerem/sumirem de acordo com o modo
    let btnAdicionar = document.getElementById('btn-adicionar-telefone');
    if (btnAdicionar) {
        btnAdicionar.style.setProperty('display', editavel ? 'block' : 'none', 'important');
        btnAdicionar.disabled = !editavel;
    }

    // Controla também os botões vermelhos "x" das linhas de telefone existentes
    document.querySelectorAll('#container-telefones .btn-remover-telefone').forEach(btnRemover => {
        btnRemover.style.setProperty('display', editavel ? 'inline-block' : 'none', 'important');
        btnRemover.disabled = !editavel;
    });
}

function abrirAba(aba, link) {
    document.querySelectorAll('.aba').forEach(div => {
        div.style.display = 'none';
    });

    const abaSelecionada = document.getElementById(aba);
    abaSelecionada.style.display = abaSelecionada.classList.contains('form-grid') ? 'grid' : 'block';

    document.querySelectorAll('#modalPaciente .nav-link').forEach(nav => {
        nav.classList.remove('active');
        nav.removeAttribute('aria-current');
    });

    if (link) {
        link.classList.add('active');
        link.setAttribute('aria-current', 'page');
    }
}

function toggleSidebar() {
  document.getElementById("sidebarMenu").classList.toggle("closed");

  const main = document.querySelector(".main-content");
  if (main) {
    main.classList.toggle("shift");
  }
}

function abrirModalPerfil() {
  const modal = document.getElementById('modalPerfil');
  if (modal) modal.style.display = 'block';
}

function fecharModalPerfil() {
  const modal = document.getElementById('modalPerfil');
  if (modal) modal.style.display = 'none';
}

function salvarEdicao() {
    // 🌟 CAPTURAR A LISTA DE TELEFONES DO CONTAINER (Igual você fez no inserirPaciente)
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

        // Identificação
        terapeuta_referencia: document.getElementById('terapeuta_referencia')?.value || '',
        nome_paciente: document.getElementById('nome_paciente').value,
        nome_social: document.getElementById('nome_social')?.value || '',
        cns_paciente: document.getElementById('cns_paciente')?.value || '',
        rg: document.getElementById('rg')?.value || '',
        cpf: document.getElementById('cpf').value,

        // Familiares
        nome_mae: document.getElementById('nome_mae')?.value || '',
        nome_pai: document.getElementById('nome_pai')?.value || '',
        nome_responsavel: document.getElementById('nome_responsavel')?.value || '',
        grau_parentesco_responsavel: document.getElementById('grau_parentesco_responsavel')?.value || '',
        telefone_responsavel: document.getElementById('telefone_responsavel')?.value || '',

        // Pessoais
        data_nascimento: document.getElementById('data_nascimento').value,
        sexo: document.getElementById('sexo')?.value || '',
        naturalidade: document.getElementById('naturalidade')?.value || '',
        raca_cor: document.getElementById('raca_cor')?.value || '',
        escolaridade: document.getElementById('escolaridade')?.value || '',
        etnia: document.getElementById('etnia')?.value || '',
        orientacao_religiosa: document.getElementById('orientacao_religiosa')?.value || '',

        // 🌟 SUBSTUIÇÃO AQUI: Enviando a lista estruturada ao invés do campo único que não existe
        telefones: listaTelefones,

        // Endereço
        municipio: document.getElementById('municipio')?.value || '',
        uf: document.getElementById('uf')?.value || '',
        zona: document.getElementById('zona')?.value || '',
        cep: document.getElementById('cep')?.value || '',
        bairro: document.getElementById('bairro')?.value || '',
        logradouro: document.getElementById('logradouro')?.value || '',
        numero: document.getElementById('numero')?.value || '',
        complemento: document.getElementById('complemento')?.value || '',

        // Status clínico
        statusPaciente: document.getElementById('statusPaciente')?.value || '',
        cid: document.getElementById('cid')?.value || '',
        data_admissao: document.getElementById('data_admissao')?.value || '',
        data_conclusao: document.getElementById('data_conclusao')?.value || ''
    };

    fetch('/atualizar_paciente', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
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

function fecharModal() {
    document.getElementById('modalPaciente').style.display = 'none';

    document.querySelectorAll('.aba').forEach(div => {
        div.style.display = 'none';
    });

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

document.addEventListener("DOMContentLoaded", function() {
    const campo = document.getElementById("prontuario_atendimento");

    if (campo) {
        campo.addEventListener("blur", function() {
            let prontuario = this.value.trim();

            if (!prontuario || prontuario === "0") {
                console.log("Prontuário inválido, não buscar");
                return;
            }

            console.log("Buscando:", prontuario);

            fetch(`/buscar_paciente?prontuario=${prontuario}`)
                .then(res => res.json())
                .then(data => {
                    const campoNome = document.getElementById("nome_paciente_atendimento");

                    if (!campoNome) return;

                    if (data.nome_paciente) {
                        campoNome.value = data.nome_paciente;
                    } else {
                        campoNome.value = "Paciente não encontrado";
                    }
                })
                .catch(() => {
                    const campoNome = document.getElementById("nome_paciente_atendimento");
                    if (campoNome) {
                        campoNome.value = "Erro na busca";
                    }
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
    const modal = document.getElementById('modalAtendimento');
    if (!modal) return;

    document.querySelectorAll('#modalAtendimento input, #modalAtendimento select, #modalAtendimento textarea')
        .forEach(el => {
            if (el.type === 'checkbox') {
                el.checked = false;
            } else {
                el.value = '';
            }
        });

    const modo = botao ? 'edit' : 'novo';
    document.getElementById('modo_atendimento').value = modo;
    document.getElementById('atendimento_id').value = botao?.dataset.id || '';

    const titulo = document.getElementById('tituloModalAtendimento');
    if (titulo) titulo.innerText = modo === 'edit' ? 'Editar Atendimento' : 'Registrar Atendimento';

    const botaoSalvar = document.getElementById('btnSalvarAtendimento');
    if (botaoSalvar) botaoSalvar.innerText = modo === 'edit' ? 'Salvar alterações' : 'Salvar Atendimento';

    if (botao) {
        document.getElementById('prontuario_atendimento').value = botao.dataset.prontuario || '';
        document.getElementById('nome_paciente_atendimento').value = botao.dataset.nomePaciente || '';
        document.getElementById('data_atendimento').value = botao.dataset.dataAtendimento || '';
        document.getElementById('acolhimento_24h').value = botao.dataset.acolhimento24h || '';
        document.getElementById('paciente_aceitou').value = botao.dataset.pacienteAceitou || '';
        document.getElementById('observacoes_atendimento').value = botao.dataset.observacoes || '';
        marcarProcedimentosAtendimento(botao.dataset.procedimentos);
    } else {
        const data = document.getElementById('data_atendimento');
        if (data) data.value = new Date().toISOString().slice(0, 10);
    }

    modal.style.display = 'block';
    document.getElementById('prontuario_atendimento')?.focus();
}

function fecharModalAtendimento() {
    const modal = document.getElementById('modalAtendimento');
    if (modal) modal.style.display = 'none';
}

function salvarAtendimento() {
    const valor = (id) => document.getElementById(id)?.value || '';
    const modo = valor('modo_atendimento') || 'novo';
    const procedimentos = Array.from(document.querySelectorAll('input[name="procedimentos_atendimento"]:checked'))
        .map(input => input.value)
        .join(', ');

    const dados = {
        id: valor('atendimento_id'),
        prontuario: valor('prontuario_atendimento'),
        data_atendimento: valor('data_atendimento'),
        procedimentos,
        acolhimento_24h: valor('acolhimento_24h'),
        paciente_aceitou: valor('paciente_aceitou'),
        observacoes: valor('observacoes_atendimento')
    };

    if (!dados.prontuario.trim()) {
        alert("Informe o prontuario.");
        document.getElementById('prontuario_atendimento')?.focus();
        return;
    }

    if (!dados.data_atendimento) {
        alert("Informe a data do atendimento.");
        document.getElementById('data_atendimento')?.focus();
        return;
    }

    if (!dados.procedimentos) {
        alert("Selecione pelo menos um procedimento.");
        return;
    }

    const url = modo === 'edit' ? '/atualizar_atendimento' : '/novo_atendimento';

    fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.erro || 'Erro ao cadastrar atendimento');
        return data;
    }))
    .then(data => {
        alert(data.mensagem || "Atendimento salvo!");
        fecharModalAtendimento();
        location.reload();
    })
    .catch(err => {
        console.error(err);
        alert(err.message || "Erro ao cadastrar atendimento");
    });
}

function inserirPaciente() {
    const valor = (id) => document.getElementById(id)?.value || '';

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
        nome_paciente: valor('nome_paciente'),
        nome_social: valor('nome_social'),
        cpf: valor('cpf'),
        rg: valor('rg'),
        cns_paciente: valor('cns_paciente'),
        data_nascimento: valor('data_nascimento'),
        sexo: valor('sexo'),
        naturalidade: valor('naturalidade'),
        raca_cor: valor('raca_cor'),
        escolaridade: valor('escolaridade'),
        etnia: valor('etnia'),
        orientacao_religiosa: valor('orientacao_religiosa'),
        nome_mae: valor('nome_mae'),
        nome_pai: valor('nome_pai'),
        nome_responsavel: valor('nome_responsavel'),
        grau_parentesco_responsavel: valor('grau_parentesco_responsavel'),
        telefone_responsavel: valor('telefone_responsavel'),
        municipio: valor('municipio'),
        uf: valor('uf'),
        zona: valor('zona'),
        cep: valor('cep'),
        bairro: valor('bairro'),
        logradouro: valor('logradouro'),
        numero: valor('numero'),
        complemento: valor('complemento'),
        statusPaciente: valor('statusPaciente'),
        terapeuta_referencia: valor('terapeuta_referencia'),
        cid: valor('cid'),
        data_admissao: valor('data_admissao'),
        data_conclusao: valor('data_conclusao'),
        telefones: listaTelefones 
    };

    if (!dados.nome_paciente.trim()) {
        alert("Informe o nome do paciente.");
        document.getElementById('nome_paciente')?.focus();
        return;
    }
    if (!dados.data_nascimento) {
        alert("Informe a data de nascimento.");
        document.getElementById('data_nascimento')?.focus();
        return;
    }

    fetch('/novo_paciente', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dados)
    })
    .then(res => res.json().then(data => {
        if (!res.ok) throw new Error(data.erro || 'Erro ao cadastrar paciente');
        return data;
    }))
    .then(data => {
        alert(data.mensagem || "Paciente cadastrado!");
        fecharModal();
        location.reload();
    })
    .catch(err => {
        console.error(err);
        alert(err.message || "Erro ao cadastrar paciente");
    });
}

function salvarPaciente() {
    const modo = document.getElementById("modo").value;
    if (modo === "novo") {
        inserirPaciente();
    } else {
        salvarEdicao();
    }
}

// 1. Função principal corrigida para gerenciar corretamente as permissões de edição
function adicionarTelefone(dadosTel = null) {
    const container = document.getElementById('container-telefones');
    if (!container) return;

    const modoAtual = document.getElementById('modo').value;
    // O campo é editável se for 'edit' ou se for um cadastro 'novo'
    const modoEdicao = (modoAtual === 'edit' || modoAtual === 'novo');

    const linha = document.createElement('div');
    linha.className = 'linha-telefone';
    linha.style = "display: grid; grid-template-columns: repeat(12, minmax(0, 1fr)); gap: 10px; align-items: end; background: #f8f9fa; padding: 10px; border-radius: 6px; margin-bottom: 10px; border: 1px solid #e6eaf0;";

    const ddd = dadosTel ? dadosTel.ddd : '';
    const numero = dadosTel ? dadosTel.numero : '';
    const tipo = dadosTel ? dadosTel.tipo : 'Paciente';
    const nome_familiar = dadosTel ? dadosTel.nome_familiar || '' : '';
    const parentesco_familiar = dadosTel ? dadosTel.parentesco_familiar || '' : '';
    const classOculto = tipo === 'Familiar' ? '' : 'oculto';

    // 🌟 CORREÇÃO BOOLEANA AQUI: Se for modoEdicao, NÃO coloca readonly. Se NÃO for modoEdicao, coloca readonly.
    linha.innerHTML = `
        <div style="grid-column: span 2;">
            <label style="font-size: 11px; color: #666;">DDD</label>
            <input type="text" name="ddd[]" value="${ddd}" placeholder="Ex: 11" maxlength="2" required ${!modoEdicao ? 'readonly' : ''}>
        </div>
        <div style="grid-column: span 3;">
            <label style="font-size: 11px; color: #666;">Número</label>
            <input type="text" name="numero_telefone[]" value="${numero}" placeholder="99999-9999" required ${!modoEdicao ? 'readonly' : ''}>
        </div>
        <div style="grid-column: span 3;">
            <label style="font-size: 11px; color: #666;">Pertence a</label>
            <select name="tipo_telefone[]" onchange="toggleCamposFamiliar(this)" ${!modoEdicao ? 'disabled' : ''}>
                <option value="Paciente" ${tipo === 'Paciente' ? 'selected' : ''}>Paciente</option>
                <option value="Familiar" ${tipo === 'Familiar' ? 'selected' : ''}>Familiar</option>
            </select>
        </div>

        <div class="campos-familiar ${classOculto}" style="grid-column: span 3; display: ${tipo === 'Familiar' ? 'grid' : 'none'}; grid-template-columns: 1fr 1fr; gap: 8px;">
            <div>
                <label style="font-size: 11px; color: #666;">Nome do Parente</label>
                <input type="text" name="nome_familiar[]" value="${nome_familiar}" placeholder="Nome" ${!modoEdicao ? 'readonly' : ''}>
            </div>
            <div>
                <label style="font-size: 11px; color: #666;">Parentesco</label>
                <input type="text" name="parentesco_familiar[]" value="${parentesco_familiar}" placeholder="Ex: Mãe" ${!modoEdicao ? 'readonly' : ''}>
            </div>
        </div>

        <div style="grid-column: span 1; display: flex; align-items: flex-end; justify-content: flex-end; width: 100%; padding-bottom: 4px;">
            <button type="button" class="btn-remover-telefone" onclick="removerLinhaTelefone(this)" 
            style="background: #dc3545; color: white; border: none; border-radius: 4px; padding: 4px 10px; display: ${modoEdicao ? 'inline-block' : 'none'};" 
            ${!modoEdicao ? 'disabled' : ''}>&times;</button>
        </div>
    `;

    container.appendChild(linha);
}

function toggleCamposFamiliar(selectElement) {
    const linha = selectElement.closest('.linha-telefone');
    const camposFamiliar = linha.querySelector('.campos-familiar');
    if (selectElement.value === 'Familiar') {
        camposFamiliar.classList.remove('oculto');
    } else {
        camposFamiliar.classList.add('oculto');
        camposFamiliar.querySelectorAll('input').forEach(i => i.value = ''); 
    }
}

function removerLinhaTelefone(botao) {
    const linha = botao.closest('.linha-telefone');
    if (linha) {
        linha.remove();
    }
}