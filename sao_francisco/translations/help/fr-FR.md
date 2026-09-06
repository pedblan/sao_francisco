# Aide de São Francisco

São Francisco transforme l’audio et la vidéo en texte. Choisissez un fichier sur votre ordinateur ou collez l’adresse publique d’une vidéo. L’interface démarre en anglais ; changez-la dans **Paramètres → Langue de l’interface**, sans modifier la langue des enregistrements.

## Premiers pas

Commencez par un enregistrement court :

1. Ouvrez **Paramètres** et ajoutez une clé API OpenAI ou Gemini.
2. Revenez à **Transcrire**.
3. Choisissez un fichier ou collez une adresse vidéo.
4. Sélectionnez le service et le modèle.
5. Cochez les formats de sortie souhaités.
6. Choisissez le dossier de destination.
7. Appuyez sur **Démarrer la transcription**.

Les fichiers terminés seront dans ce dossier. Vous pourrez aussi les ouvrir depuis **Historique**.

## Ajouter des fichiers, vidéos ou adresses

Dans **Fichiers**, sélectionnez un ou plusieurs fichiers audio ou vidéo. Les formats courants MP3, WAV, M4A, MP4, MOV, MKV et WebM sont acceptés.

Dans **YouTube ou adresse**, collez l’adresse publique de la vidéo. Un contenu nécessitant une connexion, un abonnement, un paiement ou une autorisation particulière peut être indisponible.

Pour réutiliser le texte publié avec la vidéo, cochez **Utiliser les sous-titres disponibles de la vidéo**. São Francisco supprime les répétitions progressives avant de créer le document. Cette option est désactivée par défaut ; laissez-la ainsi pour obtenir une nouvelle transcription de l’audio.

Une vidéo accessible en ligne n’est pas nécessairement libre d’utilisation. Ne transcrivez que les contenus que vous avez le droit ou l’autorisation d’utiliser.

### Détecter la langue

**Détecter automatiquement** laisse le service reconnaître la langue parlée. Vous pouvez aussi la préciser. Aucune option n’est toujours meilleure : préciser la langue peut aider avec le bruit, les accents, les noms et les langues proches ; la détection convient aux langues inconnues ou mélangées. Ce réglage est distinct de la langue de l’interface.

## Choisir un modèle

Les noms indiquent l’usage recommandé :

- **Économique — OpenAI :** un bon point de départ pour du texte continu.
- **Précision accrue — OpenAI :** privilégie les noms et le vocabulaire.
- **Identifier les locuteurs — OpenAI :** sépare les participants si possible.
- **Sous-titres et temps — OpenAI :** fournit des horodatages plus précis.
- **Gemini détaillé :** produit une transcription structurée.
- **Gemini économique :** une alternative pour les gros volumes.

La qualité dépend de l’enregistrement. Bruit, musique forte, voix superposées, microphone éloigné et noms inhabituels peuvent nécessiter une révision. Les modèles et leur disponibilité peuvent changer selon le service.

## Clés OpenAI et Gemini

Une clé API est un identifiant secret permettant à São Francisco d’envoyer l’audio au service choisi. Il n’est pas nécessaire d’être développeur pour en créer une.

L’abonnement à un chatbot et l’utilisation de l’API sont des services distincts. Par exemple, ChatGPT Plus n’inclut pas automatiquement de crédits API OpenAI. Chaque fournisseur gère sa facturation, ses limites et l’accès aux modèles.

São Francisco conserve la clé dans le coffre-fort sécurisé du système et n’en affiche plus la valeur complète.

### Créer une clé OpenAI

