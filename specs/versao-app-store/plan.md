# Plano — próxima versão para a Mac App Store

## Encerramento da frente App Store — 29 de agosto de 2026

O autor descartou a Mac App Store. Este plano inteiro passa a histórico, sem execução
automática das tarefas. A direção vigente está em
[distribuição comercial](../distribuicao-comercial/spec.md), com tradução e pacotes Mac/Windows.
Não retirar URLs nem implementar fila/paralelismo com base neste plano anterior.

## Regra de execução

Cada linha da tabela é uma unidade de trabalho própria, com branch, diff, critérios e
validação independentes. Não se deve combinar tarefas apenas porque pertencem à mesma
versão. A próxima tarefa começa somente quando suas dependências estiverem estáveis.

Os modelos abaixo estão disponíveis na data desta spec. Se uma combinação deixar de
estar disponível, usar a alternativa mais próxima da mesma família e esforço e registrar
o ajuste na seção da tarefa antes de executar. Uma troca que aumente materialmente custo
ou risco exige confirmação do usuário.

## Mapa de tarefas

| ID | Resultado único | Branch proposta | Modelo | Esforço | Estado | Depende de |
| --- | --- | --- | --- | --- | --- | --- |
| T00 | specs e inventário editorial | `codex/especificar-versao-app-store` | `gpt-5.6-sol` | xhigh | aguardando aprovação editorial | — |
| T01 | texto comercial, Ajuda e avisos | `codex/app-store-textos-licencas` | `gpt-5.6-terra` | high | pendente | T00, português aprovado |
| T02 | catálogo de idiomas por provedor/modelo | `codex/idiomas-por-provedor` | `gpt-5.6-terra` | high | pendente | T00 |
| T03 | fila persistente de múltiplas fontes | `codex/fila-transcricoes` | `gpt-5.6-sol` | xhigh | pendente | T00 |
| T04 | agendador paralelo limitado por recursos | `codex/paralelismo-por-memoria` | `gpt-5.6-sol` | xhigh | pendente | T03 |
| T05 | infraestrutura de internacionalização | `codex/internacionalizar-gui` | `gpt-5.6-sol` | high | pendente | T00, português aprovado |
| T06 | traduções e revisão de layout | `codex/traduzir-gui` | `gpt-5.6-sol` | high | pendente | T05, variante chinesa decidida |
| T07 | harness completo de GUI e DOCX | `codex/validar-gui-docx` | `gpt-5.6-sol` | xhigh | pendente | T02–T06 |
| T08 | edição sandboxed e autocontida | `codex/mac-app-store-sandbox` | `gpt-5.6-sol` | xhigh | descartada — decisão do autor | T01–T06, decisão sobre URL e Qt |
| T09 | metadados, privacidade e candidato TestFlight | `codex/mac-app-store-candidato` | `gpt-5.6-sol` | high | descartada — decisão do autor | T07–T08 |
| T10 | submissão e verificação da versão | `codex/mac-app-store-release` | `gpt-5.6-sol` | high | descartada — decisão do autor | T09 |

T01 possui uma decisão jurídica humana que o modelo não substitui. T08 e T10 permanecem
bloqueadas até essa evidência existir.

## T00 — fechar especificação e português

### Objetivo

Entregar um contrato revisável sem mudar o comportamento do app.

### Passos

1. Revisar `spec.md`, `requirements.md`, `plan.md` e `validation.md`.
2. Entregar `textos-gui-pt-BR.md` ao autor.
3. Registrar decisões pendentes e aceitar edições do texto.
4. Sincronizar requisitos e inventário depois da aprovação editorial.
5. Revisar diff e confirmar que não há mudança de código/artefato.

### Aceitação

- todos os oito pedidos estão mapeados;
- cada implementação tem branch/modelo/esforço;
- o inventário identifica texto atual, texto proposto e mensagens dinâmicas;
- nenhuma chamada paga, build ou alteração externa foi feita.

## T01 — comunicação, custos e licença

### Objetivo

Aplicar somente as mudanças editoriais aprovadas, mantendo a licença MIT e distinguindo-a
do preço da distribuição oficial.

### Passos

1. Auditar dependências e confirmar a continuidade de `LICENSE`/metadados MIT.
2. Atualizar Sobre, Ajuda, README, metadados e avisos de primeira parte sem retirar a MIT.
3. Remover o parágrafo dirigido ao desenvolvedor das duas cópias sincronizadas.
4. Substituir tabelas de preços por explicação e links oficiais.
5. Preservar estimativa operacional com rótulo e proveniência adequados.
6. Atualizar testes de catálogo e buscas por alegações antigas.
7. Revisar somente o diff editorial/licenciamento e provar que não criou restrição
   adicional ao código MIT.

### Aceitação

- `AS-ED-*`, `AS-LI-*`, `AS-AJ-*` passam;
- licenças históricas continuam recuperáveis;
- o bundle de teste contém avisos completos e sincronizados;
- não há texto interno de build na janela de avisos.

## T02 — idiomas aceitos

### Objetivo

