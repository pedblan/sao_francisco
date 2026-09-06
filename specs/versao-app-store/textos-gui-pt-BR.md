# Textos da GUI — português do Brasil

**Estado:** rascunho editorial para edição do autor

**Locale-fonte:** `pt-BR`

**Escopo:** rascunho original da proposta App Store; reaproveitamento editorial pendente

**Data do inventário:** 13 de agosto de 2026

**Nota de escopo — 29/08/2026:** a Mac App Store foi descartada. A direção vigente está em
[distribuição comercial](../distribuicao-comercial/spec.md). Este arquivo continua como
rascunho, preservado para edição do autor. Antes de traduzir, sincronizar com a GUI real e
separar propostas de fila/paralelismo e controles da loja que não serão implementados.
As referências à App Store abaixo são texto antigo a revisar, não decisão vigente.
Nenhum texto visível do aplicativo foi alterado nesta revisão.

Este é o arquivo único para revisar o texto da interface antes das traduções. Ele consolida
o que hoje está em QML, Python, Ajuda e avisos, e acrescenta o texto proposto para fila,
paralelismo, privacidade e App Store.

Edite o texto depois do travessão em cada entrada. Não altere o identificador entre
crases: ele será a chave estável do catálogo. Expressões entre chaves, como `{arquivo}` e
`{quantidade}`, são placeholders e devem continuar presentes. Blocos marcados como
**condicionais** pertencem somente à variante indicada.

Textos integrais de licenças de terceiros, nomes de produtos/modelos, URLs, extensões e
caminhos gerados não são traduzidos. Seus títulos e explicações de primeira parte entram
neste inventário.

## Alterações editoriais deliberadas

| Superfície | Texto/comportamento atual | Proposta desta versão |
| --- | --- | --- |
| Sobre — divulgação | “São Francisco é software livre!…” | frase de projeto independente e privacidade aprovada pelo autor |
| Sobre — licença | afirmação MIT junto dos terceiros | MIT permanece explícita, separada das licenças de terceiros |
| Ação principal | **Iniciar transcrição** | **Adicionar à fila** |
| Fonte remota | um campo **YouTube ou endereço** | vários endereços autorizados; ausente da edição da loja sem autorização |
| Custos na Ajuda | tabelas datadas por token/minuto | explicação sem valores unitários e links oficiais |
| Execução | fila serial implícita e um cartão ativo | fila visível, ações por item e paralelismo condicionado a recursos |
| Idioma do conteúdo | lista fixa no QML | lista filtrada por provedor/modelo e catálogo versionado |
| Idioma da interface | somente português | seletor separado do idioma transcrito e oito locales no bundle |
| Privacidade | explicação geral na Ajuda | consentimento por provedor antes do primeiro envio |

## Texto deliberadamente fora do catálogo da GUI

- instruções e prompts enviados aos modelos;
- exceções exclusivamente internas, asserts e mensagens de smoke/CI;
- nomes técnicos de estados, campos, modelos, formatos e códigos de idioma;
- caminhos, títulos de arquivos, conteúdo transcrito e valores produzidos pelo usuário;
- textos integrais oficiais das licenças de terceiros.

## Aplicativo, rotas e navegação

- `app.name` — São Francisco
- `app.tagline` — Abençoe sua transcrição
- `route.transcribe` — Transcrever
- `route.history` — Histórico
- `route.settings` — Configurações
- `route.help` — Ajuda
- `route.about` — Sobre
- `sidebar.section.work` — TRABALHO
- `sidebar.collapse` — Recolher
- `sidebar.expand` — Expandir
- `sidebar.current.accessible` — Página atual
- `sidebar.open.accessible` — Abrir {pagina}
- `sidebar.artwork.accessible` — Símbolo Bauhaus de São Francisco
- `shell.busy.accessible` — Operação em andamento
- `shell.help.open` — Ajuda
- `shell.help.tooltip` — Abrir a Ajuda
- `shell.author.site.accessible` — Abrir o site de Pedro Duarte Blanco
- `shell.action.failed` — Não foi possível concluir esta ação.

## Menus

### Arquivo

- `menu.file` — Arquivo
- `menu.file.new` — Nova transcrição
- `menu.file.add_files` — Adicionar arquivos…
- `menu.file.use_urls` — Usar endereços…
- `menu.file.history` — Histórico
- `menu.file.settings` — Configurações…
- `menu.file.quit` — Sair do São Francisco

`menu.file.use_urls` é condicional à variante com URL autorizada.

### Transcrição

- `menu.transcription` — Transcrição
- `menu.transcription.start` — Adicionar à fila
- `menu.transcription.cancel_selected` — Cancelar transcrição selecionada
- `menu.transcription.cancel_all` — Cancelar todas…
- `menu.transcription.open` — Abrir resultado
- `menu.transcription.reveal` — Mostrar pasta do resultado

### Visualizar, Ir, Janela e Ajuda

- `menu.view` — Visualizar
- `menu.view.show_sidebar` — Mostrar barra lateral
- `menu.view.hide_sidebar` — Recolher barra lateral
- `menu.view.fullscreen` — Tela cheia
- `menu.view.exit_fullscreen` — Sair da tela cheia
- `menu.go` — Ir
- `menu.window` — Janela
- `menu.window.minimize` — Minimizar
- `menu.window.zoom` — Alternar zoom
- `menu.window.front` — Trazer para a frente
- `menu.help` — Ajuda
- `menu.help.manual` — Ajuda do São Francisco
- `menu.help.topics` — Tópicos
- `menu.help.getting_started` — Primeiros passos
- `menu.help.sources` — Arquivos e endereços
- `menu.help.api_keys` — Chaves de API
- `menu.help.long_media` — Mídias longas
- `menu.help.queue` — Fila e memória
- `menu.help.problems` — Problemas comuns
- `menu.help.about` — Sobre o São Francisco

## Tela Transcrever

### Cabeçalho e fontes

- `transcribe.content.accessible` — Conteúdo da tela Transcrever
- `transcribe.artwork.accessible` — Ilustração Bauhaus de São Francisco
- `transcribe.title` — Transforme áudio e vídeo em texto
- `transcribe.description.store_no_url` — Escolha um ou mais arquivos do computador.
  Depois, selecione o serviço, o modelo e os arquivos que deseja receber.
- `transcribe.description.with_url` — Escolha arquivos do computador ou cole endereços de
  mídias autorizadas. Depois, selecione o serviço, o modelo e os arquivos que deseja
  receber.
