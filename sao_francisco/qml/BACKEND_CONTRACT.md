# Contrato QML do `appBackend`

O launcher injeta um `QObject` chamado `appBackend` antes de carregar `Main.qml`. A
interface possui fallbacks para leitura e pré-visualização, mas as ações persistentes
dependem deste contrato.

## Propriedades notificáveis

| Propriedade | Tipo | Uso |
|---|---|---|
| `currentRoute` | `str` | Uma de `transcribe`, `history`, `settings`, `help`, `about`. |
| `sidebarCollapsed` | `bool` | Largura da barra lateral: 224 ou 64 px. |
| `busy` | `bool` | Bloqueia nova execução e mostra atividade global. |
| `appVersion` | `str` | Rodapé e página Sobre. |
| `thirdPartyNoticesMarkdown` | `str` | Avisos exibidos no pop-up da página Sobre. |
| `activeJobState` | `str` | Estado resumido para ações do menu. |
| `canOpenOutput` | `bool` | Habilita ações de resultado no menu. |
| `activeJob` | `QVariantMap` | Trabalho visível na página Transcrever. |
| `pendingSources` | `QVariantList[str]` | Arquivos selecionados ainda não enviados. |
| `outputFolder` | `str` | Destino sugerido. |
| `historyItems` | `QVariantList[QVariantMap]` | Fallback para `history()`. |
| `settings` | `QVariantMap` | Preferências atuais e chaves mascaradas. |
| `helpAnchor` | `str` | Única fonte canônica da seção de Ajuda selecionada. |

Cada propriedade mutável deve emitir o sinal `<nome>Changed`.

## Navegação e janela

- `navigate(route: str)`.
- `toggleSidebar()` ou `setSidebarCollapsed(collapsed: bool)`.
- `navigateHelp(anchor: str)`: valida a âncora, define `helpAnchor` e navega para
  `help`.
- `openExternalUrl(url: str)`: aceita apenas esquemas aprovados, preferencialmente
  `https`.
- Sinal `toastRequested(message: str)`.

Âncoras usadas pela interface:

- `primeiros-passos`
- `adicionar-arquivo-video-ou-url`
- `escolher-um-modelo`
- `chaves-da-openai-e-do-gemini`
- `como-midias-longas-sao-processadas`
- `acompanhar-cancelar-e-retomar`
- `formatos-de-saida`
- `custos-dados-e-armazenamento`
- `problemas-comuns`
- `atalhos-e-navegacao`
- `licencas-e-sobre`

## Catálogo e transcrição

- `modelsForProvider(provider_id: str) -> QVariantList[QVariantMap]`.
  Cada modelo fornece `id`, `name` (ou `label`) e, opcionalmente, `summary`.
- `setPendingSources(urls: QVariantList[str])`.
- `chooseOutputFolder() -> str`.
- `startTranscription(options: QVariantMap)`.
- `cancelTranscription()`.
- `openActiveOutput()` e `revealActiveOutput()`.

Mapa enviado a `startTranscription`:

```text
sourceType: "files" | "url"
sources: [URL local ou remota]
provider: "openai" | "gemini"
model: ID do catálogo
language: "auto" | código BCP-47 reduzido
formats: subconjunto não vazio de ["docx", "txt", "srt", "vtt"]
outputFolder: caminho ou string vazia
preferExistingCaptions: bool (somente para endereços de vídeo; padrão `false`)
includeTimestamps: bool
improveWithAi: bool (padrão `false`; exige DOCX ou TXT)
```

`activeJob` aceita:

```text
id, title/sourceName, state, stage, detail, progress (0..1),
completedParts, totalParts, provenance, costLabel, usageLabel,
outputPaths, outputGroups, originalReady, improvementState,
remoteResultAmbiguous
```

`state` é um de `queued`, `preparing`, `running`, `paused`, `completed`,
`failed`, `cancelling`, `cancelled`. `cancelling` é o estado transitório da interface
enquanto o processo recebe até cinco segundos para encerrar. Novos trabalhos usam
`audio_transcription`. Valores antigos de
`provenance` continuam aceitos para que o Histórico possa exibir trabalhos criados por
versões anteriores:

- `existing_captions` → **Legenda existente**
- `author_captions` → **Legendas do autor**
- `automatic_captions` → **Legendas automáticas**
- `audio_transcription` → **Áudio transcrito**

`stage` registra o checkpoint sequencial, entre eles `transcription_complete`,
`exporting_original`, `original_exported`, `improving`, `improvement_complete`,
`exporting_improved`, `improvement_exported` e `completed`.
`outputGroups` separa listas de caminhos em `improved`, `original` e `captions`.
`originalReady` permite oferecer o original antes do fim da melhoria;
`improvementState` é `not_requested`, `in_progress`, `not_completed` ou `ready`.
Custos chegam ao QML já formatados; preços unitários e fórmulas não fazem parte do
contrato visual.

## Histórico

- `history() -> QVariantList[QVariantMap]`.
- `openHistoryOutput(job_id)`.
- `openOutputPath(path)`.
- `resumeTranscription(job_id)`.
- `showHistoryDetails(job_id)`.
- Sinal `historyChanged()`.

Cada item do histórico aceita `id`, `title/sourceName`, `createdAtLabel/createdAt`,
`providerLabel/provider`, `modelLabel/model`, `state`, `stage`, `progress`,
`provenance`, `costLabel` e `usageLabel`.

## Configurações

- `saveSettings(values: QVariantMap) -> bool`.
- `testApiKey(provider: str, candidate: str) -> bool | str | None`.
- Sinais `settingsChanged()` e
  `apiKeyTestFinished(provider: str, ok: bool, message: str)`.

O mapa `settings` aceita `openAiKeyMasked`, `geminiKeyMasked`, `outputFolder`,
`notifyOnCompletion` e `resumeInterruptedJobs`. Campo de chave vazio em `saveSettings`
significa preservar a credencial já armazenada.

## Ajuda

- `searchHelp(query: str) -> QVariantList[QVariantMap]`, com `title`, `anchor` e
  `excerpt`.
- `helpSection(anchor: str) -> str | QVariantMap`, sendo o mapa dotado de
  `markdown`.
- Sinais `helpAnchorChanged()` e `helpContentChanged()`.

O backend normaliza caixa e acentos, recusa âncoras duplicadas e usa
`sao_francisco/AJUDA.md` como fonte versionada. A interface só abre links externos
`https`; a validação final permanece responsabilidade do backend.
