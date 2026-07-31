# Validação — cancelamento e melhoria não bloqueante

## Critérios de aceitação

| Critério | Evidência exigida | Estado |
| --- | --- | --- |
| Guard semântico removido | Testes unitários e ausência das comparações no diff | aprovado |
| Estrutura editorial continua íntegra | Testes de vazio, persistência e montagem | aprovado |
| Original é independente da melhoria | Testes de pipeline e arquivos | aprovado |
| Erro editorial não menciona arquivo | Testes dos tradutores públicos | aprovado |
| Nenhum retry pago é automático | Contadores de chamadas em falha e reinício | aprovado |
| Cancelamento incooperativo é limitado | Teste com processo fake e deadline | aprovado |
| Nova tarefa funciona após cancelar | Teste Qt com primeira travada e segunda concluída | aprovado |
| Progresso não chega cedo a 100% | Testes de pipeline, Histórico e QML | aprovado |
| Manifestos 0.1.1 continuam legíveis | Fixtures de compatibilidade | parcial |
| Processo descartável funciona empacotado | Smoke tests macOS e Windows | pendente |

## Guard editorial

- [x] resposta textual não vazia não é recusada por números diferentes;
- [x] resposta textual não vazia não é recusada por falantes ou marcações diferentes;
- [x] resposta textual não vazia não é recusada por proporção de extensão;
- [x] não existem mascaramento, placeholders ou restauração heurística;
- [x] resposta vazia continua sendo falha técnica;
- [ ] resultado sem ID ou artefato não é considerado concluído;
- [x] plano ausente, bloco duplicado ou montagem incompleta continua falhando;
- [x] `EditorialValidationError` legado recebe mensagem editorial, não de arquivo.

Esses testes verificam a política de runtime. Eles não declaram que uma mudança factual é
boa; a versão original permanece disponível para comparação.

## Qualidade editorial de versão

O conjunto de avaliação deve continuar cobrindo:

- [ ] resumo ou omissão;
- [ ] acréscimo de conteúdo;
- [ ] nomes próprios;
- [ ] números, datas, valores e percentuais;
- [ ] falantes;
- [ ] trechos inaudíveis;
- [ ] instruções faladas dirigidas à IA;
- [ ] textos maiores que um bloco.

Antes da liberação, a amostra manual curta deve confirmar que o modelo segue o prompt de
forma aceitável. Uma falha de qualidade orienta prompt, modelo ou decisão de versão; não
reintroduz um bloqueador heurístico por trabalho.

## Original e melhoria

- [x] legenda ou transcrição original é persistida antes da melhoria;
- [x] DOCX/TXT/SRT/VTT originais selecionados são exportados antes da primeira chamada
      editorial;
- [x] a melhoria cria somente DOCX/TXT adicionais;
- [ ] falha de autenticação mantém originais acessíveis;
- [x] falha de rede mantém originais acessíveis;
- [ ] timeout mantém originais acessíveis;
- [x] cancelamento mantém originais acessíveis;
- [x] retomar melhoria não retranscreve nem reexporta desnecessariamente o original;
- [x] resultado e Histórico distinguem os estados das duas etapas;
- [x] o aviso de conferência continua visível e acessível.

## Persistência e recuperação

Injetar interrupção:

- [ ] depois de salvar `running`, antes da chamada;
- [ ] depois de enviar, antes de receber;
- [ ] depois de receber, antes de salvar o artefato;
- [x] depois do artefato, antes de marcar `accepted`;
- [ ] antes do bloco seguinte;
- [ ] antes e depois da exportação melhorada.

Para cada fronteira:

- [x] resultado aceito persistido não gera nova chamada;
- [x] resultado remoto incerto vira `remote_ambiguous`;
- [x] custo conhecido não é perdido nem duplicado;
- [x] original continua disponível;
- [x] nenhuma retomada automática repete chamada ambígua;
- [x] `rejected` legado exige ação explícita.

## Cancelamento limitado

Usar processo fake que entra numa leitura sem retorno e ignora token e fechamento:

- [x] clique muda para `cancelling` imediatamente;
- [x] `cancel_requested` é persistido antes do sinal;
- [x] controlador aguarda no máximo cinco segundos;
- [x] processo fake deixa de existir depois da margem de agendamento;
- [x] estado final é `cancelled`;
- [x] chamada em voo fica `remote_ambiguous`;
- [x] artefatos concluídos permanecem;
- [ ] itens aguardando são removidos com aviso;
- [x] `busy` fica falso;
- [x] botão e atalho de iniciar ficam habilitados;
- [x] uma segunda tarefa inicia e conclui;
- [x] mensagem tardia da primeira não altera a segunda.

