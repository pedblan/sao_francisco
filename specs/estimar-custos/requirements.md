# Requisitos — estimativa de custos

## Requisitos funcionais

### RF-01 — previsão

Quando houver duração e tarifa confiável, o sistema deve calcular uma previsão para o
trabalho antes da primeira chamada paga ou assim que a preparação da mídia terminar.

### RF-02 — custo por parte

Cada resposta concluída deve produzir um registro de custo independente contendo:

- provedor e modelo;
- valor estimado em USD;
- método de cálculo;
- versão da tabela de preços;
- dados de uso recebidos, quando existirem;
- duração enviada usada como alternativa.

### RF-03 — total acumulado

O total do trabalho deve ser a soma dos registros das partes concluídas. Não deve ser
recalculado com uma tabela de preços mais nova ao reabrir o Histórico.

### RF-04 — retomada

Ao retomar, o sistema deve preservar os custos já registrados e acrescentar somente as
partes novas. Uma parte concluída não pode ser cobrada duas vezes no total local.

### RF-05 — legendas

Um trabalho concluído exclusivamente a partir de legendas e sem melhoria com IA deve
registrar custo de API zero e exibir **Sem custo de API**. Se houver melhoria, deve
registrar o custo editorial normalmente.

### RF-06 — indisponibilidade honesta

Se faltarem preço e dados de uso confiáveis, o sistema não deve fabricar um valor. A GUI
deve omitir o número ou informar de forma simples que a estimativa não está disponível.

### RF-07 — estados incompletos

Trabalhos pausados, cancelados ou com falha devem mostrar apenas o custo acumulado das
partes que possuem registro. Uma tentativa sem dados de uso não deve ser presumida como
gratuita nem somada artificialmente.

### RF-08 — apresentação

A GUI deve:

- usar `cerca de US$ 0,00` para valores de pelo menos um centavo;
- usar `menos de US$ 0,01` para valores positivos inferiores a um centavo;
- reservar `Sem custo de API` para zero comprovado por reaproveitamento de legendas;
- permitir `Uso informado: 18.240 tokens` como dado secundário quando a contagem existir;
- nunca mostrar fórmulas ou tarifas unitárias;
- identificar sempre o valor como estimativa.

### RF-09 — locais de exibição

O valor deve estar disponível:

- na tela de transcrição, sem competir com a ação principal;
- no estado de progresso, conforme partes forem concluídas;
- no resultado final;
- no Histórico.

### RF-10 — tokens informados

A interface deve mostrar somente a contagem total realmente devolvida pela provedora.
Não deve:

- estimar tokens ausentes;
- decompor entrada, saída, áudio ou raciocínio na GUI;
- mostrar tokens para o Whisper quando a resposta não os fornecer;
- confundir o total de tokens com preço ou cobrança.

### RF-11 — Ajuda

A Ajuda deve oferecer uma explicação curta e links oficiais para os painéis de uso e
preços. Pode conter a tabela de preços por milhão de tokens, claramente datada e escrita
para usuários não técnicos. Esses preços unitários não aparecem em nenhuma outra tela.

## Requisitos de cálculo

### RC-01 — precisão decimal

Os cálculos devem usar aritmética decimal. Valores persistidos não podem depender de
arredondamento binário de ponto flutuante.

### RC-02 — duração faturável

Quando o cálculo for temporal, deve usar a soma das durações efetivamente preparadas para
envio. Sobreposições planejadas entre partes entram na previsão.

### RC-03 — preferência de evidência

A ordem de preferência é:

1. dados de uso devolvidos pela resposta;
2. tarifa oficial estimada por minuto;
3. indisponível.

O método escolhido deve ser persistido, embora não seja exposto na GUI.

### RC-04 — OpenAI

Na tabela datada de 28/07/2026:

| Modelo | Entrada / 1M | Saída / 1M | Previsão temporal |
| --- | ---: | ---: | ---: |
| `gpt-4o-mini-transcribe` | US$ 1,25 | US$ 5,00 | US$ 0,003/min |
| `gpt-4o-transcribe` | US$ 2,50 | US$ 10,00 | US$ 0,006/min |
| `gpt-4o-transcribe-diarize` | US$ 2,50 | US$ 10,00 | derivada da tarifa equivalente |
| `whisper-1` | — | — | US$ 0,006/min |

