# Ajuda do São Francisco

O São Francisco transforma áudio e vídeo em texto. Você pode escolher um arquivo do
computador ou colar o endereço público de um vídeo. A interface começa em inglês;
você pode mudá-la em **Configurações → Idioma da interface**, sem alterar o idioma
das gravações.

## Primeiros passos

Para conhecer o aplicativo, comece com uma gravação curta:

1. Abra **Configurações** e cadastre uma chave da OpenAI ou do Gemini.
2. Volte a **Transcrever**.
3. Escolha um arquivo ou cole o endereço de um vídeo.
4. Selecione o serviço e o modelo.
5. Marque os formatos que deseja receber.
6. Escolha a pasta de destino.
7. Pressione **Iniciar transcrição**.

Quando o trabalho terminar, os arquivos estarão na pasta escolhida. Você também poderá
abri-los pela tela **Histórico**.

## Adicionar arquivo, vídeo ou URL

Na guia **Arquivos**, escolha um ou mais arquivos de áudio ou vídeo do computador.
Formatos comuns, como MP3, WAV, M4A, MP4, MOV, MKV e WebM, são aceitos.

Na guia **YouTube ou endereço**, cole o endereço público do vídeo. Alguns conteúdos podem
não estar disponíveis quando exigem login, assinatura, pagamento ou autorização especial
do site.

Se quiser aproveitar o texto publicado com o vídeo, marque **Usar legendas disponíveis no
vídeo**. O São Francisco remove repetições progressivas antes de criar o documento. A
opção começa desmarcada; deixe-a assim quando preferir uma nova transcrição do áudio.

Um vídeo acessível na internet não é necessariamente de uso livre. Transcreva somente
materiais que você tenha direito ou autorização para usar.

### Detectar o idioma

**Detectar automaticamente** deixa o serviço reconhecer o idioma falado. Também é
possível informar o idioma diretamente.

Nenhuma das opções é sempre melhor. Indicar o idioma pode ajudar em gravações ruidosas,
sotaques, nomes próprios e línguas parecidas. A detecção automática é útil quando você
não sabe o idioma ou quando o conteúdo mistura mais de um.

## Escolher um modelo

Os nomes da lista indicam o uso recomendado:

- **Econômico — OpenAI:** boa opção para começar e para textos contínuos.
- **Maior precisão — OpenAI:** prioriza nomes próprios e vocabulário.
- **Identificar falantes — OpenAI:** separa os participantes quando possível.
- **Legendas e tempos — OpenAI:** oferece marcações de tempo mais precisas.
- **Gemini detalhado:** produz uma transcrição estruturada.
- **Gemini econômico:** alternativa para maior volume.

A qualidade depende da gravação. Ruído, música alta, pessoas falando ao mesmo tempo,
microfone distante e nomes incomuns podem exigir revisão.

Modelos e disponibilidade podem mudar conforme cada serviço.

## Chaves da OpenAI e do Gemini

Uma chave de API é uma credencial secreta que permite ao São Francisco enviar o áudio ao
serviço escolhido. Você não precisa ser desenvolvedor para criar uma.

A assinatura de um chatbot e o uso da API são serviços separados. ChatGPT Plus, por
exemplo, não inclui automaticamente créditos da API OpenAI. Cada serviço administra
cobrança, limites e acesso aos modelos em sua própria plataforma.

O São Francisco guarda a chave no cofre seguro do sistema e nunca volta a exibi-la por
inteiro.

### Criar uma chave da OpenAI

