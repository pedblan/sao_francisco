# Ayuda de São Francisco

São Francisco convierte audio y vídeo en texto. Elige un archivo del ordenador o pega una dirección pública de vídeo. La interfaz empieza en inglés; cámbiala en **Configuración → Idioma de la interfaz** sin cambiar el idioma de tus grabaciones.

## Primeros pasos

Empieza con una grabación corta:

1. Abre **Configuración** y añade una clave API de OpenAI o Gemini.
2. Vuelve a **Transcribir**.
3. Elige un archivo o pega una dirección de vídeo.
4. Selecciona el servicio y el modelo.
5. Marca los formatos de salida.
6. Elige la carpeta de destino.
7. Pulsa **Iniciar transcripción**.

Los archivos terminados estarán en la carpeta elegida. También puedes abrirlos desde **Historial**.

## Añadir archivos, vídeos o direcciones

En **Archivos**, selecciona uno o varios archivos de audio o vídeo. Se admiten formatos comunes como MP3, WAV, M4A, MP4, MOV, MKV y WebM.

En **YouTube o dirección**, pega la dirección pública del vídeo. Puede que no esté disponible si exige inicio de sesión, suscripción, pago o autorización especial.

Para reutilizar el texto publicado con el vídeo, marca **Usar los subtítulos disponibles del vídeo**. São Francisco elimina las repeticiones progresivas antes de crear el documento. Esta opción está desactivada de forma predeterminada; déjala así si prefieres una nueva transcripción del audio.

Que un vídeo sea accesible en internet no significa que su uso sea libre. Transcribe solo material que tengas derecho o autorización para usar.

### Detectar el idioma

**Detectar automáticamente** permite al servicio reconocer el idioma hablado. También puedes indicarlo. Ninguna opción es siempre mejor: indicar el idioma puede ayudar con ruido, acentos, nombres y lenguas parecidas; la detección es útil para idiomas desconocidos o mezclados. No es el idioma de la interfaz.

## Elegir un modelo

Los nombres indican el uso recomendado:

- **Económico — OpenAI:** buen punto de partida para texto continuo.
- **Mayor precisión — OpenAI:** prioriza nombres y vocabulario.
- **Identificar hablantes — OpenAI:** separa participantes cuando es posible.
- **Subtítulos y tiempos — OpenAI:** ofrece marcas de tiempo más precisas.
- **Gemini detallado:** produce una transcripción estructurada.
- **Gemini económico:** alternativa para grandes volúmenes.

La calidad depende de la grabación. El ruido, la música alta, las voces superpuestas, un micrófono distante y nombres poco habituales pueden requerir revisión. Los modelos y su disponibilidad pueden cambiar.

## Claves de OpenAI y Gemini

Una clave API es una credencial secreta que permite a São Francisco enviar audio al servicio elegido. No necesitas ser desarrollador para crearla.

La suscripción a un chatbot y el uso de su API son servicios separados. Por ejemplo, ChatGPT Plus no incluye automáticamente créditos API de OpenAI. Cada proveedor gestiona la facturación, los límites y el acceso a modelos en su plataforma.

São Francisco guarda la clave en el almacén seguro del sistema y no vuelve a mostrarla completa.

### Crear una clave de OpenAI