Para o modelo com falantes, a previsão temporal é uma aproximação interna baseada na
mesma tarifa de tokens do GPT-4o Transcribe; a estimativa apurada deve preferir dados de
uso, quando presentes.

### RC-05 — Gemini

Na tabela datada de 28/07/2026:

| Modelo | Entrada / 1M | Saída e raciocínio / 1M |
| --- | ---: | ---: |
| `gemini-3.6-flash` | US$ 1,50 | US$ 7,50 |
| `gemini-3.5-flash-lite` | US$ 0,30 | US$ 2,50 |

O cálculo apurado deve usar o uso cumulativo devolvido pela Interactions API, evitando
somar duas vezes tokens que já estejam incluídos em um total. Caso a resposta não
permita separar com segurança entrada, saída e raciocínio, o valor deve ficar
indisponível.

### RC-06 — tabela de preços

A tabela deve ser:

- localizada em um único módulo;
- imutável durante a execução;
- identificada por data ou versão;
- coberta por testes;
- revisada quando um modelo for adicionado, removido ou renomeado.

Uma mudança futura de preço vale apenas para novos registros. O Histórico preserva o
valor e a versão usados na ocasião.

### RC-07 — melhoria editorial

Quando **Melhorar com IA** estiver ativa:

- transcrição e melhoria mantêm registros internos separados;
- o rótulo apresentado usa a soma dos dois;
- os tokens visíveis usam o total informado de todas as etapas, sem duplicação;
- antes da transcrição existir, a previsão não fabrica tokens editoriais;
- depois da montagem do texto, a previsão pode ser atualizada;
- legendas deixam de representar custo total zero, pois a etapa editorial usa a API.

Na tabela OpenAI datada de 28/07/2026, para contexto curto e processamento padrão:

| Modelo editorial | Entrada / 1M | Entrada em cache / 1M | Saída / 1M |
| --- | ---: | ---: | ---: |
| `gpt-5.6-terra` | US$ 2,50 | US$ 0,25 | US$ 15,00 |
| `gpt-5.6-sol` | US$ 5,00 | US$ 0,50 | US$ 30,00 |

Blocos editoriais devem permanecer abaixo do limiar de contexto longo. Caso uma requisição
ultrapasse o limiar vigente, a tabela deve aplicar a tarifa correspondente em vez de usar
silenciosamente a tarifa curta.

## Requisitos de dados e integração

### RD-01

O objeto de transcrição deve aceitar metadados de uso sem misturá-los ao texto ou aos
segmentos exportados.

### RD-02

O manifesto do trabalho deve aceitar um resumo de custo opcional e continuar compatível
com manifestos antigos.

### RD-03

O contrato Python–QML deve expor apenas propriedades prontas para apresentação, como o
rótulo formatado, a contagem total de tokens e a disponibilidade. A decomposição técnica
permanece no backend.

### RD-04

DOCX, TXT, SRT e VTT não devem receber informações de custo.

### RD-05

Nenhuma chave, conteúdo de áudio ou resposta bruta deve ser incluída nos registros de
custo.

### RD-06

Uma nova tentativa de exportação deve reutilizar custos e tokens persistidos sem
recalcular nem repetir chamadas pagas.

## Requisitos de interface e acessibilidade

### RI-01

A informação deve usar a tipografia e as cores de Terra Franciscana, com peso visual
secundário em relação ao botão de transcrever e ao resultado.

### RI-02

A linha deve quebrar corretamente, manter contraste suficiente e não causar truncamento
na largura mínima suportada.

### RI-03

O valor não pode ser comunicado somente por cor. Leitores de tela devem receber o rótulo
completo.

### RI-04

Detalhes adicionais pertencem à Ajuda. A GUI não deve ganhar pop-up técnico, tabela
detalhada de tokens ou configuração avançada.

## Requisitos não funcionais

- Testes automatizados não fazem chamadas pagas.
- A captura de uso não pode impedir a entrega da transcrição quando um campo opcional
  estiver ausente.
- A persistência do custo deve ser atômica junto ao resultado da parte.
- O cálculo deve ser determinístico para uma mesma resposta e uma mesma versão de preço.
- O acréscimo visual deve preservar rolagem, foco, redimensionamento e desempenho das
  telas existentes.
