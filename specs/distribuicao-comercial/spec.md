# São Francisco — distribuição comercial multilíngue

**Estado:** interface multilíngue implementada; preparação comercial em andamento, sem publicação.

**Data:** 29 de agosto de 2026.

**Escopo autorizado em 29/08:** implementar tradução com inglês padrão, manter MIT,
preparar venda a US$ 5 e abrir cadastros para conclusão pelo autor. Não criar contas,
aceitar contratos, contratar serviços ou publicar. Ver [execução](implementacao.md)
e [roteiro de lançamento](../../LANCAMENTO.md).

## Objetivo e decisão

O autor decidiu deixar a Mac App Store de lado. A próxima entrega deve concentrar-se em
traduzir o aplicativo existente e oferecer pacotes oficiais pagos para Mac e Windows,
mantendo o código aberto sob MIT. A compra remunera a distribuição oficial, sem retirar
os direitos da licença. Não haverá assinatura recorrente de uso, DRM ou chave de ativação
do app.

Esta spec substitui o plano de execução de
[`versao-app-store`](../versao-app-store/spec.md), conservado como histórico. Não se deve
retomar sandbox, TestFlight ou submissão à Mac App Store a partir desse plano antigo.

A [pesquisa de lojas](lojas.md) distingue loja hospedada, marketplace e serviço de
pagamentos. A recomendação não equivale a aprovação da conta, do app ou do fluxo de URLs
por qualquer plataforma.

## Base observada

- Implementação em `codex/comercial-i18n-rtl`, base
  `3bc3f2aa4610207566a5a13f1e75ad019e523c81`; alterações documentais anteriores preservadas.
- A [release 0.1.2](../release-0.1.2/spec.md) documenta Mac Apple Silicon/arm64, DMG e ZIP,
  e Windows x64 em ZIP portátil. A mesma documentação registra Windows sem assinatura
  comercial; isso não demonstra prontidão de um futuro candidato assinado.
- O app atual aceita arquivos e URLs; yt-dlp baixa mídia e FFmpeg prepara áudio.
  Nenhuma função foi retirada ou renomeada nesta tarefa.
- O catálogo `SUPPORTED_INTERFACE_LOCALES` de
  `/Users/pedblan/Developer/maestro/core/i18n.py` foi inspecionado em 29/08/2026 para
  interpretar “as mesmas línguas do Maestro + árabe”. Não é prova de tradução já feita
  no São Francisco nem avaliação da qualidade dos catálogos do Maestro.

## Requisitos

### DC-01 — idiomas da interface

Uma distribuição por plataforma, contendo todos os idiomas; não criar um executável por
língua. Português brasileiro permanece a fonte editorial.

| Idioma | Locale de referência |
| --- | --- |
| Português brasileiro | `pt-BR` |
| Inglês | `en-US` |
| Alemão | `de-DE` |
| Espanhol | `es-ES` |
| Francês | `fr-FR` |
| Italiano | `it-IT` |
| Russo | `ru-RU` |
| Chinês simplificado | `zh-CN` |
| Árabe padrão moderno | `ar`, layout Qt RTL |

São nove idiomas, contando português. Japonês constava do pedido inicial, mas não está no
catálogo atual do Maestro: fica como opção adicional a confirmar, não como décimo idioma
automaticamente incluído. Árabe sem associação automática a um país. Inglês é o idioma
da primeira abertura e de fallback; seleção manual persistida prevalece nos reinícios.

### DC-02 — catálogo da GUI efetiva

O [inventário editorial anterior](../versao-app-store/textos-gui-pt-BR.md) fica preservado
como rascunho histórico. O [catálogo da GUI atual](../../TEXTOS_DA_GUI_ATUAL.md) contém
os textos implementados e separa-os de fila/paralelismo e controles futuros não entregues.

Aplicar à proposta editorial a frase Sobre já solicitada pelo autor, retirar a nota
interna dos avisos sem retirar licenças obrigatórias e substituir referências à compra
na App Store por distribuição oficial. A proposta de links para preços dos provedores
pode ser preservada, sem alegar uma proibição geral de mostrar preços. O pedido explícito
de tradução autoriza esta implementação; a revisão editorial humana continua possível
no Markdown, sem bloquear a tradução previamente autorizada.

### DC-03 — tradução sem mudança do processamento

