# Validação — próxima versão para a Mac App Store

**Estado:** histórico; Mac App Store descartada; execução funcional não iniciada

**Direção vigente:** [distribuição comercial](../distribuicao-comercial/spec.md).
O registro abaixo preserva a análise anterior à decisão final de abandonar a loja.
Seus gates não são o plano de aceitação da próxima versão.

**Regra:** marcar um gate somente com comando, artefato ou roteiro reproduzível registrado.

## Revisão de viabilidade — 29 de agosto de 2026

- conferidas as regras 2.3.1, 5.2.2 e 5.2.3 na página oficial da Apple vinculada em `spec.md`;
- inspecionados `sao_francisco/pipeline.py::_prepare_local_source` e
  `sao_francisco/core/media.py::{download_url,split_audio}`: download com yt-dlp para
  workspace e conversão de áudio com FFmpeg; nenhum download real foi executado;
- não foi apresentada autorização das fontes nesta revisão, nem aprovada uma variante
  somente de arquivos locais;
- registrada a suspensão de T08–T10, sem renomear controles ou alterar código;
- inventário em português preservado como rascunho, sem aprovação editorial presumida;
- revisão limitada às cinco specs existentes; chamadas pagas, builds, uploads e submissões:
  zero.

### Gate para eventual retomada — ainda não executado

- [ ] autor escolheu explicitamente a variante e autorizou retomar a frente App Store;
- [ ] edição local: artefato sem ingestão remota, inclusive CLI, retomada e entradas indiretas;
- [ ] edição remota, se escolhida: evidências cobrem cada fonte e operação; fontes fora do
  escopo são rejeitadas, inclusive após redirecionamento;
- [ ] teste negativo: chamar o mesmo download de “streaming” ou marcar uma declaração de
  direitos não libera uma fonte sem autorização;
- [ ] interface, Ajuda, bundle e notas da revisão descrevem a mesma funcionalidade;
- [ ] demais gates de licenças, privacidade, sandbox e validação continuam exigidos.

## Baseline observado em 13 de agosto de 2026

- branch inicial `main` limpa e sincronizada com `origin/main` no commit `3bc3f2a`;
- versão declarada `0.1.2`;
- CI mais recente inspecionada: 109 testes, Ruff, mypy e wheel smoke aprovados;
- build macOS atual é Developer ID/notarizado, não Mac App Store/sandbox;
- FFmpeg/ffprobe não estão incorporados no pacote macOS atual;
- lista de idiomas está fixa no QML;
- vários arquivos já podem ser selecionados, mas o executor mantém um único processo
  ativo e a entrada por URL aceita um endereço;
- Help contém preços unitários datados;
- QML, Help, README, `pyproject.toml`, LICENSE e avisos afirmam MIT/software livre;
- cópias de avisos raiz/pacote contêm o parágrafo interno a remover.

O Python padrão local é 3.14, fora do intervalo do projeto, e o Python 3.13 disponível
não possui as dependências de desenvolvimento. Por isso nenhuma suíte foi repetida para
esta tarefa exclusivamente documental; a execução começa na primeira tarefa de código em
ambiente isolado compatível.

## Gate T00 — especificação

- [x] os oito pedidos do usuário aparecem em `spec.md` e `requirements.md`;
- [x] objetivo, requisitos, não objetivos, casos e validação estão explícitos;
- [x] toda tarefa executável tem modelo e esforço;
- [x] decisões não tomadas estão marcadas como pendentes;
- [x] inventário editorial foi criado e entregue ao autor;
- [ ] português do inventário foi aprovado pelo autor;
- [x] `git diff --check` passa;
- [x] diff contém somente specs, inventário e ponteiro para o inventário novo.

### Execução documental — 13 de agosto de 2026

- branch: `codex/especificar-versao-app-store`;
- base: `3bc3f2aa4610207566a5a13f1e75ad019e523c81`;
- arquivos novos: `spec.md`, `requirements.md`, `plan.md`, `validation.md` e
  `textos-gui-pt-BR.md`;
- arquivo existente alterado: somente `TEXTOS_DO_APP.md`, com um ponteiro para o novo
  inventário e sem mudar o texto da versão 0.1.2;
- auditoria estrutural: 449 IDs de texto únicos, 64 IDs de requisitos únicos e 11 tarefas
  únicas, todas com modelo, esforço e estado;
- links locais resolvidos e chaves de placeholders balanceadas;
- `git diff --check` executado para a alteração rastreada;
- `git diff --no-index --check /dev/null <arquivo>` executado separadamente para cada um
  dos cinco arquivos ainda não rastreados;
- espaços finais encontrados na primeira execução foram removidos; a segunda execução
  aprovou todos os arquivos;
