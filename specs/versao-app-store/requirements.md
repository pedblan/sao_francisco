# Requisitos — próxima versão para a Mac App Store

**Documento histórico:** a Mac App Store foi descartada pelo autor em 29/08/2026.
Os requisitos vigentes estão em [distribuição comercial](../distribuicao-comercial/spec.md).
O conteúdo abaixo preserva a proposta anterior e não autoriza sua implementação.

## Editorial, marca e modelo comercial

### AS-ED-01 — frase da tela Sobre

A tela Sobre deve exibir exatamente a frase aprovada em `spec.md`. O link da página de
autor deve conservar rótulo e nome acessível que deixem claro que abrirá um site externo.

### AS-ED-02 — coerência entre preço e licença

Todas as superfícies pertinentes devem afirmar, de modo coerente, que o código-fonte do
São Francisco continua aberto sob a licença MIT. A busca inclui QML, Ajuda, README,
`LICENSE`, metadados de pacote, avisos, ficha da loja e textos de release.

O texto não deve sugerir que o pagamento na App Store revoga, restringe ou substitui a
MIT, nem confundir a licença do app com as licenças dos componentes de terceiros.

### AS-ED-03 — preço da loja

O app será vendido por preço fixo configurado no App Store Connect. O bundle não deve:

- fixar ou prometer o preço da App Store;
- implementar checkout, assinatura, crédito ou compra dentro do app;
- exibir licença própria no primeiro uso;
- exigir chave de ativação do São Francisco.

### AS-ED-04 — página de autor

O link da página do autor é informativo. Antes da submissão, a ficha e o link devem ser
revistos contra as regras do storefront escolhido. O aplicativo não deve afirmar que a
compra de livro desbloqueia funcionalidade.

## Licenças e avisos

### AS-LI-01 — parágrafo removido

As cópias raiz e empacotada de `THIRD_PARTY_NOTICES.md` devem permanecer idênticas e não
conter o parágrafo iniciado por **Antes de publicar um instalador**.

### AS-LI-02 — inventário derivado do artefato

O build da loja deve produzir um inventário automatizado do bundle final com executáveis,
bibliotecas, frameworks, versões, origem, licença, textos exigidos e hashes. A nota
interna de build não deve ser mostrada ao usuário, mas o inventário deve alimentar os
avisos distribuídos.

### AS-LI-03 — continuidade da licença MIT

`LICENSE` e `project.license` devem permanecer MIT. README, Sobre, Ajuda, repositório e
metadados da loja devem apontar para a mesma licença, sem inserir termos adicionais que
restrinjam os direitos da MIT. A decisão de cobrar pelo binário oficial não altera este
requisito.

### AS-LI-04 — Qt for Python

O candidato da loja deve usar wheels comerciais de Qt for Python cobertos
por licença válida ou apresentar parecer jurídico e evidência de conformidade integral
com a opção LGPL/GPL. A origem e edição dos wheels devem constar no manifesto.

Usar os wheels comunitários por hábito, omitir o aviso ou presumir compatibilidade com a
loja reprova o gate.

### AS-LI-05 — FFmpeg e ferramentas

FFmpeg/ffprobe incorporados devem ter configuração reprodutível e auditável. O build
registra `-version` e `-buildconf`, não pode habilitar componente GPL sem uma decisão
jurídica compatível e deve incluir textos/código-fonte/oferta exigidos pela licença
efetiva.

### AS-LI-06 — nenhum apagamento de avisos

Retirar o parágrafo dirigido ao desenvolvedor não autoriza remover nomes, atribuições,
licenças completas, instruções de substituição/relink ou ofertas de fonte exigidas pelos
componentes efetivamente distribuídos.

## Ajuda, preços e privacidade

### AS-AJ-01 — preços externos

A seção de custos não deve conter tabelas ou valores unitários de preço por token,
segundo, minuto, arquivo ou modelo. Deve conter links às páginas oficiais de preços da
OpenAI e do Gemini e declarar que preços, impostos, gratuidade, descontos e limites são
controlados pelo provedor.

### AS-AJ-02 — estimativa no trabalho

Estimativas já calculadas pelo aplicativo podem continuar visíveis quando baseadas em
dados conhecidos, desde que:

