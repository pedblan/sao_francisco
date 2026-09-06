# Especificação — próxima versão para a Mac App Store

**Estado:** plano histórico substituído; Mac App Store descartada pelo autor

**Data de referência:** 13 de agosto de 2026

**Revisão de viabilidade 5.2.3:** 29 de agosto de 2026

**Versão:** a definir antes da implementação

**Plataforma desta entrega:** macOS pela Mac App Store

**Branch desta especificação:** `codex/especificar-versao-app-store`

## Decisão de continuidade — 29 de agosto de 2026

Depois da análise inicial de suspensão, o autor decidiu: “Vamos deixar a App Store para
lá.” A direção vigente está em
[`distribuicao-comercial/spec.md`](../distribuicao-comercial/spec.md): traduzir e preparar
venda fora da Mac App Store, para Mac e Windows, mantendo MIT.

O restante deste documento é histórico, não autorização nem plano ativo. T08–T10 foram
descartadas; fila/paralelismo não integram a próxima versão reduzida. O inventário
editorial é preservado para revisão, sem aprovação presumida. Nenhuma função do app foi
retirada ou renomeada. Não houve build, upload ou submissão.

## Objetivo

Preparar uma nova versão paga do São Francisco para distribuição pela Mac App Store,
preservando privacidade, transcrições recuperáveis e o original produzido pelo provedor.
A versão, cujo código continua aberto sob a licença MIT, deve acrescentar fila de
trabalhos com paralelismo limitado pelos recursos do computador, internacionalização e
validação ampla da interface e dos DOCX.

A especificação também separa o que é uma mudança de produto do que depende de revisão
jurídica, de infraestrutura da App Store ou de uma decisão editorial do autor. Nenhum
gate jurídico ou de revisão da Apple será tratado como aprovado por inferência.

## Rastreabilidade do pedido

| Pedido | Contrato principal | Validação |
| --- | --- | --- |
| 1. frase nova, app pago e MIT | `AS-ED-01` a `AS-ED-03`, `AS-LI-03` | T01 e busca de coerência |
| 2. retirar nota interna dos avisos | `AS-LI-01` e `AS-LI-06` | cópias sincronizadas e bundle |
| 3. remover tabela de preços | `AS-AJ-01` a `AS-AJ-03` | Ajuda, links e notas de revisão |
| 4. validar idiomas OpenAI/Gemini | `AS-ID-01` a `AS-ID-06` | contratos estáticos e amostra limitada |
| 5. fila e paralelismo por RAM | `AS-FI-*` e `AS-PA-*` | matriz Q01–Q12 e perfis M08–M32 |
| 6. GUI, fluxos e DOCX | `AS-DO-*` e `AS-TE-*` | matrizes G01–G16, F/L e D01–D07 |
| 7. texto e traduções | `AS-IN-*` | inventário, T05/T06 e pseudolocale |
| 8. Mac App Store | `AS-MS-*`, `AS-PR-*` e `AS-LI-04/05` | sandbox, TestFlight e App Review |

## Resultado de produto

A pessoa deve poder:

- comprar o aplicativo por um preço inicial mínimo definido no App Store Connect;
- adicionar vários arquivos a uma fila visível e, somente na variante autorizada,
  vários endereços;
- deixar mais de uma transcrição avançar ao mesmo tempo quando houver memória disponível;
- acompanhar e cancelar cada trabalho sem perder partes concluídas;
- escolher somente idiomas compatíveis com o provedor e o modelo selecionados;
- entender que OpenAI e Gemini têm cobrança, preços e termos próprios;
- consultar a interface e a Ajuda no idioma escolhido;
- abrir DOCX regulares, com conteúdo e estrutura equivalentes à transcrição preservada.

## Decisões já tomadas

### Comunicação e preço

- A frase de divulgação da tela Sobre passa a ser:

  > São Francisco é um projeto independente que respeita sua privacidade. Se você quiser
  > valorizar o trabalho, leia os livros e conheça os outros projetos na minha página de
  > autor.

- A edição da Mac App Store será paga desde o download, sem assinatura, licença própria,
  chave de ativação ou desbloqueio interno do São Francisco.
- O código-fonte do São Francisco continuará publicado sob a licença MIT. O preço compra
  a distribuição oficial pela loja; não retira os direitos concedidos pela licença.
- O preço não será codificado no aplicativo; será configurado no App Store Connect.
- O parágrafo dirigido ao desenvolvedor no fim dos avisos de terceiros será retirado da
  cópia exibida e das duas fontes sincronizadas do inventário.

### Custos de API

