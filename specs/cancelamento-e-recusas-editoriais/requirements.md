# Requisitos — cancelamento e melhoria não bloqueante

## Resultado principal e melhoria opcional

### CM-RF-01 — original canônico

A transcrição ou legenda normalizada persistida é o resultado canônico do trabalho. A
versão melhorada é um artefato opcional e separado.

### CM-RF-02 — exportação do original

Depois de montar e persistir o original, o app deve exportar imediatamente todos os
formatos originais selecionados. Ele não aguarda a melhoria para disponibilizar DOCX, TXT,
SRT ou VTT originais.

### CM-RF-03 — melhoria posterior

Quando solicitada, a melhoria começa somente depois da persistência e exportação do
original. Seu sucesso acrescenta DOCX ou TXT de **texto melhorado** sem alterar os arquivos
originais.

### CM-RF-04 — falha independente

Falha, timeout ou cancelamento da melhoria não apaga nem invalida o original. O trabalho
deve distinguir **Transcrição pronta** de **Melhoria não concluída** e oferecer retomada
explícita somente da etapa editorial.

### CM-RF-05 — formatos

SRT e VTT continuam derivados exclusivamente do original. A melhoria só produz DOCX e TXT
adicionais.

## Validação editorial

### CM-RV-01 — remover guard semântico

O runtime não deve rejeitar uma resposta por diferenças de:

- números, datas, valores ou percentuais;
- falantes;
- indicações de inaudível;
- tamanho relativo do texto;
- pontuação ou paragrafação.

`validate_editorial_result` deve ser removido ou reduzido a verificações técnicas. Não
devem ser acrescentados mascaramento, placeholders ou reparo heurístico de conteúdo.

### CM-RV-02 — verificações técnicas

Uma resposta editorial só é tecnicamente utilizável quando:

- contém texto não vazio e decodificável;
- está associada ao bloco solicitado;
- foi persistida atomicamente;
- pode participar de uma montagem completa, única e ordenada.

Essas verificações não alegam avaliar fidelidade factual.

### CM-RV-03 — contrato no prompt

O prompt continua orientando o modelo a não resumir, traduzir, inventar ou mudar nomes,
números, falantes e marcações. O texto transcrito continua sendo tratado como dado, não
instrução.

### CM-RV-04 — aviso ao usuário

A interface e a Ajuda devem manter aviso claro de que a melhoria pode errar e que nomes,
números e trechos pouco claros devem ser conferidos contra o original.

### CM-RV-05 — avaliação de versão

Preservação de conteúdo é critério de avaliação antes da liberação, não condição
bloqueante durante cada trabalho. O conjunto de avaliação deve observar resumo, omissão,
acréscimo, números, nomes e falantes.

### CM-RV-06 — erro legado

`EditorialValidationError` de trabalhos ou caminhos legados deve ser classificado antes de
`ValueError`. A mensagem não pode mencionar arquivo; deve informar que o original está
preservado.

## Tentativas, custo e retomada

### CM-RP-01 — tentativa antes do efeito

Antes de cada chamada remota, persistir tentativa com ID estável, unidade, provedor,
modelo, horários e estado `running`.

### CM-RP-02 — estados

Uma tentativa nova deve distinguir:

- `running`;
- `accepted`;
- `failed`;
- `cancel_requested`;
- `cancelled`;
- `remote_ambiguous`.

`accepted` exige texto e artefato persistido. `remote_ambiguous` significa que o app não
sabe se o provedor concluiu ou cobrou a chamada.

O leitor continua aceitando `rejected` legado sem tratá-lo como unidade concluída.

### CM-RP-03 — sem retry automático

Falha de rede, timeout, resposta vazia, cancelamento, tentativa ambígua e registro
`rejected` legado não iniciam outra chamada automaticamente.

### CM-RP-04 — retomada explícita

Retomar reutiliza blocos aceitos e envia somente unidades ausentes. Uma unidade ambígua ou
rejeitada por versão antiga exige confirmação de possível nova cobrança.

### CM-RP-05 — custo

Custos conhecidos de tentativas aceitas e legadas são preservados. Tentativa ambígua fica
identificada como custo possivelmente incompleto e não recebe valor inventado.

### CM-RP-06 — escrita atômica

Resposta, artefato e estado devem ser conciliáveis após interrupção. Um resultado aceito e
salvo não pode ser reenviado porque o processo parou antes de atualizar o manifesto.

### CM-RP-07 — compatibilidade