- sejam rotuladas como estimativa e nunca como cobrança final;
- identifiquem o provedor responsável;
- não sejam usadas para vender créditos;
- não mostrem valor quando o cálculo não for confiável;
- o histórico preserve a base do cálculo e a data/revisão do catálogo usada.

### AS-AJ-03 — BYOK e revisão

A Ajuda deve explicar que a compra do app não inclui créditos de API e que ChatGPT/Gemini
de consumo e APIs são serviços distintos. Notas de App Review devem fornecer uma conta
ou roteiro de teste, explicar o BYOK e declarar que as chaves não destravam uma modalidade
do aplicativo.

### AS-PR-01 — política acessível

Uma política de privacidade pública e estável deve estar:

- vinculada no App Store Connect;
- acessível pela Ajuda ou Sobre;
- traduzida ou acompanhada por uma versão compreensível nos idiomas da ficha;
- coerente com a transmissão de mídia/texto a OpenAI ou Google, armazenamento local,
  retenção, exclusão, suporte e logs.

### AS-PR-02 — consentimento informado

Antes da primeira chamada a cada provedor, a interface deve informar que o conteúdo será
enviado ao terceiro selecionado e apontar para a política aplicável. O consentimento e a
escolha do provedor devem ser explícitos; trocar o provedor exige informação equivalente.

A aceitação deve ser persistida por provedor e versão da política. Mudança material na
política invalida a aceitação anterior. Cancelar o diálogo não inicia processo nem chamada
remota e conserva o item como rascunho, sem colocá-lo na fila.

### AS-PR-03 — declarações da loja

As respostas de App Privacy devem incluir as práticas do aplicativo e dos SDKs integrados.
O `PrivacyInfo.xcprivacy`, quando aplicável, deve estar em `Contents/Resources/` e ser
validado como plist. Dados de trabalhos reais, chaves, URLs privadas, transcrições e logs
pessoais não podem entrar no bundle nem em evidências públicas.

## Idiomas de transcrição

### AS-ID-01 — registro único de capacidades

Deve existir um registro tipado, testável e versionado que relacione, no mínimo:

- provedor;
- modelo e endpoint;
- código canônico BCP 47/ISO usado internamente;
- rótulo localizado;
- valor e campo enviados à API;
- suporte a detecção automática;
- fonte oficial e data da última verificação.

QML, backend e pipeline devem consumir o mesmo registro.

### AS-ID-02 — lista dependente do contexto

O menu deve mostrar somente a interseção documentada para a seleção atual de
provedor/modelo. **Detectar automaticamente** aparece somente quando o contrato real do
adaptador permitir omitir a dica de idioma.

### AS-ID-03 — mapeamentos conhecidos

O registro inicial deve cobrir todos os idiomas atuais, mas aplicar estes limites:

- `ca` não é oferecido para Gemini enquanto não houver fonte oficial que o aceite;
- hebraico permanece `he` na UI e pode ser convertido para `iw` no adaptador Gemini;
- chinês deve usar o grau de especificidade aceito pelo endpoint, sem inventar variante;
- códigos regionais só aparecem quando documentados pelo modelo/endpoint.

### AS-ID-04 — mudança incompatível

Se o usuário trocar provedor/modelo e o idioma deixar de ser válido, a seleção volta para
automático e a GUI anuncia: **O idioma anterior não é compatível com este modelo; a
detecção automática foi selecionada.**

### AS-ID-05 — falha defensiva

Payload com idioma ausente do registro deve ser recusado antes de iniciar trabalho ou
chamada remota, com mensagem pública localizada. Não deve haver fallback silencioso no
pipeline.

### AS-ID-06 — manutenção

Mudança de catálogo exige atualizar fonte/data, testes de contrato e texto exibido. A
lista não deve depender de conhecimento memorado do modelo ou de scraping em execução.

## Fila de fontes

### AS-FI-01 — múltiplas fontes

O seletor aceita vários arquivos. A entrada por URL, se autorizada para a variante,
aceita vários endereços HTTP(S), um por linha. Cada fonte válida vira um item independente.

### AS-FI-02 — fotografia das opções

