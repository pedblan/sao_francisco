# Validação — release 0.1.2

## Matriz de aceitação

| Gate | Evidência | Estado |
| --- | --- | --- |
| Versão 0.1.2 sincronizada | busca e testes de metadados | aprovado |
| Specs funcionais refletidas | revisão cruzada de specs e diff | aprovado |
| Testes, Ruff e mypy | logs dos comandos | aprovado |
| QML e interface | qmllint, offscreen e capturas | aprovado |
| Processo congelado macOS | smoke de conclusão, cancelamento e reutilização | aprovado |
| Processo congelado Windows | smoke de conclusão, cancelamento e reutilização | aprovado |
| macOS arm64 / mínimo 12.0 | `file`, `lipo` e `vtool` | aprovado |
| App assinado e notarizado | `codesign`, ID, log, `stapler`, `spctl` | aprovado |
| DMG assinado e notarizado | ID, log, `codesign`, `stapler`, `spctl`, `hdiutil` | aprovado |
| ZIP macOS deriva do app grampeado | inventário e validação extraída | aprovado |
| ZIP Windows portátil | workflow, extração e helpers | aprovado |
| Manifesto e SHA-256 | verificador e hashes finais | aprovado |
| GitHub Release público | URL, ativos baixados e hashes | aprovado |
| WordPress mínimo e público | hashes dos blocos, URL e teste do link | aprovado |

## Gates de código

```text
python -m pytest -q tests/test_costs_editorial.py tests/test_pipeline.py
python -m pytest -q tests/test_backend.py tests/test_qml_offscreen.py
python -m pytest -q
python -m ruff check .
python -m mypy sao_francisco
git diff --check
```

Registrar também o comando de `qmllint` efetivamente disponível no ambiente.

### Execução em código-fonte — 30 de julho de 2026

- `python -m pytest -q`: **109 aprovados**;
- `ruff check .`: aprovado;
- `mypy sao_francisco`: aprovado em 26 arquivos;
- `git diff --check`: aprovado;
- `tests/test_qml_offscreen.py`: **14 aprovados** em 1280×800 e 1024×680;
- `pyside6-qmllint`: aprovado sem diagnóstico;
- smoke real por `spawn`: início, encerramento forçado e segunda execução aprovados;
- inspeção visual: Transcrever, Histórico, Configurações, Ajuda, Sobre, avisos de
  terceiros, resultado concluído e melhoria não concluída aprovados;
- chamadas pagas e acessos a credenciais: zero.

Os smokes do código-fonte foram complementados pelos smokes dos dois pacotes congelados
descritos abaixo.

## Gate do processo empacotado

Para cada plataforma:

- [x] processo filho congelado inicia por `spawn`;
- [x] fixture curta retorna resultado;
- [x] fixture incooperativa é encerrada no limite;
- [x] controlador fica livre;
- [x] segunda fixture conclui;
- [x] nenhum filho permanece vivo;
- [x] teste não acessa rede, Keychain ou API.

## macOS

- [x] commit/tag registrados;
- [x] host e Python são arm64;
- [x] bundle ID e versões corretos;
- [x] recursos, licenças, fontes, Ajuda e QML presentes;
- [x] yt-dlp embutido responde;
- [x] abertura normal permanece viva por pelo menos cinco segundos;
- [x] todos os Mach-O contêm arm64;
- [x] macOS mínimo não excede 12.0;
- [x] assinatura Developer ID contém timestamp e runtime;
- [x] `get-task-allow` ausente;
- [x] submissão do app `Accepted`, sem problemas;
- [x] ticket do app grampeado;
- [x] submissão do DMG `Accepted`, sem problemas;
- [x] ticket do DMG grampeado;
- [x] Gatekeeper aceita app e DMG;
- [x] ZIP e DMG contêm o mesmo app aprovado.

### Execução macOS — 31 de julho de 2026

- origem: tag `v0.1.2`, commit `c17dbd6b3e672fef0ce075b1ad1bd0290718ee00`;
- ambiente final: macOS arm64, Python.org 3.13.0 executado em arm64, PyInstaller
  6.21.0 e PySide6 6.9.3;
- inventário: 233 Mach-O, todos arm64; 141 com mínimo 11.0 e 92 com mínimo 12.0;
- abertura normal pelo LaunchServices: processo vivo após sete segundos e encerrado sem
  deixar processo;
- submissão final do app: `07c957d6-c906-436b-928a-240de113ade3`, `Accepted`, zero
  problemas;
- submissão final do DMG: `a5c3d5ad-51e9-4a98-85ee-7908d250cced`, `Accepted`, zero
  problemas;
- `CDHash` do app-fonte e do app montado no DMG:
  `c58e36393e1148a532997208cb0d35dec854827b`;
- o validador de notarização aprovou app, app extraído do ZIP e DMG final.