Repetir cancelamento:

- [ ] durante obtenção de legenda;
- [ ] durante transcrição;
- [ ] durante melhoria;
- [ ] durante exportação local;
- [ ] imediatamente antes da conclusão;
- [ ] durante fechamento do app.

## Timeout

- [x] timeout editorial usa constante de cinco minutos;
- [ ] relógio ou transporte falso expira sem espera real;
- [ ] expiração torna a melhoria retomável e preserva o original;
- [x] **Cancelar** termina em cerca de cinco segundos, sem esperar timeout;
- [x] nenhuma etapa nova começa depois de `cancel_requested`.

## Progresso e GUI

- [x] legenda `1/1` com melhoria pendente não aparece como trabalho 100% concluído;
- [x] melhoria mostra `n de 9`;
- [x] progresso geral é coerente com o plano de etapas;
- [x] exportação pendente impede conclusão prematura;
- [x] `cancelling` não parece processamento normal;
- [x] cartão e Histórico chegam ao mesmo estado;
- [x] **Transcrição pronta** pode coexistir com melhoria em andamento ou falha;
- [x] estados não dependem apenas de cor;
- [x] layouts 1280×800 e 1024×680 funcionam;
- [ ] Tab, botão e atalho permanecem acessíveis;
- [x] QML carrega sem warning.

## Compatibilidade e empacotamento

- [ ] abrir manifestos 0.1.1 concluídos, falhos, cancelados e em andamento;
- [x] trabalho antigo `running/improving` fica pausado sem auto-retry;
- [x] `rejected` e custos legados continuam legíveis;
- [ ] resultados antigos continuam abrindo;
- [x] código-fonte inicia o processo;
- [ ] app macOS congelado inicia, cancela e recria o processo;
- [ ] app Windows congelado inicia, cancela e recria o processo;
- [x] nenhum processo filho fica órfão;
- [ ] caminho com espaços e acentos funciona;
- [x] nenhum segredo aparece em argumentos, IPC, manifesto ou QML.

## Comandos previstos

```text
python -m pytest -q tests/test_costs_editorial.py tests/test_pipeline.py
python -m pytest -q tests/test_backend.py tests/test_qml_offscreen.py
python -m pytest -q
python -m ruff check .
python -m mypy sao_francisco
```

Smoke tests usam os scripts oficiais e não repetem builds sem nova hipótese.

## Execução automatizada — 30 de julho de 2026

- `python -m pytest -q`: **109 aprovados**, incluindo metadados de 0.1.2 e smoke real do
  subprocesso;
- `ruff check .`: aprovado;
- `mypy sao_francisco`: aprovado em 26 arquivos;
- `git diff --check`: aprovado;
- abertura offscreen pelo código-fonte com `--smoke-test`: aprovada;
- processo real com `spawn`, cancelamento forçado e reutilização do controlador: aprovados.

Não foram gerados pacotes nesta tarefa. Permanecem pendentes os smoke tests do executável
congelado em macOS e Windows e a avaliação manual paga, que exige autorização própria.

## Custos e operações externas

- **Chamadas executadas nesta investigação:** zero.
- **Repetições evitadas:** o vídeo de 2h09m e o bloco falho não foram reenviados.
- **Custo editorial conhecido do incidente:** aproximadamente US$ 0,147, incluindo duas
  respostas descartadas pelo guard antigo.
- **Chamadas automatizadas permitidas:** zero.
- **Chamadas manuais máximas:** duas com fixture curta.
- **Teto planejado:** US$ 0,05.
- **Condição de parada:** retry inesperado, processo órfão ou estado não diagnosticado.

## Revisão final

- [x] diff contém somente o escopo do incidente;
- [x] nenhuma limpeza ampla de legado foi misturada;
- [x] specs e código final descrevem o mesmo comportamento;
- [x] não há URL privada, chave, resposta bruta, mídia ou manifesto real no Git;
- [x] não há processo, temporário ou build acidental;
- [x] o vídeo longo só será reavaliado depois das fixtures e com autorização de custo.
