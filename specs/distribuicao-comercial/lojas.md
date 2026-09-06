# Canais de venda — São Francisco para Mac e Windows

> Atualização operacional: [matriz Banco do Brasil, US$ 5 e oito canais](lojas-banco-do-brasil.md).
> Abaixo está a pesquisa inicial preservada. A nova matriz prevalece para recebimento,
> prioridades, novos canais e pendências; cadastro/repasse ainda não foram validados.

**Pesquisa:** 29 de agosto de 2026. Fontes primárias; sem cadastro, contato, compra ou upload.
Taxas e elegibilidade precisam ser reconferidas no onboarding. A conta brasileira é uma
hipótese de planejamento, não uma confirmação da residência fiscal ou titularidade.

## Conclusão prática

**Prioridade para avaliação: Lemon Squeezy**, se o repasse para a conta do autor no Brasil
for confirmado. É adequada à venda internacional de downloads e assume a operação de
impostos sobre vendas como merchant of record (MoR). A limitação de recebimento abaixo é
um gate real, não um detalhe já resolvido.

**Alternativa: Gumroad**, com caminho documentado para Stripe Connect no Brasil e operação
simples de produto digital, mas taxas desfavoráveis a preço muito baixo.

**Opção enxuta: Ko-fi Shop**, especialmente para venda à audiência do autor. Permite
software e termos próprios, mas deixa impostos, reembolsos e disputas com o vendedor.

Essas são avaliações de adequação, não certificações ou promessas de aprovação. Nenhuma
loja foi escolhida. As vitrines hospedadas dependem principalmente de tráfego próprio;
marketplace pode ajudar na descoberta, mas não garante compradores.

## Comparativo

| Canal | Entrega e perfil | Custo publicado | Principal ressalva |
| --- | --- | --- | --- |
| Lemon Squeezy | loja hospedada, checkout e downloads; MoR | 5% + US$ 0,50, com adicionais | Brasil ausente da lista de repasse bancário; confirmar rota PayPal/conta |
| Gumroad | loja hospedada e marketplace Discover; MoR | direta: 10% + US$ 0,50 **mais processamento**; Discover: 30% incluindo processamento | peso alto em preço mínimo; validar Stripe Connect da conta brasileira |
| Ko-fi Shop | loja de autor, software e downloads; recebimento direto | 5% mais PayPal/Stripe; sem mensalidade obrigatória | não é MoR; gestão fiscal/comercial pelo autor |
| itch.io | marketplace e cliente de distribuição, com foco indie | participação escolhida pelo vendedor mais processamento | público menos alinhado a produtividade e possível retenção tributária no payout |
| Payhip | loja de downloads com gateways, inclusive Mercado Pago | plano sem mensalidade: 5% mais gateway | licença-padrão de uso pessoal/não comercial conflita com a proposta MIT; esclarecer antes de escolher |

As taxas da tabela não são custo total líquido: câmbio, processamento, impostos,
reembolsos e repasses variam por canal, conta e território. Fontes e ressalvas abaixo.

## Lemon Squeezy