Um primeiro candidato, construído com o Python 3.13 do Homebrew, foi aceito pela Apple na
submissão `5901d8fb-1b36-4cd1-a889-733dd372ffa5`, mas reprovado pelo gate da release:
61 Mach-O exigiam macOS 15.0. Seus pacotes não foram publicados. O build final usou um
ambiente novo cuja compatibilidade efetiva foi verificada antes de nova assinatura e nova
submissão.

## Windows

- [x] workflow executado em Windows x64 a partir de `v0.1.2`;
- [x] ZIP contém uma única pasta portátil;
- [x] `São Francisco.exe` abre antes e depois da compactação;
- [x] smoke do processo congelado passa;
- [x] yt-dlp, FFmpeg, ffprobe e Deno respondem;
- [x] Ajuda, assets, QML, licenças e `LEIA-ME.txt` presentes;
- [x] pacote não depende do checkout ou Python instalado;
- [x] versão exibida é 0.1.2.

O workflow nativo `windows-latest` executou no mesmo commit e terminou com sucesso no
run [30598945728](https://github.com/pedblan/sao_francisco/actions/runs/30598945728).
O artefato baixado foi desembrulhado e o ZIP interno passou novamente pela verificação de
integridade antes da publicação.

## GitHub

- [x] tag anotada aponta para o commit aprovado;
- [x] release começou como rascunho;
- [x] notas descrevem benefícios e limitações sem jargão indevido;
- [x] somente os quatro ativos previstos foram enviados;
- [x] release está público e não é prerelease;
- [x] cada download responde;
- [x] downloads públicos têm os mesmos tamanhos e SHA-256 locais.

O release [São Francisco 0.1.2](https://github.com/pedblan/sao_francisco/releases/tag/v0.1.2)
foi publicado em 31 de julho de 2026. Os quatro ativos foram baixados novamente; os três
pacotes e `SHA256SUMS.txt` ficaram byte a byte idênticos aos candidatos locais.

## WordPress.com

- [x] site e página resolvidos sem ambiguidade;
- [x] conteúdo bruto e campos imutáveis fotografados;
- [x] índices, tipos e hashes dos blocos registrados;
- [x] diff mínimo apresentado;
- [x] usuário confirmou o diff concreto;
- [x] escrita usou trava otimista;
- [x] nenhum warning de conteúdo;
- [x] conteúdo não alvo dentro do bloco composto permaneceu byte a byte intacto;
- [x] campos imutáveis permaneceram idênticos;
- [x] página está pública;
- [x] links renderizados abrem os downloads 0.1.2 corretos.

A página [São Francisco](https://pedblan.wordpress.com/sao-francisco/) contém um único
bloco superior `core/group`. Por isso, a substituição do bloco foi protegida por
`modified`, `content_hash` e `block_hash`, e o patch literal foi verificado antes e depois
da escrita:

- SHA-256 bruto original:
  `1c2601f64d3b490a6579f82eff4a08e7216d37d017e9d7d307eb2cda3a9201fb`;
- SHA-256 bruto publicado:
  `11a8c25710c052ea5e161cd30812583938c8b75a4ea11c8c9686b9e9617fea83`;
- `content_hash` anterior: `d25b6ec2849b28a7662ea89eace35b5534235fa7`;
- `content_hash` posterior: `f3c516f2ae3a32b52aaeb1c7cd591493784e1400`;
- operação: bloco 0, `core/group`; onze trocas literais de versão, uma troca do aviso de
  notarização e uma inserção factual de novidades;
- `_content_warnings`: vazio;
- título, slug, status, autor, data, imagem, resumo, ordem, template e comentários:
  invariantes.

## Registro de execução

As evidências posteriores ao congelamento da tag devem ser preservadas no diretório local
ignorado `dist/release-evidence-0.1.2/`, para não alterar o commit que originou os
artefatos. Preencher ali durante o fluxo:

```text
Commit: c17dbd6b3e672fef0ce075b1ad1bd0290718ee00
Tag: v0.1.2
Python/Qt/PyInstaller macOS: Python 3.13.0 / PySide6 6.9.3 / PyInstaller 6.21.0
Workflow Windows: https://github.com/pedblan/sao_francisco/actions/runs/30598945728
ID da submissão do app: 07c957d6-c906-436b-928a-240de113ade3
ID da submissão do DMG: a5c3d5ad-51e9-4a98-85ee-7908d250cced
SHA-256 DMG macOS: 9cb90b4ecd8fe159c038c5abffc0cafe4d95ec2d198a30cd2efc03ea2bbf3a30
SHA-256 ZIP macOS: c6d982ccdecabe0b265c32b0b552e4cda48d4bff79736dd94646d66c1c8fd008
SHA-256 ZIP Windows: 82de8fc12f9d4f08741d98e74572242df632266815656c11c4ac6fd7aa39f435
URL do release: https://github.com/pedblan/sao_francisco/releases/tag/v0.1.2
Página WordPress: https://pedblan.wordpress.com/sao-francisco/
Blocos WordPress alterados: índice 0, core/group, por patch literal confirmado
Chamadas pagas: 0
Limitações: sem macOS Intel/universal; pacote Windows sem assinatura comercial
```
