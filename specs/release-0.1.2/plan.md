# Plano — release 0.1.2

## 1. Fechar o contrato

- registrar versão, tag, repositório, página e matriz de plataformas;
- revisar as specs funcionais e transformar pendências de empacotamento em gates;
- sincronizar fontes de versão e automações;
- revisar o diff para impedir mudanças independentes.

## 2. Aprovar o fonte

- executar testes focados do incidente;
- executar suíte completa, Ruff, mypy e `git diff --check`;
- executar lint QML e provas offscreen nos tamanhos aplicáveis;
- inspecionar visualmente capturas das rotas alteradas;
- criar smoke interno do subprocesso quando necessário para testar o pacote congelado;
- confirmar zero chamadas pagas.

## 3. Congelar a proveniência

- criar commit coerente na branch da correção;
- integrar o commit à branch principal;
- confirmar CI;
- criar e enviar a tag anotada `v0.1.2`;
- usar um checkout limpo da tag para cada build;
- registrar SHA, host, Python, Qt, PyInstaller e arquitetura.

## 4. Build macOS arm64

- executar uma vez o build-base num Python arm64 compatível com macOS 12;
- inventariar o `.app`;
- verificar recursos e ausência de dados privados;
- executar smoke, helper do yt-dlp e abertura normal;
- reprovar o candidato se o subprocesso congelado não iniciar ou não for recriável.

## 5. Assinar e notarizar macOS

- executar preflight online com a identidade e o perfil do Keychain;
- copiar o candidato para diretório imutável e registrar seu inventário;
- assinar código aninhado de dentro para fora e o app por último;
- submeter ZIP de transporte sem `--wait`, persistir ID e aguardar o mesmo ID;
- exigir `Accepted`, arquivar log, grampear e validar o app;
- criar ZIP público e DMG a partir do app grampeado;
- assinar e submeter o DMG, persistir ID, exigir `Accepted` e grampear;
- validar app, ZIP extraído e DMG com os scripts da skill;
- calcular hashes somente ao final.

## 6. Build Windows x64

- disparar o workflow no commit/tag de release;
- construir num runner Windows x64;
- testar o app antes e depois da compactação;
- verificar subprocesso, yt-dlp, FFmpeg, ffprobe e Deno;
- baixar o artefato do workflow;
- conferir nome, estrutura, versão e SHA-256.

Mac e Windows podem ser construídos em ordem diferente, mas só entram no manifesto depois
de ambos satisfazerem os respectivos gates.

## 7. Manifesto e revisão final

- gerar `release-manifest.json` local e `SHA256SUMS.txt`;
- executar o verificador de artefatos;
- revisar tamanhos, hashes, arquiteturas, assinatura e notarização;
- comparar código, specs e artefatos;
- confirmar que o worktree e os pacotes não contêm arquivos acidentais.

## 8. GitHub Release

- fotografar o release 0.1.1 e seus ativos como referência recuperável;
- criar release 0.1.2 em rascunho;
- enviar os três pacotes e `SHA256SUMS.txt`;
- conferir uploads, nomes, tamanhos e notas;
- publicar o rascunho;
- abrir o release e baixar cada ativo;
- exigir igualdade byte a byte com os candidatos.

## 9. WordPress.com

- descobrir o site e a página existentes;
- ler conteúdo bruto, campos e blocos com contexto de edição;
- identificar o bloco exato do download e o bloco de versão;
- montar e apresentar diff mínimo, com hashes e campos preservados;
- aguardar confirmação explícita;
- aplicar somente as operações confirmadas com trava otimista;
- reler, verificar invariantes e abrir a página pública;
- testar o link renderizado.

## 10. Encerramento

- preencher `validation.md` com comandos, IDs, hashes, URLs e limitações;
- confirmar que release e página estão públicos;
- preservar evidências locais ignoradas pelo Git;
- informar exatamente o que foi publicado e o que ficou fora do escopo.

## Condições de parada

- divergência de versão ou commit;
- teste funcional, visual ou de subprocesso vermelho;
- arquitetura diferente da declarada;
- identidade, perfil ou Gatekeeper reprovado;
- notarização `Invalid` ou com problemas;
- download público com hash divergente;
- ambiguidade ou mudança concorrente na página;
- qualquer segredo ou dado privado em pacote ou log.