Manifestos 0.1.1 continuam legíveis. Trabalho antigo `running/improving` sem registro de
tentativa fica pausado e exige retomada explícita.

## Erros públicos

### CM-RE-01 — origem correta

Falha editorial, falha de arquivo, falha de exportação, credencial, timeout e cancelamento
devem ter categorias distintas.

### CM-RE-02 — detalhes seguros

Persistir código da etapa, tentativa, provedor, bloco, horário e uso quando disponíveis.
Não persistir chave, cabeçalho HTTP, traceback ou resposta editorial em log global.

### CM-RE-03 — mensagem útil

Quando a melhoria falhar, a mensagem principal deve confirmar que a transcrição original
está pronta e indicar se a melhoria pode ser retomada.

## Cancelamento e isolamento

### CM-RC-01 — estado imediato

Ao clicar **Cancelar**, o trabalho entra imediatamente em `cancelling` ou
`cancel_requested`. O botão deixa de aceitar cliques repetidos.

### CM-RC-02 — limite

O worker recebe até cinco segundos para encerrar cooperativamente. Depois, o controlador
encerra sua fronteira descartável e marca o trabalho como `cancelled`.

### CM-RC-03 — processo descartável

Transcrição, melhoria e exportação devem executar fora do processo da GUI numa unidade que
possa ser encerrada. Matar o `QThread` da aplicação não satisfaz este requisito.

### CM-RC-04 — chamada em voo

Se o cancelamento interromper chamada remota sem resposta confirmada, persistir
`remote_ambiguous`. Nenhuma nova etapa do trabalho cancelado pode começar.

### CM-RC-05 — preservação

Cancelar preserva legendas, chunks, original, arquivos já exportados, blocos editoriais
aceitos, custos e diagnósticos.

### CM-RC-06 — fila liberada

Depois do encerramento cooperativo ou forçado, a tarefa ativa fica vazia, `busy` fica falso
e uma fronteira limpa fica pronta.

### CM-RC-07 — nova transcrição

Um novo trabalho deve iniciar e concluir depois de cancelar um fake que ignora token,
fechamento de cliente e timeout cooperativo.

### CM-RC-08 — itens aguardando

Preservar o comportamento 0.1.1 de remover itens aguardando ao cancelar a execução ativa e
informar essa remoção. Controles individuais de fila ficam fora do escopo.

### CM-RC-09 — fechamento

Fechar o app não pode aguardar indefinidamente nem destruir um `QThread` vivo. O estado
atômico deve continuar acessível na próxima execução.

## Timeout

### CM-RT-01 — configuração central

Timeouts de conexão e leitura devem ser constantes nomeadas, distintos do deadline de
cancelamento e testados com transporte ou relógio falso.

### CM-RT-02 — editorial

Uma chamada editorial sem resposta não pode esperar 1.800 segundos. O limite inicial é
cinco minutos; ao expirar, a melhoria fica retomável e o original continua disponível.

### CM-RT-03 — cancelamento prioritário

O botão **Cancelar** não espera o timeout editorial. Seu limite de cinco segundos funciona
mesmo se a pilha HTTP ignorar fechamento.

## Progresso e interface

### CM-RI-01 — progresso geral

O progresso geral considera aquisição ou transcrição, exportação original, melhoria
solicitada e exportação melhorada. Só chega a 100% quando o estado apresentado é terminal.

### CM-RI-02 — progresso da etapa

Etapa, unidades concluídas e total de unidades são informados separadamente. Durante
melhoria de nove blocos, a interface mostra a contagem editorial, não `1 de 1` da legenda.

### CM-RI-03 — cancelando

Durante `cancelling`, o último percentual pode ficar estável, mas o texto deve indicar
cancelamento. Depois do limite, cartão e Histórico mostram `cancelled`.

### CM-RI-04 — início habilitado

Botão e atalho de iniciar ficam habilitados quando o cancelamento termina e a nova
fronteira está pronta.

### CM-RI-05 — estado composto

A interface deve conseguir mostrar **Transcrição pronta** junto de **Melhoria em
andamento**, **Melhoria não concluída** ou **Texto melhorado pronto**, sem depender apenas
de cor.

## Compatibilidade, segurança e restrições

- O fluxo sem **Melhorar com IA** continua funcional.
- Legendas automáticas e humanas mantêm o normalizador atual.
- Testes automatizados não fazem rede nem chamada paga.
- A chave não aparece em argumentos de processo, manifesto, log ou QML.
- A solução funciona no código-fonte e nos pacotes macOS e Windows.
- Esta tarefa não inclui limpeza ampla do worker legado.