Substituir a lista QML fixa por uma fonte única de capacidades e mapeamentos reais.

### Passos

1. Caracterizar payloads atuais de cada adaptador/modelo.
2. Criar o registro tipado com fontes e datas.
3. Implementar mapeadores OpenAI/Gemini e filtro da UI.
4. Tratar mudança incompatível e detecção automática.
5. Cobrir cada idioma do registro com testes locais de contrato.
6. Realizar uma pequena amostra real somente sob orçamento aprovado.

### Aceitação

- nenhum código fora do registro chega ao provedor;
- catalão não aparece para Gemini sem nova evidência;
- hebraico usa código correto em cada camada;
- testes provam sincronismo entre catálogo, QML/backend e payload.

## T03 — fila persistente

### Objetivo

Representar vários arquivos/endereços como trabalhos independentes e recuperáveis,
mantendo uma única execução ativa durante esta tarefa.

### Passos

1. Criar testes de caracterização do executor atual e `JobStore`.
2. Definir entidades de fila, estados e fotografia das opções.
3. Implementar lote de arquivos e, na variante autorizada, URLs em múltiplas linhas.
4. Persistir fila e estados sem alterar o contrato de tentativa remota.
5. Implementar ações por item, duplicatas e reserva atômica de nomes.
6. Adaptar Histórico/Transcrever e acessibilidade.
7. Validar reinício, cancelamento e término fora de ordem com executor serial falso.

### Aceitação

- vários itens persistem e avançam em FIFO;
- ainda há no máximo um processo ativo, isolando o escopo de T04;
- cancelar/remover um item não altera os demais;
- nenhuma chamada incerta é repetida automaticamente.

## T04 — paralelismo por recursos

### Objetivo

Permitir vários trabalhos ativos com admissão conservadora por memória, disco e provedor.

### Passos

1. Instrumentar RSS/pico dos estágios sem registrar conteúdo privado.
2. Medir fixtures curtas/longas em Macs de 8, 16 e 32 GB ou equivalentes controlados.
3. Especificar reserva, estimador, teto absoluto e limites por provedor.
4. Generalizar o controlador para processos independentes por job.
5. Tornar persistência e reserva de saídas seguras entre processos.
6. Implementar estados `aguardando_memoria` e observabilidade sanitizada.
7. Testar pressão, término fora de ordem, cancelamento individual e saída global.

### Aceitação

- ao menos dois trabalhos avançam em paralelo quando há margem;
- nenhuma admissão ocorre abaixo da reserva medida;
- reduzir memória disponível impede novos processos, sem corromper ativos;
- encerrar o app não deixa filhos;
- comportamento em 8 GB é seguro mesmo que resulte em execução serial.

## T05 — infraestrutura de internacionalização

### Objetivo

Extrair todo texto traduzível para catálogos Qt com IDs/contextos estáveis.

### Passos

1. Conciliar os literais do código com `textos-gui-pt-BR.md`.
2. Definir convenção de IDs, placeholders, plurais e contexto.
3. Converter QML, Python, Ajuda e notificações.
4. Criar seleção/persistência do idioma da interface, separada do conteúdo.
5. Gerar catálogo `pt-BR`, fallback e pseudolocale.
6. Criar teste que falha com novo literal de primeira parte não catalogado.

### Aceitação

- cada entrada do inventário aponta para um ID;
- nenhuma mensagem pública importante fica fora do mecanismo;
- trocar locale não muda trabalhos existentes;
- pseudolocale expõe expansão, placeholders e plurais corretamente.

## T06 — traduções

### Objetivo

Produzir e revisar inglês, francês, espanhol, alemão, russo, japonês e chinês aprovado,
sem alterar comportamento.

### Passos

1. Congelar o hash do português aprovado.
2. Traduzir preservando termos técnicos, placeholders, links e nomes próprios.
3. Fazer segunda revisão por idioma, com glossário e back-check de frases críticas.
4. Inspecionar layouts, quebras, acessibilidade, atalhos e busca da Ajuda.
5. Marcar como pendente qualquer ambiguidade editorial; não inventar decisão.
6. Incluir todos os catálogos no mesmo bundle.

### Aceitação

- 100% dos IDs obrigatórios têm tradução revisada;
- nenhum placeholder/link foi perdido;
- layouts mínimos funcionam em todos os locales;
- licenças de terceiros permanecem em suas versões oficiais.

## T07 — validação da GUI e DOCX

### Objetivo

Transformar a matriz de `validation.md` em testes automatizados e roteiro manual do pacote.

### Passos

1. Criar doubles determinísticos para cada estado e erro.
2. Exercitar rotas, menus, diálogos, foco, teclado, scroll e acessibilidade.
3. Executar fluxos curtos e longos, fila e paralelismo sob falhas injetadas.
4. Gerar matriz de DOCX Unicode/original/melhorado/tempos/falantes.
5. Validar OPC, `python-docx`, LibreOffice e Word real.
6. Registrar screenshots, logs sanitizados e divergências.

### Aceitação