1. Ouvrez la [page officielle des clés OpenAI](https://platform.openai.com/api-keys).
2. Connectez-vous ou créez un compte.
3. Créez une clé pour le projet souhaité.
4. Copiez-la lorsqu’elle apparaît.
5. Collez-la dans **Paramètres → OpenAI** de São Francisco.
6. Choisissez **Vérifier**, puis **Enregistrer les paramètres**.

Une clé valide peut manquer de crédit, de quota ou d’accès au modèle choisi. Vérifiez la facturation et les limites sur la plateforme OpenAI.

### Créer une clé Gemini

1. Ouvrez la [page officielle des clés Gemini](https://ai.google.dev/gemini-api/docs/api-key).
2. Connectez-vous à Google AI Studio.
3. Choisissez un projet et créez une clé.
4. Collez-la dans **Paramètres → Gemini**.
5. Choisissez **Vérifier**, puis **Enregistrer les paramètres**.

> [!WARNING]
> Ne partagez jamais une clé dans un document, une capture, un message ou une demande d’assistance. Si elle est exposée, révoquez-la et créez-en une autre.

## Traitement des médias longs

São Francisco prépare les vidéos longues par petites parties puis les réunit en une transcription, sans envoyer toute la vidéo en une fois.

Les parties terminées sont enregistrées. Après une interruption, reprenez depuis **Historique** sans tout recommencer. Le temps nécessaire dépend de la durée, de la connexion internet et de la disponibilité du service.

## Suivre, annuler et reprendre

L’écran affiche la progression et la partie en cours.

**Annuler** fait passer la fiche à **Annulation** et arrête l’exécution en environ cinq secondes. Les parties et fichiers terminés restent disponibles. Une requête déjà reçue par le service peut se terminer ou être facturée après l’annulation.

**Reprendre** continue une tâche interrompue. Modifier le fichier source, le service, le modèle ou la langue de transcription exige une nouvelle tâche. Si le résultat d’une requête précédente est incertain, l’application avertit avant d’en autoriser une nouvelle, car elle peut entraîner une nouvelle facturation.

## Formats de sortie

- **TXT :** texte brut pour la lecture et la recherche.
- **DOCX :** document mis en forme pour les traitements de texte.
- **SRT :** sous-titres pour lecteurs et éditeurs vidéo.
- **VTT :** sous-titres utilisés principalement sur le web.

Les horodatages DOCX et TXT sont facultatifs et désactivés par défaut. Cochez **Inclure les horodatages dans les fichiers DOCX et TXT** avant de démarrer. SRT et VTT nécessitent toujours des temps. Si le modèle n’en fournit pas de précis, ajustez les sous-titres dans un éditeur vidéo.

Pour une vidéo en ligne, son titre sert de nom aux fichiers, adapté si nécessaire. Si ce nom existe déjà, un numéro est ajouté au nouveau résultat.

### Améliorer avec l’IA

Cochez **Améliorer avec l’IA** pour recevoir une seconde version plus agréable à lire en plus de l’original. L’application organise les paragraphes et corrige ponctuation, majuscules et erreurs de reconnaissance évidentes.

L’amélioration ne doit ni résumer, ni traduire, ni embellir, ni compléter les passages douteux. Vérifiez néanmoins les noms, les nombres et les passages peu clairs.

DOCX et TXT reçoivent des fichiers **transcription** et **texte amélioré** séparés. Les horodatages restent dans l’original. SRT et VTT ne sont pas réécrits.

L’original est d’abord terminé, enregistré et exporté ; l’amélioration facultative crée ensuite des fichiers supplémentaires. Si elle est interrompue, les originaux restent disponibles. La reprise réutilise les étapes acceptées et ne répète pas automatiquement une requête au résultat incertain.

## Coûts, données et stockage

L’achat de l’application est distinct de l’utilisation des API. São Francisco ne facture pas chaque transcription. Les frais API éventuels sont prélevés directement par OpenAI ou Google selon votre compte et votre modèle ; l’achat n’inclut pas de crédits API.

Chaque partie envoyée peut consommer du quota. La reprise réutilise le travail terminé. Lorsque les données suffisent, un coût estimé en dollars américains apparaît. Les petits montants sont indiqués comme **moins de 0,01 $US**. Un texte issu entièrement de sous-titres existants sans amélioration affiche **Sans coût d’API**.

Ce n’est qu’une estimation. Offres gratuites, taxes, réductions, tentatives interrompues et changements de tarif peuvent modifier le montant officiel. Consultez [l’utilisation OpenAI](https://platform.openai.com/usage) ou la [facturation Google Cloud](https://console.cloud.google.com/billing).

Si le service fournit un décompte fiable, l’application peut afficher les tokens : petites unités mesurant l’entrée et la réponse. Elle n’invente pas de décompte non fourni.

### Tarifs API actuels

Consultez les pages officielles des [tarifs OpenAI](https://developers.openai.com/api/docs/pricing) et [tarifs Gemini](https://ai.google.dev/gemini-api/docs/pricing). Tarifs, unités, modèles et offres gratuites peuvent changer. Vérifiez-les avant un travail payant.

L’audio est envoyé au service sélectionné. L’historique et les fichiers de travail restent sur votre ordinateur. Les résultats restent dans le dossier choisi jusqu’à leur suppression. Consultez les [conditions OpenAI](https://openai.com/policies) et les [conditions de l’API Gemini](https://ai.google.dev/gemini-api/terms).

## Problèmes courants

### La clé est refusée

**Symptôme :** les paramètres signalent une clé invalide. **Action :** vérifiez le fournisseur, la copie complète et l’activation de la clé, puis la facturation, les limites et l’accès au modèle.

### Le fichier n’a pas d’audio

**Symptôme :** la tâche s’arrête avant de transcrire. **Action :** ouvrez le fichier et vérifiez le son. Les fichiers endommagés ou les vidéos uniquement composées d’images ne peuvent pas être transcrits.

### L’adresse vidéo ne fonctionne plus

**Symptôme :** impossible de récupérer la vidéo. **Action :** mettez São Francisco à jour et réessayez. Un contenu protégé par connexion, payant, en direct ou bloqué par le site peut rester indisponible.

### Le traitement semble bloqué

**Symptôme :** la même partie reste active plusieurs minutes. **Action :** les enregistrements longs et services occupés prennent du temps. En cas de message de réseau ou de quota, annulez puis reprenez plus tard.

### Les sous-titres sont décalés

**Symptôme :** SRT ou VTT précède ou suit la parole. **Action :** utilisez **Sous-titres et temps** et vérifiez avec la vidéo.

### Le disque est plein

**Symptôme :** la préparation ou la création de fichiers s’interrompt. **Action :** libérez de l’espace puis réessayez.

## Raccourcis et navigation

- `⌘N` sous macOS ou `Ctrl+N` ailleurs ouvre **Transcrire**.
- `⌘K` ou `Ctrl+K` ouvre l’**Aide**.
- `⌘,` ou `Ctrl+,` ouvre **Paramètres**.
- `Tab` et `Shift+Tab` déplacent le focus.
- `Entrée` ou `Espace` active le contrôle ciblé.
- `Page Up`, `Page Down`, `Home` et `End` parcourent les textes longs.
- `Esc` ferme les fenêtres d’avis.

Le sommaire et l’article de l’aide défilent indépendamment.

## Licences et à propos

Le code de São Francisco est distribué sous licence MIT. La vente des téléchargements prêts à installer ne retire pas les libertés de cette licence. Composants, bibliothèques et polices conservent leurs licences. Ouvrez **À propos → Voir les avis de tiers** pour lire l’inventaire.