- `transcribe.files.tab` — Arquivos
- `transcribe.files.tab.accessible` — Usar arquivos
- `transcribe.urls.tab` — Endereços
- `transcribe.urls.tab.accessible` — Usar endereços da internet
- `transcribe.drop.empty` — Arraste arquivos de áudio ou vídeo
- `transcribe.drop.one` — 1 arquivo selecionado
- `transcribe.drop.many` — {quantidade} arquivos selecionados
- `transcribe.drop.helper` — ou escolha no computador
- `transcribe.files.choose` — Escolher arquivos
- `transcribe.files.add_more` — Adicionar mais
- `transcribe.files.remove` — Remover
- `transcribe.files.remove.accessible` — Remover {arquivo}
- `transcribe.file_dialog.title` — Escolher áudio ou vídeo
- `transcribe.file_dialog.media_filter` — Áudio e vídeo
- `transcribe.file_dialog.all_filter` — Todos os arquivos

### Endereços — condicional à variante autorizada

- `transcribe.urls.label` — Endereços das mídias
- `transcribe.urls.placeholder` — Um endereço HTTP(S) por linha
- `transcribe.urls.accessible` — Endereços das mídias
- `transcribe.urls.helper` — Cole somente endereços que esta edição esteja autorizada a
  processar.
- `transcribe.urls.captions` — Usar legendas disponíveis nas mídias

### Modelo e resultado

- `transcribe.options.title` — Modelo e resultado
- `transcribe.provider` — Provedor
- `transcribe.provider.accessible` — Provedor de transcrição
- `transcribe.model` — Modelo
- `transcribe.model.accessible` — Modelo de transcrição
- `transcribe.content_language` — Idioma do conteúdo
- `transcribe.content_language.accessible` — Idioma do conteúdo
- `transcribe.output_folder` — Pasta de destino
- `transcribe.output_folder.accessible` — Pasta de destino
- `transcribe.output_folder.source_default` — Usar a pasta do arquivo
- `transcribe.output_folder.documents_default` — Usar a pasta Documentos
- `common.choose` — Escolher…
- `transcribe.formats` — Formatos de saída
- `transcribe.format.docx.accessible` — Gerar arquivo DOCX
- `transcribe.format.txt.accessible` — Gerar arquivo TXT
- `transcribe.format.srt.accessible` — Gerar legenda SRT
- `transcribe.format.vtt.accessible` — Gerar legenda VTT
- `transcribe.timestamps` — Incluir marcações de tempo no DOCX e TXT
- `transcribe.improve` — Melhorar com IA
- `transcribe.improve.description` — Organiza em parágrafos e corrige pontuação e erros
  evidentes, sem resumir.
- `transcribe.improve.review` — Confira especialmente nomes, números e trechos pouco
  claros.
- `transcribe.cost.notice` — O valor aproximado aparecerá durante o trabalho. A cobrança
  oficial fica na conta do provedor escolhido.
- `transcribe.enqueue` — Adicionar à fila
- `transcribe.invalid_draft` — Adicione ao menos uma fonte válida e escolha um formato.
- `transcribe.new_ready` — Nova transcrição pronta para configurar.

### Provedores e modelos

- `provider.openai` — OpenAI
- `provider.gemini` — Google Gemini
- `model.openai.economical.name` — Econômico
- `model.openai.economical.summary` — Boa qualidade com menor custo e resposta rápida.
- `model.openai.accurate.name` — Maior precisão
- `model.openai.accurate.summary` — Prioriza fidelidade quando nomes e vocabulário
  importam.
- `model.openai.speakers.name` — Identificar falantes
- `model.openai.speakers.summary` — Separa as falas por participante e preserva seus
  intervalos.
- `model.openai.timestamps.name` — Legendas e tempos
- `model.openai.timestamps.summary` — Fornece segmentos precisos para SRT e VTT.
- `model.gemini.detailed.name` — Gemini detalhado
- `model.gemini.detailed.summary` — Alternativa multimodal com saída estruturada e
  contexto amplo.
- `model.gemini.economical.name` — Gemini econômico
- `model.gemini.economical.summary` — Opção rápida para grande volume e extração
  estruturada.
- `model.capability.speakers` — Falantes e marcações de tempo
- `model.capability.timestamps` — Marcações de tempo precisas
- `model.capability.continuous` — Texto contínuo

Os IDs técnicos dos modelos não são traduzidos.

### Idiomas do conteúdo

- `content_language.auto` — Detectar automaticamente
- `content_language.pt` — Português
- `content_language.en` — Inglês
- `content_language.es` — Espanhol
- `content_language.fr` — Francês
- `content_language.de` — Alemão
- `content_language.it` — Italiano
- `content_language.ca` — Catalão
- `content_language.nl` — Holandês
- `content_language.pl` — Polonês
- `content_language.ru` — Russo
- `content_language.uk` — Ucraniano
- `content_language.ar` — Árabe
- `content_language.he` — Hebraico
- `content_language.hi` — Hindi
- `content_language.ja` — Japonês
- `content_language.ko` — Coreano
- `content_language.zh` — Chinês
- `content_language.incompatible` — O idioma anterior não é compatível com este modelo;
  a detecção automática foi selecionada.
- `content_language.invalid` — Este idioma não é aceito pelo provedor e pelo modelo
  escolhidos.

Catalão não aparece para Gemini sem nova comprovação oficial. Os códigos enviados às APIs
não são texto de interface.

## Fila e cartão de trabalho

### Cabeçalho e ações

- `queue.title` — Fila de transcrições
- `queue.summary.none` — Nenhum trabalho na fila
- `queue.summary.one` — 1 trabalho na fila
- `queue.summary.many` — {quantidade} trabalhos na fila
- `queue.cancel_all` — Cancelar todas…
- `queue.cancel_all.title` — Cancelar todos os trabalhos?
- `queue.cancel_all.body` — Trabalhos aguardando serão cancelados. Trabalhos ativos
  receberão pedido de cancelamento, e partes já concluídas serão preservadas.
- `queue.cancel_all.confirm` — Cancelar todos
- `queue.cancel_all.dismiss` — Voltar
- `queue.clear_completed` — Ocultar concluídos
- `queue.item.cancel` — Cancelar
- `queue.item.cancelling` — Cancelando…
- `queue.item.remove` — Remover da fila
- `queue.item.open` — Abrir resultado
- `queue.item.reveal` — Mostrar na pasta
- `queue.item.details` — Mostrar detalhes
- `queue.progress.accessible` — Progresso do trabalho
- `queue.progress.unknown.accessible` — Progresso ainda não calculado

