# Ajuda do São Francisco

O São Francisco transforma áudio, vídeo e mídias públicas da internet em texto.

Para gravações longas, ele prepara o áudio no computador, divide a mídia em partes
menores e preserva cada resultado concluído. Assim, uma interrupção não obriga você a
começar tudo novamente.

## Primeiros passos

Faça o primeiro teste com uma gravação curta e sem conteúdo importante:

1. Abra **Configurações** e cadastre uma chave da OpenAI ou do Gemini.
2. Volte a **Transcrever**.
3. Escolha um arquivo local ou cole a URL de uma mídia pública.
4. Selecione o modelo conforme a finalidade.
5. Marque os formatos de saída desejados.
6. Escolha a pasta de destino e pressione **Iniciar transcrição**.
7. Acompanhe as etapas até aparecer **Concluído**.

Os resultados ficam na pasta escolhida e também podem ser abertos pelo **Histórico**.

## Adicionar arquivo, vídeo ou URL

O São Francisco aceita arquivos comuns de áudio e vídeo sempre que o FFmpeg conseguir
ler a faixa de som. Entre os formatos habituais estão MP3, WAV, M4A, MP4, MOV, MKV e
WebM.

Para uma URL, o aplicativo usa o yt-dlp para obter apenas o áudio necessário. O suporte a
sites pode mudar quando a plataforma altera seu funcionamento. Conteúdo privado, pago,
protegido por DRM, dependente de login ou transmitido ao vivo pode não funcionar.

**URL pública** significa apenas que a mídia pode ser acessada sem autenticação. Isso não
transforma o conteúdo em domínio público. Transcreva somente materiais que você tenha
direito ou autorização para usar.

### Aproveitar legendas existentes

Ative **Preferir legendas existentes** para tentar evitar uma nova transcrição:

1. Em arquivos locais, o aplicativo procura `.srt` ou `.vtt` com o mesmo nome e faixas de
   legenda textuais incorporadas ao vídeo.
2. Em URLs, procura primeiro legendas publicadas pelo autor e depois legendas automáticas,
   dando preferência à faixa padrão ou ao idioma original informado pelo site.
3. Se não encontrar uma legenda compatível, informa a situação e volta à transcrição do
   áudio.

Essa rota não usa a API e preserva as marcações de tempo. Legendas baseadas em imagem,
como PGS e VobSub, exigem reconhecimento óptico e não são aproveitadas nesta versão.

### Detectar o idioma

**Detectar automaticamente — recomendado** deixa a OpenAI ou o Gemini reconhecer o idioma
falado. Essa opção funciona bem quando a gravação contém um idioma principal e evita uma
escolha desnecessária antes de começar.

Escolha um idioma somente quando você já souber qual é o conteúdo ou precisar desfazer uma
ambiguidade. A escolha funciona como pista para a API e como filtro para as legendas: uma
faixa marcada como inglês, por exemplo, não será usada em um trabalho configurado como
português. Se não existir legenda compatível, o aplicativo transcreve o áudio normalmente.

## Escolher um modelo

Os nomes da lista descrevem o uso recomendado:

- **Econômico — OpenAI:** boa opção inicial para texto contínuo.
- **Maior precisão — OpenAI:** prioriza fidelidade em nomes e vocabulário.
- **Identificar falantes — OpenAI:** separa participantes e fornece intervalos de fala.
- **Legendas e tempos — OpenAI:** usa `whisper-1` para obter tempos precisos de segmentos.
- **Gemini detalhado:** gera uma transcrição estruturada com falantes e tempos estimados.
- **Gemini econômico:** alternativa de menor custo para grande volume.

Os tempos do Gemini são produzidos pelo próprio modelo e podem exigir revisão. Para
legendas que precisam de sincronização precisa, prefira **Legendas e tempos**, uma legenda
existente ou confira o resultado no vídeo.

Modelos, capacidades e disponibilidade podem mudar. Esta lista foi revisada em
27/07/2026.

## Chaves da OpenAI e do Gemini