- chamadas de API pagas, builds, testes funcionais, publicação e alterações externas:
  zero.

T00 permanece **aguardando aprovação editorial** porque somente o autor pode aprovar o
português-fonte. Nenhuma tarefa de implementação deve começar como continuação implícita.

## Matriz completa da GUI

### Superfícies

| ID | Superfície | Estados/ações obrigatórios |
| --- | --- | --- |
| G01 | menu Arquivo | nova, adicionar arquivos, URL se disponível, Histórico, Configurações, sair |
| G02 | menu Transcrição | iniciar desabilitado/habilitado, cancelar, abrir, mostrar pasta |
| G03 | menus Visualizar/Ir/Janela/Ajuda | sidebar, tela cheia, rotas, tópicos, minimizar/zoom/frente |
| G04 | sidebar/cabeçalho/rodapé | expandida/recolhida, rota ativa, busy, Ajuda, link externo |
| G05 | Transcrever — fontes | vazio, vários arquivos, duplicata, inválido, remover, drag/drop |
| G06 | Transcrever — URLs | zero/uma/várias, linha inválida, duplicata, legendas, variante sem URL |
| G07 | Transcrever — opções | provedor, modelo, idioma compatível/incompatível, destino, formatos, tempos, melhoria |
| G08 | fila | vazia, 1/muitos, esperando, esperando memória, ativos paralelos, fora de ordem |
| G09 | cartão de trabalho | indeterminado/determinado, custos/uso, original, melhorado, legendas, partes |
| G10 | Histórico | vazio, busca sem resultado, filtros, todos os estados, abrir/retomar/detalhes |
| G11 | Configurações | chaves vazias/mascaradas, verificar sucesso/falha, pasta, continuidade, salvar |
| G12 | Ajuda | índice, busca com/sem resultado, links, artigo longo, rolagens independentes |
| G13 | Sobre | texto novo, versão, página do autor, licenças, aviso longo e fechar |
| G14 | diálogos do sistema | abrir vários, escolher destino, cancelamento, bookmark revogado |
| G15 | toasts/notificações/erros | cada mensagem catalogada, longa, placeholder e locale |
| G16 | saída do app | nenhum job, fila esperando, um/muitos ativos, processo incooperativo |

Cada superfície deve ser exercitada nos seguintes eixos, usando cobertura pairwise quando
o produto cartesiano não acrescentar comportamento:

- janela 1280×800 e 1024×680;
- escala 100% e 200%;
- mouse e somente teclado;
- `pt-BR`, pseudolocale e cada locale final;
- sem job, job ativo e estado terminal quando aplicável;
- aparência disponível do sistema (clara/escura) quando o app a respeitar.

### Critérios visuais e de acessibilidade

- [ ] sem texto cortado, sobreposto ou inacessível por rolagem;
- [ ] foco visível e ordem coerente;
- [ ] `Tab`, `Shift+Tab`, `Enter`, `Espaço`, `Esc`, Page Up/Down, Home/End funcionam;
- [ ] nomes/descrições acessíveis refletem rótulos e estado;
- [ ] ação desabilitada não pode ser disparada por menu/atalho;
- [ ] atualização dinâmica é anunciada sem tomar foco indevidamente;
- [ ] links externos identificam o destino antes de abrir;
- [ ] screenshot de cada superfície/locale crítico é preservada com nome determinístico.

## Matriz de fluxos

### Curtos, sem rede

| ID | Fluxo | Resultado esperado |
| --- | --- | --- |
| F01 | um áudio curto → TXT | texto integral e job concluído |
| F02 | um áudio curto → DOCX | DOCX regular e semanticamente equivalente |
| F03 | um áudio curto → todos os formatos | quatro saídas coerentes |
| F04 | melhoria desmarcada/marcada | original sempre; melhorado só quando pedido |
| F05 | falha da melhoria | original preservado e estado específico |
| F06 | cancelamento antes da chamada | zero chamada e item cancelado |
| F07 | cancelamento durante chamada falsa | tentativa incerta persistida, sem retry |
| F08 | retomar trabalho interrompido | partes aceitas reaproveitadas |

### Fila e paralelismo

