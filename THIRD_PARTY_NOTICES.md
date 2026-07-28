# Componentes de terceiros

O São Francisco é distribuído sob a licença MIT. Seus componentes conservam
licenças próprias.

- **Qt for Python, PySide6 e Shiboken6:** LGPLv3/GPLv3 ou licença comercial da Qt.
  O aplicativo usa as bibliotecas dinamicamente e o pacote distribuível deve
  acompanhar os textos integrais aplicáveis e a informação necessária para
  substituição das bibliotecas.
- **FFmpeg e ffprobe:** licença conforme o build distribuído. Builds LGPL e GPL
  não são intercambiáveis; registre `ffmpeg -buildconf`, acompanhe a licença
  correspondente e ofereça o código-fonte exigido.
- **yt-dlp e yt-dlp-ejs:** avisos e licenças do projeto yt-dlp e dos componentes
  incorporados pela distribuição escolhida.
- **Deno:** licença MIT quando o runtime for incluído no pacote.
- **OpenAI Python:** licença Apache-2.0.
- **Google Gen AI Python SDK:** licença Apache-2.0.
- **python-docx:** licença MIT.
- **PyObjC e PyObjC Security:** licença MIT; integração usada para armazenar
  credenciais no macOS Keychain.
- **Jost e Source Sans 3:** SIL Open Font License 1.1. Os textos estão em
  `sao_francisco/licenses/fonts/`.

Antes de publicar um instalador, gere um inventário do artefato final. Este
arquivo não substitui os textos completos das licenças nem obrigações de
fornecimento de código-fonte.
