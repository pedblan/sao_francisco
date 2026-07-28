# Especificação — estimativa de custos

**Estado:** implementado; validação automatizada concluída
**Branch:** `estimar-custos`
**Referência de preços:** 28 de julho de 2026

## Problema

O usuário precisa ter uma noção do custo de uma transcrição sem conhecer preços por
milhão ou a forma como a mídia é dividida. Hoje o São Francisco não conserva os dados de
uso devolvidos pelas APIs e não apresenta nenhuma estimativa.

## Objetivo

Apresentar um valor simples, honesto e persistente para cada trabalho:

- uma previsão quando já houver informação suficiente;
- um total acumulado enquanto as partes forem concluídas;
- uma estimativa final no resultado e no Histórico.

A cobrança exibida pela provedora é sempre a referência oficial.

## Experiência do usuário

### Antes e durante a transcrição

Assim que a duração e o modelo forem conhecidos, a tela pode mostrar uma linha discreta:

> Custo estimado: cerca de US$ 0,08

Durante o processamento, o valor passa a representar o que já foi enviado:

> Custo até agora: cerca de US$ 0,04

Quando ainda não houver base confiável para calcular, a linha não apresenta números
inventados. Ela pode ficar ausente ou dizer:

> A estimativa aparecerá durante a transcrição.

### Ao concluir

O resultado e o cartão correspondente no Histórico mostram:

> Custo estimado: cerca de US$ 0,08

Quando a provedora informar uma contagem confiável, pode aparecer abaixo, com menor peso:

> Uso informado: 18.240 tokens

O app mostra apenas o total. Uma breve explicação na Ajuda dá contexto ao termo. Se a
provedora não informar tokens, a linha fica ausente; o app não fabrica uma contagem.

Se o documento tiver sido produzido somente com legendas existentes e a melhoria com IA
estiver desativada:

> Sem custo de API

Com legendas e melhoria ativada, o valor corresponde à etapa editorial.

Valores positivos menores que um centavo aparecem como:

> Custo estimado: menos de US$ 0,01

Isso evita que uma chamada paga seja apresentada como `US$ 0,00`.

### Ajuda

A Ajuda explica, em poucos parágrafos, que:

- o valor é aproximado;
- preços e planos gratuitos podem mudar;
- tentativas canceladas ou recusadas após o envio podem aparecer de modo diferente;
- o painel da OpenAI ou do Gemini contém a cobrança oficial.

Os links abrem as páginas oficiais de uso e preços. Os preços por milhão de tokens ficam
somente na Ajuda. A interface principal pode mostrar o total de tokens, mas não mostra
fórmulas, preços unitários, nomes de campos da API nem detalhes sobre as partes.

## Comportamento do cálculo

1. A previsão usa a soma das durações planejadas para envio, incluindo pequenas
   sobreposições entre partes, e não apenas a duração visível do vídeo.
2. Cada parte concluída conserva sua própria estimativa junto ao resultado persistido.
3. Quando a API devolver dados de uso suficientes, o cálculo da parte usa esses dados.
4. Quando a resposta não trouxer dados de uso, pode ser usada uma tarifa oficial por
   minuto, se ela existir para aquele modelo.
5. Sem dados de uso e sem tarifa confiável, o custo fica indisponível.
6. Retomadas reutilizam os valores persistidos e somam somente as novas partes.
7. O uso integral de legendas tem custo de API zero somente quando não houver melhoria.
8. Quando **Melhorar com IA** estiver ativa, o custo final soma transcrição e melhoria. A
   previsão editorial é acrescentada depois que o texto original existir.
9. Falhas sem resposta de uso não recebem custo presumido. A Ajuda esclarece que a
   provedora pode registrar uma tentativa que o app não conseguiu medir.

## Persistência e compatibilidade

Os dados de custo fazem parte dos metadados do trabalho e dos resultados de cada parte.
Devem conter o valor decimal em dólares, o método usado, a versão da tabela de preços e os
dados de uso necessários à auditoria.

Esses campos são opcionais. Trabalhos antigos continuam abrindo normalmente e aparecem
sem estimativa, salvo quando forem retomados e novas partes gerarem dados mensuráveis.

## Limites

- A primeira versão trabalha apenas em dólares americanos; não consulta câmbio.
- Não acessa a conta de cobrança nem a fatura do usuário.
- Não promete igualdade exata com créditos gratuitos, descontos, impostos, arredondamento
  ou alterações posteriores da provedora.
- Não atualiza preços silenciosamente pela internet. A tabela é revisada junto com o
  catálogo de modelos e registra sua data.
- Não adiciona uma configuração para ativar ou desativar a estimativa.

## Fontes oficiais vigentes na data de referência

- [Preços de transcrição da OpenAI](https://developers.openai.com/api/docs/pricing)
- [GPT-4o Transcribe](https://developers.openai.com/api/docs/models/gpt-4o-transcribe)
- [GPT-4o mini Transcribe](https://developers.openai.com/api/docs/models/gpt-4o-mini-transcribe)
- [GPT-4o Transcribe Diarize](https://developers.openai.com/api/docs/models/gpt-4o-transcribe-diarize)
- [Whisper](https://developers.openai.com/api/docs/models/whisper-1)
- [Preços da Gemini API](https://ai.google.dev/gemini-api/docs/pricing)
- [Uso da Gemini Interactions API](https://ai.google.dev/api/interactions-api)

## Fora do escopo

- orçamento mensal;
- limites automáticos de gasto;
- consulta às faturas ou aos saldos das contas;
- conversão para reais;
- comparação comercial entre provedores;
- exibição de fórmulas, preços unitários ou detalhamento por parte na GUI.
