# Especificação — cancelamento limitado e melhoria não bloqueante

**Estado:** implementada e validada em código-fonte; smoke dos pacotes pendente
**Branch:** `corrigir-bug-cancelar-envio-e-falhas`
**Incidente de referência:** 30 de julho de 2026, São Francisco 0.1.1 notarizado

## Objetivo

Fazer a transcrição continuar sendo o resultado confiável do São Francisco, mesmo quando
a melhoria opcional com IA falhar ou uma chamada não responder.

Depois desta mudança:

- a transcrição original fica disponível assim que for persistida;
- o app não tenta garantir em tempo de execução que a IA produziu um texto perfeito;
- uma falha editorial não aparece como falha de arquivo;
- cancelar termina em tempo limitado e libera uma nova transcrição;
- nenhuma tentativa paga incerta é repetida automaticamente.

## Diagnóstico do incidente

### O que foi concluído

O manifesto local do trabalho do incidente mostra que a origem e a transcrição não
falharam:

- o vídeo público tinha `7.774,52` segundos;
- as legendas automáticas foram obtidas e normalizadas;
- a legenda e a transcrição original foram persistidas integralmente;
- o texto editorial foi dividido em nove blocos;
- o primeiro bloco melhorado foi aceito e salvo.

### O que falhou

O segundo bloco recebeu duas respostas pagas, ambas registradas como `rejected`. As duas
somaram aproximadamente US$ 0,095. O manifesto não registra qual comparação bloqueante —
extensão, números, marcações ou falantes — recusou a resposta, e não preserva o texto
recusado. Não é possível determinar honestamente a comparação exata sem fazer outra
chamada paga, o que não será feito.

É possível provar o caminho do erro: `validate_editorial_result` lançou
`EditorialValidationError`; como essa classe deriva de `ValueError`, o tradutor público a
converteu incorretamente em:

> Um arquivo necessário não pôde ser processado.

O arquivo original já estava íntegro. O erro foi uma política editorial bloqueante, não
uma falha de arquivo.

### Por que o cancelamento não terminou

O backend executa toda a fila em um único `QThread`. Cancelar apenas sinaliza um token e
tenta fechar o cliente HTTP. A fila só é liberada quando o worker retorna.

Uma amostragem do processo notarizado vivo mostrou `transcription-worker` bloqueado numa
leitura SSL. Fechar o cliente a partir da interface não interrompeu a leitura, cujo timeout
era de 1.800 segundos. Enquanto isso:

- a tarefa ativa permaneceu ocupada;
- `busy` permaneceu verdadeiro;
- o botão de iniciar ficou desativado;
- o progresso conservou o último valor;
- nenhuma nova transcrição pôde começar.

O teste atual de cancelamento usa um fake cooperativo. O fake incooperativo existente só
testa o fechamento de todo o aplicativo.

## Decisão de produto

### Abolir o protetor semântico

O São Francisco promete transcrição e oferece uma melhoria opcional, não uma certificação
de perfeição editorial. A transcrição original separada é a referência. A própria
interface já orienta a conferir nomes, números e trechos pouco claros.

Por isso, o runtime deixa de comparar e bloquear:

- números, datas, valores e percentuais;
- falantes;
- marcações de inaudível;
- proporção de extensão do texto.

Não haverá mascaramento, placeholders nem tentativa de corrigir deterministicamente a
saída da IA.

Permanecem somente verificações técnicas:

- o provedor devolveu texto não vazio e decodificável;
- o resultado está associado ao ID correto do bloco;
- os artefatos puderam ser persistidos;
- todos os blocos exigidos existem uma vez e podem ser montados na ordem.

O contrato de fidelidade continua no prompt e na avaliação de qualidade antes da
liberação. Ele deixa de ser uma barreira heurística dentro de cada trabalho real.

### A transcrição original não espera pela melhoria

Assim que a transcrição ou legenda normalizada for montada e persistida, os formatos
originais selecionados são exportados. A melhoria roda depois e produz somente os arquivos
adicionais de **texto melhorado**.

Se a melhoria falhar ou for cancelada:

- os arquivos originais continuam disponíveis;
- o Histórico informa que a transcrição ficou pronta e a melhoria não;
- o usuário pode retomar explicitamente só a melhoria;
- a falha editorial não ocupa indefinidamente a fila.

Esta decisão refina o sequenciamento de `MI-RF-02`, `MI-RF-07` e `MI-RF-12`: persistir a
transcrição continua sendo pré-requisito da melhoria, mas exportar o original não depende
mais do sucesso da etapa opcional.

