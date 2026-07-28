# Validação — estimativa de custos

## Critérios de aceite do domínio

- [ ] Dez minutos em `gpt-4o-mini-transcribe`, pela tarifa temporal vigente, resultam em
      `US$ 0,030`.
- [ ] Dez minutos em `gpt-4o-transcribe` ou `whisper-1` resultam em `US$ 0,060`.
- [ ] O cálculo usa a soma das partes com sobreposição, não apenas a duração original.
- [ ] Cálculos por tokens separam corretamente entrada, saída e raciocínio conforme a
      semântica de cada resposta.
- [ ] Valores usam aritmética decimal e permanecem iguais após serializar e restaurar.
- [ ] Uma tabela desconhecida ou incompleta produz estado indisponível.

## Critérios de aceite da persistência

- [ ] Cada parte concluída possui no máximo um registro de custo.
- [ ] Pausar e retomar não duplica valores já salvos.
- [ ] Cancelar conserva somente os valores mensuráveis já acumulados.
- [ ] Um trabalho com falha continua abrindo no Histórico mesmo sem custo.
- [ ] Manifestos criados antes desta funcionalidade continuam válidos.
- [ ] Reabrir um trabalho não recalcula seu valor com preços atuais.
- [ ] Legendas integrais persistem zero comprovado sem criar registros fictícios de API.
- [ ] Legendas com melhoria registram custo editorial e não exibem zero total.
- [ ] Repetir uma exportação não altera custo ou tokens e não chama uma provedora.

## Fixtures de provedor

Os testes devem simular, sem rede:

- resposta OpenAI com uso completo;
- resposta OpenAI sem uso, usando tarifa por minuto;
- resposta do Whisper;
- resposta Gemini com entrada, saída e raciocínio;
- resposta Gemini sem uso suficiente;
- campos adicionais desconhecidos;
- contagens nulas ou ausentes;
- tentativa que falha antes de devolver uso.

Nenhum teste automatizado pode usar chave real ou gerar cobrança.

## Critérios de apresentação

- [ ] Zero por legendas sem melhoria: **Sem custo de API**.
- [ ] Valor positivo menor que US$ 0,01: **menos de US$ 0,01**.
- [ ] Valor a partir de um centavo: **cerca de US$ 0,00**, com duas casas na GUI.
- [ ] Valor desconhecido não aparece como zero.
- [ ] Todos os valores visíveis contêm “estimado”, “estimativa” ou “cerca de”.
- [ ] Quando disponível, a GUI mostra somente o total de tokens informado.
- [ ] A ausência de tokens não produz contagem estimada ou linha vazia.
- [ ] Nenhuma tela, exceto a Ajuda, mostra preços por milhão.
- [ ] Nenhuma tela mostra fórmulas, IDs de campos ou detalhes das partes.
- [ ] A Ajuda contém preços por milhão datados e links para as fontes oficiais.
- [ ] DOCX, TXT, SRT e VTT permanecem sem informação de custo.

## Matriz de fluxo

| Origem e estado | Resultado esperado |
| --- | --- |
| Arquivo local concluído | previsão, acumulado e total final |
| URL transcrita por áudio | mesmos estados do arquivo local |
| URL concluída por legendas, sem melhoria | custo zero explícito |
| URL por legendas com melhoria | somente custo editorial |
| Trabalho pausado | total apenas das partes medidas |
| Trabalho retomado | total anterior mais partes novas |
| Trabalho cancelado | acumulado preservado |
| Trabalho com falha antes da resposta | custo desconhecido, sem zero falso |
| Trabalho antigo | abre normalmente, sem estimativa |

## Validação da GUI Qt

- [ ] Carregar todas as rotas offscreen no tamanho padrão e no mínimo suportado.
- [ ] Testar a tela de transcrição em preparação, execução, pausa, erro e conclusão.
- [ ] Testar o Histórico com lista vazia, muitos itens e todos os estados de custo.
- [ ] Usar nome de vídeo longo e valores que produzam todos os rótulos previstos.
- [ ] Confirmar que a nova linha quebra sem elisão, não desloca ações e não encobre o
      rodapé.
- [ ] Demonstrar que o último item continua alcançável por roda, trackpad e teclado.
- [ ] Confirmar contraste, foco visível e nome acessível completo.
- [ ] Inspecionar capturas das telas inteiras, não apenas do novo rótulo.

## Comandos de verificação

```bash
python -m pytest
ruff check .
mypy sao_francisco
pyside6-qmllint -I sao_francisco/qml \
  sao_francisco/qml/Main.qml \
  sao_francisco/qml/Theme.qml \
  sao_francisco/qml/components/*.qml \
  sao_francisco/qml/pages/*.qml
```

O ambiente pode usar `python3` ou o interpretador do projeto quando `python` não estiver
disponível.

## Validação manual opcional com provedor

Antes de publicar uma versão, executar uma única amostra curta por provedor em conta de
teste:

1. anotar modelo e duração enviada;
2. concluir a transcrição;
3. conferir o valor mostrado pelo app;
4. comparar posteriormente com o painel oficial, considerando o período em UTC;
5. registrar qualquer diferença explicável por camada gratuita, atraso, arredondamento ou
   preço alterado.

Essa conferência nunca transforma a estimativa do app em fatura oficial.

## Registro de validação da implementação

Em 28 de julho de 2026:

- a suíte automatizada foi concluída sem rede e sem usar credenciais reais;
- as rotas editoriais Terra e Sol foram conferidas separadamente com uma amostra curta
  autorizada, preservando falante, data, número e marcação de trecho inaudível;
- a estimativa usou as contagens efetivamente devolvidas pelas duas respostas;
- as rotas Qt foram carregadas nos tamanhos padrão e mínimo, e os estados de conclusão e
  falha editorial foram inspecionados em capturas de tela.

Também foi concluído um ensaio de 19min35s com o vídeo `xjTU-mcJTs8`. O app aproveitou
as legendas automáticas originais em português, dividiu a melhoria em dois blocos Terra,
informou 8.461 tokens e estimou US$ 0,064639125. TXT, DOCX e VTT foram exportados sem
marcações de tempo nos documentos. O ensaio revelou e permitiu corrigir falsos positivos
na proteção de datas e falantes, quebras arbitrárias herdadas das legendas e a permanência
de uma antiga mensagem de erro após uma retomada bem-sucedida.

A comparação posterior com os painéis oficiais continua sendo uma conferência manual
anterior à distribuição.

## Liberação

O build fica bloqueado se houver:

- zero falso para uma tentativa possivelmente paga;
- duplicação de custo ao retomar;
- perda de compatibilidade com trabalhos antigos;
- exposição de detalhes técnicos na GUI;
- preços por milhão fora da Ajuda;
- clipping, rolagem insuficiente ou ação encoberta;
- divergência entre a tabela embarcada e as fontes oficiais verificadas na data do build.
- custo ou tokens da melhoria ausentes do total.
