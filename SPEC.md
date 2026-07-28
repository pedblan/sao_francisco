# Especificação do produto — São Francisco

Este documento registra as decisões de produto que devem permanecer sincronizadas com a
interface, a Ajuda e os testes.

## Propósito

São Francisco é um aplicativo desktop de transcrição para pessoas que não precisam
conhecer os componentes técnicos usados internamente. Ele transforma arquivos locais e
vídeos públicos da internet em DOCX, TXT, SRT ou VTT.

O subtítulo da marca é **Abençoe sua transcrição**.

## Princípios da interface

- Usar linguagem cotidiana e orientar pela tarefa do usuário.
- Não citar ferramentas internas nas telas, mensagens de erro ou Ajuda.
- Manter textos curtos na interface e explicações mais amplas na Ajuda.
- Preservar o tema **Terra Franciscana**, com Jost nos títulos e Source Sans 3 na
  interface.
- Garantir rolagem, navegação por teclado e foco visível em todas as telas.

## Entrada e transcrição

- Aceitar arquivos locais de áudio ou vídeo e endereços públicos de vídeo.
- Usar **Detectar automaticamente** como opção inicial neutra, sem apresentá-la como
  superior aos idiomas escolhidos pelo usuário.
- Transcrever o áudio por padrão.
- Em endereços de vídeo, oferecer **Usar legendas disponíveis no vídeo**, desativado por
  padrão. Remover repetições progressivas antes de exportar essas legendas.
- Dividir mídias longas em partes antes do envio, salvar cada parte concluída e reuni-las
  em uma transcrição contínua.
- Permitir cancelar e retomar trabalhos.
- Manter compatibilidade de leitura com trabalhos antigos que tenham usado legendas.

## Saída

- Oferecer DOCX, TXT, SRT e VTT.
- Iniciar com DOCX, TXT e SRT marcados; VTT desmarcado.
- Oferecer **Incluir marcações de tempo no DOCX e TXT**, desativado por padrão.
- SRT e VTT mantêm seus tempos obrigatórios.
- Para endereços da internet, aproveitar o título do vídeo no nome dos arquivos,
  sanitizado e limitado a um tamanho seguro.
- Nunca sobrescrever silenciosamente: acrescentar um número quando o nome já existir.
- Executar o fluxo em ordem estrita: obter ou transcrever e persistir o texto; melhorar e
  persistir, quando solicitado; somente então exportar os arquivos finais.
- Se a exportação falhar, retomar apenas a exportação, sem repetir transcrição, obtenção de
  legendas ou melhoria já concluídas.

## Melhorar com IA

- Oferecer **Melhorar com IA** como caixa de seleção, desativada por padrão.
- Explicar em uma única frase: **Organiza em parágrafos e corrige pontuação e erros
  evidentes, sem resumir.**
- Concluir e persistir a transcrição original antes de iniciar qualquer melhoria.
- Quando a opção estiver marcada, produzir versões separadas e claramente nomeadas da
  transcrição e do texto melhorado.
- Aplicar a melhoria somente a DOCX e TXT. SRT e VTT permanecem fiéis à transcrição e às
  marcações de tempo.
- Manter marcações de tempo apenas na versão original. O texto melhorado é contínuo e
  paragrafado.
- Dividir textos longos em partes seguras, salvar cada parte concluída e permitir retomar
  a melhoria sem retranscrever o áudio.
- Se a melhoria falhar, manter a transcrição persistida para retomada. Os arquivos finais
  ainda não são exportados.
- Corrigir apenas paragrafação, pontuação, maiúsculas e erros de reconhecimento evidentes.
  Não resumir, traduzir, embelezar, completar trechos duvidosos nem alterar o sentido.
- Preservar falantes, nomes, números, citações, hesitações relevantes e indicações de
  trechos inaudíveis.
