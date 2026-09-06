# Lojas e recebimento no Banco do Brasil

Pesquisa em fontes oficiais em 29/08/2026. Preço-base autorizado: **US$ 5, compra única**.
Nenhuma conta foi criada, contrato aceito, informação bancária enviada ou venda publicada.
Elegibilidade documental não significa aprovação comercial, aceite do aplicativo ou repasse
testado. O levantamento cobre oito canais; não é uma lista exaustiva de lojas mundiais.

## O caminho confirmado até o BB

O [PayPal Brasil documenta especificamente como vincular Banco do Brasil](https://www.paypal.com/br/cshelp/article/como-fa%C3%A7o-para-adicionar-um-conta-banc%C3%A1ria-%C3%A0-minha-conta-do-paypal-help183).
Conta bancária e PayPal devem ter o mesmo CPF/CNPJ; em conta conjunta, somente o titular
principal pode vinculá-la. Siga as instruções oficiais sobre agência, dígitos e zeros;
não reutilize exemplos numéricos como dados reais.

Os [repasses são automáticos para banco brasileiro](https://www.paypal.com/br/cshelp/article/como-fazer-para-transferir-saldo-da-minha-conta-do-paypal-help394?locale.x=pt_BR),
sujeitos a análise e prazo bancário. Valores recebidos em moeda estrangeira passam por
[conversão para reais](https://www.paypal.com/br/cshelp/article/como-receber-recursos-com-o-paypal-help667).
Portanto, a rota operacional documentada é **loja → PayPal Brasil → Banco do Brasil**,
não um depósito garantido de US$ 5 líquidos ou em dólares no BB. Taxas, câmbio, reembolsos,
tributação e retenções podem reduzir o líquido.

A aceitação bancária abaixo é uma inferência explícita da combinação da documentação
de cada loja com a documentação PayPal/BB. É preciso concluir KYC e testar um repasse
real autorizado antes de chamar qualquer canal de “recebimento validado”.

## Matriz para ativação

| Canal | Rota documentada / situação BB | Preparação e pendência |
| --- | --- | --- |
| **Lemon Squeezy** | PayPal em países atendidos; BB via PayPal. Brasil não consta da lista de repasse bancário direto. | Prioridade: download de software e MoR; ativação e avaliação do produto pendentes. |
| **Ko-fi Shop** | Recebimento direto em PayPal; BB via PayPal. | Preparar loja a US$ 5. Vendedor assume obrigações fiscais/comerciais; validar tipo da conta PayPal. |
| **itch.io** | PayPal em venda direta ou payout do modelo coletado; BB via PayPal. | Categoria Tools; decidir modelo de pagamentos e entrevista fiscal. Preço mínimo de US$ 5, plataforma pode permitir contribuição maior. |
| **Gumroad** | Regra geral de PayPal para países sem depósito direto; Brasil tem também exceção Stripe Connect. | Preparar ficha; confirmar método efetivamente oferecido no onboarding brasileiro. Não confundir PayPal do comprador com payout. |
| **Microsoft Store (Windows)** | Brasil listado com suporte de pagamento Microsoft Store/PayPal; BB via PayPal. | Condicional a cadastro fiscal, tipo de conta, aceite do produto e instalador assinado adequado. ZIP atual não basta. |
| **Payhip** | PayPal pessoal brasileiro explicitamente admitido; BB via PayPal. | **Suspensa por conflito com licença padrão**: obter autorização escrita para distribuição MIT antes de aceitar/ativar. |
| **Sellfy** | Pagamentos diretos PayPal/Stripe; BB via PayPal. | Condicional à decisão de pagar mensalidade; sem contratação. Não é MoR. |
| **Paddle** | Wire/SWIFT ou Payoneer; não PayPal. | **BB específico não confirmado**. Pedir confirmação do payout brasileiro e dos dados exigidos; integração de entrega ainda necessária. |

“Preparar” não é “publicar em todos agora”. A Mac App Store está excluída por decisão
do autor. Microsoft Store é outro canal, apenas para Windows, com gates próprios.

## Taxas e adequação a US$ 5

- **Lemon Squeezy:** [5% + US$ 0,50](https://www.lemonsqueezy.com/pricing), mais
  [adicionais e custos de repasse](https://docs.lemonsqueezy.com/help/getting-started/fees).
  Só a tarifa-base equivale a US$ 0,75 num pedido de US$ 5, antes dos demais descontos.
  MoR trata impostos sobre vendas; não elimina obrigações do autor sobre sua renda.
  [Países](https://docs.lemonsqueezy.com/help/getting-started/supported-countries),
  [arquivos de apps](https://docs.lemonsqueezy.com/help/products/adding-products) e
  [produtos proibidos](https://docs.lemonsqueezy.com/help/getting-started/prohibited-products).
- **Ko-fi:** [5% no Shop mais processamento](https://help.ko-fi.com/hc/en-us/articles/360002506494-Does-Ko-fi-take-a-fee).
  [Software e entrega digital admitidos](https://help.ko-fi.com/hc/en-us/articles/360009712917-Ko-fi-Shop-Sell-digital-physical-products).
  [Não é MoR](https://help.ko-fi.com/hc/en-us/articles/10792069957661-How-tax-works-on-Ko-fi).
- **itch.io:** [participação ajustável, processamento e modalidades de pagamento](https://itch.io/docs/creators/payments).
  O modelo coletado exige entrevista fiscal e pode ter retenção para vendedor estrangeiro;
  não calcular líquido sem conhecer o resultado do cadastro. No modelo direto, a documentação
  restringe Stripe a determinados países, sem Brasil na lista: usar a avaliação PayPal,
  não presumir que todo Stripe brasileiro serve. [Termos](https://itch.io/docs/legal/terms).
- **Gumroad:** [direta 10% + US$ 0,50, mais processamento; Discover 30% incluindo processamento](https://gumroad.com/help/article/66-gumroads-fees).
  [Payouts](https://gumroad.com/help/article/13-getting-paid.html) e
  [exceção Stripe Connect Brasil](https://gumroad.com/help/article/330-stripe-connect.html).
  [PayPal Connect de checkout](https://gumroad.com/help/article/275-paypal-connect) exclui
  criadores brasileiros; a própria página distingue esse recurso do método de repasse.
  Confirmar a rota exibida, piso de payout, tarifas e prazo na conta do autor.
- **Payhip:** [plano gratuito com 5% mais gateway](https://payhip.com/pricing);
  [PayPal pessoal no Brasil](https://help.payhip.com/article/376-cant-connect-paypal).
  [Termos, seção 6](https://payhip.com/terms), limitam uso pessoal/não comercial e
  redistribuição, em tensão com a MIT. Não “resolver” removendo MIT. EXE/DMG precisam
  ser entregues em [ZIP, segundo o guia de produto digital](https://help.payhip.com/article/59-adding-a-digital-product).
- **Sellfy:** [plano Starter publicado a US$ 39/mês ou US$ 348/ano](https://docs.sellfy.com/article/138-what-is-sellfy).
  Custo fixo pouco atraente para app de US$ 5 sem volume conhecido.
  [Pagamentos diretos](https://docs.sellfy.com/article/42-how-to-receive-payments-from-customers);
  [não é MoR](https://docs.sellfy.com/article/366-merchant-of-record).
- **Paddle:** [5% + US$ 0,50](https://www.paddle.com/pricing), MoR, mas não substitui
  automaticamente loja e entrega. [Payout por wire ou Payoneer, piso usual US$ 100](https://www.paddle.com/help/manage/get-paid/when-and-how-do-i-get-paid).
  [SWIFT internacional pode custar US$ 15, com outros encargos/câmbio](https://www.paddle.com/help/manage/get-paid/is-there-a-fee-taken-for-payouts).
  Para este preço, avaliar custo e integração antes de priorizar.

Tarifas acima são fotografias da pesquisa, não promessa contratual nem aconselhamento
tributário. Reconferir no cadastro; não contratar planos pagos sem decisão do autor.

## Microsoft Store: gates adicionais

A [tabela oficial de pagamentos](https://learn.microsoft.com/en-us/partner-center/marketplace-offers/payment-thresholds-methods-timeframes)
lista Brasil, Microsoft Store e PayPal. O cadastro de
[pagamento e impostos](https://learn.microsoft.com/en-us/partner-center/account-settings/set-up-your-payout-account)
ainda precisa passar por validação e corresponder à titularidade do banco.

As [políticas Windows](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies)
exigem representação honesta e direitos para o conteúdo. Na rota de instalador Win32
por URL, o pacote deve ser EXE/MSI versionado, assinado, instalável silenciosamente e
hospedado em HTTPS imutável, com dependências atendidas; o ZIP portátil não satisfaz isso.
Definir Win32/instalador ou MSIX e verificar elegibilidade à venda paga nessa rota antes
de configurar preço. A política 10.8.3 inclui chaves secretas de API em contexto de dados
financeiros: esclarecer a aplicação ao BYOK de OpenAI/Gemini e eventual exigência de
conta empresarial, sem presumir elegibilidade da conta individual.

Não submeter o app apenas para “tentar”. Se houver rejeição estrutural ao fluxo de URLs,
registrar a impossibilidade do canal sem esconder o comportamento nem alterar o app
fora de tarefa própria.

## Amanhã: sequência por conta

1. Decidir pessoa física/jurídica e confirmar que PayPal e BB têm o mesmo titular fiscal.
2. Vincular/validar o BB no PayPal usando a página oficial, sem enviar dados pelo chat.
3. Completar onboarding das lojas prioritárias e informar software MIT, preço-base
   US$ 5, chaves próprias, custos de API separados e funcionamento real de URLs.
4. Rever país, moeda, taxas, retenções, política de reembolso e suporte. Não escolher
   país fictício para liberar um gateway nem alterar país de conta existente sem análise.
5. Cadastrar como **rascunho** com a [ficha multilíngue](fichas-lojas.md). Não subir
   candidato não notarizado/sem assinatura como instalador pronto para venda.
6. Somente após aprovação dos pacotes, autorizar compra-teste, entrega e repasse pequeno;
   comprovar o crédito no BB e o re-download. Sandbox não prova dinheiro recebido.
7. Autorizar publicação por canal após revisar campos e bytes finais.

## Perguntas prontas para suporte — não enviadas

**Aceite do produto e payout:**

> I am preparing São Francisco, an MIT-licensed open-source desktop transcription app
> for macOS and Windows, sold as official downloads for US$5, one time. Users bring their
> own OpenAI/Gemini API keys and pay those providers separately. The app processes local
> files and can retrieve media or existing captions from public video URLs using yt-dlp;
> users must hold the necessary rights and comply with source-service terms. It does not
> claim unrestricted access to third-party media. Is this product eligible, and can a
> Brazilian seller receive payouts through a Brazilian PayPal account linked to Banco
> do Brasil? Please confirm any account-type, withholding or payout restrictions.

**Complemento Payhip:**

> Your section 6 appears to prohibit commercial use and redistribution by buyers. Our
> product remains under MIT, which grants those rights. Can you explicitly support this
> license without imposing conflicting end-user restrictions? We will not activate the
> product unless this is resolved.

**Complemento Paddle:**

> Can you pay a Brazilian resident/entity to Banco do Brasil in Brazil? Please specify
> supported account type, payout currency, bank identifiers, minimum and all payout/FX
> fees, including intermediary-bank fees. PayPal availability is not assumed.

**Complemento Microsoft:**

> Please confirm the suitable paid distribution route and whether customer-supplied
> OpenAI/Gemini API keys require a company developer account under policy 10.8.3. Please
> also confirm product eligibility for the described public-URL media/caption workflow.

Nenhuma dessas mensagens foi enviada. Contratos e respostas dependem do autor.