### Não repetir chamadas pagas automaticamente

Cada resposta textual não vazia é aceita e persistida. Falha de rede, timeout, resposta
vazia ou interrupção não inicia retry automático.

Uma tentativa cujo resultado remoto é incerto fica marcada como ambígua. Retomá-la exige
ação explícita, pois o provedor pode ter processado e cobrado a chamada anterior.

Os registros `rejected` de trabalhos 0.1.1 continuam legíveis. Como suas respostas foram
descartadas, eles não podem ser reaproveitados; uma nova tentativa exige retomada explícita
e aviso de possível nova cobrança.

### O cancelamento terá uma fronteira encerrável

O trabalho caro deve executar num processo descartável, ou fronteira equivalente que
possa ser encerrada sem matar o `QThread` da aplicação.

Ao cancelar:

1. persistir `cancel_requested`;
2. sinalizar cancelamento cooperativo;
3. aguardar no máximo cinco segundos;
4. encerrar o processo de trabalho se ele não retornar;
5. marcar a tentativa em voo como `remote_ambiguous`;
6. marcar o trabalho como `cancelled`;
7. recriar a fronteira de execução e liberar a interface.

`QThread.terminate()` continua restrito ao fallback de encerramento do aplicativo e não é
uma solução aceitável para o botão **Cancelar**.

### A recuperação será conservadora

Uma etapa concluída e persistida é reutilizada. Uma tentativa ambígua não é reenviada
automaticamente. Manifestos 0.1.1 permanecem legíveis; um trabalho antigo interrompido
durante `improving` é pausado e exige retomada explícita.

### O progresso representará todas as etapas pedidas

`progress = 1` fica reservado à conclusão de todas as etapas solicitadas. O Histórico não
pode usar apenas `completed_chunks / chunks` quando ainda há melhoria ou exportação.

A interface recebe progresso geral e progresso da etapa. Durante a melhoria, mostra a
contagem editorial real. Depois do clique, mostra **Cancelando** em vez de sugerir que o
percentual continua avançando.

## Escopo

- remover as verificações semânticas bloqueantes do resultado editorial;
- manter validação estrutural de resposta, persistência e montagem;
- exportar o original antes da melhoria opcional;
- distinguir transcrição concluída de melhoria falha ou cancelada;
- corrigir a classificação pública do erro legado;
- persistir tentativas e resultados remotos ambíguos;
- impedir retry pago automático;
- limitar cancelamento e liberar a fila;
- corrigir progresso e estados da interface;
- manter compatibilidade com trabalhos 0.1.1.

## Fora do escopo

- mudar modelos ou provedores;
- prometer ou medir perfeição factual por trabalho;
- acrescentar resumo, tradução ou edição criativa;
- executar duas transcrições simultaneamente;
- redesenhar toda a fila ou o Histórico;
- apagar ou reprocessar automaticamente o trabalho do incidente;
- remover legado em larga escala;
- gerar e notarizar um pacote antes da validação desta mudança.

## Critério de conclusão

A mudança estará concluída quando testes sem rede provarem que:

- uma resposta editorial textual não é recusada por comparação de conteúdo;
- resposta vazia, artefato ausente e montagem incompleta ainda falham tecnicamente;
- o original é exportado antes da melhoria e sobrevive a qualquer falha editorial;
- nenhuma falha editorial é apresentada como erro de arquivo;
- nenhum retry pago acontece sem ação explícita;
- um worker incooperativo é encerrado em até cinco segundos mais pequena margem;
- uma nova transcrição conclui depois do cancelamento;
- uma tentativa ambígua não é retomada automaticamente;
- manifestos antigos continuam abrindo;
- a fronteira de execução funciona nos pacotes macOS e Windows.

## Limite de esforço e custo

- **Hipótese:** remover o guard semântico elimina a recusa que bloqueou o trabalho; isolar
  o worker torna o cancelamento limitado.
- **Amostra inicial:** fixtures locais com a topologia de nove blocos, sem copiar o
  conteúdo do vídeo.
- **Chamadas pagas automatizadas:** zero.
- **Validação manual paga:** no máximo duas chamadas com fixture curta, com teto planejado
  de US$ 0,05 no total.
- **Builds demorados:** um smoke build por plataforma somente depois dos testes locais.
- **Condição de parada:** o primeiro retry inesperado, processo órfão ou falha sem estado
  estruturado exige novo diagnóstico antes de repetir.