### Estados

- `job.state.waiting` — Aguardando
- `job.state.waiting_memory` — Aguardando memória
- `job.state.preparing` — Preparando
- `job.state.running` — Em andamento
- `job.state.cancelling` — Cancelando
- `job.state.paused` — Pausada
- `job.state.completed` — Concluída
- `job.state.failed` — Falhou
- `job.state.cancelled` — Cancelada
- `job.state.unknown` — Estado desconhecido
- `job.state.original_improving` — Transcrição pronta · Melhorando texto
- `job.state.original_improvement_incomplete` — Transcrição pronta · Melhoria não concluída
- `job.state.original_and_improved` — Transcrição e texto melhorado prontos
- `job.state.exporting` — Criando arquivos
- `job.state.improvement_failed` — Não foi possível melhorar
- `job.state.export_failed` — Não foi possível exportar
- `job.state.improvement_interrupted` — Melhoria interrompida
- `job.state.export_interrupted` — Exportação interrompida

### Progresso, detalhes e saídas

- `job.detail.queued` — Na fila para iniciar.
- `job.title.default` — Transcrição
- `job.detail.next_stage` — Preparando a próxima etapa…
- `job.detail.checking_source` — Verificando a fonte…
- `job.detail.checking_captions` — Verificando a fonte e as legendas disponíveis…
- `job.detail.caption_found` — Legenda existente encontrada; preparando os arquivos…
- `job.detail.no_caption_local` — Nenhuma legenda compatível; analisando o áudio da mídia…
- `job.detail.no_caption_remote` — Nenhuma legenda compatível; obtendo a mídia para
  transcrever o áudio…
- `job.detail.analyzing` — Analisando o áudio da mídia…
- `job.detail.obtaining_remote` — Obtendo a mídia para transcrever o áudio…
- `job.detail.waiting_memory` — Aguardando memória disponível para iniciar com segurança.
- `job.detail.preparing_source` — Preparando a fonte…
- `job.detail.measuring` — Medindo a duração e procurando pausas naturais…
- `job.detail.preparing_part` — Preparando parte {atual} de {total}…
- `job.detail.transcribing_part` — Transcrevendo parte {atual} de {total}…
- `job.detail.part_completed` — Parte {atual} de {total} concluída.
- `job.detail.improving_part` — Melhorando o texto — parte {atual} de {total}…
- `job.detail.exporting_original` — Transcrição pronta; criando os arquivos originais…
- `job.detail.original_ready` — Transcrição original pronta.
- `job.detail.starting_improvement` — Transcrição original pronta; iniciando a melhoria…
- `job.detail.improved_ready` — Texto melhorado pronto; criando os arquivos…
- `job.detail.exporting_improved` — Criando os arquivos do texto melhorado…
- `job.detail.completed` — Concluída; os arquivos estão prontos.
- `job.detail.cancel_requested` — Cancelamento solicitado; preservando as partes
  concluídas.
- `job.detail.cancelling` — Cancelando; preservando a transcrição e as partes concluídas…
- `job.detail.cancelled_before_start` — Cancelada antes de iniciar.
- `job.detail.cancelled_resume` — Cancelada; você pode retomar pelo Histórico.
- `job.detail.cancelled_original_ready` — Cancelada; a transcrição original está pronta.
  Você pode retomar a melhoria pelo Histórico.
- `job.detail.cancelled_ambiguous` — Cancelada; a transcrição original foi preservada. Uma
  chamada em andamento pode ter sido processada pelo serviço.
- `job.detail.interrupted_local` — Interrompida quando o aplicativo foi fechado.
- `job.detail.interrupted_before_start` — Interrompida antes de iniciar.
- `job.detail.interrupted_remote` — Interrompida durante uma chamada remota; retome
  explicitamente porque o serviço pode ter processado a tentativa.
- `job.parts.one` — {concluidas} de 1 parte concluída
- `job.parts.many` — {concluidas} de {total} partes concluídas
- `job.output.improved` — Texto melhorado
- `job.output.original` — Transcrição original
- `job.output.captions` — Legendas
- `job.output.not_available` — O resultado não está disponível neste computador.
- `job.output.file_not_available` — Este arquivo não está disponível neste computador.
- `job.output.folder_not_available` — A pasta do resultado não está disponível.

### Proveniência e custos

- `provenance.existing_captions` — Legenda existente
- `provenance.author_captions` — Legendas do autor
- `provenance.automatic_captions` — Legendas automáticas
- `provenance.audio_transcription` — Áudio transcrito
- `cost.estimated` — Custo estimado: cerca de US$ {valor}
- `cost.under_cent` — Custo estimado: menos de US$ 0,01
- `cost.running` — Custo até agora: cerca de US$ {valor}
- `cost.running_under_cent` — Custo até agora: menos de US$ 0,01
- `cost.no_api` — Sem custo de API
- `usage.tokens` — Uso informado: {quantidade} tokens

## Histórico

- `history.title` — Histórico
- `history.description` — Acompanhe tarefas, retome transcrições interrompidas e abra os
  arquivos produzidos.
- `history.search.placeholder` — Buscar por arquivo, endereço ou modelo
- `history.search.accessible` — Buscar no histórico
- `history.filter.all` — Todos os estados
- `history.filter.running` — Em andamento
- `history.filter.completed` — Concluídas
- `history.filter.paused` — Pausadas
- `history.filter.failed` — Com falha
- `history.filter.accessible` — Filtrar por estado
- `history.refresh` — Atualizar
- `history.list.accessible` — Lista do histórico de transcrições
- `history.untitled` — Transcrição sem título
- `history.open` — Abrir
- `history.resume` — Retomar
- `history.details` — Mostrar detalhes
- `history.empty.title` — Nenhuma transcrição ainda
- `history.empty.body` — Quando você iniciar uma tarefa, o progresso e os resultados
  aparecerão aqui.
- `history.no_match.title` — Nenhum item corresponde à busca
- `history.no_match.body` — Experimente remover o filtro ou buscar outro termo.
- `history.start_now` — Transcrever agora
- `history.missing` — Este item não existe mais no histórico.
- `history.output_missing` — O arquivo de resultado não foi encontrado.
- `history.already_queued` — Este trabalho já está na fila.
- `history.paid_retry` — A tentativa anterior pode ter sido cobrada. Escolha Retomar
  novamente para confirmar uma nova chamada.

## Configurações

### Cabeçalho e chaves

