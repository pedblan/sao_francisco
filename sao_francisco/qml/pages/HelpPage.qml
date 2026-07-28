pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as App
import "../components" as Components

Item {
    id: root

    property var shell: null
    property string selectedAnchor: "primeiros-passos"
    property var results: []
    property string loadingError: ""

    function backendValue(name, fallbackValue) {
        return shell ? shell.backendValue(name, fallbackValue) : fallbackValue
    }

    function callBackend(name, args, fallbackValue) {
        return shell ? shell.callBackend(name, args, fallbackValue) : fallbackValue
    }

    function normalize(value) {
        let text = String(value || "").toLocaleLowerCase()
        try {
            text = text.normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        } catch (error) {
            // Case-insensitive search still works on older engines.
        }
        return text
    }

    function plainText(markdown) {
        return String(markdown || "")
                .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
                .replace(/[#*`>\[\]()]/g, " ")
                .replace(/\s+/g, " ")
                .trim()
    }

    function updateResults() {
        const backendResults = callBackend(
                    "searchHelp", [helpSearch.text], null)
        if (backendResults !== null && backendResults !== undefined) {
            results = backendResults
            loadingError = ""
            return
        }
        results = []
        loadingError = "A Ajuda integrada não pôde ser carregada. Reinstale o aplicativo para restaurar o manual."
    }

    function sectionMarkdown(anchor) {
        const backendSection = callBackend("helpSection", [anchor], null)
        if (backendSection !== null && backendSection !== undefined) {
            if (typeof backendSection === "string")
                return backendSection
            if (backendSection.markdown !== undefined)
                return String(backendSection.markdown)
        }
        return loadingError.length > 0
               ? "## Ajuda indisponível\n\n" + loadingError
               : "## Carregando\n\nO manual está sendo preparado."
    }

    function selectAnchor(anchor) {
        const value = String(anchor || "")
        if (value.length === 0)
            return
        selectedAnchor = value
        callBackend("navigateHelp", [value])
        articleScroll.contentY = 0
    }

    function markdownBlocks(markdown) {
        const rawBlocks = String(markdown || "").split(/\n\s*\n/)
        const blocks = []
        for (let index = 0; index < rawBlocks.length; index++) {
            let block = rawBlocks[index].trim()
            if (block.length === 0)
                continue
            const warning = /^>\s*\[!WARNING\]/.test(block)
            const note = /^>\s*\[!NOTE\]/.test(block)
            if (warning || note) {
                block = block
                        .replace(/^>\s*\[!(WARNING|NOTE)\]\s*/i, "")
                        .replace(/^>\s?/gm, "")
            }
            blocks.push({
                "markdown": block,
                "heading": /^#{1,6}\s/.test(block),
                "warning": warning,
                "note": note,
                "link": firstLink(block)
            })
        }
        return blocks
    }

    function firstLink(markdown) {
        const match = /\[[^\]]+\]\(([^)]+)\)/.exec(String(markdown || ""))
        return match ? String(match[1]) : ""
    }

    function activateLink(link) {
        const value = String(link || "")
        if (value.indexOf("#") === 0) {
            selectAnchor(value.substring(1))
        } else if (value.indexOf("https://") === 0) {
            callBackend("openExternalUrl", [value])
        } else if (shell) {
            shell.showToast("Este endereço não pode ser aberto com segurança.")
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

    onShellChanged: {
        selectedAnchor = String(backendValue(
                                    "helpAnchor", "primeiros-passos"))
        updateResults()
    }

    Rectangle {
        anchors.fill: parent
        color: App.Theme.surface
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.preferredWidth: 304
            Layout.fillHeight: true
            color: App.Theme.background

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 14

                Text {
                    Layout.fillWidth: true
                    text: "Ajuda"
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 23
                    font.weight: Font.Medium
                    wrapMode: Text.WordWrap
                }
                Text {
                    Layout.fillWidth: true
                    text: "Orientações claras para cada etapa da transcrição."
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    lineHeight: 1.35
                    wrapMode: Text.WordWrap
                }

                TextField {
                    id: helpSearch
                    Layout.fillWidth: true
                    implicitHeight: 38
                    placeholderText: "Buscar na ajuda"
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    leftPadding: 12
                    rightPadding: 12
                    selectByMouse: true
                    Accessible.name: "Buscar na Ajuda"
                    background: Rectangle {
                        radius: App.Theme.radius
                        color: App.Theme.surface
                        border.width: helpSearch.activeFocus ? 2 : 1
                        border.color: helpSearch.activeFocus
                                      ? App.Theme.focus
                                      : App.Theme.border
                    }
                    onTextChanged: root.updateResults()
                }

                Text {
                    Layout.fillWidth: true
                    text: helpSearch.text.length > 0
                          ? root.results.length
                            + (root.results.length === 1
                               ? " resultado"
                               : " resultados")
                          : "TÓPICOS"
                    color: App.Theme.textSoft
                    font.family: App.Theme.uiFont
                    font.pixelSize: 9
                    font.weight: Font.DemiBold
                    font.letterSpacing: 0.9
                    Layout.topMargin: 4
                }

                ListView {
                    id: topicList

                    objectName: "helpTopicList"
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    Layout.rightMargin: 4
                    clip: true
                    spacing: 3
                    model: root.results
                    activeFocusOnTab: true
                    Accessible.name: "Tópicos da Ajuda"
                    boundsBehavior: Flickable.StopAtBounds
                    Keys.onPressed: event => root.handleScrollKey(
                                        event, topicList)
                    Rectangle {
                        parent: topicList
                        anchors.fill: parent
                        color: "transparent"
                        border.width: topicList.activeFocus ? 2 : 0
                        border.color: App.Theme.focus
                        z: 1000
                    }
                    ScrollBar.vertical: ScrollBar {
                        objectName: "helpTopicScrollBar"
                        policy: ScrollBar.AsNeeded
                        interactive: true
                    }

                    delegate: ItemDelegate {
                        id: topicDelegate

                        required property var modelData

                        width: ListView.view.width
                        height: resultColumn.implicitHeight + 20
                        padding: 0
                        hoverEnabled: true
                        activeFocusOnTab: true
                        Accessible.name: String(modelData.title)
                        Accessible.description: root.selectedAnchor
                                                === modelData.anchor
                                                ? "Tópico selecionado"
                                                : "Abrir tópico da Ajuda"
                        onClicked: root.selectAnchor(
                                       String(modelData.anchor))

                        contentItem: ColumnLayout {
                            id: resultColumn
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: 10
                            anchors.rightMargin: 10
                            spacing: 3

                            Text {
                                Layout.fillWidth: true
                                text: String(topicDelegate.modelData.title)
                                color: root.selectedAnchor
                                       === topicDelegate.modelData.anchor
                                       ? App.Theme.primary
                                       : App.Theme.text
                                font.family: root.selectedAnchor
                                             === topicDelegate.modelData.anchor
                                             ? App.Theme.displayFont
                                             : App.Theme.uiFont
                                font.pixelSize: App.Theme.bodySize
                                font.weight: root.selectedAnchor
                                             === topicDelegate.modelData.anchor
                                             ? Font.Medium
                                             : Font.Normal
                                wrapMode: Text.WordWrap
                            }
                            Text {
                                visible: helpSearch.text.length > 0
                                         && topicDelegate.modelData.excerpt
                                            !== undefined
                                Layout.fillWidth: true
                                text: String(topicDelegate.modelData.excerpt
                                             || "")
                                color: App.Theme.textSoft
                                font.family: App.Theme.uiFont
                                font.pixelSize: 10
                                wrapMode: Text.WordWrap
                                maximumLineCount: 2
                                elide: Text.ElideRight
                            }
                        }

                        background: Rectangle {
                            radius: App.Theme.radius
                            color: root.selectedAnchor
                                   === topicDelegate.modelData.anchor
                                   ? App.Theme.primarySoft
                                   : topicDelegate.hovered
                                     ? App.Theme.surfaceMuted
                                     : "transparent"
                            border.width: topicDelegate.activeFocus ? 2 : 0
                            border.color: App.Theme.focus
                        }
                    }
                }

                Text {
                    visible: root.results.length === 0
                             && helpSearch.text.length > 0
                    Layout.fillWidth: true
                    text: "Nenhum tópico encontrado. Tente palavras mais curtas."
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: 12
                    lineHeight: 1.3
                    wrapMode: Text.WordWrap
                }
            }

            Rectangle {
                anchors.right: parent.right
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                width: 1
                color: App.Theme.border
            }
        }

        Flickable {
            id: articleScroll

            objectName: "helpArticleScroll"
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.rightMargin: 20
            clip: true
            contentWidth: width
            contentHeight: articleFrame.height
            flickableDirection: Flickable.VerticalFlick
            boundsBehavior: Flickable.StopAtBounds
            activeFocusOnTab: true
            Accessible.name: "Artigo da Ajuda"

            Keys.onPressed: event => root.handleScrollKey(
                                event, articleScroll)

            Rectangle {
                parent: articleScroll
                anchors.fill: parent
                color: "transparent"
                border.width: articleScroll.activeFocus ? 2 : 0
                border.color: App.Theme.focus
                z: 1000
            }

            ScrollBar.vertical: ScrollBar {
                objectName: "helpArticleScrollBar"
                policy: ScrollBar.AlwaysOn
                interactive: true
            }

            Item {
                id: articleFrame

                objectName: "helpArticleFrame"
                width: articleScroll.width
                height: article.implicitHeight + 74

                ColumnLayout {
                    id: article

                    objectName: "helpArticleColumn"
                    width: Math.min(720, parent.width - 80)
                    anchors.top: parent.top
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.topMargin: 40
                    spacing: 18

                    Components.AppCard {
                        visible: root.selectedAnchor === "primeiros-passos"
                        Layout.fillWidth: true
                        padding: 18
                        spacing: 0
                        cardColor: App.Theme.background

                        GridLayout {
                            Layout.fillWidth: true
                            columns: article.width < 570 ? 1 : 2
                            columnSpacing: 20
                            rowSpacing: 16

                            Components.BauhausArtwork {
                                Layout.preferredWidth: article.width < 570
                                                       ? 220 : 210
                                Layout.preferredHeight: article.width < 570
                                                        ? 220 : 190
                                Layout.alignment: Qt.AlignHCenter
                            }

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 9
                                Text {
                                    Layout.fillWidth: true
                                    text: "Comece com tranquilidade"
                                    color: App.Theme.text
                                    font.family: App.Theme.displayFont
                                    font.pixelSize: 20
                                    font.weight: Font.Medium
                                    wrapMode: Text.WordWrap
                                }
                                Text {
                                    Layout.fillWidth: true
                                    text: "A Ajuda explica cada escolha, inclusive chaves, custos, vídeos longos e retomada."
                                    color: App.Theme.textMuted
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: App.Theme.bodySize
                                    lineHeight: 1.4
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }

                    Repeater {
                        model: root.markdownBlocks(
                                   root.sectionMarkdown(
                                       root.selectedAnchor))

                        delegate: Rectangle {
                            id: articleBlockFrame

                            required property var modelData

                            Layout.fillWidth: true
                            implicitHeight: articleBlock.implicitHeight
                                            + (modelData.warning
                                               || modelData.note ? 28 : 0)
                            radius: App.Theme.radius
                            color: modelData.warning
                                   ? App.Theme.warningSoft
                                   : modelData.note
                                     ? App.Theme.primarySoft
                                     : "transparent"
                            border.width: modelData.warning
                                          || modelData.note ? 1 : 0
                            border.color: modelData.warning
                                          ? App.Theme.accent
                                          : App.Theme.focus

                            Text {
                                id: articleBlock

                                anchors.left: parent.left
                                anchors.right: parent.right
                                anchors.verticalCenter: parent.verticalCenter
                                anchors.leftMargin: articleBlockFrame.modelData.warning
                                                    || articleBlockFrame.modelData.note
                                                    ? 16 : 0
                                anchors.rightMargin: anchors.leftMargin
                                text: articleBlockFrame.modelData.markdown
                                textFormat: Text.MarkdownText
                                color: App.Theme.text
                                linkColor: App.Theme.primary
                                font.family: articleBlockFrame.modelData.heading
                                             ? App.Theme.displayFont
                                             : App.Theme.uiFont
                                font.pixelSize: articleBlockFrame.modelData.heading
                                                ? 18 : 15
                                font.weight: articleBlockFrame.modelData.heading
                                             ? Font.Medium
                                             : Font.Normal
                                wrapMode: Text.WordWrap
                                lineHeight: articleBlockFrame.modelData.heading
                                            ? 1.22 : 1.42
                                activeFocusOnTab: articleBlockFrame.modelData.link.length
                                                  > 0
                                Accessible.role: articleBlockFrame.modelData.link.length
                                                 > 0
                                                 ? Accessible.Link
                                                 : Accessible.StaticText
                                Accessible.name: root.plainText(text)
                                onLinkActivated: link => root.activateLink(link)
                                Keys.onReturnPressed: {
                                    if (articleBlockFrame.modelData.link.length > 0)
                                        root.activateLink(
                                                    articleBlockFrame.modelData.link)
                                }
                                Keys.onEnterPressed: {
                                    if (articleBlockFrame.modelData.link.length > 0)
                                        root.activateLink(
                                                    articleBlockFrame.modelData.link)
                                }
                                Keys.onSpacePressed: {
                                    if (articleBlockFrame.modelData.link.length > 0)
                                        root.activateLink(
                                                    articleBlockFrame.modelData.link)
                                }

                                Rectangle {
                                    visible: articleBlock.activeFocus
                                    anchors.fill: parent
                                    anchors.margins: -4
                                    radius: App.Theme.radiusSmall
                                    color: "transparent"
                                    border.width: 2
                                    border.color: App.Theme.focus
                                }
                            }
                        }
                    }

                    Item {
                        id: articleEndMarker
                        objectName: "helpArticleEndMarker"
                        Layout.fillWidth: true
                        Layout.preferredHeight: 1
                    }
                }
            }
        }
    }

    Connections {
        target: root.shell ? root.shell.backend : null
        ignoreUnknownSignals: true

        function onHelpAnchorChanged() {
            root.selectedAnchor = String(root.backendValue(
                                             "helpAnchor",
                                             root.selectedAnchor))
            articleScroll.contentY = 0
        }
        function onHelpContentChanged() {
            root.updateResults()
        }
    }
}
