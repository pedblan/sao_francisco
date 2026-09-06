# Privacy information — draft, not published

Technical draft based on the source code reviewed on 29 August 2026. The publisher must
complete the contact, effective date, public URL and jurisdiction-specific disclosures
before using this as a store privacy policy. This is not a legal-compliance certification.

## São Francisco

São Francisco is a desktop application that processes audio, video and captions into
transcripts and subtitles. Its source code is available under the MIT license at
https://github.com/pedblan/sao_francisco.

## Files, transcripts and settings

The app stores job history, progress, file references and results on your computer so
that supported interrupted work can be resumed. It creates temporary working media
and saves exported documents to the selected output location. These records can contain
source filenames, URLs and transcript content. Protect your computer and backups; do
not assume local files are encrypted by the app. Deleting an exported document does
not necessarily delete every job record, temporary file or backup.

## External services

When you choose API transcription, the app sends media to your chosen OpenAI or Google
Gemini service using your API key. Optional text improvement sends transcript text to
the selected service. Provider processing, retention and account settings are governed
by that provider's terms and privacy information. The app does not guarantee immediate
or complete deletion of all provider-side records.

The Gemini integration attempts to delete its uploaded media file when processing ends;
network errors or interruption may prevent that attempt from succeeding. This is not
a promise of zero retention. The OpenAI transcription integration sends media with the
transcription request. Inspect provider account controls and applicable agreements
before processing confidential or sensitive recordings.

When you use a video URL, the app accesses the source service to retrieve media or
available captions. That service receives the network request and may apply its own
access rules and privacy practices. Public availability does not grant permission to
download or process a recording. Only use content you are entitled to process.

## API keys

Saved keys use macOS Keychain or Windows Credential Manager. Session environment
variables may also provide keys. Keys authenticate requests to the chosen provider and
must be kept secret. Store downloads do not include shared provider keys or API credit.

## App sales and support

The store and payment provider process purchase, billing and payout information under
their own policies. The desktop transcription pipeline does not need the buyer's bank
account or payment-card details. A support request may disclose files or account
information you voluntarily send; do not send API keys or private media unnecessarily.

No advertising or usage-analytics integration was added by this localization release.
Before publication, the publisher should verify the final executable and any additional
store integrations against this statement.

## Contact and publication checklist

- Publisher legal identity: **TO BE CONFIRMED BY THE AUTHOR**.
- Public support/privacy contact: **TO BE PROVIDED**.
- Effective date and permanent public URL: **TO BE PROVIDED**.
- Verify final data paths, deletion guidance, retention practices, support handling and
  required privacy-rights wording for intended territories.
- Reconcile store privacy forms with actual network behavior and installed dependencies.
- Translate the final approved policy where a store requires it; do not publish draft
  placeholders or claim this draft is an approved legal policy.