- cada célula obrigatória da matriz tem evidência;
- nenhum DOCX pede reparo;
- comparação semântica prova que não houve mistura entre jobs;
- testes offline têm zero chamadas pagas.

## T08 — sandbox e bundle da loja

### Objetivo

Produzir uma edição autocontida que rode sob App Sandbox e possa ser assinada para a loja.

### Pré-condições

- retomada explicitamente autorizada pelo autor após a suspensão de 29/08/2026;
- decisão sobre a variante local ou de fontes autorizadas, conforme `AS-MS-05`;
- licença comercial Qt ou parecer jurídico documentado;
- licença/configuração do FFmpeg decidida;
- política de privacidade preliminar disponível.

### Passos

1. Criar configuração de build da App Store separada da Developer ID.
2. Incorporar e inventariar dependências permitidas.
3. Implementar entitlements mínimos e security-scoped bookmarks.
4. Adaptar acesso do processo filho, Keychain e paths do container.
5. Remover dependências/recursos proibidos da variante.
6. Gerar e validar privacy manifest.
7. Assinar de dentro para fora com identidade de desenvolvimento/distribuição adequada.
8. Testar em usuário limpo, sandbox real, sem Homebrew/Python/Qt instalados.

### Aceitação

- `AS-MS-01` a `AS-MS-10` passam;
- inventário prova bundle autocontido e licenças;
- relançamento acessa apenas bookmarks válidos e revogáveis;
- Keychain, fila, helpers, rede e encerramento funcionam no pacote.

## T09 — candidato e TestFlight

### Objetivo

Construir um candidato rastreável, completar metadados/políticas e obter processamento
válido no App Store Connect/TestFlight.

### Passos

1. Definir versão/build, preço, territórios, categoria e locales da ficha.
2. Completar política, App Privacy, export compliance e contato de revisão.
3. Criar screenshots/descrições a partir do pacote aprovado.
4. Construir em checkout limpo, assinar e gerar formato de upload aceito.
5. Validar e enviar uma vez; guardar identificador/log.
6. Corrigir somente problemas concretos do processamento.
7. Distribuir a grupo TestFlight autorizado e executar o roteiro real.

### Aceitação

- build processado sem erro bloqueante;
- TestFlight instala e executa a matriz crítica;
- ficha e comportamento são coerentes;
- nenhum segredo ou mídia privada está no upload/evidência.

## T10 — submissão e encerramento

### Objetivo

Submeter o candidato aprovado, responder honestamente à revisão e verificar a versão
publicada.

### Passos

1. Congelar commit, build, hashes, textos e notas de revisão.
2. Submeter o build sem criar nova variante funcional.
3. Responder perguntas com evidências, sem ocultar BYOK, provedores ou fluxo de mídia.
4. Se rejeitado, abrir tarefa limitada ao motivo; não enviar correções especulativas.
5. Depois da aprovação, verificar ficha, preço, idiomas, instalação, recibo, abertura e
   atualização pela loja.
6. Preencher `validation.md` e encerrar a release.

### Aceitação

- status aprovado/disponível nos territórios escolhidos;
- bytes/build conferem com o candidato;
- compra e instalação funcionam sem licença adicional;
- documentação registra limitações e decisões finais.

## Estratégia de integração

```text
T00
 ├─ T01 ───────────────┐
 ├─ T02 ───┐           │
 ├─ T03 ─ T04 ─────────┤
 └─ T05 ─ T06 ─────────┤
                       ├─ T07
                       └─ T08
                          └─ T09 ─ T10
```

T03 deve ser integrado antes de T04. T05 pode avançar paralelamente às tarefas de fila,
mas conflitos QML precisam ser resolvidos por rebase consciente e nova validação. Uma
integração só entra na branch da versão quando seus testes e specs estiverem verdes.

## Orçamento de validação

### Sem custo

- suíte, lints, tipos, QML offscreen, fixtures de mídia e provedores falsos;
- benchmark local, DOCX estrutural, LibreOffice e screenshots;
- validação de bundle, assinatura local e sandbox antes do upload.

### Custo/limite pré-aprovado necessário

- chamadas reais propostas: até 40;
- duração por fixture: 5–8 segundos;
- teto total proposto: US$ 1,00;
- uploads App Store Connect: um por hipótese/correção concreta;
- builds completos: um candidato por mudança que altere bytes do bundle.

Nenhuma chamada paga está autorizada apenas pela existência deste plano.

## Condições de parada

- frente App Store suspensa, sem decisão explícita de retomada;
- texto português ainda não aprovado para T01/T05/T06;
- divergência entre código, specs ou catálogo de idiomas;
- ausência de decisão sobre URL antes de T08;
- licença Qt/FFmpeg sem evidência suficiente;
- cálculo de memória sem benchmark representativo;
- corrida/corrupção de manifesto ou retry pago automático;
- DOCX que abre com reparo ou mistura conteúdo;
- segredo/dado pessoal em log, bundle ou evidência;
- pacote que depende de ferramenta externa;
- falha de sandbox, assinatura ou processamento no App Store Connect;
- rejeição da Apple que exija mudança de produto não prevista.
