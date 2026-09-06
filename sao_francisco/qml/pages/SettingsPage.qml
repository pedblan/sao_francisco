import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as App
import "../components" as Components

Item {
    id: root

    property var shell: null
    property bool dirty: false
    property string openAiStatus: ""
    property string geminiStatus: ""

    function backendValue(name, fallbackValue) {
        return shell ? shell.backendValue(name, fallbackValue) : fallbackValue
    }

    function callBackend(name, args, fallbackValue) {
        return shell ? shell.callBackend(name, args, fallbackValue) : fallbackValue
    }

    function loadSettings() {
        const settings = backendValue("settings", {})
        if (settings.openAiKeyMasked)
            openAiKey.placeholderText = String(settings.openAiKeyMasked)
        if (settings.geminiKeyMasked)
            geminiKey.placeholderText = String(settings.geminiKeyMasked)
        outputFolder.text = String(settings.outputFolder || "")
        notifications.checked = settings.notifyOnCompletion !== false
        autoResume.checked = settings.resumeInterruptedJobs !== false
        dirty = false
    }

    function saveSettings() {
        const values = {
            "openAiApiKey": openAiKey.text.trim(),
            "geminiApiKey": geminiKey.text.trim(),
            "outputFolder": outputFolder.text.trim(),
            "notifyOnCompletion": notifications.checked,
            "resumeInterruptedJobs": autoResume.checked
        }
        const saved = callBackend("saveSettings", [values], false)
        if (saved !== false) {
            openAiKey.clear()
            geminiKey.clear()
            dirty = false
            if (shell)
                shell.showToast(qsTranslate("App", "Configurações salvas."))
        }
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

    function testProvider(provider, field) {
        const key = field.text.trim()
        if (provider === "openai")
            openAiStatus = "checking"
        else
            geminiStatus = "checking"
        const result = callBackend("testApiKey", [provider, key], null)
        if (result !== null) {
            const label = result === true ? "valid" : String(result)
            if (provider === "openai")
                openAiStatus = label
            else
                geminiStatus = label
        }
    }

    function statusText(status) {
        // Track locale changes without changing draft settings or raw error data.
        const locale = backendValue("interfaceLanguage", "en-US")
        if (status === "checking")
            return qsTranslate("App", "Verificando…")
        if (status === "valid")
            return qsTranslate("App", "Chave válida")
        if (status === "invalid")
            return qsTranslate("App", "Não foi possível validar")
        return callBackend("translateMessage", [status], status)
    }

    onShellChanged: loadSettings()

    Rectangle {
        anchors.fill: parent
        color: App.Theme.surfaceRaised
    }

    Flickable {
        id: settingsScroll

        objectName: "settingsPageScroll"
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: body.implicitHeight + 64
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        activeFocusOnTab: true
        Accessible.name: qsTranslate("App", "Conteúdo das Configurações")
        Keys.onPressed: event => root.handleScrollKey(event, settingsScroll)

        Rectangle {
            parent: settingsScroll
            anchors.fill: parent
            color: "transparent"
            border.width: settingsScroll.activeFocus ? 2 : 0
            border.color: App.Theme.focus
            z: 1000
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            interactive: true
        }

        ColumnLayout {
            id: body
            width: Math.min(900, settingsScroll.width - 64)
            x: Math.max(32, (settingsScroll.width - width) / 2)
            y: 32
            spacing: 22

            Components.PageHeader {
                Layout.fillWidth: true
                title: qsTranslate("App", "Configurações")
                description: qsTranslate("App", "Cadastre as chaves dos provedores e escolha como o São Francisco deve guardar e retomar seu trabalho.")
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                Text {
                    text: qsTranslate("App", "Idioma da interface")
                    font.family: App.Theme.displayFont
                    font.pixelSize: 19
                    color: App.Theme.text
                }
                ComboBox {
                    id: interfaceLanguage
                    objectName: "interfaceLanguageSelector"
                    Layout.fillWidth: true
                    model: root.backendValue("interfaceLanguages", [])
                    textRole: "name"
                    valueRole: "id"
                    currentIndex: Math.max(0, indexOfValue(
                        root.backendValue("interfaceLanguage", "en-US")))
                    Accessible.name: qsTranslate("App", "Idioma da interface")
                    onActivated: root.callBackend("setInterfaceLanguage", [currentValue], false)
                }
                Text {
                    Layout.fillWidth: true
                    text: qsTranslate("App", "A interface muda imediatamente. O idioma da transcrição não é alterado.")
                    wrapMode: Text.WordWrap
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                }
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                spacing: 18

                RowLayout {
                    Layout.fillWidth: true
                    spacing: 10
                    Rectangle {
                        Layout.preferredWidth: 34
                        Layout.preferredHeight: 34
                        radius: 17
                        color: App.Theme.primarySoft
                        Components.Icon {
                            anchors.centerIn: parent
                            name: "key"
                            iconSize: 18
                            iconColor: App.Theme.primary
                        }
                    }
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2
                        Text {
                            Layout.fillWidth: true
                            text: qsTranslate("App", "Chaves de API")
                            color: App.Theme.text
                            font.family: App.Theme.displayFont
                            font.pixelSize: 19
                            font.weight: Font.Medium
                        }
                        Text {
                            Layout.fillWidth: true
                            text: qsTranslate("App", "As chaves são guardadas pelo cofre seguro do sistema. O valor completo não volta a ser exibido.")
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: 12
                            wrapMode: Text.WordWrap
                        }
                    }
                    Components.AppButton {
                        text: qsTranslate("App", "Como obter")
                        variant: "ghost"
                        compact: true
                        onClicked: {
                            if (root.shell)
                                root.shell.navigateHelp(
                                            "chaves-da-openai-e-do-gemini")
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: openAiColumn.implicitHeight + 28
                    radius: App.Theme.radius
                    color: App.Theme.background
                    border.width: 1
                    border.color: App.Theme.border

                    ColumnLayout {
                        id: openAiColumn
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                Layout.fillWidth: true
                                text: "OpenAI"
                                color: App.Theme.text
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: Font.DemiBold
                            }
                            Components.StatusPill {
                                visible: root.openAiStatus.length > 0
                                objectName: "openAiKeyStatus"
                                text: root.statusText(root.openAiStatus)
                                tone: root.openAiStatus === "valid"
                                      ? "success"
                                      : "neutral"
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            TextField {
                                id: openAiKey
                                objectName: "openAiKeyInput"
                                LayoutMirroring.enabled: false
                                horizontalAlignment: TextInput.AlignLeft
                                Layout.fillWidth: true
                                implicitHeight: 38
                                echoMode: TextInput.Password
                                passwordCharacter: "•"
                                placeholderText: "sk-…"
                                selectByMouse: true
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                Accessible.name: qsTranslate("App", "Chave da API da OpenAI")
                                onTextChanged: root.dirty = true
                            }
                            Components.AppButton {
                                text: qsTranslate("App", "Verificar")
                                variant: "secondary"
                                compact: true
                                onClicked: root.testProvider("openai", openAiKey)
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: geminiColumn.implicitHeight + 28
                    radius: App.Theme.radius
                    color: App.Theme.background
                    border.width: 1
                    border.color: App.Theme.border

                    ColumnLayout {
                        id: geminiColumn
                        anchors.fill: parent
                        anchors.margins: 14
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            Text {
                                Layout.fillWidth: true
                                text: "Google Gemini"
                                color: App.Theme.text
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: Font.DemiBold
                            }
                            Components.StatusPill {
                                visible: root.geminiStatus.length > 0
                                text: root.statusText(root.geminiStatus)
                                tone: root.geminiStatus === "valid"
                                      ? "success"
                                      : "neutral"
                            }
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8
                            TextField {
                                id: geminiKey
                                objectName: "geminiKeyInput"
                                LayoutMirroring.enabled: false
                                horizontalAlignment: TextInput.AlignLeft
                                Layout.fillWidth: true
                                implicitHeight: 38
                                echoMode: TextInput.Password
                                passwordCharacter: "•"
                                placeholderText: qsTranslate("App", "Cole a chave do Google AI Studio")
                                selectByMouse: true
                                font.family: App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                Accessible.name: qsTranslate("App", "Chave da API do Google Gemini")
                                onTextChanged: root.dirty = true
                            }
                            Components.AppButton {
                                text: qsTranslate("App", "Verificar")
                                variant: "secondary"
                                compact: true
                                onClicked: root.testProvider("gemini", geminiKey)
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
                    text: qsTranslate("App", "Arquivos e continuidade")
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 19
                    font.weight: Font.Medium
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 6
                    Text {
                        text: qsTranslate("App", "Pasta de saída padrão")
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
                            LayoutMirroring.enabled: false
                            horizontalAlignment: TextInput.AlignLeft
                            Layout.fillWidth: true
                            placeholderText: qsTranslate("App", "Pasta da fonte; Documentos para URLs")
                            selectByMouse: true
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            Accessible.name: qsTranslate("App", "Pasta de saída padrão")
                            onTextChanged: root.dirty = true
                        }
                        Components.AppButton {
                            text: qsTranslate("App", "Escolher…")
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

                CheckBox {
                    id: autoResume
                    Layout.fillWidth: true
                    text: qsTranslate("App", "Retomar automaticamente tarefas interrompidas")
                    checked: true
                    font.family: App.Theme.uiFont
                    Accessible.name: text
                    onToggled: root.dirty = true
                }

                CheckBox {
                    id: notifications
                    Layout.fillWidth: true
                    text: qsTranslate("App", "Avisar quando uma transcrição terminar")
                    checked: true
                    font.family: App.Theme.uiFont
                    Accessible.name: text
                    onToggled: root.dirty = true
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                Text {
                    Layout.fillWidth: true
                    text: root.dirty ? qsTranslate("App", "Há alterações ainda não salvas.") : ""
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: 12
                }
                Components.AppButton {
                    text: qsTranslate("App", "Salvar configurações")
                    enabled: root.dirty
                    onClicked: root.saveSettings()
                }
            }

            Item {
                objectName: "settingsEndMarker"
                Layout.fillWidth: true
                Layout.preferredHeight: 1
            }
        }
    }

    Connections {
        target: root.shell ? root.shell.backend : null
        ignoreUnknownSignals: true

        function onSettingsChanged() {
            root.loadSettings()
        }
        function onInterfaceLanguageChanged() {
            const settings = root.backendValue("settings", {})
            openAiKey.placeholderText = settings.openAiKeyMasked
                    || "sk-…"
            geminiKey.placeholderText = settings.geminiKeyMasked
                    || qsTranslate("App", "Cole a chave do Google AI Studio")
        }
        function onApiKeyTestFinished(provider, ok, message) {
            const label = ok ? "valid" : String(message || "invalid")
            if (provider === "openai")
                root.openAiStatus = label
            else if (provider === "gemini")
                root.geminiStatus = label
        }
    }
}
