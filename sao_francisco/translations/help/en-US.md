# São Francisco Help

São Francisco turns audio and video into text. Choose a file on your computer or paste a public video address. The interface starts in English; change it in **Settings → Interface language**. This does not change the language spoken in your recordings.

## Getting started

Start with a short recording:

1. Open **Settings** and add an OpenAI or Gemini API key.
2. Return to **Transcribe**.
3. Choose a file or paste a video address.
4. Select the service and model.
5. Select the output formats.
6. Choose the destination folder.
7. Press **Start transcription**.

Once finished, your files will be in the chosen folder. You can also open them from **History**.

## Adding files, videos or URLs

Under **Files**, select one or more audio or video files from your computer. Common formats include MP3, WAV, M4A, MP4, MOV, MKV and WebM.

Under **YouTube or URL**, paste the video's public address. Content requiring login, a subscription, payment or special site permission may be unavailable.

To reuse the text published with a video, select **Use available video captions**. São Francisco removes progressive repetitions before creating the document. This option is off by default; leave it off if you prefer a fresh transcription of the audio.

An accessible online video is not necessarily free to use. Only transcribe material you have the right or permission to use.

### Detecting the language

**Detect automatically** lets the service recognize the spoken language. You can also specify it yourself. Neither option is always better: specifying a language can help with noise, accents, names and similar languages; automatic detection is useful for unknown or mixed languages. This is separate from the interface language.

## Choosing a model

The names describe the recommended use:

- **Economy — OpenAI:** a good starting point for continuous text.
- **Higher accuracy — OpenAI:** prioritizes names and vocabulary.
- **Identify speakers — OpenAI:** separates participants where possible.
- **Subtitles and timing — OpenAI:** offers more precise timestamps.
- **Detailed Gemini:** produces a structured transcription.
- **Economy Gemini:** an alternative for larger volumes.

Quality depends on the recording. Noise, loud music, overlapping speakers, distant microphones and unusual names may require review. Models and availability can change with each service.

## OpenAI and Gemini keys

An API key is a secret credential that lets São Francisco send audio to your chosen service. You do not need to be a developer to create one.

A chatbot subscription and API usage are separate services. For example, ChatGPT Plus does not automatically include OpenAI API credits. Each provider manages billing, limits and model access on its own platform.

São Francisco stores keys in the system's secure vault and never displays the full key again.

### Creating an OpenAI key