Separar idioma da interface, idioma do conteúdo transcrito e idioma de eventual texto
editorial. Traduzir a GUI não adiciona suporte a idiomas nos provedores nem traduz
automaticamente as transcrições. Não mudar prompts, modelos, formatos de saída,
segmentação, custos, cancelamento ou retries nesta entrega por conveniência.

Preservar placeholders, plurais, atalhos, links, nomes de modelos e mensagens dinâmicas.
Usar inglês como padrão/fallback. Catálogo incompleto reprova a auditoria; mensagens
externas não reconhecidas e dados do usuário não são traduzidos por heurística. Locales
dos testes precisam estar contidos nos pacotes, não apenas disponíveis no checkout.

### DC-04 — árabe e texto bidirecional

Validar layout da direita para a esquerda, ordem de foco, menus, diálogos, acessibilidade,
quebras e glifos. URLs, paths, chaves, extensões e identificadores técnicos mantêm sua
direção apropriada. Testar misturas de árabe, caracteres latinos, números e timestamps.

A direção da GUI não pode inverter indevidamente a ordem ou a direção de uma transcrição
exportada. DOCX com conteúdo árabe precisa ser verificado separadamente em leitor real;
um teste com texto sintético não é prova de qualidade de transcrição pelo provedor.

### DC-05 — licença, produto e privacidade

Conservar MIT, autoria, repositório público, avisos e licenças de terceiros. Os termos da
loja não devem ser apresentados como se restringissem os direitos MIT. Auditar Qt/FFmpeg
e demais componentes no pacote real; o abandono da App Store não dispensa essas obrigações.

Compra de app e cobrança de OpenAI/Gemini são separadas. A ficha deve explicar o uso de
chaves próprias e que créditos de API não estão incluídos. Recibos e dados de compradores
pertencem ao sistema comercial, não ao pipeline; nunca incorporar chaves de API em
pacotes, catálogos, logs ou evidências. Não incluir nova telemetria comercial no app.

### DC-06 — URLs e conformidade do canal

Preservar o comportamento existente nesta tarefa, sem afirmar que seja
automaticamente aceito por outra loja. Não usar “streaming” para esconder download.
Antes de cadastrar o produto, revisar política do canal, termos das fontes e descrição
honesta do uso. Quando houver dúvida material, obter confirmação do canal mediante
autorização do autor, sem mensagens externas automáticas.

Notarização não é aprovação jurídica nem App Review. Exemplos de venda/teste devem usar
mídia própria ou legitimamente licenciada, sem prometer acesso irrestrito a serviços.
Se um canal exigir mudança funcional, decidir isso em tarefa própria antes da publicação.

### DC-07 — macOS fora da loja

Tomar arm64 como base de planejamento; não prometer Intel/universal sem candidato e teste.
Preservar a meta de compatibilidade existente somente se dependências e pacote a comprovarem.
Pacote deve abrir em máquina sem ferramentas de desenvolvimento e documentar/incorporar
dependências necessárias; não vender uma instalação que dependa de etapas omitidas.

Usar Developer ID, hardened runtime e timestamp; assinar de dentro para fora; persistir
IDs de notarização; exigir `Accepted`, logs sem problemas, ticket grampeado e Gatekeeper
aprovado. Testar download, abertura normal e atualização. Publicar os mesmos bytes testados.
Referência: [notarização da Apple](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution).

### DC-08 — Windows

Tomar x64 como base de planejamento. Construir e testar em Windows nativo/runner Windows,
sem usar execução no Mac como prova. Definir ZIP portátil ou instalador antes de congelar
os arquivos comerciais. Versão mínima suportada será declarada pelo candidato testado.

Exigir assinatura Authenticode pública e timestamp, com identidade e serviço de assinatura
ainda a escolher. Avaliar elegibilidade e custo antes de contratar; não presumir que um
serviço gratuito aceite todo projeto MIT comercial. Verificar assinatura, extração,
instalação/atualização quando aplicável, recursos e execução em conta limpa.

Isso não é o serviço de notarização da Apple e não garante ausência imediata de avisos
SmartScreen. Referência: [reputação de apps no Windows](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation).

### DC-09 — venda e atualizações

Preparar os canais examinados com recebimento documentado até o Banco do Brasil, inclusive
via intermediário, sem confundir elegibilidade com aprovação da conta. Preço definido:
US$ 5, compra única. Países, pessoa física/jurídica, reembolso e atualizações cobertas
dependem do cadastro. Proposta operacional: um produto com downloads Mac e Windows;
não liberar o Windows antes da validação nativa. Não prometer levantamento exaustivo de
todas as lojas existentes nem aceitação automática do produto.