No momento de adicionar/iniciar o lote, cada item deve persistir fonte, provedor, modelo,
idioma, formatos, destino, preferência por legendas, tempos, melhoria e locale da UI.
Editar o formulário depois disso não altera itens já enfileirados.

### AS-FI-03 — validação do lote

Antes de enfileirar:

- normalizar URLs apenas de modo que não altere seu significado;
- rejeitar scheme não HTTP(S), caminho ilegível e fonte inexistente;
- listar cada erro sem descartar as fontes válidas do mesmo lote;
- detectar duplicata exata dentro do lote e contra itens ainda ativos;
- reservar nomes de saída de forma atômica.

Nenhuma validação pode fazer chamada paga.

### AS-FI-04 — estados

Os estados públicos mínimos são:

`aguardando`, `aguardando_memoria`, `preparando`, `executando`, `cancelando`, `pausado`,
`concluido`, `falhou` e `cancelado`.

O estado persistido deve continuar distinguindo tentativa remota incerta, original pronto,
melhoria incompleta e falha de exportação.

### AS-FI-05 — ações por item

- item aguardando pode ser cancelado/removido sem criar processo;
- item ativo pode ser cancelado sem afetar os demais;
- item falho/pausado/cancelado pode usar o fluxo de retomada existente;
- item concluído pode abrir cada saída e ser ocultado da fila sem apagar arquivos;
- **Cancelar todos** requer confirmação e não remove resultados concluídos.

Reordenação não é requisito desta versão.

### AS-FI-06 — ordem e término

A admissão é FIFO entre trabalhos elegíveis. Um item bloqueado apenas por memória ou
limite do provedor não deve impedir indefinidamente outro item mais leve e elegível; esse
desvio deve ser registrado. Término fora de ordem não pode associar progresso/saídas ao
item errado.

### AS-FI-07 — reinício

Depois de queda ou fechamento, itens não iniciados continuam aguardando e itens ativos
seguem o contrato de reconciliação existente. O app nunca repete automaticamente uma
chamada paga cujo resultado ficou incerto.

## Paralelismo e recursos

### AS-PA-01 — agendador central

Somente um agendador pode admitir processos. A restrição atual de um único processo ativo
deve ser substituída sem criar vários controladores concorrentes sobre a mesma fila.

### AS-PA-02 — memória observável

O agendador deve obter memória física total e memória disponível por API compatível com
macOS. A medição e a estimativa usadas em cada decisão devem poder aparecer em log técnico
local sanitizado.

### AS-PA-03 — reserva e estimativa

A admissão exige:

`memória disponível - reserva de segurança >= estimativa do pico do novo trabalho`.

Reserva, estimativa mínima/máxima e fatores por estágio devem ser configuráveis em código
e definidos por benchmark. O algoritmo deve ser conservador quando duração ou codec forem
desconhecidos.

### AS-PA-04 — teto

O modo padrão é **Automático**. Se houver controle manual, ele significa teto, não promessa
de paralelismo. O máximo absoluto deve impedir explosão de processos mesmo em máquinas
com muita RAM.

### AS-PA-05 — limites de provedor

O número de chamadas remotas concorrentes deve ser separado do número de preparações
locais. Erros 429/limite não autorizam retry automático pago nem crescimento de
concorrência. Backoff só pode ocorrer antes de nova chamada e de acordo com o contrato de
retomada.

### AS-PA-06 — pressão durante execução

Pressão de memória suspende novas admissões e muda os itens elegíveis para
`aguardando_memoria`. O sistema não mata à força um job saudável apenas para respeitar a
estimativa. Situação crítica do sistema deve gerar aviso e permitir cancelamento humano.

### AS-PA-07 — isolamento e atomicidade

Cada trabalho tem diretório, manifesto, canal, evento de cancelamento e processo próprios.
Atualizações de manifesto e reserva de nomes devem ser atômicas entre processos. Um job
não pode fechar fila/canal de outro.

### AS-PA-08 — encerramento

Ao sair, o app deve solicitar cancelamento, respeitar o limite de cinco segundos por
processo incooperativo dentro de um limite global definido, encerrar os restantes e provar
que não deixou filhos. A GUI não pode desaparecer mantendo transcrições ocultas.

