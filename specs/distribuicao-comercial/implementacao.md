# Execução — interface multilíngue e preparação comercial

## Autorização de 29/08/2026

O autor pediu implementar as traduções, usar inglês como padrão, manter MIT e preparar
lançamento a US$ 5 nos canais compatíveis com recebimento no Banco do Brasil. Autorizou
abrir páginas para completar decisões e cadastros depois. Isso substitui a espera de
aprovação editorial anterior: traduzir a GUI efetiva, não as funções futuras do rascunho.

## Recortes e fronteiras

- Implementação nesta branch `codex/comercial-i18n-rtl`: nove idiomas, escolha persistida,
  inglês inicial/fallback, Ajuda localizada, RTL árabe, catálogos no pacote e testes.
- Preparação comercial documental: ficha US$ 5, materiais e checklist por canal,
  recebimento direto versus intermediado identificado, links de cadastro abertos.
- Não publicar, aceitar contratos, enviar dados bancários/fiscais, contratar assinatura
  de código ou submeter um candidato que ainda não passou pelas provas.
- Não executar chamadas pagas para tradução ou transcrição nesta etapa. Usar fixtures
  locais, dados artificiais claramente identificados e APIs falsas nos testes.
- Manter pipeline, fontes, prompts e conteúdo de documentos intactos; somente localizar
  mensagens determinísticas na camada de apresentação.

## Aceitação

1. Primeira abertura em inglês independentemente do idioma do sistema; seleção manual
   persistida entre reinícios. Idioma inválido retorna ao inglês.
2. Português, inglês, francês, espanhol, alemão, italiano, russo, chinês simplificado e
   árabe incluídos, sem misturar idioma de interface com idioma de transcrição.
3. Todas as rotas, mensagens da aplicação, Ajuda, acessibilidade e diálogos traduzíveis;
   textos legais de terceiros e dados do usuário permanecem originais.
4. Inglês de fallback completo; catálogo incompleto reprova auditoria de cobertura.
5. RTL árabe testado com paths/URLs em LTR; nenhuma transcrição é invertida ou traduzida.
6. Testes unitários/offscreen, lint, tipagem e inspeção de screenshots. Provas de pacote
   e sistema-alvo explicitamente separadas de testes do código-fonte.
7. Lojas classificadas por evidência de recebimento no BB, inclusive via processador;
   “aceita Brasil” não é prova de aceitação da conta específica nem de repasse direto.

## Matriz de preparação

| Alvo | Base | Runner | Formato | Assinatura | Estado |
| --- | --- | --- | --- | --- | --- |
| Mac | arm64 | Mac local | app/DMG/ZIP | Developer ID + notarização | pendente de validação e autorização disponível |
| Windows | x64 | Windows nativo/CI | ZIP/instalador a confirmar | Authenticode, serviço pendente | sem candidato nesta etapa |

Não afirmar que o pacote Windows foi testado no Mac. Não promover artefatos de teste
como release comercial, nem aumentar versão/publicar tag sem congelar o candidato.

## Registro

Estado inicial: apenas docs anteriores modificadas; runtime sem internacionalização.
Estado final da localização: nove idiomas implementados, 141 testes aprovados,
catálogo editorial real e ficha comercial a US$ 5 preparados. Sem alterações do pipeline,
prompts, provedores ou exportadores. Inglês padrão/fallback, árabe RTL e seleção persistida.

Evidências: [validação](validacao.md). Entrega e decisões pendentes:
[LANCAMENTO.md](../../LANCAMENTO.md). Candidato Mac local ad-hoc, não notarizado;
Windows nativo e assinatura pendentes. Pesquisa de oito canais, rota PayPal/BB
documentada e páginas enfileiradas para o retorno do autor. Nada publicado ou contratado.
