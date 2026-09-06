# São Francisco — ponto de retomada

Atualizado em 29/08/2026. **Tradução implementada; lançamento ainda não publicado.**
Código MIT preservado. Preço-base definido: **US$ 5, pagamento único**, sem créditos de API.
Mac App Store fora do plano.

## O que está pronto

- Inglês como idioma inicial e fallback; seleção persistida em Settings → Interface language.
- Português, francês, espanhol, alemão, italiano, russo, chinês simplificado e árabe;
  nove idiomas no total. Árabe com layout da direita para a esquerda.
- Menus, cinco telas, Ajuda com onze tópicos, avisos, rótulos acessíveis e mensagens
  determinísticas localizados. Dados, caminhos, chaves e transcrições não são traduzidos.
- [Textos completos da GUI para editar](TEXTOS_DA_GUI_ATUAL.md).
- [Fichas de loja nos nove idiomas](specs/distribuicao-comercial/fichas-lojas.md).
- [Pesquisa de oito canais e recebimento no Banco do Brasil](specs/distribuicao-comercial/lojas-banco-do-brasil.md).
- [Provas e limitações da validação](specs/distribuicao-comercial/validacao.md): 141 testes,
  lint/tipagem, 108 capturas e candidato Mac com recursos conferidos.

O fluxo documentado mais simples é **loja → PayPal Brasil → Banco do Brasil**. A
[documentação do PayPal cita o BB](https://www.paypal.com/br/cshelp/article/como-fa%C3%A7o-para-adicionar-um-conta-banc%C3%A1ria-%C3%A0-minha-conta-do-paypal-help183).
Cadastro, titularidade, conversão cambial, taxas e primeiro repasse continuam pendentes.
Isso não significa depósito em dólares, US$ 5 líquidos ou aceitação garantida por uma loja.

## Amanhã: suas decisões e cadastros

As páginas abaixo foram solicitadas ao navegador do Codex. O aplicativo respondeu
`queued`: devem abrir quando esta tarefa estiver visível. Links diretos ficam aqui
caso a interface não preserve todas as abas. Nada foi preenchido ou enviado.

| Página | Ação / decisão |
| --- | --- |
| [PayPal — carteira](https://www.paypal.com/myaccount/money/) | confirmar conta brasileira, titular fiscal e vínculo com BB |
| [Lemon Squeezy — cadastro](https://app.lemonsqueezy.com/register) | prioridade para checkout/downloads com MoR; confirmar payout PayPal e aceite do produto |
| [Gumroad — cadastro](https://gumroad.com/signup) | conferir método oferecido à conta brasileira e custo total |
| [Ko-fi — cadastro](https://ko-fi.com/account/register) | loja simples; decidir como cumprir obrigações fiscais e de suporte |
| [itch.io — cadastro](https://itch.io/register) | classificar como Tools e decidir modalidade de pagamento |
| [Microsoft Store — tipo de conta](https://developer.microsoft.com/en-us/microsoft-store/register) | confirmar conta comercial e rota Windows; não submeter ZIP atual |
| [Payhip — termos](https://payhip.com/terms) | suspensa até esclarecer por escrito licença compatível com MIT |
| [Sellfy — planos](https://sellfy.com/pricing/) | decidir se vale a mensalidade; nenhuma contratação realizada |
| [Paddle — avaliação](https://www.paddle.com/pricing) | BB específico e integração de entrega ainda não confirmados |

Não é necessário abrir todas as lojas de uma vez. A preparação abrange os canais
examinados, mas cada ativação depende de suas condições reais. Perguntas prontas para
suporte estão na pesquisa; **não foram enviadas**.

Antes de completar cadastros, definir:

1. Pessoa física/jurídica e titularidade consistente entre loja, processador e BB.
2. E-mail público de suporte, privacidade e dados legais do vendedor — não enviar
   documentos ou dados bancários pelo chat se puder inseri-los diretamente na plataforma.
3. Reembolso, países, impostos no checkout e quais atualizações a compra cobrirá.
4. Um produto com downloads Mac/Windows ou fichas separadas; proposta preparada como
   produto único, sem liberar um sistema cujo pacote ainda não esteja aprovado.

[Rascunho técnico de privacidade](specs/distribuicao-comercial/privacidade-rascunho.md)
aguarda dados e revisão do autor; não serve ainda como política pública final.

## Candidato local: somente inspeção

[ZIP Mac Apple Silicon](build/i18n-candidate-final/Sao-Francisco-i18n-preview-macos-arm64.zip)
e [aplicativo](build/i18n-candidate-final/dist/São%20Francisco.app) produzidos nesta tarefa.
Assinatura **ad-hoc**, sem Developer ID e sem notarização. Versão interna ainda 0.1.2,
build 2: identifica a base, **não** uma nova release pública. Não enviar esse ZIP à loja
como produto comercial pronto. Artefatos em `build/` são locais e ignorados pelo Git.

SHA-256 do ZIP:

```text
fa1f8ae5b45f6833f3cf36674c85e5bd7a12ea68e8cba11bbb70272f60fa1739
```

## Gates técnicos antes da venda

- [ ] Resolver FFmpeg/ffprobe e Deno para instalação comercial: ainda externos ao bundle.
  Não depender silenciosamente do Homebrew/PATH do desenvolvedor. Distribuir com licença
  auditada ou oferecer instalação claramente documentada e testada.
- [ ] Completar inventário de componentes/licenças do pacote final, incluindo Qt/Python
  e obrigações de terceiros. MIT própria e licenças das fontes já acompanham o candidato.
- [ ] Congelar versão comercial, build, SHA e requisitos mínimos reais por sistema.
- [ ] Mac: Developer ID, hardened runtime, timestamp, notarização `Accepted`, ticket
  grampeado e Gatekeeper; pausar para autorização humana se o sistema solicitar.
- [ ] Windows: construir no runner Windows, validar execução/instalação nativas e
  assinar com Authenticode e timestamp. Certificado/serviço ainda a escolher.
- [ ] Microsoft Store, se elegível: preparar a rota de pacote aceita, instalador e
  assinatura exigidos; o ZIP portátil existente não comprova compatibilidade.
- [ ] Fazer prova final de GUI, arquivos locais/URLs autorizadas, fluxos curtos/longos,
  cancelamento/retomada e DOCX aberto em leitor real nos dois sistemas. Definir amostra
  e teto antes de qualquer consumo pago de API.
- [ ] Revisar fichas/privacidade, aprovar produto nas lojas e testar compra/download,
  atualização/re-download e repasse real ao BB, mediante autorização.
- [ ] Autorizar publicação e conferir que os arquivos baixados têm os hashes aprovados.

Receita Windows já existente: [.github/workflows/windows-release.yml](.github/workflows/windows-release.yml)
e [script PowerShell](scripts/build_windows_x64.ps1). Não foi disparada: este trabalho
ainda é local, sem commit/push, e um build da branch remota antiga não conteria a tradução.
Primeiro revisar/congelar as mudanças e autorizar o envio; depois executar o workflow
no ref correto. O workflow atual produz ZIP, não assinatura comercial nem submissão.

## Retomada técnica

Branch: `codex/comercial-i18n-rtl`; base `3bc3f2aa4610207566a5a13f1e75ad019e523c81`.
Alterações anteriores foram preservadas. Não houve commit, push, release, upload,
cadastro, cobrança, envio de suporte nem chamada paga de transcrição/tradução.

```bash
.venv/bin/python -m pytest -q
.venv/bin/ruff check sao_francisco scripts/inventory_i18n.py tests
.venv/bin/mypy sao_francisco
.venv/bin/python scripts/inventory_i18n.py --markdown
```

O último comando imprime uma nova cópia editorial; não sobrescreve suas edições.
Não executar os scripts antigos de release contra artefatos existentes sem revisar seus
destinos. O candidato desta tarefa usa pasta isolada para preservar releases anteriores.