- `settings.title` — Configurações
- `settings.description` — Cadastre as chaves dos provedores e escolha como o São
  Francisco deve guardar, retomar e organizar seu trabalho.
- `settings.content.accessible` — Conteúdo das Configurações
- `settings.keys.title` — Chaves de API
- `settings.keys.description` — As chaves são guardadas pelo cofre seguro do sistema. O
  valor completo não volta a ser exibido.
- `settings.keys.how` — Como obter
- `settings.openai.key.accessible` — Chave da API da OpenAI
- `settings.openai.key.placeholder` — sk-…
- `settings.gemini.key.placeholder` — Cole a chave do Google AI Studio
- `settings.gemini.key.accessible` — Chave da API do Google Gemini
- `settings.key.verify` — Verificar
- `settings.key.verifying` — Verificando…
- `settings.key.valid` — Chave válida
- `settings.key.invalid` — Não foi possível validar
- `settings.key.unknown_provider` — Provedor desconhecido.
- `settings.key.read_failed` — A chave não pôde ser lida no cofre seguro.
- `settings.key.empty` — Nenhuma chave foi informada.

### Arquivos, continuidade, idioma e recursos

- `settings.files.title` — Arquivos e continuidade
- `settings.output_default` — Pasta de saída padrão
- `settings.output_dialog.title` — Escolher pasta de saída
- `settings.output_default.placeholder.no_url` — Pasta do arquivo selecionado
- `settings.output_default.placeholder.with_url` — Pasta da fonte; Documentos para
  endereços
- `settings.output_default.accessible` — Pasta de saída padrão
- `settings.resume` — Retomar automaticamente tarefas interrompidas
- `settings.notify` — Avisar quando uma transcrição terminar
- `settings.interface_language` — Idioma da interface
- `settings.interface_language.description` — Esta escolha não muda o idioma do conteúdo
  transcrito.
- `settings.concurrency` — Execuções simultâneas
- `settings.concurrency.auto` — Automático (recomendado)
- `settings.concurrency.maximum` — No máximo {quantidade}
- `settings.concurrency.description` — O limite é um teto. O São Francisco pode executar
  menos trabalhos para preservar memória e estabilidade.
- `settings.unsaved` — Há alterações ainda não salvas.
- `settings.save` — Salvar configurações
- `settings.saved` — Configurações salvas.
- `settings.output_not_folder` — A pasta de saída não é uma pasta.
- `settings.save_failed` — As preferências não puderam ser gravadas.

## Consentimento e privacidade

- `privacy.provider_consent.title` — Enviar conteúdo para {provedor}?
- `privacy.provider_consent.body` — Para realizar esta transcrição, o São Francisco
  enviará o conteúdo ao {provedor}. A cobrança, o processamento e a retenção no serviço
  seguem os termos e a política desse provedor.
- `privacy.provider_consent.policy` — Ler a política de privacidade
- `privacy.provider_consent.provider_terms` — Ler os termos do {provedor}
- `privacy.provider_consent.cancel` — Voltar
- `privacy.provider_consent.confirm` — Concordar e adicionar à fila
- `privacy.provider_consent.accessible` — Consentimento para envio ao {provedor}
- `privacy.bookmark.revoked` — O acesso a {item} não está mais disponível. Selecione-o
  novamente para continuar.
- `privacy.source.reselect` — Selecionar novamente…

### Idiomas da interface

Estes nomes são autônimos e não devem ser traduzidos para outro nome no próprio seletor.

- `interface_language.pt_BR` — Português (Brasil)
- `interface_language.en` — English
- `interface_language.fr` — Français
- `interface_language.es` — Español
- `interface_language.de` — Deutsch
- `interface_language.ru` — Русский
- `interface_language.ja` — 日本語
- `interface_language.zh_Hans` — 简体中文

## Ajuda — moldura

- `help.title` — Ajuda
- `help.description` — Orientações claras para cada etapa da transcrição.
- `help.search.placeholder` — Buscar na ajuda
- `help.search.accessible` — Buscar na Ajuda
- `help.topics` — TÓPICOS
- `help.results.one` — 1 resultado
- `help.results.many` — {quantidade} resultados
- `help.topics.accessible` — Tópicos da Ajuda
- `help.topic.selected.accessible` — Tópico selecionado
- `help.topic.open.accessible` — Abrir tópico da Ajuda
- `help.no_results` — Nenhum tópico encontrado. Tente palavras mais curtas.
- `help.article.accessible` — Artigo da Ajuda
- `help.hero.title` — Comece com tranquilidade
- `help.hero.body` — A Ajuda explica cada escolha, inclusive chaves, custos, fila, mídias
  longas e retomada.
- `help.loading` — O manual está sendo preparado.
- `help.unavailable.title` — Ajuda indisponível
- `help.unavailable.body` — A Ajuda integrada não pôde ser carregada. Reinstale o
  aplicativo para restaurar o manual.
- `help.link.unsafe` — Este endereço não pode ser aberto com segurança.

## Sobre

- `about.content.accessible` — Conteúdo da tela Sobre
- `about.name` — São Francisco
- `about.tagline` — Transcrição cuidadosa para áudio e vídeo de qualquer duração.
- `about.description` — Transforma gravações e vídeos longos em textos e legendas, com
  acompanhamento do início ao fim.
- `about.version` — Versão {versao}
- `about.author.badge` — SAIBA MAIS
- `about.author.title` — Conheça os livros e outros trabalhos
- `about.author.body` — São Francisco é um projeto independente que respeita sua
  privacidade. Se você quiser valorizar o trabalho, leia os livros e conheça os outros
  projetos na minha página de autor.
- `about.author.role` — Autor e programador
- `about.author.name` — Pedro Duarte Blanco
- `about.author.action` — Clique para conhecer
- `about.author.artwork.accessible` — Ilustração Bauhaus de uma xícara de café com gesto
  de regência
- `about.author.site.accessible` — Abrir pedblan.github.io
- `about.licenses.title` — Software e licenças
- `about.licenses.body` — O código do São Francisco é aberto sob a licença MIT.
  Componentes, bibliotecas, ferramentas e fontes de terceiros conservam suas próprias
  licenças.
- `about.fonts` — Jost e Source Sans 3 acompanham a identidade visual sob a SIL Open Font
  License.
- `about.notices.open` — Ver avisos de terceiros
- `about.privacy.open` — Ler a política de privacidade

## Pop-up Avisos de terceiros