1. Abre la [página oficial de claves de OpenAI](https://platform.openai.com/api-keys).
2. Inicia sesión o crea una cuenta.
3. Crea una clave para el proyecto deseado.
4. Cópiala cuando aparezca.
5. Pégala en **Configuración → OpenAI** de São Francisco.
6. Elige **Verificar** y después **Guardar configuración**.

Una clave válida puede carecer de saldo, cuota o acceso al modelo. Revisa la facturación y los límites en la plataforma OpenAI.

### Crear una clave de Gemini

1. Abre la [página oficial de claves de Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Inicia sesión en Google AI Studio.
3. Elige un proyecto y crea una clave.
4. Pégala en **Configuración → Gemini**.
5. Elige **Verificar** y después **Guardar configuración**.

> [!WARNING]
> Nunca compartas una clave en documentos, capturas, mensajes ni solicitudes de ayuda. Si se expone, revócala y crea otra.

## Cómo se procesa el contenido largo

São Francisco prepara los vídeos largos en partes pequeñas y las reúne en una sola transcripción, sin enviar todo el vídeo de una vez.

Las partes completadas se guardan. Tras una interrupción, puedes continuar desde **Historial** sin repetir todo el trabajo. El tiempo depende de la duración de la grabación, la velocidad de internet y la disponibilidad del servicio.

## Seguir, cancelar y reanudar

La pantalla muestra el progreso y la parte que se está procesando.

**Cancelar** cambia la tarjeta a **Cancelando** y detiene la ejecución en unos cinco segundos. Las partes y los archivos completados siguen disponibles. Una solicitud que ya haya llegado al servicio puede terminar o generar cobros después de cancelar.

**Reanudar** continúa una tarea interrumpida. Cambiar el archivo, servicio, modelo o idioma de transcripción exige una tarea nueva. Si el resultado de una solicitud anterior es incierto, la aplicación avisa antes de permitir otra, porque puede generar un nuevo cobro.

## Formatos de salida

- **TXT:** texto sencillo para leer y buscar.
- **DOCX:** documento con formato para procesadores de texto.
- **SRT:** subtítulos para reproductores y editores de vídeo.
- **VTT:** subtítulos usados principalmente en la web.

Las marcas de tiempo de DOCX y TXT son opcionales y están desactivadas por defecto. Marca **Incluir marcas de tiempo en DOCX y TXT** antes de iniciar. SRT y VTT siempre necesitan tiempos. Si el modelo no los ofrece con precisión, puede ser necesario ajustarlos en un editor de vídeo.

En los vídeos de internet, el título sirve de nombre de archivo, adaptado cuando sea necesario. Si ya existe un archivo con ese nombre, se añade un número al nuevo resultado.

### Mejorar con IA

Marca **Mejorar con IA** para recibir una segunda versión más cómoda de leer junto a la transcripción original. Organiza párrafos y corrige puntuación, mayúsculas y errores evidentes de reconocimiento.

La mejora no debe resumir, traducir, embellecer ni completar pasajes dudosos. Aun así, revisa especialmente nombres, números y pasajes poco claros.

DOCX y TXT reciben archivos separados de **transcripción** y **texto mejorado**. Las marcas de tiempo permanecen solo en el original. La mejora no reescribe SRT ni VTT.

Primero se termina, guarda y exporta el original; después, la mejora opcional crea archivos adicionales. Si se interrumpe, los originales siguen disponibles. La reanudación reutiliza etapas aceptadas y no repite automáticamente una solicitud de resultado incierto.

## Costes, datos y almacenamiento

La compra de la aplicación es independiente del uso de las API. São Francisco no cobra por transcripción. OpenAI o Google cobran directamente el uso de API según tu cuenta y modelo; comprar la aplicación no incluye créditos API.

Cada parte enviada puede consumir cuota. Al reanudar se reutiliza lo terminado. Con datos suficientes se muestra una estimación en dólares estadounidenses. Los importes pequeños aparecen como **menos de US$0,01**. Si todo el texto procede de subtítulos existentes y no hay mejora, aparece **Sin coste de API**.

Es solo una estimación. Planes gratuitos, impuestos, descuentos, intentos interrumpidos y cambios de precio pueden variar el importe oficial. Consulta el [uso de OpenAI](https://platform.openai.com/usage) o la [facturación de Google Cloud](https://console.cloud.google.com/billing).

Si el servicio proporciona un recuento fiable, se pueden mostrar tokens: pequeñas unidades que miden la entrada y la respuesta. La aplicación no inventa recuentos no proporcionados.

### Precios actuales de API

Consulta las páginas oficiales de [precios de OpenAI](https://developers.openai.com/api/docs/pricing) y [precios de Gemini](https://ai.google.dev/gemini-api/docs/pricing). Precios, unidades, modelos y planes gratuitos pueden cambiar. Confírmalos antes de iniciar un trabajo de pago.

El audio se envía al servicio seleccionado. El historial y los archivos de trabajo quedan en el ordenador. Los resultados permanecen en la carpeta elegida hasta que los borres. Consulta los [términos de OpenAI](https://openai.com/policies) y los [términos de la API Gemini](https://ai.google.dev/gemini-api/terms).

## Problemas comunes

### La clave no se acepta

**Síntoma:** Configuración indica una clave no válida. **Acción:** comprueba el proveedor, que la copiaste completa y que sigue activa. Revisa facturación, límites y acceso al modelo.

### El archivo no tiene audio

**Síntoma:** la tarea termina antes de transcribir. **Acción:** abre el archivo y comprueba que hay sonido. No se pueden transcribir archivos dañados ni vídeos hechos solo de imágenes.

### La dirección del vídeo ya no funciona

**Síntoma:** no se puede obtener el vídeo. **Acción:** actualiza São Francisco y prueba otra vez. El contenido con inicio de sesión, pago, emisión en directo o bloqueo puede seguir sin estar disponible.

### El procesamiento parece detenido

**Síntoma:** la misma parte sigue activa varios minutos. **Acción:** las grabaciones largas y los servicios ocupados tardan. Ante un mensaje de red o cuota, cancela y reanuda más tarde.

### Los subtítulos no están sincronizados

**Síntoma:** SRT o VTT se adelanta o retrasa respecto a la voz. **Acción:** usa **Subtítulos y tiempos** y revisa el resultado junto al vídeo.

### No queda espacio

**Síntoma:** se interrumpe la preparación o creación de archivos. **Acción:** libera espacio y prueba otra vez.

## Atajos y navegación

- `⌘N` en macOS o `Ctrl+N` en otros sistemas abre **Transcribir**.
- `⌘K` o `Ctrl+K` abre **Ayuda**.
- `⌘,` o `Ctrl+,` abre **Configuración**.
- `Tab` y `Shift+Tab` mueven el foco.
- `Intro` o `Espacio` activa el control enfocado.
- `Page Up`, `Page Down`, `Home` y `End` recorren textos largos.
- `Esc` cierra los cuadros de avisos.

El índice y el artículo de ayuda se desplazan de forma independiente.

## Licencias y acerca de

El código de São Francisco se distribuye bajo la licencia MIT. Cobrar por las descargas empaquetadas no elimina sus libertades. Componentes, bibliotecas y fuentes mantienen sus propias licencias. Abre **Acerca de → Ver avisos de terceros** para leer el inventario.
