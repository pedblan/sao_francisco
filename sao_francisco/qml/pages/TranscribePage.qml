pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Dialogs
import QtQuick.Layouts
import ".." as App
import "../components" as Components

Item {
    id: root

    property var shell: null
    property string sourceMode: "files"
    property var selectedFiles: []
    property var activeJob: ({})
    property var providerOptions: [
        { "label": "OpenAI", "id": "openai" },
        { "label": "Google Gemini", "id": "gemini" }
    ]
    property var modelOptions: []

    function backendValue(name, fallbackValue) {
        return shell ? shell.backendValue(name, fallbackValue) : fallbackValue
    }

    function callBackend(name, args, fallbackValue) {
        return shell ? shell.callBackend(name, args, fallbackValue) : fallbackValue
    }

    function modelsFor(providerId) {
        const backendModels = callBackend("modelsForProvider", [providerId], [])
        if (backendModels && backendModels.length > 0) {
            const normalizedModels = []
            for (let index = 0; index < backendModels.length; index++) {
                const option = backendModels[index]
                const name = String(option.label || option.name
                                    || option.displayName || option.id)
                const summary = String(option.summary || "")
                normalizedModels.push({
                    "label": summary.length > 0
                             ? name + " — " + summary
                             : name,
                    "id": String(option.id)
                })
            }
            return normalizedModels
        }
        if (providerId === "gemini") {
            return [
                {
                    "label": "Gemini detalhado — saída estruturada",
                    "id": "gemini-3.6-flash"
                },
                {
                    "label": "Gemini econômico — grande volume",
                    "id": "gemini-3.5-flash-lite"
                }
            ]
        }
        return [
            {
                "label": "Econômico — recomendado para começar",
                "id": "gpt-4o-mini-transcribe"
            },
            {
                "label": "Maior precisão — nomes e vocabulário",
                "id": "gpt-4o-transcribe"
            },
            {
                "label": "Identificar falantes — separação por participante",
                "id": "gpt-4o-transcribe-diarize"
            },
            {
                "label": "Legendas e tempos — segmentos precisos",
                "id": "whisper-1"
            }
        ]
    }

    function acceptFiles(urls) {
        const values = selectedFiles.slice()
        for (let index = 0; index < urls.length; index++) {
            const value = String(urls[index])
            if (values.indexOf(value) < 0)
                values.push(value)
        }
        selectedFiles = values
        sourceMode = "files"
        callBackend("setPendingSources", [values])
    }

    function handleScrollKey(event, view) {
        const origin = Number(view.originY || 0)
        const maximum = origin + Math.max(
                            0,
                            Number(view.contentHeight) - Number(view.height))
        if (event.key === Qt.Key_PageDown)
            view.contentY = Math.min(maximum, view.contentY + view.height * 0.85)
        else if (event.key === Qt.Key_PageUp)
            view.contentY = Math.max(origin, view.contentY - view.height * 0.85)
        else if (event.key === Qt.Key_Home)
            view.contentY = origin
        else if (event.key === Qt.Key_End)
            view.contentY = maximum
        else
            return
        event.accepted = true
    }

    function removeFile(index) {
        const values = selectedFiles.slice()
        values.splice(index, 1)
        selectedFiles = values
        callBackend("setPendingSources", [values])
    }

    function resetDraft() {
        selectedFiles = []
        sourceUrl.clear()
        sourceMode = "files"
        providerCombo.currentIndex = 0
        languageCombo.currentIndex = 0
        preferCaptions.checked = true
        docxFormat.checked = true
        txtFormat.checked = true
        srtFormat.checked = true
        vttFormat.checked = false
        callBackend("setPendingSources", [[]])
        pageScroll.contentY = Number(pageScroll.originY || 0)
        if (shell)
            shell.showToast("Nova transcrição pronta para configurar.")
    }

    function openFilePicker() {
        sourceMode = "files"
        fileDialog.open()
    }

    function focusUrlField() {
        sourceMode = "url"
        Qt.callLater(function() {
            sourceUrl.forceActiveFocus()
        })
    }

    function selectedFormats() {
        const formats = []
        if (docxFormat.checked)
            formats.push("docx")
        if (txtFormat.checked)
            formats.push("txt")
        if (srtFormat.checked)
            formats.push("srt")
        if (vttFormat.checked)
            formats.push("vtt")
        return formats
    }

    function canStart() {
        const hasSource = sourceMode === "files"
                          ? selectedFiles.length > 0
                          : sourceUrl.text.trim().length > 0
        return hasSource && selectedFormats().length > 0
               && !(shell && shell.backendBusy)
    }

    function startTranscription() {
        if (!canStart()) {
            if (shell)
                shell.showToast("Adicione uma fonte e escolha ao menos um formato.")
            return
        }
        const payload = {
            "sourceType": sourceMode,
            "sources": sourceMode === "files"
                       ? selectedFiles
                       : [sourceUrl.text.trim()],
            "provider": String(providerCombo.currentValue),
            "model": String(modelCombo.currentValue),
            "language": String(languageCombo.currentValue),
            "formats": selectedFormats(),
            "outputFolder": outputFolder.text.trim(),
            "preferExistingCaptions": preferCaptions.checked
        }
        callBackend("startTranscription", [payload])
    }

    function provenanceLabel(value) {
        const labels = {
            "existing_captions": "Legenda existente",
            "author_captions": "Legendas do autor",
            "automatic_captions": "Legendas automáticas",
            "audio_transcription": "Áudio transcrito"
        }
        return labels[value] || ""
    }

    function jobStatusLabel(value) {
        const labels = {
            "preparing": "Preparando",
            "running": "Em andamento",
            "paused": "Pausada",
            "completed": "Concluída",
            "failed": "Falhou",
            "cancelled": "Cancelada"
        }
        return labels[value] || "Em espera"
    }

    function jobTone(value) {
        if (value === "completed")
            return "success"
        if (value === "failed" || value === "cancelled")
            return "danger"
        if (value === "paused")
            return "warning"
        return "accent"
    }

    function syncJob() {
        activeJob = backendValue("activeJob", {})
        const pendingSources = backendValue("pendingSources", [])
        if (selectedFiles.length === 0 && pendingSources
                && pendingSources.length > 0)
            selectedFiles = pendingSources
        const destination = String(backendValue("outputFolder", ""))
        if (destination.length > 0 && outputFolder.text.length === 0)
            outputFolder.text = destination
        if (activeJob.focusDetails === true) {
            Qt.callLater(function() {
                pageScroll.contentY = Math.max(
                            Number(pageScroll.originY || 0),
                            Number(pageScroll.contentHeight)
                            - Number(pageScroll.height))
            })
        }
    }

    onShellChanged: {
        modelOptions = modelsFor(String(providerCombo.currentValue || "openai"))
        syncJob()
    }

    FileDialog {
        id: fileDialog
        title: "Escolher áudio ou vídeo"
        fileMode: FileDialog.OpenFiles
        nameFilters: [
            "Áudio e vídeo (*.mp3 *.m4a *.wav *.aac *.flac *.ogg *.mp4 *.mov *.mkv *.webm *.avi)",
            "Todos os arquivos (*)"
        ]
        onAccepted: root.acceptFiles(selectedFiles)
    }

    Rectangle {
        anchors.fill: parent
        color: App.Theme.surfaceRaised
    }

    Flickable {
        id: pageScroll

        objectName: "transcribePageScroll"
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: pageBody.implicitHeight + 64
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        activeFocusOnTab: true
        Accessible.name: "Conteúdo da tela Transcrever"
        Keys.onPressed: event => root.handleScrollKey(event, pageScroll)

        Rectangle {
            parent: pageScroll
            anchors.fill: parent
            color: "transparent"
            border.width: pageScroll.activeFocus ? 2 : 0
            border.color: App.Theme.focus
            z: 1000
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            interactive: true
        }

        ColumnLayout {
            id: pageBody

            width: Math.min(960, pageScroll.width - 64)
            x: Math.max(32, (pageScroll.width - width) / 2)
            y: 32
            spacing: 22

            Components.PageHeader {
                Layout.fillWidth: true
                title: "Transforme áudio e vídeo em texto"
                description: "Use arquivos do computador ou um endereço do YouTube e serviços semelhantes. Vídeos longos são processados em partes e retomados com segurança."
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                spacing: 18

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Button {
                        id: filesTab
                        text: "Arquivos"
                        checked: root.sourceMode === "files"
                        checkable: true
                        autoExclusive: true
                        Accessible.name: "Usar arquivos"
                        onClicked: root.sourceMode = "files"

                        contentItem: RowLayout {
                            spacing: 8
                            Components.Icon {
                                name: "file"
                                iconSize: 17
                                iconColor: filesTab.checked
                                           ? App.Theme.primary
                                           : App.Theme.textMuted
                            }
                            Text {
                                text: filesTab.text
                                color: filesTab.checked
                                       ? App.Theme.text
                                       : App.Theme.textMuted
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: Font.DemiBold
                            }
                        }
                        background: Rectangle {
                            radius: App.Theme.radius
                            color: filesTab.checked
                                   ? App.Theme.primarySoft
                                   : filesTab.hovered
                                     ? App.Theme.surfaceMuted
                                     : "transparent"
                            border.width: filesTab.activeFocus ? 2 : 0
                            border.color: App.Theme.focus
                        }
                    }

                    Button {
                        id: urlTab
                        text: "YouTube ou endereço"
                        checked: root.sourceMode === "url"
                        checkable: true
                        autoExclusive: true
                        Accessible.name: "Usar endereço da internet"
                        onClicked: root.focusUrlField()

                        contentItem: RowLayout {
                            spacing: 8
                            Components.Icon {
                                name: "link"
                                iconSize: 17
                                iconColor: urlTab.checked
                                           ? App.Theme.primary
                                           : App.Theme.textMuted
                            }
                            Text {
                                text: urlTab.text
                                color: urlTab.checked
                                       ? App.Theme.text
                                       : App.Theme.textMuted
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: Font.DemiBold
                            }
                        }
                        background: Rectangle {
                            radius: App.Theme.radius
                            color: urlTab.checked
                                   ? App.Theme.primarySoft
                                   : urlTab.hovered
                                     ? App.Theme.surfaceMuted
                                     : "transparent"
                            border.width: urlTab.activeFocus ? 2 : 0
                            border.color: App.Theme.focus
                        }
                    }

                    Item { Layout.fillWidth: true }
                }

                Rectangle {
                    visible: root.sourceMode === "files"
                    Layout.fillWidth: true
                    implicitHeight: Math.max(154, dropColumn.implicitHeight + 40)
                    radius: App.Theme.radiusLarge
                    color: dropArea.containsDrag
                           ? App.Theme.primarySoft
                           : App.Theme.background
                    border.width: 2
                    border.color: dropArea.containsDrag
                                  ? App.Theme.primary
                                  : App.Theme.borderStrong

                    ColumnLayout {
                        id: dropColumn
                        anchors.centerIn: parent
                        width: Math.min(parent.width - 48, 560)
                        spacing: 8

                        Components.Icon {
                            Layout.alignment: Qt.AlignHCenter
                            name: "folder"
                            iconSize: 28
                            iconColor: App.Theme.primary
                        }
                        Text {
                            Layout.fillWidth: true
                            text: root.selectedFiles.length > 0
                                  ? root.selectedFiles.length
                                    + (root.selectedFiles.length === 1
                                       ? " arquivo selecionado"
                                       : " arquivos selecionados")
                                  : "Arraste arquivos de áudio ou vídeo"
                            color: App.Theme.text
                            font.family: App.Theme.displayFont
                            font.pixelSize: 17
                            font.weight: Font.Medium
                            horizontalAlignment: Text.AlignHCenter
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "ou escolha no computador"
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            horizontalAlignment: Text.AlignHCenter
                        }
                        Components.AppButton {
                            Layout.alignment: Qt.AlignHCenter
                            text: root.selectedFiles.length > 0
                                  ? "Adicionar mais"
                                  : "Escolher arquivos"
                            variant: "secondary"
                            onClicked: root.openFilePicker()
                        }
                    }

                    DropArea {
                        id: dropArea
                        anchors.fill: parent
                        onDropped: drop => {
                            if (drop.hasUrls)
                                root.acceptFiles(drop.urls)
                        }
                    }
                }

                ColumnLayout {
                    visible: root.sourceMode === "files"
                             && root.selectedFiles.length > 0
                    Layout.fillWidth: true
                    spacing: 5

                    Repeater {
                        model: root.selectedFiles

                        delegate: Rectangle {
                            id: fileRow

                            required property string modelData
                            required property int index

                            Layout.fillWidth: true
                            implicitHeight: 38
                            radius: App.Theme.radius
                            color: App.Theme.surfaceMuted

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: 11
                                anchors.rightMargin: 5
                                spacing: 9

                                Components.Icon {
                                    name: "file"
                                    iconSize: 16
                                    iconColor: App.Theme.textMuted
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: decodeURIComponent(
                                              fileRow.modelData.split("/").pop())
                                    color: App.Theme.text
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: App.Theme.bodySize
                                    elide: Text.ElideMiddle
                                    ToolTip.visible: fileHover.hovered
                                    ToolTip.text: fileRow.modelData

                                    HoverHandler { id: fileHover }
                                }
                                Button {
                                    id: removeButton

                                    text: "Remover"
                                    flat: true
                                    implicitHeight: 30
                                    Accessible.name: "Remover " + fileRow.modelData
                                    onClicked: root.removeFile(fileRow.index)
                                    contentItem: Text {
                                        text: removeButton.text
                                        color: App.Theme.secondary
                                        font.family: App.Theme.uiFont
                                        font.pixelSize: 12
                                        font.weight: Font.DemiBold
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                }
                            }
                        }
                    }
                }

                ColumnLayout {
                    visible: root.sourceMode === "url"
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: "Endereço do vídeo"
                        color: App.Theme.text
                        font.family: App.Theme.uiFont
                        font.pixelSize: App.Theme.bodySize
                        font.weight: Font.DemiBold
                    }
                    TextField {
                        id: sourceUrl
                        Layout.fillWidth: true
                        implicitHeight: 42
                        placeholderText: "https://www.youtube.com/watch?v=…"
                        selectByMouse: true
                        inputMethodHints: Qt.ImhUrlCharactersOnly
                        font.family: App.Theme.uiFont
                        font.pixelSize: App.Theme.bodySize
                        leftPadding: 13
                        rightPadding: 13
                        Accessible.name: "Endereço do vídeo"
                        background: Rectangle {
                            radius: App.Theme.radius
                            color: App.Theme.surface
                            border.width: sourceUrl.activeFocus ? 2 : 1
                            border.color: sourceUrl.activeFocus
                                          ? App.Theme.focus
                                          : App.Theme.borderStrong
                        }
                    }
                    Text {
                        Layout.fillWidth: true
                        text: "São aceitos endereços públicos compatíveis com o baixador configurado pelo aplicativo."
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: captionsLayout.implicitHeight + 24
                    radius: App.Theme.radius
                    color: App.Theme.primarySoft

                    RowLayout {
                        id: captionsLayout
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 12

                        Switch {
                            id: preferCaptions
                            checked: true
                            Accessible.name: "Preferir legendas existentes"
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 2
                            Text {
                                Layout.fillWidth: true
                                text: "Preferir legendas existentes"
                                color: App.Theme.text
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: Font.DemiBold
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                Layout.fillWidth: true
                                text: root.sourceMode === "url"
                                      ? "Legendas manuais ou automáticas serão usadas sem API. Se não existirem, o áudio será transcrito normalmente."
                                      : "O aplicativo procura arquivos SRT/VTT ao lado da mídia e faixas textuais incorporadas. Se não encontrar, transcreve o áudio."
                                color: App.Theme.textMuted
                                font.family: App.Theme.uiFont
                                font.pixelSize: 12
                                lineHeight: 1.25
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                }
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                spacing: 16

                Text {
                    Layout.fillWidth: true
                    text: "Modelo e resultado"
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 19
                    font.weight: Font.Medium
                }

                GridLayout {
                    Layout.fillWidth: true
                    columns: width < 700 ? 1 : 2
                    columnSpacing: 18
                    rowSpacing: 14

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Text {
                            text: "Provedor"
                            color: App.Theme.text
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            font.weight: Font.DemiBold
                        }
                        ComboBox {
                            id: providerCombo
                            Layout.fillWidth: true
                            model: root.providerOptions
                            textRole: "label"
                            valueRole: "id"
                            Accessible.name: "Provedor de transcrição"
                            onCurrentValueChanged: {
                                root.modelOptions = root.modelsFor(
                                            String(currentValue))
                                modelCombo.currentIndex = 0
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Text {
                            text: "Modelo"
                            color: App.Theme.text
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            font.weight: Font.DemiBold
                        }
                        ComboBox {
                            id: modelCombo
                            Layout.fillWidth: true
                            model: root.modelOptions
                            textRole: "label"
                            valueRole: "id"
                            Accessible.name: "Modelo de transcrição"
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Text {
                            text: "Idioma"
                            color: App.Theme.text
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            font.weight: Font.DemiBold
                        }
                        ComboBox {
                            id: languageCombo
                            Layout.fillWidth: true
                            textRole: "label"
                            valueRole: "id"
                            model: [
                                {
                                    "label": "Detectar automaticamente — recomendado",
                                    "id": "auto"
                                },
                                { "label": "Português", "id": "pt" },
                                { "label": "Inglês", "id": "en" },
                                { "label": "Espanhol", "id": "es" },
                                { "label": "Francês", "id": "fr" }
                            ]
                            Accessible.name: "Idioma do conteúdo"
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 6
                        Text {
                            text: "Pasta de destino"
                            color: App.Theme.text
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            font.weight: Font.DemiBold
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            TextField {
                                id: outputFolder
                                Layout.fillWidth: true
                                placeholderText: root.sourceMode === "url"
                                                 ? "Usar a pasta Documentos"
                                                 : "Usar a pasta do arquivo"
                                selectByMouse: true
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                Accessible.name: "Pasta de destino"
                            }
                            Components.AppButton {
                                text: "Escolher…"
                                variant: "secondary"
                                compact: true
                                onClicked: {
                                    const selected = root.callBackend(
                                                "chooseOutputFolder", [], "")
                                    if (selected)
                                        outputFolder.text = String(selected)
                                }
                            }
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Text {
                        text: "Formatos de saída"
                        color: App.Theme.text
                        font.family: App.Theme.uiFont
                        font.pixelSize: App.Theme.bodySize
                        font.weight: Font.DemiBold
                    }
                    Flow {
                        Layout.fillWidth: true
                        spacing: 18

                        CheckBox {
                            id: docxFormat
                            text: "DOCX"
                            checked: true
                            Accessible.name: "Gerar arquivo DOCX"
                        }
                        CheckBox {
                            id: txtFormat
                            text: "TXT"
                            checked: true
                            Accessible.name: "Gerar arquivo TXT"
                        }
                        CheckBox {
                            id: srtFormat
                            text: "SRT"
                            checked: true
                            Accessible.name: "Gerar legenda SRT"
                        }
                        CheckBox {
                            id: vttFormat
                            text: "VTT"
                            checked: false
                            Accessible.name: "Gerar legenda VTT"
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: summaryRow.implicitHeight + 22
                    radius: App.Theme.radius
                    color: App.Theme.background
                    border.width: 1
                    border.color: App.Theme.border

                    RowLayout {
                        id: summaryRow
                        anchors.fill: parent
                        anchors.margins: 11
                        spacing: 10

                        Components.Icon {
                            name: "check"
                            iconSize: 18
                            iconColor: App.Theme.primary
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "O áudio é extraído, dividido em partes seguras e reunido em uma transcrição contínua."
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: "O uso de modelos em nuvem pode gerar cobrança no provedor."
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }
                    Components.AppButton {
                        text: "Iniciar transcrição"
                        enabled: root.canStart()
                        onClicked: root.startTranscription()
                    }
                }
            }

            Components.AppCard {
                visible: root.activeJob && Object.keys(root.activeJob).length > 0
                Layout.fillWidth: true
                padding: 22
                spacing: 14
                cardColor: App.Theme.primarySoft
                strokeColor: App.Theme.focus

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 3
                        Text {
                            Layout.fillWidth: true
                            text: String(root.activeJob.title
                                         || root.activeJob.sourceName
                                         || "Transcrição")
                            color: App.Theme.text
                            font.family: App.Theme.displayFont
                            font.pixelSize: 19
                            font.weight: Font.Medium
                            elide: Text.ElideMiddle
                        }
                        Text {
                            Layout.fillWidth: true
                            text: String(root.activeJob.detail
                                         || "Preparando a próxima etapa…")
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }
                    }

                    Components.StatusPill {
                        text: root.jobStatusLabel(
                                  String(root.activeJob.state || ""))
                        tone: root.jobTone(
                                  String(root.activeJob.state || ""))
                    }
                }

                ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 1
                    value: Number(root.activeJob.progress || 0)
                    indeterminate: (root.activeJob.state === "queued"
                                    || root.activeJob.state === "preparing"
                                    || root.activeJob.state === "running")
                                   && (root.activeJob.progress === undefined
                                       || Number(root.activeJob.totalParts || 0) <= 0)
                    Accessible.name: "Progresso da transcrição"
                    Accessible.description: indeterminate
                                            ? "Progresso ainda não calculado"
                                            : Math.round(value * 100) + "%"
                }

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10

                    Components.StatusPill {
                        visible: root.provenanceLabel(
                                     String(root.activeJob.provenance || "")
                                     ).length > 0
                        text: root.provenanceLabel(
                                  String(root.activeJob.provenance || ""))
                        tone: "success"
                    }
                    Text {
                        Layout.fillWidth: true
                        visible: Number(root.activeJob.totalParts || 0) > 0
                        text: {
                            const total = Number(root.activeJob.totalParts || 0)
                            return String(root.activeJob.completedParts)
                                    + " de "
                                    + String(total)
                                    + (total === 1
                                       ? " parte concluída"
                                       : " partes concluídas")
                        }
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 12
                    }
                    Components.AppButton {
                        visible: root.activeJob.state === "running"
                                 || root.activeJob.state === "preparing"
                        text: "Cancelar"
                        variant: "ghost"
                        compact: true
                        onClicked: root.callBackend(
                                       "cancelTranscription", [])
                    }
                    Components.AppButton {
                        visible: root.activeJob.state === "completed"
                        text: "Abrir resultado"
                        compact: true
                        onClicked: root.callBackend(
                                       "openActiveOutput", [])
                    }
                }
            }

            Item {
                objectName: "transcribePageEndMarker"
                Layout.fillWidth: true
                Layout.preferredHeight: 1
            }
        }
    }

    Connections {
        target: root.shell ? root.shell.backend : null
        ignoreUnknownSignals: true

        function onActiveJobChanged() {
            root.syncJob()
        }
        function onPendingSourcesChanged() {
            const values = root.backendValue("pendingSources", [])
            if (values)
                root.selectedFiles = values
        }
        function onOutputFolderChanged() {
            outputFolder.text = String(root.backendValue("outputFolder", ""))
        }
    }
}