- `notices.title` — Avisos de terceiros
- `notices.close` — Fechar
- `notices.close.accessible` — Fechar avisos de terceiros
- `notices.content.accessible` — Conteúdo dos avisos de terceiros
- `notices.unavailable` — Conteúdo indisponível.
- `notices.not_found` — Os avisos não foram encontrados neste pacote.
- `notices.read_failed` — Os avisos não puderam ser lidos.

### Texto introdutório e inventário visível

> # Componentes de terceiros
>
> O São Francisco é distribuído sob a licença MIT. Seus componentes conservam licenças
> próprias.
>
> - **Qt for Python, PySide6 e Shiboken6:** licença correspondente à edição efetivamente
>   incorporada ao bundle.
> - **FFmpeg e ffprobe:** licença correspondente ao build distribuído, acompanhada dos
>   textos e da oferta de código-fonte aplicáveis.
> - **OpenAI Python:** licença Apache-2.0.
> - **Google Gen AI Python SDK:** licença Apache-2.0.
> - **python-docx:** licença MIT.
> - **PyObjC e PyObjC Security:** licença MIT.
> - **Jost e Source Sans 3:** SIL Open Font License 1.1.

Se a variante autorizada incorporar yt-dlp, yt-dlp-ejs ou Deno, seus avisos retornam a
esta lista. Os textos integrais de licença incluídos no bundle são exibidos em sua forma
oficial e não passam pela tradução editorial.

O parágrafo **Antes de publicar um instalador…** não faz parte deste texto.

## Mensagens comuns, validação e erros

### Entrada e opções

- `error.source.choose` — Escolha arquivos ou endereços.
- `error.source.add` — Adicione um arquivo ou endereço para transcrever.
- `error.source.local_invalid` — O endereço de arquivo local é inválido.
- `error.source.local_choose` — Escolha um arquivo local.
- `error.source.missing` — O arquivo selecionado não existe: {arquivo}.
- `error.source.scheme` — Somente arquivos locais e endereços HTTP(S) são aceitos.
- `error.url.invalid` — Informe um endereço HTTP(S) válido.
- `error.options.missing` — As opções do trabalho estão ausentes.
- `error.provider.choose` — Escolha OpenAI ou Gemini.
- `error.model.missing` — O modelo de transcrição não existe no catálogo.
- `error.model.provider` — O modelo escolhido não pertence ao provedor.
- `error.format.choose` — Escolha ao menos um formato de saída.
- `error.format.unsupported` — Formato de saída não suportado: {formatos}.
- `error.format.list` — A lista de formatos é inválida.
- `error.language.code` — O código de idioma não é válido.
- `error.improve.format` — Para melhorar o texto, escolha DOCX ou TXT.
- `error.output.create` — A pasta de saída não pôde ser criada.
- `error.source.resume_missing` — A fonte original não está mais disponível para
  retomada.
- `error.source.resume_changed` — A fonte original foi alterada; inicie um novo trabalho.
- `error.improvement.version` — A melhoria salva usa uma versão incompatível. Inicie um
  novo trabalho.
- `error.improvement.attempt_reconcile` — A tentativa remota ativa não pôde ser
  reconciliada.
- `error.captions.resume_missing` — A legenda original não está mais disponível para
  retomada.

### Chaves e provedores

- `error.key.configure_openai.transcribe` — Configure uma chave da OpenAI antes de
  transcrever.
- `error.key.configure_gemini.transcribe` — Configure uma chave do Gemini antes de
  transcrever.
- `error.key.configure_service.improve` — Configure a chave do serviço escolhido antes
  de melhorar o texto.
- `error.key.configure_openai.improve` — Configure uma chave da OpenAI antes de melhorar
  o texto.
- `error.key.configure_gemini.improve` — Configure uma chave do Gemini antes de melhorar
  o texto.
- `error.component.openai` — O componente da OpenAI não foi instalado corretamente.
- `error.component.gemini` — O componente do Gemini não foi instalado corretamente.
- `error.openai.auth` — A OpenAI não aceitou a chave configurada.
- `error.gemini.auth` — O Gemini não aceitou a chave configurada.
- `error.openai.permission.transcribe` — A chave não tem acesso ao modelo de transcrição
  escolhido.
- `error.openai.permission.improve` — A chave não tem acesso à melhoria de texto
  escolhida.
- `error.gemini.permission` — A chave não tem acesso ao modelo Gemini escolhido.
- `error.openai.rate` — A OpenAI informou limite de uso ou cota indisponível. Confira o
  faturamento e tente retomar depois.
- `error.gemini.rate` — O Gemini informou limite de uso ou cota indisponível. Confira o
  projeto e tente retomar depois.
- `error.openai.connection` — A conexão com a OpenAI foi interrompida.
- `error.gemini.connection` — A conexão com o Gemini foi interrompida.
- `error.openai.unavailable` — A OpenAI está temporariamente indisponível.
- `error.gemini.unavailable` — O Gemini está temporariamente indisponível.
- `error.openai.transcribe` — A OpenAI não conseguiu transcrever esta parte.
- `error.openai.audio_open` — A parte de áudio preparada não pôde ser aberta.
- `error.openai.upload_large` — Uma parte excedeu o limite de upload da OpenAI. O trabalho
  pode ser retomado após subdividi-la.
- `error.gemini.transcribe` — O Gemini não conseguiu transcrever esta parte.
- `error.gemini.prepare` — O Gemini não conseguiu preparar a parte enviada.
- `error.gemini.prepare_timeout` — O Gemini demorou demais para preparar a parte enviada.
- `error.gemini.invalid` — O Gemini devolveu uma transcrição em formato inválido.
- `error.gemini.unusable` — O Gemini não devolveu uma transcrição utilizável.
- `error.gemini.no_speech` — O Gemini não reconheceu fala nesta parte.

### Melhoria, mídia, persistência e saída

- `error.openai.improve.empty` — A OpenAI não devolveu um texto melhorado utilizável.
- `error.gemini.improve.empty` — O Gemini não devolveu um texto melhorado utilizável.
- `error.openai.improve.rate` — A OpenAI atingiu um limite de uso. Retome a melhoria mais
  tarde.
- `error.gemini.improve.rate` — O Gemini atingiu um limite de uso. Retome a melhoria mais
  tarde.
- `error.improve.connection` — A conexão caiu durante a melhoria. O texto original está
  preservado.
- `error.improve.general` — Não foi possível melhorar o texto. A transcrição original está
  preservada.
- `error.improve.unusable` — A melhoria não devolveu um texto utilizável. A transcrição
  original está preservada.