A Ajuda não exibirá tabelas com preços unitários por token ou minuto. A Apple não declara
uma proibição específica contra mencionar esses valores, mas a tabela fica obsoleta e
pode confundir o preço do aplicativo com a cobrança externa. A versão proposta deve:

- manter apenas a explicação de que a cobrança pertence ao provedor;
- manter estimativas de uso durante/depois do trabalho, quando tecnicamente confiáveis,
  sempre identificadas como aproximadas;
- apontar para as páginas oficiais de preços da
  [OpenAI](https://developers.openai.com/api/docs/pricing) e do
  [Gemini](https://ai.google.dev/gemini-api/docs/pricing);
- apontar para os painéis oficiais de uso/faturamento, sem vender créditos nem prometer
  valores dentro do aplicativo;
- explicar nas notas para a revisão que a chave autentica uma conta mantida diretamente
  pelo usuário no provedor e não desbloqueia uma modalidade paga do São Francisco.

Essa solução reduz o risco, mas não garante aprovação. Se a Apple entender o fluxo de
BYOK como compra externa de funcionalidade consumida no app, a submissão deverá parar e
ser reavaliada, sem contornar a revisão.

### Idiomas

O código canônico de idioma será separado do código enviado a cada API. A lista será
derivada de um registro de capacidades versionado por provedor e modelo, e não ficará
mais escrita diretamente no QML.

Na documentação oficial consultada:

- a OpenAI aceita dicas de idioma nos modelos de transcrição, com formato dependente do
  endpoint/modelo;
- o Gemini relaciona os idiomas que suporta, mas usa `iw` para hebraico na lista publicada;
- catalão (`ca`) aparece na lista atual da interface e é aceito pelo Whisper, mas não
  consta na lista oficial de idiomas do Gemini consultada;
- `he` continuará sendo o código canônico interno de hebraico e será convertido para a
  forma exigida pelo adaptador, quando necessário.

Ao trocar de provedor ou modelo, uma seleção incompatível deve voltar para **Detectar
automaticamente** com aviso claro. O aplicativo não enviará silenciosamente um código
sem suporte documentado.

### Texto e traduções

O arquivo [textos-gui-pt-BR.md](textos-gui-pt-BR.md) é o inventário editorial desta
versão. Primeiro o autor revisará e aprovará o português. Somente depois serão produzidas
as traduções para:

- inglês (`en`);
- francês (`fr`);
- espanhol (`es`);
- alemão (`de`);
- russo (`ru`);
- japonês (`ja`);
- chinês simplificado (`zh-Hans`), provisoriamente, até confirmação explícita da variante.

Todos os idiomas distribuídos devem estar no mesmo bundle, como exige a regra da Mac App
Store. Português do Brasil (`pt-BR`) será a fonte e o fallback.

## Fila e paralelismo

### Unidade de fila

Cada arquivo ou endereço válido cria um trabalho independente com seu próprio ID,
workspace, manifesto, tentativas remotas e conjunto de saídas. As opções comuns escolhidas
no formulário são fotografadas no momento da inclusão; alterações posteriores afetam
somente novos itens.

A primeira entrega da fila inclui:

- inclusão de vários arquivos por seletor e arrastar/soltar;
- inclusão de vários endereços, um por linha;
- eliminação explícita de duplicatas exatas antes de cobrar qualquer chamada;
- lista com os estados aguardando, preparando, executando, cancelando, concluído, pausado
  e falhou;
- cancelamento de um item aguardando ou ativo;
- remoção de itens ainda não iniciados e limpeza dos concluídos da visualização;
- preservação de resultados quando trabalhos terminarem fora da ordem de inclusão.

Reordenação manual, prioridades, execução agendada e paralelismo entre partes do mesmo
arquivo ficam fora desta versão.

### Admissão por recursos

O paralelismo será automático, com um teto configurável pelo usuário. O agendador só
inicia um trabalho quando todos estes limites permitirem:

1. memória disponível acima de uma reserva de segurança medida;
2. estimativa conservadora do pico do novo trabalho, calibrada por tipo e duração da
   mídia;
3. teto de trabalhos simultâneos;
4. limite de chamadas concorrentes do provedor/modelo;
5. espaço em disco suficiente para workspace e saídas.

Se a memória cair abaixo do limite durante a execução, o aplicativo não mata chamadas
remotas em andamento: deixa de admitir novos trabalhos, mostra **Aguardando memória** e
retoma a fila quando houver margem. Valores numéricos de reserva, estimativa e teto não
serão escolhidos por intuição; serão fixados após medição em Macs de referência de 8, 16
e 32 GB. O modo automático deve ser o padrão seguro.

Cada processo filho deve ser registrado e encerrado ao sair. O agendador não pode permitir
corrida de nomes de saída, reuso de workspace, gravação concorrente no mesmo manifesto ou
retry automático de chamada potencialmente paga.

## Compatibilidade com a Mac App Store

A edição da loja é um alvo de empacotamento próprio, não uma simples mudança da assinatura
Developer ID atual.

### Requisitos técnicos mínimos

- App Sandbox habilitado e entitlements mínimos.
- Acesso de leitura/escrita concedido por seletores do sistema.
- Security-scoped bookmarks para retomar fontes e destinos depois de reiniciar o app.
- Direito de rede somente como cliente para APIs e, se aprovado, fontes autorizadas.
- Chaves armazenadas no Keychain compatível com a identidade sandboxed.
- App único, autocontido e submetido com tecnologias do Xcode/App Store Connect.
- FFmpeg e ffprobe compatíveis incorporados ao bundle; nenhuma dependência de Homebrew,
  Python, Qt, Deno ou utilitário instalado no sistema.
- Nenhum download de executável, script ou recurso que acrescente funcionalidade.
- Nenhum processo órfão depois que o aplicativo sair.
- `PrivacyInfo.xcprivacy` válido no bundle e declaração coerente no App Store Connect.
- política de privacidade pública, acessível no app e na ficha da loja.
- avaliação e declaração de export compliance para o HTTPS usado pelas APIs.
- ícone, categoria, versões, screenshots, textos, contato de revisão e notas da revisão
  completos para todos os idiomas oferecidos.

### URLs e mídia de terceiros

A [regra 5.2.3](https://developer.apple.com/app-store/review/guidelines/#audio-video-downloading)
trata da capacidade de salvar, converter ou baixar mídia de terceiros sem autorização
explícita das fontes, não do nome do controle. Ela também alerta para os termos dos
serviços no streaming. A regra 5.2.2 exige uso permitido pelos termos do serviço; a 2.3.1
exige transparência sobre as funcionalidades. Essas regras foram conferidas em 29/08/2026.

O comportamento atual foi verificado em
[`_prepare_local_source`](../../sao_francisco/pipeline.py),
[`download_url` e `split_audio`](../../sao_francisco/core/media.py): URLs HTTP(S) são
encaminhadas ao yt-dlp, a mídia é gravada no workspace e o FFmpeg prepara trechos de áudio.
Renomear esse fluxo não altera o download/conversão. Arquivos temporários, saída final
somente em texto ou uma declaração do usuário não demonstram autorização da fonte.

Para uma eventual retomada, há duas alternativas de produto, ainda não aprovadas:

1. **edição somente de arquivos locais:** transcrever mídia obtida legitimamente e
   escolhida no seletor do sistema; excluir a ingestão remota do artefato da loja;
2. **edição com fontes autorizadas:** restringir a ingestão a fontes cujo uso esteja
   documentado e autorizado para as operações efetivas, com evidências disponíveis para
   App Review. Não equivale a aceitar qualquer URL nem a permitir todo um serviço porque
   um usuário declara ser autor de um vídeo.

O consentimento para enviar conteúdo a OpenAI/Gemini é separado da autorização para
obtê-lo na fonte. Nenhuma dessas alternativas garante aprovação pela Apple ou resolve os
outros gates da versão. Sem escolha explícita e evidência suficiente, manter a suspensão.
A distribuição direta também não dispensa direitos sobre o conteúdo e termos dos serviços;
esta revisão não a modifica nem conclui sua conformidade jurídica.

### Licenciamento do app e das dependências

São Francisco continuará sob a licença MIT, inclusive nesta versão paga. `LICENSE`,
`project.license`, README, Sobre, código-fonte publicado e ficha da loja devem ser
coerentes. Preço e licença não serão apresentados como equivalentes: pagar pela versão
oficial da loja não limita os direitos que a MIT concede sobre o código.

O artefato deve conservar todos os avisos, textos e ofertas de código-fonte exigidos por
terceiros e registrar a configuração e licença efetiva do FFmpeg incorporado.

PySide6/Qt for Python está disponível sob LGPLv3/GPLv3 ou licença comercial. A própria Qt
alerta que regras de lojas podem conflitar com a opção LGPL. Portanto, a liberação do app
pela Mac App Store fica bloqueada até existir uma destas evidências:

- licença comercial de Qt for Python válida para a versão e a distribuição; ou
- parecer jurídico documentado e pacote auditado que demonstrem cumprimento integral da
  licença aberta e compatibilidade com os termos da loja.

O mesmo gate vale para qualquer componente GPL encontrado no inventário final. Esta spec
não oferece parecer jurídico.

## Qualidade da interface e dos documentos

O pedido de testar “todas as possibilidades” será atendido por um contrato finito e
repetível, não pela afirmação impossível de testar toda combinação de mídia, rede e texto.
A cobertura compreende:

- todas as rotas, diálogos, menus, estados de fila e ações habilitadas/desabilitadas;
- tamanhos padrão e mínimo, teclado, foco, rolagem e acessibilidade;
- cada locale distribuído, mais pseudolocalização para detectar cortes;
- fluxos curtos e longos, sucesso, falha, cancelamento, retomada, término fora de ordem,
  falta de rede, limite de API, disco insuficiente e pressão de memória;
- origem local curta, local longa e, somente se autorizada para a loja, URL;
- formatos DOCX, TXT, SRT e VTT, com e sem tempos e com melhoria opcional;
- DOCX semântico e estruturalmente válido, aberto por `python-docx`, LibreOffice e uma
  instalação real do Microsoft Word para macOS.

Testes de GUI e de estados usarão doubles locais para não multiplicar cobranças. Chamadas
reais de API terão amostra, finalidade e orçamento aprovados previamente.

## Fora do escopo

- iPhone, iPad, Catalyst, visionOS ou uma reescrita nativa em Swift;
- assinatura, compra dentro do app, consumíveis, créditos ou StoreKit para recursos;
- licença própria, tela de licença, DRM ou chave de ativação;
- migração oportunista dos modelos de transcrição/editoriais;
- reordenação, prioridade ou agendamento da fila;
- processamento paralelo de partes do mesmo trabalho;
- tradução antes da aprovação do inventário em português;
- remoção da distribuição direta, Windows ou releases antigos;
- remoção ampla de código de URL da base comum antes da decisão de produto;
- garantia de aprovação pela Apple ou conclusão jurídica fornecida pelo agente.

## Decisões pendentes do autor

| Decisão | Prazo | Efeito |
| --- | --- | --- |
| número da versão | antes da primeira branch de implementação | metadados e migração |
| preço e países de venda | antes do cadastro no App Store Connect | ficha comercial |
| retomar a App Store com arquivos locais ou fontes autorizadas | antes de T08; suspensa até decisão explícita | escopo e regra 5.2.3 |
| licença comercial Qt ou parecer jurídico | antes de gerar candidato | gate de distribuição |
| continuar distribuição direta | antes do desenho de variantes | bundle e CI |
| variante de chinês | antes da tradução | `zh-Hans` ou `zh-Hant` |
| URL pública da política de privacidade | antes do TestFlight | metadados obrigatórios |
| teto manual de concorrência na GUI | antes do desenho final | Configurações |

## Critério de conclusão da versão

A versão só estará concluída quando:

- o português estiver aprovado e todas as traduções revisadas dentro do bundle;
- requisitos funcionais, de memória, acessibilidade e DOCX estiverem aprovados;
- catálogo de idiomas corresponder aos contratos oficiais e adaptadores reais;
- o artefato não depender de ferramentas externas e passar no App Sandbox;
- bookmarks, subprocessos, Keychain, rede e encerramento funcionarem no pacote assinado;
- licenças de primeira e terceira parte tiverem evidências compatíveis com a distribuição;
- política de privacidade, App Privacy e export compliance estiverem coerentes;
- um build limpo passar validação e upload no App Store Connect/TestFlight;
- a Apple aprovar a versão, sem contorno de política;
- specs e `validation.md` registrarem o estado e as evidências finais.

## Referências oficiais consultadas

Somente as regras 2.3.1, 5.2.2 e 5.2.3 foram reconferidas em 29/08/2026 nesta revisão.
As demais referências conservam a data-base de 13/08/2026 e exigem nova conferência na retomada.

- [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), em
  especial 2.4.5, 2.5.2, 3.1.1, 5.1 e 5.2.3;
- [App Sandbox](https://developer.apple.com/documentation/security/app-sandbox);
- [Acesso a arquivos no App Sandbox](https://developer.apple.com/documentation/security/accessing-files-from-the-macos-app-sandbox);
- [Upload de builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/);
- [Privacidade no App Store Connect](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/);
- [Privacy manifest](https://developer.apple.com/documentation/bundleresources/privacy-manifest-files);
- [Export compliance](https://developer.apple.com/help/app-store-connect/manage-app-information/overview-of-export-compliance);
- [OpenAI — speech to text](https://developers.openai.com/api/docs/guides/speech-to-text);
- [Google Gemini — idiomas](https://ai.google.dev/gemini-api/docs/models/gemini);
- [Qt for Python — licenciamento](https://doc.qt.io/qtforpython-6/);
- [Qt — obrigações LGPL](https://www.qt.io/development/open-source-lgpl-obligations);
- [FFmpeg — licença](https://ffmpeg.org/legal.html).
