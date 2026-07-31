# Plano — cancelamento e melhoria não bloqueante

## 1. Caracterizar o incidente sem rede

- Criar fixture sintética de nove blocos com original concluído e um bloco editorial
  aceito.
- Confirmar que a versão atual transforma `EditorialValidationError` em erro de arquivo.
- Confirmar que o original persistido ainda não é exportado quando a melhoria falha.
- Criar fake de chamada que ignora token, fechamento e timeout cooperativo.
- Contar chamadas e registrar estados antes da alteração.

Não usar o vídeo original nem chamar a OpenAI.

## 2. Remover o guard semântico

- Remover comparações bloqueantes de extensão, números, marcações e falantes.
- Não criar mascaramento, placeholders ou reparo heurístico.
- Manter somente resposta textual não vazia, associação ao bloco, persistência e montagem
  completa/ordenada.
- Corrigir o tradutor do erro legado para nunca mencionar arquivo.
- Manter o contrato editorial no prompt e nas avaliações de versão.

## 3. Separar original e melhoria

- Persistir e exportar todos os formatos originais antes da etapa editorial.
- Registrar a transcrição como concluída independentemente da melhoria.
- Fazer a melhoria acrescentar somente DOCX/TXT melhorados.
- Preservar originais quando houver falha, timeout ou cancelamento.
- Permitir retomada explícita apenas dos blocos editoriais ausentes.
- Atualizar agrupamento de resultados e estados compostos no Histórico.

## 4. Persistir tentativas

- Acrescentar registros compatíveis de tentativa ao manifesto.
- Escrever `running` antes da chamada e `accepted` depois do artefato.
- Representar falha, cancelamento e resultado remoto ambíguo.
- Impedir retry automático.
- Somar custo conhecido sem duplicação.
- Ler `rejected` legado e exigir retomada explícita.
- Pausar manifestos 0.1.1 ambíguos sem auto-retry.

## 5. Isolar a execução

- Definir mensagem serializável sem segredo em argumentos ou logs.
- Executar uma tarefa por vez num processo descartável.
- Usar IPC mínimo para progresso, resultado e diagnóstico.
- Carregar a credencial dentro da fronteira segura.
- Persistir `cancel_requested`, sinalizar e aguardar cinco segundos.
- Encerrar o processo incooperativo e criar worker limpo.
- Marcar chamada em voo como `remote_ambiguous`.

### Ponto de decisão de empacotamento

Validar cedo macOS `spawn`, Windows e PyInstaller, com `freeze_support` ou helper dedicado.
Se o processo não iniciar de modo confiável nos pacotes, interromper e escolher outra
fronteira descartável segura. Não substituir por `QThread.terminate()` no botão
**Cancelar**.

## 6. Backend e fila

- Acrescentar `cancelling` ao contrato Qt.
- Implementar deadline no controlador.
- Aceitar uma única conclusão por chave e ignorar mensagem tardia do worker descartado.
- Limpar tarefa ativa, atualizar Histórico, restaurar `busy` e recriar a fronteira.
- Preservar a remoção informada de itens aguardando.
- Provar que uma segunda tarefa conclui depois da primeira incooperativa.

## 7. Timeout e progresso

- Trocar o timeout editorial de 1.800 segundos por constante inicial de cinco minutos.
- Manter timeout de rede e deadline de cancelamento independentes.
- Separar progresso geral e progresso da etapa.
- Evitar 100% durante melhoria ou exportação pendente.
- Mostrar contagem editorial e estado **Cancelando**.

## 8. Interface, Ajuda e contratos

- Explicar que o original fica pronto antes da melhoria.
- Manter o aviso de conferência de nomes, números e trechos pouco claros.
- Escrever mensagens para melhoria falha, retomada e custo possivelmente ambíguo.
- Atualizar `TEXTOS_DO_APP.md`, `AJUDA.md` e `qml/BACKEND_CONTRACT.md`.
- Sincronizar `SPEC.md` e a spec de **Melhorar com IA** depois da implementação.

## 9. Validação incremental

1. testes estruturais editoriais;
2. testes de exportação original antecipada;
3. testes de tentativas e custo;
4. testes do pipeline com contador de chamadas;
5. testes Qt com processo incooperativo;
6. testes QML offscreen;
7. suíte completa, lint e tipos;
8. smoke build macOS;
9. smoke build Windows;
10. amostra manual curta dentro do limite de custo.

## Dependências

- processo compatível com PyInstaller, macOS e Windows;
- escrita atômica existente no `JobStore`;
- fakes de provedor e pipeline existentes;
- cofre seguro do sistema para credenciais.

## Condições para interromper e reavaliar

- a chave precisaria aparecer em linha de comando ou manifesto;
- resultado aceito poderia ser perdido entre artefato e estado;
- cancelamento deixaria processo órfão;
- a tarefa antiga poderia alterar a nova;
- o original deixaria de abrir por causa da melhoria;
- uma unidade seria enviada duas vezes sem ação explícita;
- o pacote congelado não iniciaria a fronteira;
- uma chamada paga manual falharia sem novo diagnóstico.