- `error.improve.start` — A melhoria não pôde ser iniciada.
- `error.provider.unknown` — O provedor de transcrição não é reconhecido.
- `error.improve.unsupported` — O serviço escolhido não pode melhorar o texto.
- `error.media.dependency` — Não foi possível preparar esta mídia. Atualize o São
  Francisco e tente novamente.
- `error.media.prepare` — A mídia não pôde ser preparada para transcrição.
- `error.export` — Um dos arquivos de saída não pôde ser gerado.
- `error.credential.read` — A credencial não pôde ser lida no cofre seguro.
- `error.job_store` — O estado salvo do trabalho não pôde ser atualizado.
- `error.file.process` — Um arquivo necessário não pôde ser processado.
- `error.transcription.general` — A transcrição não pôde ser concluída.
- `error.process.unexpected` — O processo de transcrição terminou inesperadamente.
- `error.startup.interface` — Não foi possível carregar a interface do São Francisco.
- `error.startup.pyside` — São Francisco requer PySide6. Reinstale o aplicativo para
  restaurar o Qt 6.
- `error.file.system_access` — O sistema não conseguiu acessar um arquivo necessário.
- `error.open.general` — Não foi possível abrir o endereço.
- `error.transcription.finish` — Não foi possível concluir a transcrição.

### Cofre seguro

- `credential.store.macos` — macOS Keychain
- `credential.store.windows` — Credenciais do Windows
- `credential.store.generic` — cofre seguro do sistema
- `credential.save.empty` — Cole uma chave antes de salvar.
- `credential.provider.unknown` — Provedor de credencial desconhecido.
- `credential.macos.unavailable` — macOS Keychain indisponível.
- `credential.macos.integration_missing` — A integração nativa com o macOS Keychain não
  foi instalada.
- `credential.macos.read_failed` — Não foi possível ler a chave no macOS Keychain (código
  {codigo}).
- `credential.macos.save_failed` — Não foi possível salvar a chave no macOS Keychain
  (código {codigo}).
- `credential.macos.remove_failed` — Não foi possível remover a chave do macOS Keychain
  (código {codigo}).
- `credential.windows.unavailable` — O Gerenciador de Credenciais do Windows está
  indisponível.
- `credential.windows.read_failed` — Não foi possível ler a chave nas Credenciais do
  Windows (código {codigo}).
- `credential.windows.save_failed` — Não foi possível salvar a chave nas Credenciais do
  Windows (código {codigo}).
- `credential.windows.remove_failed` — Não foi possível remover a chave nas Credenciais
  do Windows (código {codigo}).
- `credential.store.unsupported_save` — O São Francisco não salva chaves em texto simples.
  Use uma variável de ambiente nesta plataforma.
- `credential.store.unavailable` — O cofre seguro não está disponível nesta plataforma.
- `credential.store.replace_unconfirmed` — O {cofre} não confirmou a substituição da
  chave. A configuração anterior foi preservada.
- `credential.store.invalid` — O cofre seguro devolveu uma credencial em formato inválido.

### Arquivo integrado da Ajuda

- `help.error.empty` — O arquivo de Ajuda está vazio.
- `help.error.main_title` — A Ajuda precisa ter exatamente um título principal.
- `help.error.no_articles` — A Ajuda não contém artigos navegáveis.
- `help.error.duplicate_anchor` — Duas seções da Ajuda geram a mesma âncora: {ancora}.
- `help.error.security` — O manual integrado não pôde ser carregado com segurança.

### Fila e notificações

- `toast.queue.added.one` — Adicionado à fila (1 aguardando).
- `toast.queue.added.many` — Adicionado à fila ({quantidade} aguardando).
- `toast.queue.duplicates` — {quantidade} fontes duplicadas não foram adicionadas.
- `toast.queue.valid_with_errors` — Fontes válidas foram adicionadas. Revise {quantidade}
  entradas com problema.
- `toast.queue.waiting_removed` — Os itens que ainda estavam na fila foram cancelados.
- `toast.job.completed` — “{titulo}” foi concluída.
- `toast.result.unavailable` — O resultado não está disponível neste computador.
- `notification.job.completed.title` — Transcrição concluída
- `notification.job.completed.body` — “{titulo}” está pronta.

## Ajuda — texto integral proposto

O bloco abaixo substituirá `sao_francisco/AJUDA.md` depois da aprovação editorial. As duas
variantes de **Adicionar fontes** são mutuamente exclusivas; a decisão sobre URLs deve ser
tomada antes da tradução.

# Ajuda do São Francisco

O São Francisco transforma áudio e vídeo em texto. Você pode adicionar vários arquivos e
acompanhar cada um em uma fila de transcrições.

## Primeiros passos

Para conhecer o aplicativo, comece com uma gravação curta:

1. Abra **Configurações** e cadastre uma chave da OpenAI ou do Gemini.
2. Volte a **Transcrever**.
3. Escolha um ou mais arquivos.
4. Selecione o provedor, o modelo e o idioma do conteúdo.
5. Marque os formatos que deseja receber.
6. Escolha a pasta de destino.
7. Pressione **Adicionar à fila**.

Quando um trabalho terminar, os arquivos estarão na pasta escolhida. Você também poderá
abri-los pela fila ou pela tela **Histórico**.

Na primeira chamada a um provedor, o São Francisco informa que o conteúdo será enviado ao
serviço escolhido. Leia a política de privacidade e prossiga somente se estiver de acordo.

## Adicionar arquivos

Escolha um ou mais arquivos de áudio ou vídeo do computador. Formatos comuns, como MP3,
WAV, M4A, MP4, MOV, MKV e WebM, são aceitos.

Cada arquivo cria um trabalho independente. As opções de provedor, modelo, idioma,
formatos e destino são registradas quando o lote entra na fila. Alterar o formulário
depois disso não muda os trabalhos que já aguardam.

Se o mesmo arquivo já estiver aguardando ou em andamento, o aplicativo avisa e não cria
uma duplicata. Arquivos diferentes com o mesmo nome continuam separados e recebem nomes
de saída distintos.

### Variante condicional — endereços autorizados

Este trecho só entra na Ajuda de uma edição que tenha autorização documentada para
processar endereços.

Na guia **Endereços**, cole um endereço HTTP(S) por linha. O São Francisco valida cada
linha e adiciona as fontes válidas sem esconder os problemas encontrados nas demais.