| ID | Fluxo | Resultado esperado |
| --- | --- | --- |
| Q01 | 10 fontes válidas | 10 IDs/workspaces independentes |
| Q02 | válido + inválido + duplicata | válidos entram; erros individualizados |
| Q03 | dois jobs terminam invertidos | saídas/progresso continuam no job correto |
| Q04 | cancelar job aguardando | nenhum processo/chamada criado |
| Q05 | cancelar um de três ativos | outros dois continuam |
| Q06 | fechar com filhos ativos | todos encerrados no limite, estados recuperáveis |
| Q07 | nomes de fonte iguais | nomes finais únicos e estáveis |
| Q08 | mesmo destino em processos paralelos | nenhuma escrita cruzada/corrupção |
| Q09 | limite do provedor atingido | slots remotos pausam sem retry automático |
| Q10 | memória abaixo da reserva | novo job fica Aguardando memória |
| Q11 | memória volta a ficar disponível | fila retoma sem ação destrutiva |
| Q12 | disco insuficiente | apenas item afetado falha/pausa, manifestos íntegros |

### Longos

| ID | Fluxo | Fixture | Resultado esperado |
| --- | --- | --- | --- |
| L01 | mídia longa com pausas | sintética/local ≥ 90 min | chunks estáveis, reunião integral |
| L02 | longa + cancelamento tardio | provedor falso com atraso | partes prontas preservadas |
| L03 | longa + reinício | kill controlado | reconciliação sem duplicar chamada incerta |
| L04 | duas longas em paralelo | fixtures distintas | respeito à memória e isolamento |
| L05 | longa + melhoria | resposta editorial falsa | original exportado antes da melhoria |
| L06 | longa em cada locale de UI | mesma mídia | locale não altera conteúdo/payload |

Fixtures longas não precisam conter 90 minutos de fala: podem usar áudio sintético
compactável e delays/manifestos controlados, desde que exercitem o particionamento real.

## Idiomas de transcrição

### Contrato estático

Para cada linha do registro:

- [ ] aparece somente nos provedores/modelos documentados;
- [ ] código canônico é válido;
- [ ] adaptador gera campo/valor correto;
- [ ] omitir idioma ativa detecção somente onde permitido;
- [ ] fonte oficial e data existem;
- [ ] troca incompatível volta a automático com mensagem localizada;
- [ ] código desconhecido falha antes da chamada.

Casos obrigatórios:

- [ ] catalão aparece para OpenAI compatível e não para Gemini;
- [ ] hebraico `he` é mapeado corretamente para Gemini quando necessário;
- [ ] chinês não ganha variante não documentada;
- [ ] todos os idiomas atuais têm decisão explícita, não ausência acidental.

### Amostra real proposta

Depois de autorização do orçamento:

- cobrir cada idioma listado ao menos uma vez por provedor que o declara;
- cobrir cada modelo/endpoint ao menos uma vez;
- usar desenho pairwise, não idioma × modelo completo;
- áudio de 5–8 segundos sem dado pessoal;
- no máximo 40 chamadas e US$ 1,00 no total;
- registrar request sem chave/conteúdo privado, resposta, uso e custo oficial.

Uma recusa da API corrige o registro e exige nova hipótese antes de repetir a chamada.

## DOCX

### Fixtures semânticas

| ID | Conteúdo | Variações |
| --- | --- | --- |
| D01 | texto simples | curto/longo, com e sem tempos |
| D02 | múltiplos falantes | nomes conhecidos/desconhecidos, alternância rápida |
| D03 | Unicode | pt, latino acentuado, cirílico, japonês, chinês, emoji |
| D04 | limites | vazio recusado, uma palavra, parágrafo muito longo |
| D05 | caracteres especiais | `&`, `<`, `>`, aspas, tabs, quebras |
| D06 | melhoria | original e melhorado separados, sem tempos no melhorado |
| D07 | paralelismo | nomes iguais, conteúdo diferente, mesmo destino |

### Verificação automatizada por arquivo

- [ ] `zipfile.testzip()` não encontra corrupção;
- [ ] `[Content_Types].xml`, `_rels/.rels`, `word/document.xml` presentes;
- [ ] XML bem-formado e relationships resolvidos;
- [ ] `python-docx` abre, percorre e salva novamente;
- [ ] texto normalizado equivale à fonte esperada;
- [ ] falantes/tempos permanecem na ordem;
- [ ] core properties não contêm dados de outro job;
- [ ] ZIP não contém mídia, chaves, paths ou logs inesperados.

### Verificação por aplicativos

- [ ] LibreOffice headless abre e converte cada classe de fixture para PDF;
- [ ] PDF resultante contém texto esperado e páginas não vazias;
- [ ] Microsoft Word para macOS abre amostra curta, longa, Unicode e paralela;
- [ ] Word não mostra aviso de reparo e consegue salvar uma cópia;
- [ ] inspeção visual confirma estilos, parágrafos, falantes e timestamps.

## Memória, desempenho e estabilidade

### Perfis

