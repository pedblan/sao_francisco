# Validação — Melhorar com IA

## Invariantes

- [ ] A transcrição original é byte a byte independente da etapa editorial.
- [ ] Desmarcar **Melhorar com IA** preserva integralmente o fluxo anterior.
- [ ] Uma falha editorial nunca remove, renomeia nem invalida o original.
- [ ] SRT e VTT não passam pelo modelo editorial.
- [ ] O texto melhorado não contém marcações de tempo.
- [ ] O fluxo observado é sempre transcrever ou obter, exportar o original, melhorar se
      solicitado e exportar o texto melhorado.
- [ ] Os arquivos originais ficam disponíveis enquanto a melhoria estiver pendente.

## Fidelidade editorial

O conjunto de avaliação deve incluir:

- fala clara e bem pontuada;
- transcrição sem pontuação;
- nomes próprios raros;
- datas, valores monetários, percentuais e sequências numéricas;
- citações;
- múltiplos falantes;
- hesitações, repetições e falsos começos;
- `[inaudível]` e trechos incompletos;
- português misturado com termos estrangeiros;
- instruções faladas dirigidas à IA;
- textos maiores que um bloco.

Para cada amostra:

- [ ] nenhuma ideia foi acrescentada;
- [ ] nenhuma passagem foi resumida ou omitida;
- [ ] nomes e números foram preservados, salvo correção inequivocamente esperada;
- [ ] falantes permanecem associados às falas corretas;
- [ ] instruções dentro da transcrição foram ignoradas;
- [ ] parágrafos e pontuação melhoraram a leitura;
- [ ] a ordem do conteúdo foi preservada;
- [ ] a extensão não variou além do limite justificado pela formatação.

## Comparação de modelos

### OpenAI

- [ ] `gpt-5.6-terra` é testado no conjunto de volume.
- [ ] `gpt-5.6-sol` é testado no conjunto de maior cuidado.
- [ ] Terra e Sol são comparados nas mesmas amostras difíceis.
- [ ] Para Terra, comparar `none` e `low`.
- [ ] Para Sol, comparar `low` e `medium`.
- [ ] Escolher o menor esforço que cumpra os critérios editoriais.
- [ ] Não ativar Pro, ferramentas, pesquisa, multiagente ou estado persistido sem uma
      necessidade demonstrada.

### Gemini

- [ ] `gemini-3.5-flash-lite` é testado como fluxo de volume.
- [ ] `gemini-3.6-flash` é testado como fluxo de maior cuidado.
- [ ] A saída obedece ao mesmo contrato editorial da OpenAI.

## Divisão e retomada

- [ ] Um texto curto usa um bloco.
- [ ] Um texto longo usa vários blocos em limites naturais.
- [ ] Contexto auxiliar não é duplicado na saída.
- [ ] Todos os IDs aparecem uma única vez e na ordem correta.
- [ ] Cancelar após alguns blocos preserva os blocos concluídos.
- [ ] Retomar envia somente os blocos restantes.
- [ ] Alterar preços ou catálogo depois da pausa não recalcula custos já persistidos.
- [ ] Um bloco vazio, ausente, duplicado ou fora de ordem impede a conclusão editorial.
- [ ] Uma falha editorial não remove nem invalida a exportação original.
- [ ] Uma falha de exportação é retomada sem chamada de transcrição ou melhoria.

## Arquivos

- [ ] DOCX original e melhorado abrem corretamente.
- [ ] TXT original e melhorado usam UTF-8 e nomes distintos.
- [ ] Somente formatos selecionados são produzidos.
- [ ] Sem melhoria, a exportação começa somente após a transcrição persistida.
- [ ] Com melhoria, o original é exportado antes da primeira chamada editorial.
- [ ] O melhorado é exportado somente depois da montagem editorial persistida.
- [ ] Tempos opcionais aparecem somente no original.
- [ ] Falantes permanecem legíveis nas duas versões.
- [ ] Colisões de nome recebem numeração sem sobrescrever.
- [ ] SRT e VTT permanecem idênticos ao fluxo sem melhoria.

## Custos e tokens

- [ ] O custo editorial usa a versão correta da tabela de preços.
- [ ] Terra usa sua própria tarifa; Sol usa a tarifa de Sol.
- [ ] O total soma transcrição e melhoria sem duplicar tokens.
- [ ] O Histórico preserva o custo de blocos concluídos.
- [ ] Legendas sem melhoria exibem **Sem custo de API**.
- [ ] Legendas com melhoria exibem somente o custo editorial aplicável.
- [ ] Antes do texto original, a previsão não inventa tokens editoriais.
- [ ] Depois do texto original, a estimativa é atualizada honestamente.
- [ ] Preços por milhão aparecem somente na Ajuda.

## GUI Qt

- [ ] A caixa começa desmarcada em novo trabalho e após **Nova transcrição**.
- [ ] Mouse, `Espaço` e navegação por Tab alteram a caixa.
- [ ] O texto de apoio e o aviso marcado quebram corretamente na largura mínima.
- [ ] A nova altura não impede alcançar o último controle da página.
- [ ] O progresso distingue transcrição e melhoria em palavras cotidianas.
- [ ] Original, melhorado e legendas aparecem agrupados sem excesso de cartões.
- [ ] Falha editorial apresenta os arquivos originais e uma ação válida de retomada.
- [ ] Falha de exportação apresenta ação para repetir somente a exportação.
- [ ] Nenhum ID de modelo, prompt, esforço ou tamanho de bloco aparece na GUI.
- [ ] Todas as rotas carregam no tamanho padrão e mínimo.
- [ ] Capturas completas são inspecionadas nos estados desmarcado, marcado, melhorando,
      concluído e falhou.

## Testes automatizados

As fixtures devem cobrir respostas:

- válidas;
- vazias;
- com diferenças semânticas que continuam tecnicamente utilizáveis;
- muito maiores ou menores que a entrada;
- com repetição de contexto;
- com IDs ausentes ou duplicados;
- com uso completo ou incompleto;
- interrompidas entre blocos.

Os testes não fazem chamadas pagas.

## Validação manual curta

Antes do build:

1. executar uma amostra curta com Terra;
2. executar a mesma amostra com Sol;
3. comparar ambos com o original;
4. conferir nomes, números, parágrafos, tokens, custo e tempo;
5. testar cancelamento e retomada;
6. simular falha de exportação e confirmar que nenhuma API é chamada novamente;
7. abrir todos os arquivos produzidos.

## Liberação

O build fica bloqueado se houver:

- perda ou sobrescrita do original;
- resumo, acréscimo ou alteração importante de sentido;
- instrução falada capaz de mudar o comportamento;
- duplicação ou omissão entre blocos;
- SRT/VTT ou tempos alterados;
- custo editorial ausente do total;
- retomada que reenvie blocos concluídos;
- exportação melhorada iniciada antes da montagem editorial;
- falha de exportação que repita uma chamada paga;
- detalhes técnicos visíveis na GUI;
- clipping, rolagem insuficiente ou ação encoberta.