Se quiser aproveitar o texto publicado com a mídia, marque **Usar legendas disponíveis
nas mídias**. O São Francisco remove repetições progressivas antes de criar o documento.
A opção começa desmarcada; deixe-a assim quando preferir uma nova transcrição do áudio.

Uma mídia acessível na internet não é necessariamente de uso livre. Use somente fontes
que esta edição esteja autorizada a processar e materiais que você tenha direito de usar.

### Detectar o idioma

**Detectar automaticamente** deixa o serviço reconhecer o idioma falado. Também é
possível informar diretamente um idioma aceito pelo provedor e pelo modelo escolhidos.

Nenhuma das opções é sempre melhor. Indicar o idioma pode ajudar em gravações ruidosas,
sotaques, nomes próprios e línguas parecidas. A detecção automática é útil quando você
não sabe o idioma ou quando o conteúdo mistura mais de um.

A lista muda conforme o provedor e o modelo. Se uma troca tornar o idioma incompatível,
o aplicativo seleciona a detecção automática e avisa antes de iniciar.

## Escolher um modelo

Os nomes da lista indicam o uso recomendado:

- **Econômico — OpenAI:** boa opção para começar e para textos contínuos.
- **Maior precisão — OpenAI:** prioriza nomes próprios e vocabulário.
- **Identificar falantes — OpenAI:** separa os participantes quando possível.
- **Legendas e tempos — OpenAI:** oferece marcações de tempo mais precisas.
- **Gemini detalhado:** produz uma transcrição estruturada.
- **Gemini econômico:** alternativa para maior volume.

A qualidade depende da gravação. Ruído, música alta, pessoas falando ao mesmo tempo,
microfone distante e nomes incomuns podem exigir revisão.

Modelos, idiomas e disponibilidade podem mudar conforme cada serviço. O São Francisco só
mostra combinações documentadas no catálogo da versão instalada.

## Chaves da OpenAI e do Gemini

Uma chave de API é uma credencial secreta que permite ao São Francisco enviar o áudio ao
serviço escolhido. Você não precisa ser desenvolvedor para criar uma.

A compra do São Francisco na App Store não inclui créditos de API. Assinaturas de
chatbots e uso de API também são serviços separados. ChatGPT Plus, por exemplo, não
inclui automaticamente créditos da API OpenAI. Cada provedor administra cobrança,
limites e acesso aos modelos em sua própria plataforma.

A chave autentica sua conta no provedor; ela não funciona como licença nem desbloqueia uma
modalidade do São Francisco.

O São Francisco guarda a chave no cofre seguro do sistema e nunca volta a exibi-la por
inteiro.

### Criar uma chave da OpenAI

