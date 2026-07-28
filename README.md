# São Francisco

Aplicativo desktop para transformar áudio e vídeo em texto, inclusive mídias longas e
URLs públicas do YouTube e serviços compatíveis.

![São Francisco em estilo Bauhaus](sao_francisco/assets/branding/sao-francisco-bauhaus.png)

O São Francisco prepara o áudio com FFmpeg, procura pausas naturais, divide a gravação em
partes seguras e salva cada resultado antes de prosseguir. Assim, a duração da mídia não
fica limitada ao tamanho de uma única requisição e trabalhos interrompidos podem ser
retomados sem reenviar as partes já concluídas.

## Recursos

- Arquivos locais de áudio e vídeo, além de URLs públicas processadas pelo yt-dlp.
- Transcrição do áudio por padrão, com opção de aproveitar legendas de vídeos.
- Normalização de legendas automáticas progressivas para remover trechos repetidos.
- Detecção automática do idioma por padrão, com escolha manual apenas como pista explícita.
- Divisão por silêncio, pequena sobreposição em cortes forçados e montagem sem repetições
  nas emendas.
- OpenAI e Google Gemini, com modelos destinados a economia, precisão, falantes e
  marcações de tempo.
- Exportação para DOCX, TXT, SRT e WebVTT.
- Marcações de tempo opcionais no DOCX e TXT, desativadas por padrão.
- Nome do vídeo aproveitado nos arquivos exportados quando a origem é uma URL.
- Histórico, cancelamento cooperativo e retomada por parte.
- Chaves no macOS Keychain ou nas Credenciais do Windows, sem arquivo de texto como
  alternativa silenciosa.
- Interface Qt 6/QML no tema **Terra Franciscana**, com Jost e Source Sans 3.
- Ajuda integrada pesquisável, espaçada e navegável por teclado.

O projeto não inclui transcrição local com Whisper nesta versão.

## Requisitos

- Python 3.11, 3.12 ou 3.13;
- FFmpeg e FFprobe disponíveis no `PATH`;
- uma chave da OpenAI ou do Gemini para transcrever áudio;
- para URLs: yt-dlp, instalado com o projeto;
- para suporte mais completo ao YouTube: Deno 2.3 ou mais recente.

No macOS com Homebrew:

```bash
brew install ffmpeg deno
```

No Windows com WinGet:

```powershell
winget install Gyan.FFmpeg
winget install DenoLand.Deno
```

Em Debian ou Ubuntu, instale o FFmpeg pelo gerenciador do sistema e siga a
[instalação oficial do Deno](https://docs.deno.com/runtime/getting_started/installation/).

Como alternativa, `scripts/install_dependencies.sh` conduz a instalação disponível no
sistema e pede confirmação antes de fazer alterações.

## Instalação

```bash
git clone https://github.com/pedblan/sao_francisco.git
cd sao_francisco
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

No PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

## Executar

```bash
sao-francisco
```

Também é possível iniciar diretamente:

```bash
python -m sao_francisco.app
```

Cadastre a chave em **Configurações**. A Ajuda integrada explica, com links oficiais,
como criar credenciais em cada provedor. Para uma sessão sem armazenamento nativo, o
aplicativo também reconhece `OPENAI_API_KEY` e `GEMINI_API_KEY`.

## Como a mídia longa é processada

1. O FFprobe valida a mídia e mede sua duração.
2. O FFmpeg detecta silêncios próximos dos pontos de divisão.
3. O áudio é convertido para mono, 16 kHz e partes de tamanho previsível.
4. Cada parte é transcrita e persistida de forma atômica.
5. Os tempos são deslocados para a linha temporal original e sobreposições são
  deduplicadas.
6. Os formatos escolhidos são gravados sem sobrescrever silenciosamente arquivos
   anteriores.

Arquivos temporários pertencem a diretórios exclusivos e marcados pelo aplicativo. A
limpeza se recusa a operar fora desses diretórios.

## Desenvolvimento e testes

Instale também as ferramentas de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
python -m pytest
ruff check .
mypy sao_francisco
```

Para validar os QMLs:

```bash
pyside6-qmllint -I sao_francisco/qml \
  sao_francisco/qml/Main.qml \
  sao_francisco/qml/Theme.qml \
  sao_francisco/qml/components/*.qml \
  sao_francisco/qml/pages/*.qml
```

Os testes não fazem chamadas pagas. A validação manual de uma chave usa apenas a listagem
de modelos do provedor.

### Build para Apple Silicon

Em um Mac Apple Silicon com Python ARM64 3.11–3.13:

```bash
./scripts/build_macos_arm64.sh
```

O script cria um aplicativo macOS nativo, assinado ad hoc para testes locais, e o
distribui em arquivos ZIP e DMG na pasta `dist/`. O FFmpeg e o FFprobe continuam sendo
dependências do sistema; o yt-dlp é incorporado ao aplicativo.

## Custos e direitos

O aplicativo é gratuito, mas os provedores podem cobrar pelo uso de suas APIs. URLs
públicas não são necessariamente conteúdo de domínio público; use somente material que
você tenha direito ou autorização para processar.

## Licença

Código sob a licença MIT. Consulte [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) para
as bibliotecas, ferramentas, fontes e respectivas licenças.