### AS-PA-09 — disco

O scheduler deve estimar espaço temporário e de saída antes de admitir. Falta de espaço
pausa/reprova somente o item afetado e não corrompe outros manifestos.

## Internacionalização

### AS-IN-01 — fonte única

Strings de primeira parte não devem permanecer espalhadas como literais não traduzíveis
em QML e Python. Devem usar IDs estáveis, contexto e placeholders nomeados/posicionais.

### AS-IN-02 — aprovação do português

`textos-gui-pt-BR.md` deve ser revisado pelo autor antes da extração para catálogos. Uma
mudança posterior no português invalida somente traduções dos IDs alterados, que voltam
ao estado pendente.

### AS-IN-03 — idiomas da interface

O bundle contém `pt-BR`, `en`, `fr`, `es`, `de`, `ru`, `ja` e a variante chinesa aprovada.
Seleção inicial usa o locale do sistema quando disponível, com fallback para `pt-BR`. O
usuário pode escolher e persistir outro idioma.

### AS-IN-04 — separação de conceitos

Idioma da interface e idioma do conteúdo transcrito são controles independentes. Trocar a
interface não muda payloads de trabalhos já enfileirados nem o idioma da transcrição.

### AS-IN-05 — placeholders e plurais

Contagens, caminhos, nomes, percentuais, moedas e atalhos devem usar placeholders e
plurais do sistema de tradução. Não se deve montar frases traduzíveis por concatenação.

### AS-IN-06 — acessibilidade e conteúdo longo

Nomes acessíveis, tooltips, diálogos, mensagens de erro, toasts, notificações, menus,
filtros, estados, Ajuda e avisos de terceiros entram no catálogo. Nomes próprios, IDs de
modelo, caminhos, extensões e textos integrais de licenças não são traduzidos sem base
oficial.

### AS-IN-07 — layout

Cada locale deve passar em 1280×800 e 1024×680, escala 100% e 200%, tema claro/escuro se
ambos existirem, teclado e pseudolocale expandida em ao menos 35%. Japonês/chinês devem
quebrar linhas sem espaços; nenhum controle essencial pode ser cortado.

## Mac App Store e sandbox

### AS-MS-01 — alvo separado

O build da Mac App Store deve ter configuração, entitlements, certificado/perfil e
manifesto separados do build Developer ID. Não se promove um DMG notarizado existente
para a loja.

### AS-MS-02 — bundle autocontido

O `.app` não pode depender de Python, Qt, FFmpeg, ffprobe, yt-dlp, Deno, Homebrew ou outro
programa do sistema. Recursos opcionais necessários à funcionalidade aprovada devem estar
presentes no bundle na submissão.

### AS-MS-03 — sandbox e arquivos

Fontes e destinos externos ao container só podem ser acessados por painel do sistema e
entitlement adequado. Persistência depois do relançamento usa security-scoped bookmarks,
com chamadas balanceadas de início/fim de acesso. Processos filhos recebem acesso de modo
documentado e testado.

### AS-MS-04 — rede

O bundle pode iniciar conexões como cliente somente para provedores documentados e, se a
rota por URL for aprovada, fontes autorizadas. Não abre listener. Toda conexão deve usar
TLS e respeitar timeout/cancelamento.

### AS-MS-05 — URL condicionada

T08–T10 estão suspensas conforme a decisão registrada em `spec.md` em 29/08/2026. A retomada
exige escolha explícita do autor entre uma edição somente de arquivos locais e uma edição
com fontes autorizadas, além dos demais gates. Este requisito não autoriza remover URLs
do app atual nem iniciar implementação, build ou submissão.

Se escolhida a edição local, controles, backend exclusivo, dependências exclusivas e
Ajuda de download por URL devem ficar ausentes do artefato da loja. Essa exclusão é um
critério de engenharia desta spec; não deve remover conversão de arquivos locais.

Se escolhida a edição remota, registrar fontes, operações permitidas e evidências de
autorização compatíveis com 5.2.2/5.2.3, e limitar o comportamento real a esse escopo.
Validar inclusive redirecionamentos, retomadas e entradas fora da GUI. Fontes sem
evidência não podem ser habilitadas por um checkbox de direitos do usuário.

