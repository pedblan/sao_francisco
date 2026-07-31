# Especificação — release 0.1.2

**Estado:** implementada em código-fonte; pacotes e publicação pendentes
**Versão:** `0.1.2`
**Tag:** `v0.1.2`
**Repositório:** `pedblan/sao_francisco`
**Origem funcional:** `specs/cancelamento-e-recusas-editoriais/`

## Objetivo

Publicar uma versão de correção do São Francisco que entregue o novo comportamento de
cancelamento e melhoria opcional em pacotes verificáveis, sem repetir as fragilidades de
empacotamento e publicação da versão 0.1.1.

A entrega inclui:

- um DMG e um ZIP nativos para macOS Apple Silicon;
- um ZIP portátil para Windows x64;
- assinatura Developer ID, hardened runtime, notarização e ticket grampeado nos artefatos
  macOS;
- um GitHub Release público com notas e hashes coerentes;
- a troca mínima do link e das informações factuais da versão na página existente do
  WordPress.com.

## Resultado de produto

A versão 0.1.2 deve tornar distribuíveis as mudanças já especificadas em
`cancelamento-e-recusas-editoriais`:

- o original é exportado antes da melhoria opcional;
- uma resposta editorial textual não é recusada por heurísticas semânticas;
- falha ou timeout da melhoria preserva o original;
- chamadas pagas não recebem retry automático;
- cancelar uma chamada incooperativa termina em até cinco segundos mais pequena margem e
  libera outra transcrição;
- a interface distingue transcrição pronta, melhoria incompleta e cancelamento.

O release não promete transcrição perfeita. A referência continua sendo a transcrição
original, e a Ajuda continua orientando a conferência de nomes, números e trechos pouco
claros.

## Matriz da release

| Alvo | Obrigatório | Ambiente | Formato público | Assinatura |
| --- | ---: | --- | --- | --- |
| macOS arm64 | sim | macOS arm64, Python arm64 | DMG e ZIP | Developer ID e notarização |
| macOS x86_64 | não | indisponível | nenhum | fora do escopo |
| Windows x64 | sim | GitHub Actions `windows-latest`, Python x64 | ZIP portátil | não assinado |

Não se deve renomear, converter nem apresentar um pacote de outra arquitetura como Intel,
universal ou Windows. O site e as notas devem mencionar somente os alvos efetivamente
publicados.

## Artefatos previstos

- `Sao-Francisco-0.1.2-macos-arm64.dmg`;
- `Sao-Francisco-0.1.2-macos-arm64.zip`;
- `Sao-Francisco-0.1.2-windows-x64.zip`;
- `SHA256SUMS.txt`;
- manifesto local de proveniência e evidências de notarização, sem segredos.

O ZIP macOS deve conter exatamente o mesmo `.app` notarizado e grampeado usado para criar
o DMG. O DMG deve conter um único `São Francisco.app` e o atalho para `/Applications`.

## Proveniência

1. Sincronizar `0.1.2` em todas as fontes de versão e nomes de artefato.
2. Aprovar código, specs e GUI antes do primeiro build completo.
3. Integrar a mudança na branch principal e identificar um único commit de release.
4. Criar a tag anotada `v0.1.2` nesse commit.
5. Construir cada plataforma a partir dessa tag ou do mesmo SHA.
6. Registrar ambiente, arquitetura, tamanho e SHA-256 depois da última alteração.
7. Publicar exatamente os bytes aprovados.

O worktree usado para gerar o candidato deve estar limpo. Builds feitos antes do commit de
release servem somente como smoke e não podem ser promovidos.

## Assinatura e notarização macOS

- identidade: `Developer ID Application: Pedro Duarte Blanco (TF9GPA5A6H)`;
- Team ID: `TF9GPA5A6H`;
- bundle ID: `com.pedblan.saofrancisco`;
- arquitetura: `arm64`;
- macOS mínimo: `12.0`;
- perfil do `notarytool`: `maestro-notary`, armazenado no Keychain.

O app deve ser assinado de dentro para fora, sem `codesign --deep` na assinatura, com
hardened runtime e timestamp. O app é submetido, aceito, grampeado e validado antes da
criação dos formatos públicos. O DMG final recebe assinatura própria, nova submissão,
ticket e validação. Qualquer alteração posterior invalida o candidato.

Os IDs de submissão, logs, hashes e contexto ficam em diretório de evidências ignorado pelo
Git. Nenhuma credencial ou resposta privada pode entrar no repositório, nos artefatos ou
nos logs.

## GitHub Release

O release deve ser preparado como rascunho enquanto faltar qualquer artefato ou gate. As
notas, em linguagem não técnica, devem destacar:

- cancelamento que realmente libera o aplicativo;
- transcrição original disponível mesmo se a melhoria falhar;
- remoção da recusa heurística de textos úteis;
- ausência de retry pago automático;
- plataformas e instruções de primeira abertura.

O texto deve declarar honestamente que macOS é assinado e notarizado e que o pacote
Windows não possui assinatura comercial. Depois da publicação, cada ativo será baixado e
comparado byte a byte com o candidato.

## WordPress.com

A página existente será localizada de forma inequívoca pelo conector WordPress.com. A
edição permitirá somente:

- trocar o URL de download da versão anterior pelo URL final de 0.1.2;
- substituir ou inserir um bloco isolado com versão, data e novidades factuais.

Título, slug, apresentação, pontuação, formatação, imagem, autor, categorias, tags,
homepage, menu e todos os blocos não destinados à release são imutáveis.

Antes da escrita, registrar `modified`, `content_hash` e hashes dos blocos, mostrar o diff
concreto e obter confirmação explícita do usuário. A escrita usará trava otimista. Depois,
reler a página, provar a invariância dos demais blocos e testar o link público.

## Fora do escopo

- pacote macOS Intel ou universal;
- instalador, assinatura Authenticode ou Microsoft Store para Windows;
- novos recursos além dos já descritos nas specs funcionais;
- redesign, revisão editorial ampla ou alteração de menu no WordPress;
- homepage, redes sociais ou anúncios;
- chamadas pagas automatizadas;
- reprocessar automaticamente o vídeo do incidente;
- substituir ou apagar releases anteriores.

## Critério de conclusão

A tarefa termina somente quando:

- todos os gates de código e GUI passarem;
- os processos descartáveis iniciarem e puderem ser recriados nos dois pacotes;
- os artefatos finais corresponderem à matriz, versão e SHA registrados;
- app e DMG macOS estiverem assinados, aceitos pela Apple, grampeados e aprovados pelo
  Gatekeeper;
- o release público e todos os downloads forem verificados;
- o WordPress contiver apenas o patch confirmado e o link renderizado funcionar;
- specs e manifesto refletirem as evidências finais.
