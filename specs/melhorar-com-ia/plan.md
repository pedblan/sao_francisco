# Plano — Melhorar com IA

## 1. Modelo de domínio

- Acrescentar a opção editorial ao trabalho sem alterar o padrão existente.
- Definir estados e checkpoints sequenciais para transcrição, melhoria e exportação.
- Modelar blocos editoriais, resultados persistidos e montagem.
- Preservar compatibilidade com manifestos anteriores.

## 2. Provedores de melhoria

- Criar uma interface textual separada dos provedores de transcrição.
- OpenAI: usar Responses API com `gpt-5.6-terra` ou `gpt-5.6-sol` conforme o roteamento.
- Gemini: usar o modelo econômico ou detalhado já escolhido.
- Capturar texto, uso, modelo efetivo e erros públicos.
- Não habilitar ferramentas, pesquisa, Pro, multiagente ou recursos desnecessários.

## 3. Contrato editorial

- Criar um prompt curto, estável e resistente a instruções contidas na transcrição.
- Delimitar claramente contexto e bloco-alvo.
- Exigir preservação de nomes, números, falantes e marcações de incerteza.
- Exigir somente o texto melhorado do bloco-alvo.
- Versionar o contrato para que trabalhos retomados conservem o mesmo comportamento.

## 4. Divisão, persistência e montagem

- Dividir em limites naturais com IDs estáveis.
- Enviar contexto mínimo sem permitir que ele reapareça na saída.
- Persistir cada bloco de forma atômica.
- Validar ordem, completude, duplicações e variação anormal de extensão.
- Permitir retomar somente a etapa editorial.

## 5. Exportação

- Bloquear a exportação até que transcrição e eventual melhoria estejam persistidas.
- Exportar original, melhorado e legendas somente na etapa final.
- Gerar DOCX e TXT melhorados sem marcações de tempo.
- Manter SRT e VTT intocados.
- Aplicar nomes seguros com os sufixos **transcrição** e **texto melhorado**.
- Agrupar os resultados sem sobrescrever arquivos existentes.
- Permitir repetir somente a exportação quando ela falhar.

## 6. Custos

- Acrescentar Terra e Sol à tabela de preços versionada.
- Registrar uso e custo por bloco editorial.
- Somar transcrição e melhoria no total do trabalho.
- Atualizar a previsão depois que o texto original estiver disponível.
- Corrigir o caso de legendas: zero somente quando não houver etapa editorial.

## 7. Backend e GUI

- Acrescentar `improveWithAi` ao contrato de início do trabalho.
- Inserir a caixa e o texto de apoio na área de formatos.
- Mostrar estados sequenciais simples no progresso e no Histórico.
- Agrupar original, melhorado e legendas no resultado.
- Manter detalhes técnicos fora do QML.

## 8. Ajuda e inventário editorial

- Adicionar os textos definitivos a `TEXTOS_DO_APP.md`.
- Criar uma seção clara e espaçada na Ajuda.
- Explicar limites, conferência, arquivos, retomada e custos.
- Manter modelos e preços por milhão somente na Ajuda ou em documentação técnica.

## 9. Avaliação e validação

- Montar um conjunto de transcrições reais e sintéticas, incluindo os exemplos ruins já
  fornecidos.
- Comparar Terra e Sol com os esforços de raciocínio candidatos.
- Medir preservação, omissões, acréscimos, nomes, números, falantes, parágrafos, custo e
  tempo.
- Executar toda a matriz de `validation.md`.
- Somente depois gerar um novo build Apple Silicon para teste.

## Ordem de implementação

1. domínio e fixtures;
2. contrato editorial;
3. provedores textuais;
4. divisão e retomada;
5. exportação;
6. custos;
7. backend e GUI;
8. Ajuda;
9. avaliação comparativa;
10. validação completa e build.