1. Abra a [página oficial de chaves da OpenAI](https://platform.openai.com/api-keys).
2. Entre ou crie uma conta.
3. Crie uma chave para o projeto desejado.
4. Copie a chave quando ela aparecer.
5. No São Francisco, abra **Configurações → OpenAI** e cole a chave.
6. Escolha **Verificar** e, depois, **Salvar configurações**.

Uma chave pode ser válida e ainda não ter saldo, limite ou acesso ao modelo escolhido.
Nesse caso, confira a cobrança e os limites na plataforma da OpenAI.

### Criar uma chave do Gemini

1. Abra a [página oficial de chaves do Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Entre no Google AI Studio.
3. Escolha um projeto e crie a chave.
4. No São Francisco, abra **Configurações → Gemini** e cole a chave.
5. Escolha **Verificar** e, depois, **Salvar configurações**.

> [!WARNING]
> Nunca envie uma chave em documento, captura de tela, mensagem ou pedido de suporte.
> Se uma chave for exposta, revogue-a e crie outra.

## Como mídias longas são processadas

O São Francisco prepara vídeos longos em etapas menores e reúne tudo em uma única
transcrição. Isso permite trabalhar com gravações de qualquer duração sem enviar o vídeo
inteiro de uma vez.

Cada etapa concluída é guardada. Se houver uma interrupção, você poderá continuar pelo
**Histórico** sem recomeçar todo o trabalho.

O tempo necessário depende da duração da gravação, da velocidade da internet e da
disponibilidade do serviço escolhido.

## Acompanhar, cancelar e retomar

Durante a transcrição, a tela mostra o andamento e informa qual parte está sendo
processada.

**Cancelar** muda o cartão para **Cancelando** e encerra a execução em até cerca de cinco
segundos. Partes e arquivos já concluídos permanecem disponíveis. Uma chamada que já
tenha chegado ao serviço pode terminar ou gerar cobrança mesmo depois do cancelamento.

**Retomar** continua um trabalho interrompido. Se você trocar o arquivo, o serviço, o
modelo ou o idioma, será necessário iniciar uma nova transcrição. Quando o resultado de
uma chamada anterior for incerto, o aplicativo avisa antes de permitir uma nova chamada,
pois ela pode gerar outra cobrança.

## Formatos de saída

- **TXT:** texto simples, adequado para leitura e pesquisa.
- **DOCX:** documento formatado, pronto para abrir em editores de texto.
- **SRT:** legenda para reprodutores e editores de vídeo.
- **VTT:** legenda usada principalmente em páginas da internet.

As marcações de tempo no DOCX e no TXT são opcionais e ficam desativadas por padrão. Para
incluí-las, marque **Incluir marcações de tempo no DOCX e TXT** antes de iniciar.

Arquivos SRT e VTT sempre precisam de tempos para funcionar como legendas. Quando o modelo
não oferece tempos exatos, o resultado pode precisar de ajustes no editor de vídeo.

Para vídeos da internet, o São Francisco usa o título do vídeo no nome dos arquivos,
adaptando-o quando necessário. Se já existir um arquivo com o mesmo nome, acrescenta um
número ao novo resultado.

### Melhorar com IA

Marque **Melhorar com IA** quando quiser receber, além da transcrição original, uma
segunda versão mais confortável para leitura. O aplicativo organiza parágrafos e corrige
pontuação, maiúsculas e erros evidentes de reconhecimento.

A melhoria não deve resumir, traduzir, embelezar nem completar trechos duvidosos. Mesmo
assim, confira especialmente nomes, números e partes pouco claras.

DOCX e TXT recebem arquivos separados, identificados como **transcrição** e **texto
melhorado**. As marcações de tempo permanecem somente no original. SRT e VTT não são
reescritos pela etapa de melhoria.

O trabalho segue uma ordem segura: primeiro a transcrição é concluída, guardada e
exportada; depois o texto é melhorado, se você tiver marcado a opção; por último são
criados os arquivos adicionais de texto melhorado. Se a melhoria for interrompida, os
arquivos originais continuam disponíveis. A retomada reaproveita etapas aceitas e não
repete automaticamente uma chamada cujo resultado ficou incerto.

## Custos, dados e armazenamento

A compra do aplicativo é separada do uso das APIs. O São Francisco não cobra por
transcrição. Eventuais custos de API são cobrados diretamente pela OpenAI ou pelo
Google, conforme a sua conta e o modelo escolhido; a compra não inclui créditos de API.

Cada parte enviada pode gerar consumo. Ao retomar, o aplicativo reaproveita o que já foi
concluído.

Quando houver dados suficientes, o São Francisco mostra um custo aproximado em dólares.
Valores muito pequenos aparecem como **menos de US$ 0,01**. Se o texto vier integralmente
de legendas já disponíveis e não houver melhoria, aparece **Sem custo de API**.

O total é apenas uma estimativa. Planos gratuitos, impostos, descontos, tentativas
interrompidas e mudanças de preço podem fazer o painel do serviço mostrar outro valor.
Consulte a cobrança oficial no [uso da OpenAI](https://platform.openai.com/usage) ou no
[faturamento do Google Cloud](https://console.cloud.google.com/billing).

Quando o serviço informar uma contagem confiável, o aplicativo também pode mostrar o
total de tokens. Tokens são pequenas unidades usadas para medir a entrada e a resposta.
O São Francisco não inventa uma contagem quando ela não é fornecida.

### Preços atuais das APIs

Consulte as páginas oficiais de [preços da OpenAI](https://developers.openai.com/api/docs/pricing)
e de [preços do Gemini](https://ai.google.dev/gemini-api/docs/pricing). Preços, unidades,
modelos e planos gratuitos podem mudar. Confira antes de iniciar um trabalho pago.

O áudio é enviado ao serviço selecionado. O histórico e os arquivos de trabalho ficam no
computador. Os resultados permanecem na pasta de destino até que você os apague.

Consulte os [termos da OpenAI](https://openai.com/policies) e os
[termos da API Gemini](https://ai.google.dev/gemini-api/terms).

## Problemas comuns

### A chave não foi aceita

**Sintoma:** a tela Configurações informa que a chave é inválida.

**O que fazer:** confira se a chave pertence ao serviço correto, se foi copiada por
inteiro e se continua ativa. Depois, verifique cobrança, limites e acesso ao modelo.

### O arquivo não tem áudio

**Sintoma:** o trabalho termina antes de começar a transcrição.

**O que fazer:** abra o arquivo e confirme que existe som. Arquivos danificados ou vídeos
compostos apenas por imagens não podem ser transcritos.

### O endereço do vídeo deixou de funcionar

**Sintoma:** o aplicativo não consegue obter o vídeo.

**O que fazer:** atualize o São Francisco e tente novamente. Conteúdo com login,
pagamento, transmissão ao vivo ou bloqueio do site pode continuar indisponível.

### O processamento parece parado

**Sintoma:** a mesma parte permanece ativa por vários minutos.

**O que fazer:** gravações longas e serviços ocupados podem demorar. Se aparecer uma
mensagem de rede ou limite, cancele e retome depois.

### A legenda ficou fora de sincronia

**Sintoma:** o arquivo SRT ou VTT antecipa ou atrasa uma fala.

**O que fazer:** use o modelo **Legendas e tempos** e revise o resultado junto ao vídeo.

### Não há espaço no computador

**Sintoma:** o trabalho é interrompido durante a preparação ou a criação dos arquivos.

**O que fazer:** libere espaço e tente novamente.

## Atalhos e navegação

- `⌘N` no macOS ou `Ctrl+N` nos demais sistemas abre **Transcrever**.
- `⌘K` ou `Ctrl+K` abre a **Ajuda**.
- `⌘,` no macOS ou `Ctrl+,` abre **Configurações**.
- `Tab` e `Shift+Tab` movem o foco.
- `Enter` ou `Espaço` ativa o controle em foco.
- `Page Up`, `Page Down`, `Home` e `End` percorrem textos longos.
- `Esc` fecha janelas de aviso.

O índice e o artigo da Ajuda possuem rolagem independente.

## Licenças e sobre

O código do São Francisco é distribuído sob a licença MIT. A venda dos pacotes prontos
para download não retira as liberdades concedidas por essa licença.

Componentes, bibliotecas e fontes conservam suas próprias licenças. Na tela **Sobre**,
escolha **Ver avisos de terceiros** para ler o inventário dentro do aplicativo.
