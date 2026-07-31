# Requisitos — release 0.1.2

## Versão e origem

### RL-RV-01 — versão única

`pyproject.toml`, `sao_francisco.__version__`, metadados do app, textos do pacote Windows,
workflow de build, nomes dos artefatos, tag e título do release devem indicar `0.1.2`.

### RL-RV-02 — commit único

Os artefatos devem ser produzidos a partir do mesmo commit integrado à branch principal e
apontado por `v0.1.2`. O manifesto registra o SHA completo.

### RL-RV-03 — origem limpa

Nenhum candidato público pode ser construído de worktree sujo. Arquivos ignorados de
build e evidência não alteram a origem registrada.

## Gates antes do build

### RL-RG-01 — qualidade do código

Devem passar a suíte completa, Ruff, mypy, `git diff --check` e os testes focados do
incidente, sem rede e sem chamada paga.

### RL-RG-02 — QML e interface

Todos os QML devem passar pelo lint aplicável e carregar offscreen nos tamanhos padrão e
mínimo. Estados de transcrição pronta, melhoria incompleta, cancelando, cancelada e erro
devem permanecer legíveis, roláveis e operáveis por teclado.

### RL-RG-03 — processo congelado

Cada executável empacotado deve provar, com fixture interna sem rede, que:

- inicia um subprocesso pelo mecanismo usado em produção;
- recebe uma conclusão;
- encerra um subprocesso incooperativo dentro do limite;
- inicia outro subprocesso depois do cancelamento;
- não deixa processo órfão.

O smoke especial não substitui a abertura normal da GUI por pelo menos cinco segundos.

## macOS Apple Silicon

### RL-RM-01 — conteúdo

O `.app` deve conter QML, fontes, ícones, Ajuda, avisos e licenças, além do yt-dlp
embutido. FFmpeg e ffprobe continuam sendo dependências do sistema conforme o contrato
atual do macOS.

### RL-RM-02 — plataforma

Todos os Mach-O do app devem conter `arm64`; a versão mínima efetiva não pode exceder
macOS 12.0.

### RL-RM-03 — abertura

O app deve:

- passar o smoke interno;
- responder ao helper do yt-dlp;
- abrir normalmente por LaunchServices e permanecer vivo por pelo menos cinco segundos;
- abrir Ajuda e as rotas principais no pacote real.

### RL-RM-04 — assinatura

Todo código aninhado e o bundle devem usar a identidade Developer ID autorizada, timestamp
e hardened runtime, sem `get-task-allow`.

### RL-RM-05 — notarização

As submissões separadas do app e do DMG devem terminar em `Accepted` sem problemas. App e
DMG recebem e validam seus tickets. `codesign`, `stapler`, `spctl` e `hdiutil` devem
aprovar os artefatos finais.

### RL-RM-06 — identidade dos formatos

O ZIP público e o app contido no DMG devem derivar do mesmo app já notarizado e grampeado.
Nenhum formato pode reconstruir, reassinar ou alterar o app.

## Windows x64

### RL-RW-01 — runner nativo

O pacote deve ser construído e testado em runner Windows x64, a partir de `v0.1.2`.

### RL-RW-02 — conteúdo portátil

O ZIP deve incluir o executável, Qt e plugins necessários, FFmpeg, ffprobe, Deno, yt-dlp,
Ajuda, fontes, assets, licenças e `LEIA-ME.txt`. Não pode depender de Python ou Qt
instalado na máquina.

### RL-RW-03 — validação extraída

Depois de extrair o ZIP, o executável deve passar o smoke, o smoke do subprocesso e a
consulta ao yt-dlp; FFmpeg, ffprobe e Deno devem responder. O teste não pode executar o app
de dentro do ZIP.

### RL-RW-04 — comunicação honesta

Notas e página devem dizer que o pacote é para Windows 10 ou 11 x64, deve ser extraído por
completo e não possui assinatura comercial.

## Manifesto e integridade

### RL-RI-01 — manifesto

O manifesto deve registrar versão, commit, alvo, arquitetura, caminho, tamanho, SHA-256,
ambiente, estado de teste, assinatura e notarização.

### RL-RI-02 — hashes finais

`SHA256SUMS.txt` deve ser calculado somente depois de finalizar todos os artefatos. Os
hashes do manifesto, arquivo de somas, candidatos locais e downloads públicos devem ser
iguais.

### RL-RI-03 — privacidade

Pacotes e evidências não podem conter chaves, tokens, cookies, manifestos de trabalhos
reais, mídia, transcrições privadas, caches, logs pessoais ou arquivos do checkout.

## GitHub

### RL-RH-01 — rascunho primeiro

O GitHub Release permanece em rascunho enquanto faltar gate, ativo ou verificação. Tag,
título e versão devem corresponder.

### RL-RH-02 — ativos

O release contém exatamente os três pacotes previstos e `SHA256SUMS.txt`, sem arquivo
temporário, duplicado ou de arquitetura ambígua.

### RL-RH-03 — promoção e verificação

Depois de tornar o release público, abrir sua página, baixar cada ativo, verificar tamanho
e SHA-256 e testar os links. Falha parcial exige interromper a promoção e corrigir ou
restaurar o estado anterior.

## WordPress.com

### RL-RP-01 — alvo único

Site e página devem ser resolvidos para um único recurso antes da edição. Ambiguidade
bloqueia a escrita.

### RL-RP-02 — fotografia e diff

Antes da escrita, preservar conteúdo bruto, campos imutáveis, `modified`, `content_hash`,
índices, tipos e hashes dos blocos. Mostrar o patch mínimo e obter confirmação explícita.

### RL-RP-03 — escrita isolada

Usar operação de bloco com trava otimista; não reenviar o conteúdo completo. Somente URL,
versão, data e novidades confirmadas podem mudar.

### RL-RP-04 — prova posterior

Releitura deve confirmar:

- status público;
- URL de 0.1.2;
- texto factual aprovado;
- hashes iguais em todos os blocos não alvo;
- campos imutáveis idênticos;
- link de download renderizado e funcional.

## Recuperação

### RL-RC-01 — falha de build

Um candidato que falhar em qualquer gate fica reprovado e não é reutilizado. Novo build
exige uma hipótese ou correção concreta.

### RL-RC-02 — notarização retomável

Cada submissão é feita sem `--wait`; ID e hash são persistidos imediatamente. Queda de
rede retoma o mesmo ID com `info` ou `wait`, sem reenvio automático.

### RL-RC-03 — publicação externa

Antes de alterar estado público, registrar release e links atuais. Upload parcial, hash
divergente ou link quebrado bloqueiam a conclusão e exigem correção mínima ou rollback.
