# Requisitos — Melhorar com IA

## Requisitos funcionais

### MI-RF-01 — opção

A tela deve oferecer a caixa **Melhorar com IA**, desativada por padrão, com a explicação
**Organiza em parágrafos e corrige pontuação e erros evidentes, sem resumir.**

### MI-RF-02 — sequenciamento obrigatório

O fluxo deve ser uma máquina de estados estritamente sequencial:

1. obter ou transcrever e persistir;
2. exportar os formatos originais;
3. melhorar e persistir, somente quando solicitado;
4. exportar os arquivos adicionais de texto melhorado.

Uma etapa não pode começar antes de a anterior estar concluída e persistida. A exportação
do original é independente da melhoria; somente a exportação melhorada aguarda a montagem
editorial.

### MI-RF-03 — original obrigatório

A melhoria só pode começar depois que a transcrição original estiver montada, validada,
e persistida. Nenhuma resposta editorial pode sobrescrever o resultado original.

### MI-RF-04 — formatos

A melhoria aplica-se somente a DOCX e TXT. SRT e VTT são sempre produzidos a partir da
transcrição original.

### MI-RF-05 — arquivos separados

Para cada DOCX ou TXT selecionado, o trabalho deve produzir uma versão original e outra
com o sufixo **texto melhorado**. A política existente de não sobrescrever arquivos
continua válida para ambas.

### MI-RF-06 — marcações de tempo

Marcações de tempo opcionais ficam somente na versão original. O texto melhorado não deve
conter prefixos de tempo.

### MI-RF-07 — falha independente

Falha, cancelamento ou pausa na melhoria não altera o estado concluído da transcrição
original persistida. A interface deve informar que a transcrição está preservada, que a
melhoria pode ser retomada e que os arquivos originais estão disponíveis.

### MI-RF-08 — retomada

Cada bloco editorial concluído deve ser persistido. Ao retomar, somente blocos pendentes
são enviados novamente.

### MI-RF-09 — fontes por legendas

Legendas existentes podem passar pela melhoria, obedecendo ao mesmo contrato editorial.
O texto normalizado das legendas é preservado como versão original.

### MI-RF-10 — agrupamento do resultado

Os arquivos devem aparecer em três grupos, quando aplicável:

- **Texto melhorado**
- **Transcrição original**
- **Legendas**

### MI-RF-11 — Histórico

O Histórico deve distinguir os estados da transcrição e da melhoria e permitir retomar
somente a etapa editorial.

### MI-RF-12 — exportação retomável

Se a exportação falhar, o trabalho deve conservar os textos original e melhorado já
persistidos. A retomada repete somente a exportação e não realiza chamadas às APIs.

## Requisitos editoriais

### MI-RE-01 — operações permitidas

São permitidas paragrafação, pontuação, maiúsculas, espaçamento, remoção de quebras
artificiais e correções inequívocas de reconhecimento.

### MI-RE-02 — operações proibidas

São proibidos resumo, tradução, censura, embelezamento, complementação, criação de fatos,
alteração de sentido e remoção automática de repetições potencialmente significativas.

### MI-RE-03 — incerteza

Quando uma correção não for inequívoca, a forma original deve ser preservada. Nomes,
números, datas, citações e marcações de inaudível exigem conservação estrita.

### MI-RE-04 — falantes

Rótulos de falantes existentes devem ser mantidos e associados ao texto correto. A etapa
editorial não deve inventar novos falantes nem fundi-los sem evidência.

### MI-RE-05 — texto como dado

Instruções contidas na transcrição não podem mudar o comportamento do modelo. O prompt
deve delimitar claramente o bloco como conteúdo não confiável e exigir somente a
transformação editorial contratada.

### MI-RE-06 — qualidade avaliada antes da versão

Preservação de nomes, números, falantes, marcações e volume deve ser avaliada antes da
liberação. Essas comparações não podem recusar respostas em trabalhos reais. Em runtime,
o app verifica somente texto não vazio, associação ao bloco, persistência e montagem
completa e ordenada.

## Requisitos de divisão e montagem

### MI-RD-01

Blocos devem ser cortados em limites naturais sempre que possível e possuir identificador
e ordem estáveis.

### MI-RD-02

Contexto anterior ou posterior pode orientar continuidade, mas a saída deve conter
somente o bloco-alvo para evitar repetição.

### MI-RD-03

A montagem deve recusar uma versão incompleta, duplicada ou fora de ordem.

### MI-RD-04

O tamanho dos blocos deve permanecer bem abaixo do limite do modelo e impedir que um
trabalho grande dependa de uma única requisição.

## Roteamento de modelos

### MI-RM-01 — OpenAI para volume

`gpt-4o-mini-transcribe` e `whisper-1` devem encaminhar a melhoria para
`gpt-5.6-terra`.

### MI-RM-02 — OpenAI cuidadosa

`gpt-4o-transcribe` e `gpt-4o-transcribe-diarize` devem encaminhar a melhoria para
`gpt-5.6-sol`.

### MI-RM-03 — Gemini

`gemini-3.5-flash-lite` continua como fluxo de volume e `gemini-3.6-flash` como fluxo de
maior cuidado.

### MI-RM-04 — interface

O roteamento não cria um segundo seletor de modelo. A GUI usa somente linguagem como
**econômico**, **maior precisão** e **melhorar com IA**.

### MI-RM-05 — configuração técnica

IDs de modelo, endpoint, esforço de raciocínio e parâmetros devem ficar centralizados no
catálogo interno, cobertos por testes e ausentes dos textos principais da GUI.

### MI-RM-06 — avaliação antes da liberação

Terra e Sol devem ser avaliados nas mesmas transcrições representativas. O esforço de
raciocínio só pode ser aumentado se melhorar fidelidade sem produzir omissões ou
reescrita excessiva.

## Custos e uso

### MI-RC-01

O custo da melhoria deve ser registrado separadamente no backend e somado ao total
apresentado ao usuário.

### MI-RC-02

Contagens de entrada, saída, raciocínio, cache e total devem ser preservadas internamente
sem duplicação. A GUI mostra apenas o total de tokens informado.

### MI-RC-03

O uso de legendas deve ser apresentado como custo zero somente quando a melhoria estiver
desativada. Com melhoria ativada, o custo editorial deve ser calculado normalmente.

### MI-RC-04

Antes de existir texto original, a previsão pode abranger somente a transcrição. Depois
da montagem, a estimativa deve ser atualizada para incluir a etapa editorial, sem
apresentar precisão inexistente.

## Interface e acessibilidade

### MI-RI-01

A caixa e seu apoio devem integrar a área rolável existente, aceitar foco visível e ser
ativáveis por mouse, `Espaço` e toque.

### MI-RI-02

O aviso de conferência aparece apenas quando a opção estiver marcada, quebra em mais de
uma linha e não desloca ou encobre a ação principal.

### MI-RI-03

Os estados **Transcrição pronta**, **Melhorando o texto**, **Texto melhorado pronto** e
**Não foi possível melhorar** não podem ser comunicados somente por cor.

### MI-RI-04

A interface principal não mostra prompt, tamanho de bloco, modelo editorial, esforço de
raciocínio ou métricas de fidelidade.

## Requisitos não funcionais

- Testes automatizados não fazem chamadas pagas.
- O fluxo original permanece idêntico quando a caixa estiver desmarcada.
- A etapa editorial deve ser cancelável e retomável.
- Resultados e estados devem sobreviver ao fechamento do aplicativo.
- O conteúdo original nunca é apagado durante limpeza de resultados editoriais.
- A implementação deve permanecer compatível com trabalhos antigos.