- Na OpenAI, usar internamente `gpt-5.6-terra` para o fluxo de volume e
  `gpt-5.6-sol` para o fluxo de maior cuidado, sem acrescentar um seletor técnico à GUI.
- No Gemini, conservar a distinção já existente entre o modelo econômico e o modelo
  detalhado.
- Incluir o custo e os tokens da melhoria na estimativa total do trabalho.

## Configurações

- Guardar chaves da OpenAI e do Gemini no cofre seguro do sistema.
- Permitir escolher a pasta de saída, retomar tarefas interrompidas e receber aviso ao
  concluir.
- A geometria da janela é lembrada automaticamente e não aparece como configuração.

## Histórico

- Permitir buscar, filtrar, abrir, retomar e inspecionar trabalhos.
- Centralizar o texto do filtro de estado dentro do botão.
- Continuar mostrando a origem de trabalhos antigos quando disponível.

## Custos estimados

- Informar custos em linguagem cotidiana, sem exigir que o usuário entenda fórmulas ou a
  divisão interna da mídia.
- Mostrar apenas uma estimativa curta em dólares, sempre identificada como aproximada.
- Usar a duração planejada quando a provedora publicar uma estimativa por minuto e
  aperfeiçoar o valor com os dados devolvidos por cada parte, quando disponíveis.
- Somar somente partes realmente enviadas. Ao retomar um trabalho, preservar o custo das
  partes concluídas e acrescentar apenas as novas.
- Informar **Sem custo de API** quando o resultado vier integralmente de legendas já
  disponíveis e a melhoria com IA não tiver sido solicitada.
- Nunca apresentar a estimativa como fatura: a cobrança oficial continua sendo a exibida
  pela provedora.
- Permitir mostrar a quantidade total de tokens realmente informada pela provedora como
  dado secundário, sem estimar uma contagem ausente.
- Manter preços por milhão, fórmulas e fontes fora da interface principal. Esses detalhes
  pertencem aos registros internos, à especificação técnica e à Ajuda.
- Manter a tabela de preços versionada e datada. Um modelo sem preço confiável deve
  aparecer sem valor, nunca com uma estimativa inventada.

## Ajuda e Sobre

- A Ajuda é integrada, pesquisável, clara, espaçada e escrita para não desenvolvedores.
- A Ajuda explica como criar chaves, custos, idiomas, formatos, retomada e problemas
  comuns.
- Avisos de terceiros abrem em um pop-up interno, com botão ×, botão **Fechar**, tecla
  `Esc` e corpo rolável.
- A primeira arte de Sobre é São Francisco em estilo Bauhaus.
- O cartão **SAIBA MAIS** usa o café Bauhaus do Maestro recolorido em Terra Franciscana;
  não repete a imagem do santo.
- O texto de divulgação dos livros segue o mesmo sentido usado no Maestro.

## Critérios de aceite desta revisão

- Legendas progressivas do YouTube são normalizadas sem repetir trechos no documento.
- DOCX e TXT saem sem prefixos de tempo quando a opção não for marcada.
- Um vídeo com título conhecido gera arquivos que aproveitam esse título.
- Não há configuração de tamanho e posição da janela.
- Não há referências visíveis a componentes internos na interface ou na Ajuda.
- O pop-up de terceiros funciona integralmente sem aplicativo externo.

## Especificações de funcionalidades

- [Estimativa de custos](specs/estimar-custos/spec.md)
- [Requisitos da estimativa de custos](specs/estimar-custos/requirements.md)
- [Plano de implementação](specs/estimar-custos/plan.md)
- [Plano de validação](specs/estimar-custos/validation.md)
- [Melhorar com IA](specs/melhorar-com-ia/spec.md)
- [Requisitos de Melhorar com IA](specs/melhorar-com-ia/requirements.md)
- [Plano de implementação de Melhorar com IA](specs/melhorar-com-ia/plan.md)
- [Validação de Melhorar com IA](specs/melhorar-com-ia/validation.md)
