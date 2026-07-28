# Plano — estimativa de custos

## 1. Modelo de custos

- Criar tipos imutáveis para preço, uso e estimativa.
- Implementar formatação amigável em USD.
- Criar a tabela versionada de preços e os cálculos temporais ou por uso.
- Cobrir zero comprovado, valor inferior a um centavo e indisponibilidade.

**Arquivos previstos:** novo módulo em `sao_francisco/core/` e testes unitários próprios.

## 2. Captura do uso nas provedoras

- OpenAI: preservar o objeto `usage` quando a resposta de transcrição o oferecer.
- OpenAI: usar duração e tarifa oficial por minuto como alternativa compatível.
- Gemini: extrair os totais de entrada, saída e raciocínio da Interactions API.
- Normalizar os dois formatos e levar à interface somente a contagem total.
- Manter a transcrição funcional quando campos opcionais não vierem na resposta.

**Arquivos previstos:** `providers/openai_provider.py`,
`providers/gemini_provider.py`, `providers/base.py` e `tests/test_providers.py`.

## 3. Persistência e retomada

- Salvar o custo da parte junto ao resultado já persistido de forma atômica.
- Somar custos no manifesto sem recalcular registros antigos.
- Preservar o total ao pausar, cancelar, falhar ou retomar.
- Registrar custo zero para o fluxo integral de legendas sem melhoria.
- Tratar legendas com melhoria como custo editorial, não como zero.
- Ler manifestos anteriores sem migração obrigatória.

**Arquivos previstos:** `core/job_store.py`, `pipeline.py` e respectivos testes.

## 4. Contrato da interface

- Expor rótulos prontos para uso, a contagem total informada e estados simples:
  disponível, zero comprovado ou indisponível.
- Atualizar o progresso quando uma parte concluir.
- Acrescentar o rótulo discreto à tela de transcrição, ao resultado e ao Histórico.
- Não criar controles, tabelas detalhadas ou diálogos técnicos.
- Verificar quebra de linha, contraste, foco e largura mínima.

**Arquivos previstos:** `backend.py`, `qml/BACKEND_CONTRACT.md`,
`qml/pages/TranscribePage.qml`, `qml/pages/HistoryPage.qml` e testes QML.

## 5. Texto editorial

- Adicionar os textos definitivos a `TEXTOS_DO_APP.md`.
- Inserir na Ajuda uma seção curta: o que é estimativa, por que pode variar e onde
  consultar a cobrança oficial.
- Usar os links oficiais de OpenAI e Gemini.
- Colocar os preços por milhão somente na Ajuda, em uma tabela datada e contextualizada.

## 6. Validação e acabamento

- Executar a matriz de `validation.md`.
- Validar a soma de transcrição e **Melhorar com IA**, incluindo Terra e Sol.
- Inspecionar visualmente as telas padrão e mínima, com nomes longos e todos os estados
  de custo.
- Atualizar `SPEC.md`, README e contratos caso a implementação revele alguma decisão
  diferente.
- Somente então gerar e testar novamente o pacote Apple Silicon.

## Ordem de entrega

1. cálculo e testes unitários;
2. captura das provedoras;
3. persistência e retomada;
4. backend e GUI;
5. Ajuda e textos;
6. validação completa;
7. build para teste do usuário;
8. publicação posterior, após aprovação.

## Decisões já tomadas

- Moeda inicial: USD.
- Estimativa automática, sem configuração.
- Na GUI, somente o total de tokens informado; sem decomposição ou preços unitários.
- Sem consulta à conta de cobrança.
- Sem chamadas pagas nos testes automatizados.
- Legendas reutilizadas: custo de API zero.