1. Abra a [página oficial de chaves da OpenAI](https://platform.openai.com/api-keys).
2. Entre ou crie uma conta.
3. Crie uma chave para o projeto desejado.
4. Copie a chave quando ela aparecer.
5. No São Francisco, abra **Configurações → OpenAI** e cole a chave.
6. Escolha **Verificar** e, depois, **Salvar configurações**.

Uma chave pode ser válida e ainda não ter saldo, limite ou acesso ao modelo escolhido.
Nesse caso, confira a cobrança e os limites na plataforma da OpenAI.

### Criar uma chave do Gemini

1. Abra a [página oficial de chaves do Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Entre no Google AI Studio.
3. Escolha um projeto e crie a chave.
4. No São Francisco, abra **Configurações → Gemini** e cole a chave.
5. Escolha **Verificar** e, depois, **Salvar configurações**.

> [!WARNING]
> Nunca envie uma chave em documento, captura de tela, mensagem ou pedido de suporte.
> Se uma chave for exposta, revogue-a e crie outra.

## Como mídias longas são processadas

O São Francisco prepara mídias longas em etapas menores e reúne tudo em uma única
transcrição. Isso permite trabalhar com gravações de qualquer duração sem enviar o
arquivo inteiro de uma vez.

Cada etapa concluída é guardada. Se houver uma interrupção, você poderá continuar pelo
**Histórico** sem recomeçar todo o trabalho.

O tempo necessário depende da duração da gravação, da velocidade da internet e da
disponibilidade do serviço escolhido.

## Fila, memória e execuções simultâneas

Cada fonte entra na fila como um trabalho independente. Quando há memória, espaço em
disco e limite de provedor disponíveis, mais de um trabalho pode avançar ao mesmo tempo.

O modo **Automático** preserva uma reserva de memória para o sistema e deixa de iniciar
novos trabalhos quando essa margem fica pequena. Nesse caso, o item mostra **Aguardando
memória** e começa quando houver espaço seguro. Em computadores com menos memória, é
normal que o aplicativo execute apenas uma transcrição por vez.

Se você definir um número máximo de execuções simultâneas, esse número será um teto, não
uma promessa. O São Francisco ainda pode executar menos trabalhos para manter o computador
responsivo ou respeitar o limite do provedor.

Trabalhos podem terminar fora da ordem em que entraram. A fila mantém progresso,
resultados e cancelamento associados a cada fonte.

## Acompanhar, cancelar e retomar

Durante a transcrição, a fila mostra o andamento e informa qual parte está sendo
processada.

**Cancelar** muda o item para **Cancelando** e encerra sua execução em até cerca de cinco
segundos. Partes e arquivos já concluídos permanecem disponíveis. Uma chamada que já
tenha chegado ao serviço pode terminar ou gerar cobrança mesmo depois do cancelamento.

Cancelar um item não interrompe os demais. **Cancelar todas** pede confirmação, cancela
itens aguardando e solicita o encerramento dos ativos.

**Retomar** continua um trabalho interrompido. Se você trocar o arquivo, o serviço, o
modelo ou o idioma, será necessário iniciar uma nova transcrição. Quando o resultado de
uma chamada anterior for incerto, o aplicativo avisa antes de permitir uma nova chamada,
pois ela pode gerar outra cobrança.

## Formatos de saída

- **TXT:** texto simples, adequado para leitura e pesquisa.
- **DOCX:** documento formatado, pronto para abrir em editores de texto.
- **SRT:** legenda para reprodutores e editores de vídeo.
- **VTT:** legenda usada principalmente em páginas da internet.

As marcações de tempo no DOCX e no TXT são opcionais e ficam desativadas por padrão. Para
incluí-las, marque **Incluir marcações de tempo no DOCX e TXT** antes de adicionar o lote.

Arquivos SRT e VTT sempre precisam de tempos para funcionar como legendas. Quando o modelo
não oferece tempos exatos, o resultado pode precisar de ajustes no editor de vídeo.

Se já existir um arquivo com o mesmo nome, o São Francisco acrescenta um número ao novo
resultado. Trabalhos paralelos reservam nomes distintos antes de exportar.

### Melhorar com IA

Marque **Melhorar com IA** quando quiser receber, além da transcrição original, uma
segunda versão mais confortável para leitura. O aplicativo organiza parágrafos e corrige
pontuação, maiúsculas e erros evidentes de reconhecimento.

A melhoria não deve resumir, traduzir, embelezar nem completar trechos duvidosos. Mesmo
assim, confira especialmente nomes, números e partes pouco claras.

DOCX e TXT recebem arquivos separados, identificados como **transcrição** e **texto
melhorado**. As marcações de tempo permanecem somente no original. SRT e VTT não são
reescritos pela etapa de melhoria.

O trabalho segue uma ordem segura: primeiro a transcrição é concluída, guardada e
exportada; depois o texto é melhorado, se você tiver marcado a opção; por último são
criados os arquivos adicionais de texto melhorado. Se a melhoria for interrompida, os
arquivos originais continuam disponíveis. A retomada reaproveita etapas aceitas e não
repete automaticamente uma chamada cujo resultado ficou incerto.

## Custos, dados e armazenamento

O preço pago na App Store cobre o aplicativo e sua distribuição oficial. Ele não inclui
o consumo das APIs. Quando houver cobrança de transcrição ou melhoria, ela será feita
diretamente pela OpenAI ou pelo Google, conforme sua conta e o modelo escolhido. O São
Francisco não vende nem acrescenta créditos de API.

Cada parte enviada pode gerar consumo. Ao retomar, o aplicativo reaproveita o que já foi
concluído.

Quando houver dados suficientes, o São Francisco mostra um custo aproximado em dólares.
Valores muito pequenos aparecem como **menos de US$ 0,01**. Se não houver chamada de API,
aparece **Sem custo de API**.

O total é apenas uma estimativa. Planos gratuitos, impostos, descontos, tentativas
interrompidas e mudanças de preço podem fazer o painel do provedor mostrar outro valor.
Consulte as páginas oficiais de [preços da OpenAI](https://developers.openai.com/api/docs/pricing)
e de [preços do Gemini](https://ai.google.dev/gemini-api/docs/pricing), além do
[uso da OpenAI](https://platform.openai.com/usage) ou do
[faturamento do Google Cloud](https://console.cloud.google.com/billing).

Quando o serviço informar uma contagem confiável, o aplicativo também pode mostrar o
total de tokens. Tokens são pequenas unidades usadas para medir a entrada e a resposta.
O São Francisco não inventa uma contagem quando ela não é fornecida.

O áudio é enviado somente ao provedor selecionado para aquele trabalho. O histórico e os
arquivos de trabalho ficam no computador. Os resultados permanecem na pasta de destino
até que você os apague.

Leia a [política de privacidade do São Francisco]({url_politica_privacidade}), os
[termos da OpenAI](https://openai.com/policies) e os
[termos da API Gemini](https://ai.google.dev/gemini-api/terms).

## Problemas comuns

### A chave não foi aceita

**Sintoma:** a tela Configurações informa que a chave é inválida.

**O que fazer:** confira se a chave pertence ao serviço correto, se foi copiada por
inteiro e se continua ativa. Depois, verifique cobrança, limites e acesso ao modelo.

### O arquivo não tem áudio

**Sintoma:** o trabalho termina antes de começar a transcrição.

**O que fazer:** abra o arquivo e confirme que existe som. Arquivos danificados ou vídeos
compostos apenas por imagens não podem ser transcritos.

### O trabalho aguarda memória

**Sintoma:** o item permanece em **Aguardando memória**.

**O que fazer:** aguarde outro trabalho terminar ou feche aplicativos que estejam usando
muita memória. Você também pode cancelar o item. O São Francisco inicia a tarefa quando
houver margem segura.

### O processamento parece parado

**Sintoma:** a mesma parte permanece ativa por vários minutos.

**O que fazer:** gravações longas e serviços ocupados podem demorar. Se aparecer uma
mensagem de rede ou limite, cancele e retome depois.

### A legenda ficou fora de sincronia

**Sintoma:** o arquivo SRT ou VTT antecipa ou atrasa uma fala.

**O que fazer:** use o modelo **Legendas e tempos** e revise o resultado junto ao vídeo.

### Não há espaço no computador

**Sintoma:** o trabalho é interrompido durante a preparação ou a criação dos arquivos.

**O que fazer:** libere espaço e tente novamente.

### A fonte não pode mais ser retomada

**Sintoma:** o São Francisco pede que você selecione o arquivo novamente.

**O que fazer:** o acesso concedido ao arquivo ou à pasta pode ter sido revogado, ou o
arquivo pode ter sido movido. Selecione a fonte novamente. Se ela tiver mudado, inicie um
novo trabalho.

## Atalhos e navegação

- `⌘N` no macOS abre **Transcrever**.
- `⌘O` abre o seletor de arquivos.
- `⌘K` abre a **Ajuda**.
- `⌘,` abre **Configurações**.
- `Tab` e `Shift+Tab` movem o foco.
- `Enter` ou `Espaço` ativa o controle em foco.
- `Page Up`, `Page Down`, `Home` e `End` percorrem textos longos.
- `Esc` fecha janelas de aviso.

O índice e o artigo da Ajuda possuem rolagem independente.

## Licenças, privacidade e sobre

O código-fonte do São Francisco continua aberto sob a licença MIT. A versão da App Store
é paga, mas o preço da distribuição oficial não muda os direitos concedidos pela licença.

Componentes, bibliotecas, ferramentas e fontes conservam suas próprias licenças. Na tela
**Sobre**, escolha **Ver avisos de terceiros** para ler o inventário dentro do aplicativo.

Na mesma tela, escolha **Ler a política de privacidade** para saber quais dados saem do
computador, por que são enviados, onde ficam os arquivos e como revogar o acesso.

## Checklist editorial antes da tradução

- [ ] frase da página de autor aprovada;
- [ ] texto MIT + App Store paga aprovado;
- [ ] decisão sobre a variante com URL aplicada e trecho não usado removido;
- [ ] URL pública da política de privacidade substitui o placeholder;
- [ ] nomes dos modelos e idiomas confirmados pelo catálogo implementado;
- [ ] controle/teto de concorrência confirmado;
- [ ] todos os IDs curtos correspondem ao texto integral da Ajuda;
- [ ] português final recebe hash e data de aprovação.