Entregar arquivos identificados por versão, sistema e arquitetura, com hashes, instruções
e licença. Testar acesso pós-compra e re-download de atualização. A loja entregar um novo
arquivo não significa que o aplicativo tenha atualização automática; não criar updater
nesta versão. Preservar backup e links de compradores ao substituir arquivos públicos.

### DC-10 — comprovação

Revisar diff e executar testes pequenos primeiro: catálogos/placeholders, GUI em cada
locale e smoke do processamento já existente. Cobrir fluxos curtos e longos representativos,
erro/cancelamento, persistência, credenciais e DOCX nos dois sistemas. Nenhuma chamada
paga é necessária para traduzir. Builds locais e testes com fixtures estão autorizados;
testes reais pagos exigem amostra e teto de gasto antes da execução.

## Não objetivos desta versão reduzida

- Mac App Store, sandbox para a loja, TestFlight e App Review;
- fila nova, múltiplas URLs, paralelismo por RAM ou refatoração do pipeline;
- reescrita nativa, novos provedores/modelos ou novos formatos de exportação;
- DRM, ativação, assinatura de uso, créditos de API ou servidor de licenças;
- escolher outro canal e publicá-lo sem revisão humana;
- novas arquiteturas, remoção de releases antigos ou alteração de sites alheios;
- garantia de aceitação comercial, jurídica ou ausência de avisos de segurança.

As ideias de fila e paralelismo ficam conservadas no plano histórico para possível tarefa
futura; não foram implementadas nem silenciosamente incluídas na tradução.

## Plano em unidades independentes

| ID | Resultado | Branch proposta | Estado |
| --- | --- | --- | --- |
| C00 | direção comercial e pesquisa de lojas | documentação comercial | US$ 5/MIT definidos; ativação pendente |
| C01 | catálogo fiel à GUI atual | `codex/comercial-i18n-rtl` | produzido; editável pelo autor |
| C02 | internacionalização e layout RTL, sem mudar pipeline | `codex/comercial-i18n-rtl` | implementado e testado |
| C03 | catálogos traduzidos nos nove idiomas | `codex/comercial-i18n-rtl` | implementados; revisão linguística humana recomendada |
| C04 | candidato Mac assinado, notarizado e testado | `codex/comercial-macos` | proposta; depende de C03 |
| C05 | candidato Windows assinado e testado | `codex/comercial-windows` | proposta; depende de C03 e assinatura |
| C06 | canais elegíveis ativados, entrega e pós-download verificados | `codex/comercial-loja` | preparação documental pronta; ativação depende de C04/C05 e aprovação comercial |

C02/C03 foram reunidas pelo pedido explícito em uma entrega vertical de localização.
C04 e C05 continuam com gates próprios; candidato local não é release assinada. Cada
etapa terá amostra, limite de gasto/builds e aceite próprios.
Pausar diante de senha, Touch ID, Keychain ou outra autorização do sistema.

## Validação e condições de parada

As provas de código, GUI e pacote estão em [validação](validacao.md). Não foram testados
checkout, repasse real, aceitação do produto, transcrição paga ou pacote Windows nativo.

Antes de lançar:

- [ ] português e decisão final de idiomas aprovados;
- [ ] nove locales completos e GUI árabe RTL verificada em Mac/Windows;
- [ ] fluxos curtos/longos, cancelamento, dados e DOCX aprovados nos pacotes;
- [ ] identidade Windows, assinatura, notarização Mac e hashes comprovados;
- [ ] termos MIT/dependências, conteúdo remoto e políticas do canal reconciliados;
- [ ] recebimento no país da conta, taxas e obrigações fiscais confirmados;
- [ ] preço, países, reembolso, ficha e escopo de atualizações aprovados pelo autor;
- [ ] teste comercial autorizado, entrega e re-download demonstrados;
- [ ] publicação autorizada e bytes baixados iguais aos candidatos aprovados.

Parar se houver conflito de licença/política, conta inelegível, assinatura sem identidade
válida, corrupção de DOCX ou necessidade de mudança funcional além da tradução. Registrar
o problema e decidir uma unidade própria; não mascará-lo com mudança de rótulo ou de loja.