Uma chave de API é uma credencial secreta que permite ao São Francisco conversar
diretamente com o provedor escolhido. Você não precisa ser desenvolvedor para criar uma.

A assinatura de um chatbot e o uso da API são serviços separados. ChatGPT Plus, por
exemplo, não inclui automaticamente créditos da API OpenAI. Cada provedor administra
cobrança, cota, projeto e acesso a modelos em sua própria plataforma.

O São Francisco salva a chave no cofre seguro do sistema — macOS Keychain ou Credenciais
do Windows — e nunca a mostra por inteiro. Em outras plataformas, use uma variável de
ambiente; o aplicativo não cria um arquivo de texto como alternativa silenciosa.

### Criar uma chave da OpenAI

1. Abra a [página oficial de chaves da OpenAI](https://platform.openai.com/api-keys).
2. Entre ou crie uma conta da plataforma de API.
3. Crie uma chave para o projeto desejado.
4. Copie a chave quando ela aparecer; o valor completo pode ser mostrado apenas uma vez.
5. No São Francisco, abra **Configurações → OpenAI**, cole a chave e escolha
   **Verificar**.
6. Quando aparecer **Chave válida**, escolha **Salvar configurações**.

Uma chave pode ser válida e ainda não ter saldo, cota ou permissão para determinado
modelo. Confira o faturamento e os limites no painel da plataforma.

### Criar uma chave do Gemini

1. Abra a [página oficial de chaves do Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Entre no Google AI Studio e selecione ou importe um projeto.
3. Crie a chave conforme as opções disponíveis para o projeto.
4. No São Francisco, abra **Configurações → Gemini**, cole a chave e escolha
   **Verificar**.
5. Quando aparecer **Chave válida**, escolha **Salvar configurações**.

O Google está migrando os tipos de chave da API Gemini. Siga a orientação exibida pelo
Google AI Studio e mantenha o aplicativo atualizado.

> [!WARNING]
> Nunca envie uma chave em documento, captura de tela, mensagem ou pedido de suporte.
> Revogue imediatamente qualquer credencial exposta e crie outra.

## Como mídias longas são processadas

O aplicativo não envia o vídeo integral ao provedor:

1. Valida a mídia e verifica a faixa de áudio.
2. Extrai e normaliza o áudio com FFmpeg.
3. Procura pausas próximas dos pontos de divisão.
4. Cria partes com margem segura abaixo do limite de upload.
5. Transcreve e salva o resultado de cada parte.
6. Reúne os textos, ajusta os tempos e remove repetições nas emendas.
7. Gera os formatos escolhidos.

Quando não há silêncio adequado, as partes recebem uma pequena sobreposição. Isso reduz o
risco de cortar uma palavra, mas a montagem ainda deve ser revisada em conteúdo crítico.

O método remove o limite artificial de enviar o arquivo inteiro, mas tempo de
processamento, espaço em disco, internet, cota do provedor e regras do site continuam
existindo.

## Acompanhar, cancelar e retomar

O andamento usa etapas concretas:

- **Verificando a fonte e as legendas:** o aplicativo procura uma rota sem API.
- **Obtendo a mídia:** uma URL está sendo baixada quando isso é necessário.
- **Medindo a duração e procurando pausas:** FFprobe e FFmpeg analisam a mídia.
- **Preparando parte X de Y:** o FFmpeg extrai uma parte de áudio normalizada.
- **Transcrevendo parte X de Y:** a parte está sendo processada pelo provedor.
- **Montando e exportando:** textos, tempos e arquivos finais estão sendo reunidos.
- **Concluído:** os resultados estão prontos.

**Cancelar** encerra processos locais assim que possível e conserva as partes concluídas.
Uma requisição já aceita pelo provedor pode terminar ou gerar consumo mesmo depois do
cancelamento.

**Retomar** reutiliza partes cujo resultado foi salvo e recomeça na primeira parte
incompleta. Alterar a fonte, o modelo, o provedor ou o idioma cria uma configuração
diferente e pode impedir o reaproveitamento.

## Formatos de saída

- **TXT:** texto simples, adequado para leitura e pesquisa.
- **DOCX:** documento formatado, com título, origem e intervalos quando disponíveis.
- **SRT:** formato comum de legenda para players e editores.
- **VTT:** formato de legenda usado principalmente na web.

SRT e VTT precisam de segmentos com marcações de tempo. Quando o modelo fornece apenas
texto contínuo, o aplicativo distribui o conteúdo pelo intervalo da parte e marca essa
estimativa nos metadados. Para trabalho audiovisual preciso, escolha um modelo com tempos
ou aproveite legendas existentes.

O São Francisco não sobrescreve um resultado silenciosamente. Se o nome já existir,
acrescenta um número ao novo arquivo.

## Custos, dados e armazenamento

O aplicativo não cobra pela transcrição. A cobrança, quando houver, é feita diretamente
pelo provedor da API conforme a conta e o modelo escolhidos.

Cada tentativa enviada pode gerar consumo. Ao retomar, somente partes sem resultado
confirmado são reenviadas.

Áudio em partes é enviado ao provedor selecionado. Manifestos, resultados intermediários,
histórico e arquivos de trabalho permanecem no diretório de dados do São Francisco. Os
arquivos exportados permanecem na pasta de destino e não são apagados automaticamente.

Consulte os [termos atuais da OpenAI](https://openai.com/policies).

Consulte também os [termos atuais da API Gemini](https://ai.google.dev/gemini-api/terms).

## Problemas comuns

### A chave não foi aceita

**Sintoma:** Configurações informa que a credencial é inválida.

**Ação:** confira se a chave pertence ao provedor correto, se foi copiada por inteiro e se
continua ativa. Depois, verifique projeto, faturamento, cota e acesso ao modelo.

### O arquivo não tem áudio

**Sintoma:** a preparação termina antes da divisão.

**Ação:** abra o arquivo em um player e confirme que existe uma faixa de áudio. Arquivos
corrompidos ou vídeos compostos apenas por imagens não podem ser transcritos.

### A URL deixou de funcionar

**Sintoma:** o yt-dlp não consegue obter mídia ou legenda.

**Ação:** atualize o São Francisco e tente novamente. No YouTube, versões atuais do
yt-dlp também podem precisar do runtime Deno. Conteúdo com login, DRM ou bloqueio do site
pode continuar indisponível.

### O processamento parece parado

**Sintoma:** a mesma parte permanece ativa por vários minutos.

**Ação:** gravações longas e provedores ocupados podem demorar sem que haja falha. Se
aparecer uma mensagem de rede ou cota, cancele e retome depois; as partes concluídas serão
preservadas.

### A legenda ficou fora de sincronia

**Sintoma:** SRT ou VTT antecipa ou atrasa uma fala.

**Ação:** prefira uma legenda existente ou o modelo **Legendas e tempos**. Tempos gerados
pelo Gemini e tempos estimados a partir de texto contínuo devem ser revisados.

### Não há espaço em disco

**Sintoma:** a extração ou exportação é interrompida.

**Ação:** libere espaço na unidade indicada. O aplicativo precisa conservar o áudio
normalizado e os resultados intermediários até concluir ou cancelar o trabalho.

## Atalhos e navegação

- `⌘N` no macOS ou `Ctrl+N` nas demais plataformas abre **Transcrever**.
- `⌘K` ou `Ctrl+K` abre a **Ajuda**.
- `⌘,` no macOS ou `Ctrl+,` abre **Configurações**.
- `Tab` e `Shift+Tab` movem o foco.
- `Enter` ou `Espaço` ativa o controle em foco.
- `Page Up`, `Page Down`, `Home` e `End` percorrem artigos longos da Ajuda.

O índice e o artigo da Ajuda possuem rolagem independente.

## Licenças e sobre

O código do São Francisco é distribuído sob a licença MIT.

A interface usa Qt for Python/PySide6 sob os termos aplicáveis da LGPLv3 ou de uma licença
comercial. FFmpeg, yt-dlp, bibliotecas Python e fontes conservam suas próprias licenças e
avisos no pacote distribuído.

Versão, autoria, contato e inventário de terceiros ficam na tela **Sobre**.