1. Open the [official OpenAI key page](https://platform.openai.com/api-keys).
2. Sign in or create an account.
3. Create a key for the project you want to use.
4. Copy the key when it appears.
5. In São Francisco, open **Settings → OpenAI** and paste it.
6. Choose **Verify**, then **Save settings**.

A valid key may still lack credit, quota or access to the selected model. Check billing and limits on the OpenAI platform.

### Creating a Gemini key

1. Open the [official Gemini key page](https://ai.google.dev/gemini-api/docs/api-key).
2. Sign in to Google AI Studio.
3. Choose a project and create a key.
4. In São Francisco, open **Settings → Gemini** and paste it.
5. Choose **Verify**, then **Save settings**.

> [!WARNING]
> Never share a key in a document, screenshot, message or support request. If a key is exposed, revoke it and create another.

## How long media is processed

São Francisco prepares long videos in smaller parts and joins them into one transcription, without sending the entire video at once.

Completed parts are saved. After an interruption, you can continue from **History** without starting the whole task again. Processing time depends on recording length, internet speed and service availability.

## Tracking, cancelling and resuming

During transcription, the screen displays progress and the part being processed.

**Cancel** changes the card to **Cancelling** and stops execution within about five seconds. Completed parts and files remain available. A request that has already reached the service may finish or incur charges even after cancellation.

**Resume** continues an interrupted task. Changing the source file, service, model or transcription language requires a new task. If the outcome of an earlier request is uncertain, the app warns before allowing another request because it may incur another charge.

## Output formats

- **TXT:** plain text for reading and searching.
- **DOCX:** a formatted document for word processors.
- **SRT:** subtitles for video players and editors.
- **VTT:** subtitles mainly used on the web.

DOCX and TXT timestamps are optional and off by default. Select **Include timestamps in DOCX and TXT** before starting to include them. SRT and VTT always need timing information. If the model does not provide exact timing, you may need to adjust subtitles in a video editor.

For online videos, São Francisco uses the video title for output filenames, adapting it when needed. If a file with that name already exists, a number is added to the new result.

### Improve with AI

Select **Improve with AI** to receive a more readable second version alongside the original transcription. The app organizes paragraphs and corrects punctuation, capitalization and obvious recognition errors.

Improvement should not summarize, translate, embellish or fill in uncertain passages. Even so, check names, numbers and unclear passages especially carefully.

DOCX and TXT receive separate **transcription** and **improved text** files. Timestamps stay only in the original. SRT and VTT are not rewritten by improvement.

The original is completed, saved and exported first; optional improvement runs afterwards and creates additional files. If improvement is interrupted, the originals remain available. Resuming reuses accepted steps and does not automatically repeat a request with an uncertain outcome.

## Costs, data and storage

The app purchase is separate from API usage. São Francisco does not charge per transcription. Any API charges come directly from OpenAI or Google according to your account and selected model; buying the app does not include API credits.

Each submitted part may consume quota. When resuming, the app reuses completed work. When enough data is available, it displays an estimated cost in US dollars. Very small amounts appear as **less than US$0.01**. If all text comes from existing captions and improvement is off, it displays **No API cost**.

This is only an estimate. Free tiers, taxes, discounts, interrupted attempts and price changes may produce a different amount on the service's dashboard. See [OpenAI usage](https://platform.openai.com/usage) or [Google Cloud billing](https://console.cloud.google.com/billing) for official charges.

When the service provides reliable counts, the app may also display tokens: small units used to measure input and output. It does not invent a token count when none is reported.

### Current API prices

See the official [OpenAI pricing](https://developers.openai.com/api/docs/pricing) and [Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing) pages. Prices, units, model availability and free tiers can change. Confirm them before starting paid work.

Audio is sent to the selected service. History and working files stay on your computer. Results remain in the destination folder until you delete them. See the [OpenAI terms](https://openai.com/policies) and [Gemini API terms](https://ai.google.dev/gemini-api/terms).

## Common problems

### The key was not accepted

**Symptom:** Settings reports an invalid key. **Action:** check the provider, that the complete key was copied and that it is still active. Then check billing, limits and model access.

### The file has no audio

**Symptom:** the task ends before transcription starts. **Action:** open the file and check for sound. Damaged files or videos made only of images cannot be transcribed.

### The video address stopped working

**Symptom:** the app cannot retrieve the video. **Action:** update São Francisco and try again. Login-protected, paid, live or site-blocked content may remain unavailable.

### Processing seems stuck

**Symptom:** the same part stays active for several minutes. **Action:** long recordings and busy services take time. If a network or quota message appears, cancel and resume later.

### Subtitles are out of sync

**Symptom:** SRT or VTT appears ahead of or behind speech. **Action:** use **Subtitles and timing** and review the result alongside the video.

### The computer is out of space

**Symptom:** preparation or file creation stops. **Action:** free disk space and try again.

## Shortcuts and navigation

- `⌘N` on macOS or `Ctrl+N` elsewhere opens **Transcribe**.
- `⌘K` or `Ctrl+K` opens **Help**.
- `⌘,` or `Ctrl+,` opens **Settings**.
- `Tab` and `Shift+Tab` move focus.
- `Enter` or `Space` activates the focused control.
- `Page Up`, `Page Down`, `Home` and `End` navigate long text.
- `Esc` closes notice dialogs.

The Help contents and article scroll independently.

## Licenses and about

São Francisco's code is distributed under the MIT license. Charging for packaged downloads does not remove the freedoms granted by MIT. Components, libraries and fonts retain their own licenses. Open **About → View third-party notices** to read the inventory in the app.