| Perfil | RAM | Cenário mínimo |
| --- | ---: | --- |
| M08 | 8 GB | 6 itens mistos, app concorrendo com pressão sintética |
| M16 | 16 GB | 10 itens, dois trabalhos elegíveis em paralelo |
| M32 | 32 GB | 20 itens, teto absoluto e limites do provedor |

Em cada perfil registrar memória total/disponível, estimativa antes da admissão, RSS de
cada processo, pico agregado, page-outs relevantes, duração, jobs ativos e motivo de
espera. Aceitação:

- [ ] sistema permanece responsivo;
- [ ] nenhuma admissão viola a reserva calculada;
- [ ] estimativa não subestima sistematicamente o pico observado;
- [ ] modo automático pode escolher serial em 8 GB;
- [ ] teto manual nunca força admissão insegura;
- [ ] fila de 100 itens aguardando não cria 100 processos nem consumo proporcional de RAM;
- [ ] 8 horas de soak com fixtures locais não vaza processos, descritores ou memória.

## App Sandbox e bundle

### Inventário

- [ ] checkout limpo, commit e ferramentas registrados;
- [ ] um único `.app`, sem instalador próprio;
- [ ] Python/Qt/FFmpeg/ffprobe e helpers necessários dentro do bundle;
- [ ] nenhum Homebrew path, symlink externo ou dependência ausente;
- [ ] todos os Mach-O têm arquitetura e deployment target declarados;
- [ ] todos os executáveis/frameworks assinados corretamente;
- [ ] textos/licenças correspondem ao inventário;
- [ ] variante sem URL não contém yt-dlp/Deno/código executável acessível para download.

### Sandbox em usuário limpo

| ID | Prova | Resultado esperado |
| --- | --- | --- |
| S01 | abrir fonte pelo painel | leitura concedida apenas à seleção |
| S02 | escolher destino pelo painel | escrita apenas no destino concedido |
| S03 | relançar | bookmark recupera acesso válido |
| S04 | revogar/mover fonte | aviso e nova seleção, sem acesso arbitrário |
| S05 | processo filho | recebe acesso necessário, não amplia escopo |
| S06 | duas fontes/destinos paralelos | tokens/bookmarks não são trocados |
| S07 | OpenAI/Gemini | conexão de saída funciona com timeout/cancelamento |
| S08 | Keychain | salvar/ler/substituir/remover após relançar/atualizar |
| S09 | sair com trabalhos | nenhum processo órfão |
| S10 | máquina sem ferramentas | app continua funcional/autocontido |

### Privacidade e metadados

- [ ] `PrivacyInfo.xcprivacy` é plist válido e está no local correto;
- [ ] declaração de coleta corresponde aos SDKs e comportamento observado;
- [ ] política pública abre e cobre provedores, retenção e exclusão;
- [ ] URLs de privacidade por locale estão corretas;
- [ ] export compliance respondido e `Info.plist` coerente;
- [ ] screenshots, descrição e notas não prometem recurso removido;
- [ ] todos os locales estão no mesmo bundle;
- [ ] nenhum updater/download de código está presente.

## Comandos-base de código

Os comandos exatos podem ser ajustados ao ambiente, mas a evidência deve cobrir:

```text
python -m pytest -q
python -m ruff check .
python -m mypy sao_francisco
git diff --check
pyside6-qmllint <todos os QML>
```

Acrescentar suites focadas para fila, scheduler, idiomas, i18n, DOCX, sandbox e pacote.
Executar os focados primeiro e a suíte ampla uma vez por candidato relevante.

## Registro de chamadas e builds

```text
Orçamento aprovado por:
Data:
Provedores/modelos:
Idiomas:
Chamadas autorizadas / executadas:
Teto / custo observado:

Commit do candidato:
Versão/build:
Ambiente Qt/Python/PyInstaller ou ferramenta escolhida:
Licença/edição do Qt:
FFmpeg version/buildconf/licença:
Entitlements:
Certificado/perfil:
Hash do bundle/pacote:
ID do upload:
Status do processamento:
Grupo/TestFlight:
Status da revisão:
URL da App Store:
Limitações finais:
```

## Gate final

- [ ] todas as tarefas T01–T10 aceitas;
- [ ] matriz GUI sem célula obrigatória ausente;
- [ ] testes curtos/longos e soak aprovados;
- [ ] DOCX aprovado por três leitores;
- [ ] idiomas e catálogos sincronizados;
- [ ] licenciamento e inventário aprovados;
- [ ] sandbox/Keychain/bookmarks/helpers aprovados no candidato;
- [ ] App Privacy, política e export compliance coerentes;
- [ ] TestFlight aprovado;
- [ ] App Review aprovado;
- [ ] compra, instalação e abertura pública verificadas;
- [ ] specs refletem o estado final.
