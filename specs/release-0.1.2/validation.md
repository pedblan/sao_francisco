# Validação — release 0.1.2

## Matriz de aceitação

| Gate | Evidência | Estado |
| --- | --- | --- |
| Versão 0.1.2 sincronizada | busca e testes de metadados | aprovado |
| Specs funcionais refletidas | revisão cruzada de specs e diff | aprovado |
| Testes, Ruff e mypy | logs dos comandos | aprovado |
| QML e interface | qmllint, offscreen e capturas | aprovado |
| Processo congelado macOS | smoke de conclusão, cancelamento e reutilização | pendente |
| Processo congelado Windows | smoke de conclusão, cancelamento e reutilização | pendente |
| macOS arm64 / mínimo 12.0 | `file`, `lipo` e `vtool` | pendente |
| App assinado e notarizado | `codesign`, ID, log, `stapler`, `spctl` | pendente |
| DMG assinado e notarizado | ID, log, `codesign`, `stapler`, `spctl`, `hdiutil` | pendente |
| ZIP macOS deriva do app grampeado | inventário e validação extraída | pendente |
| ZIP Windows portátil | workflow, extração e helpers | pendente |
| Manifesto e SHA-256 | verificador e hashes finais | pendente |
| GitHub Release público | URL, ativos baixados e hashes | pendente |
| WordPress mínimo e público | hashes dos blocos, URL e teste do link | pendente |

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

O smoke do código-fonte não aprova por si só o executável congelado. Os respectivos gates
permanecem pendentes até a execução dos pacotes.

## Gate do processo empacotado

Para cada plataforma:

- [ ] processo filho congelado inicia por `spawn`;
- [ ] fixture curta retorna resultado;
- [ ] fixture incooperativa é encerrada no limite;
- [ ] controlador fica livre;
- [ ] segunda fixture conclui;
- [ ] nenhum filho permanece vivo;
- [ ] teste não acessa rede, Keychain ou API.

## macOS

- [ ] commit/tag registrados;
- [ ] host e Python são arm64;
- [ ] bundle ID e versões corretos;
- [ ] recursos, licenças, fontes, Ajuda e QML presentes;
- [ ] yt-dlp embutido responde;
- [ ] abertura normal permanece viva por pelo menos cinco segundos;
- [ ] todos os Mach-O contêm arm64;
- [ ] macOS mínimo não excede 12.0;
- [ ] assinatura Developer ID contém timestamp e runtime;
- [ ] `get-task-allow` ausente;
- [ ] submissão do app `Accepted`, sem problemas;
- [ ] ticket do app grampeado;
- [ ] submissão do DMG `Accepted`, sem problemas;
- [ ] ticket do DMG grampeado;
- [ ] Gatekeeper aceita app e DMG;
- [ ] ZIP e DMG contêm o mesmo app aprovado.

## Windows

- [ ] workflow executado em Windows x64 a partir de `v0.1.2`;
- [ ] ZIP contém uma única pasta portátil;
- [ ] `São Francisco.exe` abre antes e depois da compactação;
- [ ] smoke do processo congelado passa;
- [ ] yt-dlp, FFmpeg, ffprobe e Deno respondem;
- [ ] Ajuda, assets, QML, licenças e `LEIA-ME.txt` presentes;
- [ ] pacote não depende do checkout ou Python instalado;
- [ ] versão exibida é 0.1.2.

## GitHub

- [ ] tag anotada aponta para o commit aprovado;
- [ ] release começou como rascunho;
- [ ] notas descrevem benefícios e limitações sem jargão indevido;
- [ ] somente os quatro ativos previstos foram enviados;
- [ ] release está público e não é prerelease;
- [ ] cada download responde;
- [ ] downloads públicos têm os mesmos tamanhos e SHA-256 locais.

## WordPress.com

- [ ] site e página resolvidos sem ambiguidade;
- [ ] conteúdo bruto e campos imutáveis fotografados;
- [ ] índices, tipos e hashes dos blocos registrados;
- [ ] diff mínimo apresentado;
- [ ] usuário confirmou o diff concreto;
- [ ] escrita usou trava otimista;
- [ ] nenhum warning de conteúdo;
- [ ] blocos não alvo mantiveram os hashes;
- [ ] campos imutáveis permaneceram idênticos;
- [ ] página está pública;
- [ ] link renderizado abre o download 0.1.2 correto.

## Registro de execução

As evidências posteriores ao congelamento da tag devem ser preservadas no diretório local
ignorado `dist/release-evidence-0.1.2/`, para não alterar o commit que originou os
artefatos. Preencher ali durante o fluxo:

```text
Commit:
Tag:
Python/Qt/PyInstaller macOS:
Workflow Windows:
ID da submissão do app:
ID da submissão do DMG:
SHA-256 DMG macOS:
SHA-256 ZIP macOS:
SHA-256 ZIP Windows:
URL do release:
Página WordPress:
Blocos WordPress alterados:
Chamadas pagas: 0
Limitações:
```
