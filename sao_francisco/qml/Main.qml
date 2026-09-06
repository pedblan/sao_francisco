import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "." as App
import "components" as Components

ApplicationWindow {
    id: window

    // `appBackend` is injected as a context property by the launcher.
    // qmllint disable unqualified
    property var backend: appBackend
    // qmllint enable unqualified
    property string currentRoute: "transcribe"
    property bool sidebarCollapsed: false
    property bool backendBusy: false
    property string activeJobState: ""
    property bool outputAvailable: false
    property string pendingPageAction: ""
    property bool rightToLeft: Boolean(backendValue("rightToLeft", false))
    LayoutMirroring.enabled: rightToLeft
    LayoutMirroring.childrenInherit: true

    visible: true
    width: 1280
    height: 800
    minimumWidth: 1024
    minimumHeight: 680
    title: "São Francisco"
    color: App.Theme.background

    function backendValue(name, fallbackValue) {
        try {
            const value = backend[name]
            return value === undefined || value === null ? fallbackValue : value
        } catch (error) {
            return fallbackValue
        }
    }

    function backendBool(name, fallbackValue) {
        return Boolean(backendValue(name, fallbackValue))
    }

    function callBackend(name, args, fallbackValue) {
        try {
            const callable = backend[name]
            if (typeof callable === "function")
                return callable.apply(backend, args || [])
        } catch (error) {
            showToast(qsTranslate("App", "Não foi possível concluir esta ação."))
        }
        return fallbackValue
    }

    function syncBackendState() {
        const route = String(backendValue("currentRoute", currentRoute))
        if (route.length > 0)
            currentRoute = route
        sidebarCollapsed = backendBool("sidebarCollapsed", sidebarCollapsed)
        backendBusy = backendBool("busy", false)
        activeJobState = String(backendValue("activeJobState", ""))
        outputAvailable = backendBool("canOpenOutput", false)
    }

    function navigate(route) {
        const knownRoutes = ["transcribe", "history", "settings", "help", "about"]
        currentRoute = knownRoutes.indexOf(route) >= 0 ? route : "transcribe"
        callBackend("navigate", [currentRoute])
    }

    function navigateHelp(anchor) {
        currentRoute = "help"
        callBackend("navigateHelp", [anchor])
        callBackend("navigate", ["help"])
        Qt.callLater(function() {
            if (pageLoader.item
                    && typeof pageLoader.item.selectAnchor === "function")
                pageLoader.item.selectAnchor(anchor)
        })
    }

    function runPageAction(route, actionName) {
        pendingPageAction = actionName
        if (currentRoute !== route)
            navigate(route)
        else
            Qt.callLater(invokePendingPageAction)
    }

    function invokePendingPageAction() {
        if (pendingPageAction.length === 0 || !pageLoader.item)
            return
        const action = pageLoader.item[pendingPageAction]
        if (typeof action !== "function")
            return
        const actionName = pendingPageAction
        pendingPageAction = ""
        action.call(pageLoader.item)
    }

    function configureLoadedPage(page) {
        if (!page)
            return
        try {
            page.shell = window
        } catch (error) {
            // Every first-party page has `shell`; this keeps custom pages harmless.
        }
    }

    function toggleSidebar() {
        sidebarCollapsed = !sidebarCollapsed
        const backendResult = callBackend("toggleSidebar", [])
        if (backendResult === undefined)
            callBackend("setSidebarCollapsed", [sidebarCollapsed])
    }

    function toggleFullScreen() {
        if (visibility === Window.FullScreen)
            showNormal()
        else
            showFullScreen()
    }

    function showToast(message) {
        toast.message = backend && typeof backend.translateMessage === "function"
                ? backend.translateMessage(String(message)) : message
        toast.showing = true
        toastTimer.restart()
    }

    function pageSource(route) {
        const pages = {
            "transcribe": "pages/TranscribePage.qml",
            "history": "pages/HistoryPage.qml",
            "settings": "pages/SettingsPage.qml",
            "help": "pages/HelpPage.qml",
            "about": "pages/AboutPage.qml"
        }
        return Qt.resolvedUrl(pages[route] || pages.transcribe)
    }

    Component.onCompleted: syncBackendState()

    menuBar: MenuBar {
        Menu {
            title: qsTranslate("App", "Arquivo")

            Action {
                text: qsTranslate("App", "Nova transcrição")
                shortcut: StandardKey.New
                onTriggered: window.runPageAction(
                                 "transcribe", "resetDraft")
            }
            MenuSeparator {}
            Action {
                text: qsTranslate("App", "Adicionar arquivos…")
                shortcut: StandardKey.Open
                onTriggered: window.runPageAction("transcribe", "openFilePicker")
            }
            Action {
                text: qsTranslate("App", "Usar endereço…")
                onTriggered: window.runPageAction("transcribe", "focusUrlField")
            }
            MenuSeparator {}
            Action {
                text: qsTranslate("App", "Histórico")
                onTriggered: window.navigate("history")
            }
            Action {
                text: qsTranslate("App", "Configurações…")
                shortcut: StandardKey.Preferences
                onTriggered: window.navigate("settings")
            }
            MenuSeparator {}
            Action {
                text: qsTranslate("App", "Sair do São Francisco")
                shortcut: StandardKey.Quit
                onTriggered: window.close()
            }
        }

        Menu {
            title: qsTranslate("App", "Transcrição")

            Action {
                text: qsTranslate("App", "Iniciar transcrição")
                shortcut: "Ctrl+Return"
                enabled: !window.backendBusy
                onTriggered: window.runPageAction("transcribe", "startTranscription")
            }
            Action {
                text: qsTranslate("App", "Cancelar transcrição")
                enabled: window.activeJobState === "running"
                         || window.activeJobState === "preparing"
                onTriggered: window.callBackend("cancelTranscription", [])
            }
            MenuSeparator {}
            Action {
                text: qsTranslate("App", "Abrir resultado")
                enabled: window.outputAvailable
                onTriggered: window.callBackend("openActiveOutput", [])
            }
            Action {
                text: qsTranslate("App", "Mostrar pasta do resultado")
                enabled: window.outputAvailable
                onTriggered: window.callBackend("revealActiveOutput", [])
            }
        }

        Menu {
            title: qsTranslate("App", "Visualizar")

            Action {
                text: window.sidebarCollapsed
                      ? qsTranslate("App", "Mostrar barra lateral")
                      : qsTranslate("App", "Recolher barra lateral")
                onTriggered: window.toggleSidebar()
            }
            MenuSeparator {}
            Action {
                text: window.visibility === Window.FullScreen
                      ? qsTranslate("App", "Sair da tela cheia")
                      : qsTranslate("App", "Tela cheia")
                shortcut: StandardKey.FullScreen
                onTriggered: window.toggleFullScreen()
            }
        }

        Menu {
            title: qsTranslate("App", "Ir")

            Action {
                text: qsTranslate("App", "Transcrever")
                shortcut: "Ctrl+1"
                onTriggered: window.navigate("transcribe")
            }
            Action {
                text: qsTranslate("App", "Histórico")
                shortcut: "Ctrl+2"
                onTriggered: window.navigate("history")
            }
            Action {
                text: qsTranslate("App", "Configurações")
                shortcut: "Ctrl+3"
                onTriggered: window.navigate("settings")
            }
            Action {
                text: qsTranslate("App", "Ajuda")
                shortcut: "Ctrl+4"
                onTriggered: window.navigateHelp("primeiros-passos")
            }
            Action {
                text: qsTranslate("App", "Sobre")
                shortcut: "Ctrl+5"
                onTriggered: window.navigate("about")
            }
        }

        Menu {
            title: qsTranslate("App", "Janela")

            Action {
                text: qsTranslate("App", "Minimizar")
                onTriggered: window.showMinimized()
            }
            Action {
                text: qsTranslate("App", "Alternar zoom")
                onTriggered: window.visibility === Window.Maximized
                             ? window.showNormal()
                             : window.showMaximized()
            }
            Action {
                text: qsTranslate("App", "Trazer para a frente")
                onTriggered: {
                    window.raise()
                    window.requestActivate()
                }
            }
        }

        Menu {
            title: qsTranslate("App", "Ajuda")

            Action {
                text: qsTranslate("App", "Ajuda do São Francisco")
                shortcut: "Ctrl+K"
                onTriggered: window.navigateHelp("primeiros-passos")
            }
            Menu {
                title: qsTranslate("App", "Tópicos")

                Action {
                    text: qsTranslate("App", "Primeiros passos")
                    onTriggered: window.navigateHelp("primeiros-passos")
                }
                Action {
                    text: qsTranslate("App", "Arquivos e endereços")
                    onTriggered: window.navigateHelp(
                                     "adicionar-arquivo-video-ou-url")
                }
                Action {
                    text: qsTranslate("App", "Chaves de API")
                    onTriggered: window.navigateHelp(
                                     "chaves-da-openai-e-do-gemini")
                }
                Action {
                    text: qsTranslate("App", "Vídeos longos")
                    onTriggered: window.navigateHelp(
                                     "como-midias-longas-sao-processadas")
                }
                Action {
                    text: qsTranslate("App", "Problemas comuns")
                    onTriggered: window.navigateHelp("problemas-comuns")
                }
            }
            MenuSeparator {}
            Action {
                text: qsTranslate("App", "Sobre o São Francisco")
                onTriggered: window.navigate("about")
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Components.Sidebar {
            Layout.fillHeight: true
            collapsed: window.sidebarCollapsed
            activeRoute: window.currentRoute
            versionLabel: "v" + String(window.backendValue(
                                           "appVersion",
                                           Qt.application.version || "1.0.0"))
            onNavigate: route => window.navigate(route)
            onToggleCollapse: window.toggleSidebar()
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 54
                color: App.Theme.background

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 28
                    anchors.rightMargin: 28
                    spacing: 12

                    Text {
                        Layout.fillWidth: true
                        text: App.Theme.routeTitle(window.currentRoute)
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }

                    BusyIndicator {
                        visible: window.backendBusy
                        running: visible
                        implicitWidth: 22
                        implicitHeight: 22
                        Accessible.name: qsTranslate("App", "Operação em andamento")
                    }

                    Components.AppButton {
                        text: qsTranslate("App", "Ajuda")
                        variant: "ghost"
                        compact: true
                        onClicked: window.navigateHelp("primeiros-passos")
                        ToolTip.visible: hovered
                        ToolTip.text: qsTranslate("App", "Abrir a Ajuda")
                    }
                }

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    height: 1
                    color: App.Theme.border
                }
            }

            Loader {
                id: pageLoader

                Layout.fillWidth: true
                Layout.fillHeight: true
                source: window.pageSource(window.currentRoute)
                onLoaded: {
                    window.configureLoadedPage(item)
                    window.invokePendingPageAction()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 34
                color: App.Theme.background

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.top: parent.top
                    height: 1
                    color: App.Theme.border
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 28
                    anchors.rightMargin: 28
                    spacing: 6

                    Text {
                        text: "São Francisco"
                        color: App.Theme.textMuted
                        font.family: App.Theme.displayFont
                        font.pixelSize: 12
                        font.weight: Font.Medium
                    }
                    Item { Layout.fillWidth: true }
                    Text {
                        text: "Pedro Duarte Blanco"
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }
                    Text {
                        text: "·"
                        color: App.Theme.textSoft
                        font.pixelSize: 10
                    }
                    Button {
                        id: siteButton

                        flat: true
                        text: "pedblan.github.io"
                        padding: 2
                        Accessible.name: qsTranslate("App", "Abrir o site de Pedro Duarte Blanco")
                        onClicked: window.callBackend(
                                       "openExternalUrl",
                                       ["https://pedblan.github.io"])

                        contentItem: Text {
                            text: siteButton.text
                            color: App.Theme.primary
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

    Rectangle {
        id: toast

        property string message: ""
        property bool showing: false

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: showing ? 24 : -60
        width: Math.min(560, toastText.implicitWidth + 40)
        height: 44
        radius: App.Theme.radiusLarge
        color: App.Theme.text
        opacity: showing ? 1 : 0
        visible: opacity > 0
        z: 100

        Behavior on opacity {
            NumberAnimation { duration: 140 }
        }
        Behavior on anchors.bottomMargin {
            NumberAnimation { duration: 160; easing.type: Easing.OutCubic }
        }

        Text {
            id: toastText

            anchors.centerIn: parent
            width: parent.width - 32
            text: toast.message
            color: "#FFFFFF"
            font.family: App.Theme.uiFont
            font.pixelSize: App.Theme.bodySize
            horizontalAlignment: Text.AlignHCenter
            elide: Text.ElideRight
        }

        Timer {
            id: toastTimer
            interval: 3200
            onTriggered: toast.showing = false
        }
    }

    Connections {
        target: window.backend
        ignoreUnknownSignals: true

        function onCurrentRouteChanged() {
            window.currentRoute = String(window.backendValue(
                                             "currentRoute",
                                             window.currentRoute))
        }
        function onSidebarCollapsedChanged() {
            window.sidebarCollapsed = window.backendBool(
                        "sidebarCollapsed", window.sidebarCollapsed)
        }
        function onBusyChanged() {
            window.backendBusy = window.backendBool("busy", false)
        }
        function onActiveJobStateChanged() {
            window.activeJobState = String(window.backendValue(
                                               "activeJobState", ""))
        }
        function onCanOpenOutputChanged() {
            window.outputAvailable = window.backendBool(
                        "canOpenOutput", false)
        }
        function onToastRequested(message) {
            window.showToast(message)
        }
    }
}