Renomear “YouTube” para “streaming”, esconder o controle QML ou apagar temporários depois
da transcrição não satisfaz o requisito. Consentimento de envio à API não substitui a
autorização da fonte. Interface, Ajuda e notas da revisão devem descrever o fluxo real.

### AS-MS-06 — subprocessos

Todo helper executável deve estar dentro do bundle, assinado com a identidade correta e
compatível com sandbox. Nenhum processo pode sobreviver ao encerramento sem consentimento
e mecanismo explícito permitido pela Apple.

### AS-MS-07 — Keychain

Salvar, ler, substituir e remover as duas chaves deve funcionar no pacote sandboxed,
inclusive após atualização. Chaves não entram em argumentos de processo, fila, logs,
crash report, clipboard automático ou manifesto.

### AS-MS-08 — metadados e políticas

Bundle ID, versão curta, build, categoria, deployment target, copyright, idiomas,
privacy manifest, export compliance e ficha do App Store Connect devem ser coerentes. O
build enviado usa certificado **3rd Party Mac Developer Application**/equivalente vigente
e perfil/cadeia exigidos pelo fluxo atual da Apple, não Developer ID.

### AS-MS-09 — atualizações

A variante da loja não contém atualizador próprio nem link para baixar versão executável.
Atualizações chegam pela Mac App Store.

### AS-MS-10 — variante paga completa

Depois da compra, todos os recursos incluídos na edição da loja estão disponíveis. Chaves
de provedor podem ser necessárias para executar chamadas, mas não funcionam como licença
ou desbloqueio do São Francisco.

## Saídas e DOCX

### AS-DO-01 — contrato semântico

O DOCX deve preservar, conforme o tipo de resultado:

- ordem e integralidade dos segmentos aceitos;
- identificação de falante, quando disponível;
- marcações de tempo quando solicitadas;
- parágrafos e quebras definidos pelo exportador;
- Unicode dos idiomas suportados;
- distinção explícita entre original e texto melhorado.

### AS-DO-02 — regularidade estrutural

Cada DOCX deve:

- ser ZIP/OPC íntegro;
- conter content types, relationships e `word/document.xml` válidos;
- abrir e salvar por `python-docx` sem reparo;
- abrir no LibreOffice e Microsoft Word sem aviso de corrupção/reparo;
- não conter caminho local, chave, prompt, resposta bruta, log ou mídia privada fora do
  conteúdo deliberadamente exportado.

### AS-DO-03 — concorrência

Trabalhos paralelos com nomes iguais devem receber destinos distintos e determinísticos.
Nenhum DOCX pode incorporar partes, propriedades ou saídas de outro job.

### AS-DO-04 — comparação

Validação compara conteúdo normalizado e estrutura semântica, não os bytes do ZIP, pois
timestamps e ordenação interna podem variar legitimamente.

## Testes e observabilidade

### AS-TE-01 — matriz finita

A matriz em `validation.md` define o significado de cobertura completa da GUI. Qualquer
estado/ação adicionado deve ser incluído antes de implementação.

### AS-TE-02 — testes sem custo primeiro

GUI, scheduler, falhas, retomada, formatos e maior parte dos idiomas devem usar fixtures
locais e provedores falsos. Testes reais só começam depois da suíte local verde.

### AS-TE-03 — orçamento pago

Antes de chamadas reais, registrar modelos, idiomas, duração total, finalidade, teto de
chamadas e teto em dólares. A proposta inicial é até 40 chamadas com áudio de 5–8 segundos
e teto total de US$ 1,00. O usuário deve aprovar ou alterar o orçamento.

### AS-TE-04 — logs sanitizados

Logs técnicos podem registrar IDs internos, estados, memória, RSS, duração, modelo e
códigos de erro. Devem omitir chave, conteúdo transcrito, URL com query, caminho completo
quando privado e corpo de resposta do provedor.

### AS-TE-05 — pacote real

Testes no código-fonte não substituem o pacote sandboxed. Seletores, bookmarks, Keychain,
helpers, rede, fila, saída, Word e encerramento devem ser exercitados no build assinado
que será enviado.
