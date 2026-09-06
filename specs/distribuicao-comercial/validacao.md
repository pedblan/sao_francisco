# Validação da localização — 29/08/2026

Branch `codex/comercial-i18n-rtl`, base `3bc3f2aa4610207566a5a13f1e75ad019e523c81`,
alterações locais não commitadas. Ambiente macOS 26.5.1 arm64, Python 3.13.5,
PySide6 6.9.3, PyInstaller 6.22.2. Pacote candidato, não release comercial.
Versões instaladas: [ambiente-validacao.txt](ambiente-validacao.txt), incluindo dependências
de desenvolvimento; essa lista não substitui o inventário de componentes do bundle final.

## Resultado

| Verificação | Evidência |
| --- | --- |
| Baseline antes da alteração | 109 testes aprovados |
| Suíte final | **141 passed in 46.82s**; sem chamadas pagas |
| Ruff | todos os checks aprovados em runtime, inventário e testes |
| Mypy | sucesso em 28 arquivos de código |
| Compilação Python | `compileall` aprovado |
| Whitespace/diff | `git diff --check` aprovado; pipeline/provedores/exportadores não alterados |
| Catálogo | 7 JSON, 381 entradas editoriais; 401 incluindo variantes determinísticas de provedor |
| QML | 220 textos únicos detectados, catalogados e envolvidos por tradução |
| Ajuda | 8 novas edições + português; 11 seções por idioma, links e âncoras preservados |
| GUI | 9 idiomas × 5 rotas × 2 tamanhos, mais popup de avisos; 108 capturas |
| Recursos empacotados | 31 arquivos de QML/catálogos/Ajuda/avisos comparados byte a byte ao checkout; sem divergências |
| MIT própria no bundle | arquivo igual ao LICENSE da raiz |
| Bundle final | assinatura ad-hoc íntegra; smoke GUI, subprocesso e yt-dlp aprovados |
| ZIP reextraído | assinatura ad-hoc íntegra após extração em pasta separada |

Testes usam backend real com pipeline falso, QSettings isolado e credenciais de fixture.
Não apresentam transcrições fictícias como resultados de provedores reais. Os testes
pré-existentes de pipeline e exportadores também passam, mas não substituem a prova
visual de um DOCX produzido por um pacote comercial e aberto no Word.

## Casos novos exercitados

- Primeira abertura em inglês, idioma desconhecido em fallback inglês, persistência e
  reinício em cada idioma, escolha independente do idioma do áudio.
- Catálogos completos, sem duplicatas, vazios ou perda de placeholders.
- Ajuda completa, pesquisável e navegável com âncoras internas estáveis.
- Mensagens de progresso/erro, variantes OpenAI/Gemini e nomes descritivos dos modelos,
  sem alterar identificadores técnicos nem dados do usuário.
- Troca ao vivo preservando modelo, idioma da transcrição, filtro do histórico e chave
  não salva; badge de validação acompanha a nova língua.
- Histórico não vazio localizado sem modificar o manifesto salvo ou título do usuário.
- Credencial mascarada mantém a máscara e traduz apenas a origem conhecida.
- Layout RTL, ícones dentro dos botões, campos de chave em LTR, popup abrindo/fechando
  por Escape e rolagem até o fim em telas menores (1024×680) e maiores (1280×800).

As inspeções visuais encontraram e corrigiram rótulos ASCII portugueses que escapavam
ao inventário inicial, reposicionamento do ícone RTL e reset do idioma de transcrição
ao reconstruir o menu. Também foi corrigido o retorno do método `history()`, que antes
contornava a apresentação localizada da propriedade de histórico.

## Capturas

Pasta local: `build/i18n-evidence/screenshots/{locale}/`. Inspecionados visualmente
exemplos em inglês, árabe, chinês e alemão, além das verificações automáticas de todas
as rotas/idiomas. Isso não equivale a revisão humana nativa de todas as traduções nem
a auditoria exaustiva de todos os leitores de tela.

- [Inglês, formulário](../../build/i18n-evidence/screenshots/en-US/transcribe-1280x800.png)
- [Árabe RTL, janela mínima](../../build/i18n-evidence/screenshots/ar/transcribe-1024x680.png)
- [Alemão, Sobre na janela mínima](../../build/i18n-evidence/screenshots/de-DE/about-1024x680.png)
- [Chinês, Ajuda](../../build/i18n-evidence/screenshots/zh-CN/help-1280x800.png)

## Pacote local

Foram feitos dois builds isolados: prova inicial e candidato final após os ajustes de
validação/localização e inclusão do LICENSE. Nenhum release antigo foi sobrescrito.

```bash
.venv/bin/python -m PyInstaller \
  --distpath build/i18n-candidate-final/dist \
  --workpath build/i18n-candidate-final/work packaging/sao_francisco.spec
codesign --verify --deep --strict 'build/i18n-candidate-final/dist/São Francisco.app'
```

O candidato final passou em `--smoke-test` com Qt offscreen/software,
`--process-smoke-test` e `--yt-dlp --version` (2026.08.19). `codesign -dv` informa
`Signature=adhoc`, arm64, sem TeamIdentifier. O plist declara nove localizações,
idioma de desenvolvimento inglês, versão 0.1.2/build 2 e meta macOS 12. Não há prova
de execução em macOS 12, Intel ou Windows. Não houve notarização nem teste Gatekeeper
de distribuição pública.

ZIP local: `build/i18n-candidate-final/Sao-Francisco-i18n-preview-macos-arm64.zip`.
SHA-256: `fa1f8ae5b45f6833f3cf36674c85e5bd7a12ea68e8cba11bbb70272f60fa1739`.
Tamanho local aproximado: 97 MiB. A extração foi conferida em
`build/i18n-candidate-final/unpacked/`, sem substituir aplicativo instalado.

Avisos do build: módulo opcional `openai.helpers` não coletado por ausência de NumPy,
e adaptador opcional urllib3/Emscripten sem `js`; não usados pelo fluxo de transcrição
atual. Smoke Qt emite aviso de alias de fonte `Sans Serif`; as capturas renderizam
glifos, inclusive árabe e chinês. Nenhum warning QML de binding foi aceito nos testes.

## Limitações que bloqueiam release, não a tradução

1. FFmpeg/ffprobe não incorporados; Deno externo. A máquina de desenvolvimento pode
   encontrar ferramentas em seu PATH. O smoke não comprova instalação autossuficiente.
2. Inventário completo de licenças de terceiros ainda pendente: bundle contém MIT
   própria, OFL das fontes e alguns metadados de dependências, mas a pesquisa local não
   demonstrou conjunto completo de textos/licenças e obrigações Qt/Python. Aviso resumido
   na GUI não substitui essas obrigações.
3. Sem assinatura Developer ID, hardened runtime comercial, notarização e ticket.
4. Sem candidato Windows dessa alteração, assinatura Authenticode ou QA nativa Windows.
5. Sem teste de API real pago, URLs reais, DOCX em leitor real ou checkout/repasse.
6. Sem auditoria de leitor de tela ou revisão por falantes nativos. Diálogos nativos
   do sistema podem seguir a língua do sistema operacional, não a seleção do app.
7. Idiomas de entrada/modelos dos provedores não foram ampliados nem recertificados
   nesta tarefa de localização. Interface em nove línguas não implica suporte universal
   de fala nem tradução automática de conteúdo.

Esses pontos estão no [roteiro de lançamento](../../LANCAMENTO.md). Não publicar até
que os gates aplicáveis sejam atendidos e o autor aprove os campos e o envio.