- [Preço](https://www.lemonsqueezy.com/pricing): 5% + US$ 0,50, sem mensalidade obrigatória.
- [Adicionais](https://docs.lemonsqueezy.com/help/getting-started/fees): 1,5% para transação
  internacional fora dos EUA e 1,5% para PayPal; o documento também lista custos de repasse,
  inclusive 3% limitado a US$ 30 para PayPal fora dos EUA. Não confundir pagamento do
  comprador com recebimento do vendedor. Produtos abaixo de US$ 10 podem pedir preço customizado.
- [Países](https://docs.lemonsqueezy.com/help/getting-started/supported-countries): Brasil
  não aparece na lista de bancos; o serviço menciona PayPal em países atendidos, mas isso
  ainda exige confirmação específica da conta. Há países bloqueados para compradores;
  interface em russo, por exemplo, não equivale a vender na Rússia.
- [Produtos e entrega](https://docs.lemonsqueezy.com/help/products/adding-products):
  aceita arquivos de apps, disponibiliza downloads a compradores e permite entregar
  arquivos atualizados aos compradores anteriores. Não exige implementar ativação no app.
- [Política de produtos](https://docs.lemonsqueezy.com/help/getting-started/prohibited-products):
  software é categoria admitida, mas isso não aprova especificamente um transcritor com
  download por URL. Confirmar descrição real, licença do produto e elegibilidade na ativação.

## Gumroad

- A [página comercial](https://gumroad.com/pricing) informa MoR e 10% + US$ 0,50 nas vendas
  diretas; a [documentação de taxas](https://gumroad.com/help/article/66-gumroads-fees)
  esclarece que processamento é adicional. Ela cita cartão a 2,9% + US$ 0,30; não assumir
  essa tarifa para Stripe brasileiro. Discover custa 30% com processamento incluído.
- A [integração Stripe](https://gumroad.com/help/article/330-stripe-connect.html) mantém
  exceção para novas contas conectadas de usuários do Brasil. A tarifa do Stripe e câmbio
  são próprios da conta; confirmar onboarding e recebimento antes do lançamento.
- [PayPal Connect](https://gumroad.com/help/article/275-paypal-connect) no checkout exclui
  criadores do Brasil. Isso é distinto do método de payout e não deve ser generalizado.
- A mesma página de preços proíbe pirataria/violação de copyright. Apresentar o software
  como ferramenta legítima, com MIT explícita; não anunciar download irrestrito de terceiros.

Minha avaliação: alternativa operacionalmente interessante, mas comissão alta para um
app vendido por preço simbólico. Não contar com Discover como canal gratuito de aquisição.

## Ko-fi Shop

- [Loja](https://help.ko-fi.com/hc/en-us/articles/360009712917-Ko-fi-Shop-Sell-digital-physical-products):
  inclui software entre os produtos aceitos, oferece acesso a arquivos e atualizações,
  e permite definir termos do vendedor. É possível explicar a MIT sem adotar DRM.
- [Taxas](https://help.ko-fi.com/hc/en-us/articles/360002506494-Does-Ko-fi-take-a-fee):
  loja a 5% mais processador, sem mensalidade obrigatória, com pagamento direto em
  PayPal/Stripe. BRL está entre as moedas listadas; elegibilidade da conta ainda será validada.
- [Impostos](https://help.ko-fi.com/hc/en-us/articles/10792069957661-How-tax-works-on-Ko-fi):
  não é MoR, não recolhe os impostos pelo criador nem gerencia reembolsos/disputas.
- [Conteúdo](https://help.ko-fi.com/hc/en-us/articles/360007937553-Ko-fi-Content-Guidelines):
  proíbe produtos que infrinjam ou facilitem infração de direitos. Não é uma alternativa
  para esconder comportamento que outra plataforma rejeitou.

Minha avaliação: boa vitrine de autor, com custo de plataforma menor, desde que a gestão
fiscal e comercial seja viável. Compra de software deve ser descrita como compra, não como
doação para evitar regras. Sem promessa de descoberta orgânica ou Pix não verificado.

## itch.io

[Pagamentos](https://itch.io/docs/creators/payments): participação ajustável (exemplo-padrão
de 10%) mais processador. “Direct to you” e “Collected by itch.io” têm responsabilidades
diferentes; o segundo é MoR, paga por PayPal/Payoneer e exige entrevista fiscal. A documentação
prevê retenção tributária padrão de 30% para pagamentos a entidades estrangeiras, sujeita
a condições e tratados. Não calcular renda líquida só pela participação configurada.

[Termos](https://itch.io/docs/legal/terms) reconhecem propriedade do conteúdo pelo autor e
exigem direitos para distribuir; a licença concedida à plataforma é não exclusiva.
Minha avaliação: canal secundário para público indie, não primeira escolha para este app
de produtividade; avaliar impostos e forma de recebimento antes de ofertar.

## Payhip — não escolher sem esclarecer licença

[Preço](https://payhip.com/pricing): 5% no plano sem mensalidade, mais gateway.
[Mercado Pago](https://help.payhip.com/article/343-connecting-your-mercado-pago-account):
Brasil/BRL e Pix são documentados; moedas do Payhip e da conta precisam coincidir.

Mas os [termos, seção 6](https://payhip.com/terms), descrevem licença ao comprador de uso
pessoal/não comercial, sem reprodução/distribuição. Isso é incompatível com apresentar
essas restrições como direitos da MIT. Não presumir que escrever “MIT” na descrição basta;
exigir esclarecimento sobre prevalência de licença própria antes de qualquer escolha.

[Entrega](https://help.payhip.com/article/59-adding-a-digital-product): EXE e DMG não são
aceitos diretamente; a própria plataforma orienta empacotá-los em ZIP. Isso não impede
software, mas acrescenta etapa de instalação e teste.
[Tributos](https://payhip.com/features/vat-taxes): declara recolher EU/UK VAT e sales tax
EUA/Canadá; outros tributos não são automaticamente assumidos.

Minha avaliação: boa integração brasileira, porém não recomendada para adoção imediata
com a política MIT atual sem resolver a questão contratual.

## Outros canais considerados

- **Paddle:** [5% + US$ 0,50](https://www.paddle.com/pricing), com condição comercial a
  consultar abaixo de US$ 10. É infraestrutura de comércio/MoR, não uma loja pronta de
  descoberta. A [entrega de produtos digitais](https://developer.paddle.com/get-started/how-paddle-works/digital-products/)
  requer organizar fulfillment a partir da compra. Fica para eventual site próprio com
  maior integração, não o primeiro recorte de venda simples.
- **Microsoft Store:** opção futura **só para Windows**, não substituto único para Mac e
  Windows. [A Microsoft](https://learn.microsoft.com/en-us/windows/apps/publish/faq/get-started-with-the-microsoft-store)
  informa comissão de 15% para apps com seu comércio, ou ausência da comissão Microsoft
  usando comércio próprio em apps não-jogos. Processamento próprio ainda tem custo.
  Tem certificação e [políticas próprias](https://learn.microsoft.com/en-us/windows/apps/publish/store-policies);
  nenhuma elegibilidade do São Francisco foi estabelecida. Não iniciar migração para
  essa loja apenas porque a Mac App Store foi descartada.

## Critérios antes da escolha final

1. Confirmar titular, país, moeda, verificação de identidade e repasse realmente disponível.
2. Confirmar termos compatíveis com MIT e dependências, e aceite do produto descrito sem
   ocultar download/conversão. Contato externo somente com autorização do autor.
3. Calcular custo efetivo no preço pretendido: em US$ 1, somente uma parcela fixa de
   US$ 0,50 já representa 50%, antes de qualquer percentual. “Preço mínimo” requer simulação.
4. Definir obrigações fiscais, reembolsos, atendimento e atualizações. MoR trata tributos
   sobre vendas no escopo contratado; não presumir que elimina obrigações do autor no Brasil.
5. Testar, após autorização, compra/recibo, downloads de ambos os sistemas, re-download de
   atualização e reembolso. Conferir hashes e abertura a partir desses downloads.
6. Aprovar ficha, preço e arquivos antes da venda pública; manter backups e possibilidade
   de rollback sem retirar acesso de compradores.

## Limitações da pesquisa

Não foram auditadas contas existentes, certificados, orçamento de assinatura Windows,
enquadramento tributário, termos de cada fonte de mídia ou aceitação específica por lojas.
Não há promessa de aprovação de checkout, saque, distribuição ou isenção jurídica.
Preservar essas pendências; não convertê-las em fatos pela existência desta recomendação.
