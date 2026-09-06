pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as App
import "../components" as Components

Item {
    id: root
    property string savedStateFilter: "all"

    property var shell: null
    property var historyItems: []
    property var filteredItems: []

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
            // Older JavaScript engines still get case-insensitive matching.
        }
        return text
    }

    function refreshHistory() {
        const backendItems = callBackend("history", [], null)
        historyItems = backendItems !== null
                       ? backendItems
                       : backendValue("historyItems", [])
        applyFilters()
    }

    function applyFilters() {
        const query = normalize(historySearch.text.trim())
        const state = String(stateFilter.currentValue || "all")
        const matches = []
        for (let index = 0; index < historyItems.length; index++) {
            const item = historyItems[index]
            const haystack = normalize(
                        String(item.title || item.sourceName || "")
                        + " " + String(item.providerLabel || item.provider || "")
                        + " " + String(item.modelLabel || item.model || ""))
            const matchesText = query.length === 0
                                || haystack.indexOf(query) >= 0
            const matchesState = state === "all"
                                 || String(item.state || "") === state
            if (matchesText && matchesState)
                matches.push(item)
        }
        filteredItems = matches
    }

    function stateLabel(item) {
        const value = String(item.state || "")
        const stage = String(item.stage || "")
        if (Boolean(item.originalReady)
                && String(item.improvementState || "") === "in_progress")
            return qsTranslate("App", "Transcrição pronta · Melhorando texto")
        if (Boolean(item.originalReady)
                && String(item.improvementState || "") === "not_completed"
                && (value === "failed" || value === "cancelled"
                    || value === "paused"))
            return qsTranslate("App", "Transcrição pronta · Melhoria não concluída")
        if (Boolean(item.originalReady)
                && String(item.improvementState || "") === "ready")
            return qsTranslate("App", "Transcrição e texto melhorado prontos")
        if (value === "running"
                && (stage === "exporting_original"
                    || stage === "exporting_improved"))
            return qsTranslate("App", "Criando arquivos")
        if (value === "failed" && stage === "improving")
            return qsTranslate("App", "Melhoria interrompida")
        if (value === "failed" && stage === "export_failed")
            return qsTranslate("App", "Exportação interrompida")
        const labels = {
            "queued": qsTranslate("App", "Na fila"),
            "preparing": qsTranslate("App", "Preparando"),
            "running": qsTranslate("App", "Em andamento"),
            "paused": qsTranslate("App", "Pausada"),
            "completed": qsTranslate("App", "Concluída"),
            "failed": qsTranslate("App", "Falhou"),
            "cancelled": qsTranslate("App", "Cancelada")
        }
        return labels[value] || qsTranslate("App", "Desconhecido")
    }

    function stateTone(value) {
        if (value === "completed")
            return "success"
        if (value === "failed" || value === "cancelled")
            return "danger"
        if (value === "paused")
            return "warning"
        return "accent"
    }

    function provenanceLabel(value) {
        const labels = {
            "existing_captions": qsTranslate("App", "Legenda existente"),
            "author_captions": qsTranslate("App", "Legendas do autor"),
            "automatic_captions": qsTranslate("App", "Legendas automáticas"),
            "audio_transcription": qsTranslate("App", "Áudio transcrito")
        }
        return labels[value] || ""
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

    onShellChanged: refreshHistory()

    Rectangle {
        anchors.fill: parent
        color: App.Theme.surfaceRaised
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.leftMargin: 32
        anchors.rightMargin: 32
        anchors.topMargin: 30
        anchors.bottomMargin: 24
        spacing: 20

        Components.PageHeader {
            Layout.fillWidth: true
            title: qsTranslate("App", "Histórico")
            description: qsTranslate("App", "Acompanhe tarefas, retome transcrições interrompidas e abra os arquivos produzidos.")
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            TextField {
                id: historySearch
                Layout.fillWidth: true
                implicitHeight: 38
                placeholderText: qsTranslate("App", "Buscar por arquivo, endereço ou modelo")
                selectByMouse: true
                leftPadding: 13
                rightPadding: 13
                font.family: App.Theme.uiFont
                font.pixelSize: App.Theme.bodySize
                Accessible.name: qsTranslate("App", "Buscar no histórico")
                onTextChanged: root.applyFilters()
                background: Rectangle {
                    radius: App.Theme.radius
                    color: App.Theme.surface
                    border.width: historySearch.activeFocus ? 2 : 1
                    border.color: historySearch.activeFocus
                                  ? App.Theme.focus
                                  : App.Theme.border
                }
            }

            ComboBox {
                id: stateFilter
                objectName: "historyStateFilter"
                Layout.preferredWidth: 196
                implicitHeight: 38
                leftPadding: 20
                rightPadding: 20
                textRole: "label"
                valueRole: "id"
                model: [
                    { "label": qsTranslate("App", "Todos os estados"), "id": "all" },
                    { "label": qsTranslate("App", "Em andamento"), "id": "running" },
                    { "label": qsTranslate("App", "Concluídas"), "id": "completed" },
                    { "label": qsTranslate("App", "Pausadas"), "id": "paused" },
                    { "label": qsTranslate("App", "Com falha"), "id": "failed" }
                ]
                Accessible.name: qsTranslate("App", "Filtrar por estado")
                onCurrentValueChanged: root.applyFilters()
                contentItem: Text {
                    leftPadding: stateFilter.leftPadding
                    rightPadding: stateFilter.rightPadding
                    text: stateFilter.displayText
                    color: stateFilter.enabled
                           ? App.Theme.text
                           : App.Theme.textSoft
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    elide: Text.ElideRight
                }
            }

            Components.AppButton {
                text: qsTranslate("App", "Atualizar")
                variant: "secondary"
                onClicked: root.refreshHistory()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            implicitHeight: 1
            color: App.Theme.border
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: historyList

                objectName: "historyList"
                anchors.fill: parent
                clip: true
                spacing: 10
                model: root.filteredItems
                activeFocusOnTab: true
                Accessible.name: qsTranslate("App", "Lista do histórico de transcrições")
                boundsBehavior: Flickable.StopAtBounds
                Keys.onPressed: event => root.handleScrollKey(
                                    event, historyList)
                Rectangle {
                    parent: historyList
                    anchors.fill: parent
                    color: "transparent"
                    border.width: historyList.activeFocus ? 2 : 0
                    border.color: App.Theme.focus
                    z: 1000
                }
                ScrollBar.vertical: ScrollBar {
                    objectName: "historyScrollBar"
                    policy: ScrollBar.AsNeeded
                    interactive: true
                }

                delegate: Rectangle {
                    id: historyCard

                    required property var modelData

                    width: ListView.view.width - 10
                    height: 120
                    radius: App.Theme.radiusLarge
                    color: App.Theme.surface
                    border.width: 1
                    border.color: App.Theme.border

                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 16

                        Rectangle {
                            Layout.preferredWidth: 42
                            Layout.preferredHeight: 42
                            radius: 21
                            color: App.Theme.primarySoft

                            Components.Icon {
                                anchors.centerIn: parent
                                name: historyCard.modelData.state === "completed"
                                      ? "check"
                                      : "transcribe"
                                iconSize: 20
                                iconColor: App.Theme.primary
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 4

                            Text {
                                Layout.fillWidth: true
                                text: String(historyCard.modelData.title
                                             || historyCard.modelData.sourceName
                                             || qsTranslate("App", "Transcrição sem título"))
                                color: App.Theme.text
                                font.family: App.Theme.displayFont
                                font.pixelSize: 16
                                font.weight: Font.Medium
                                elide: Text.ElideMiddle
                                ToolTip.visible: titleHover.hovered
                                ToolTip.text: text
                                HoverHandler { id: titleHover }
                            }
                            Text {
                                Layout.fillWidth: true
                                text: [
                                    historyCard.modelData.createdAtLabel
                                    || historyCard.modelData.createdAt || "",
                                    historyCard.modelData.providerLabel
                                    || historyCard.modelData.provider || "",
                                    historyCard.modelData.modelLabel
                                    || historyCard.modelData.model || ""
                                ].filter(function(value) {
                                    return String(value).length > 0
                                }).join("  ·  ")
                                color: App.Theme.textMuted
                                font.family: App.Theme.uiFont
                                font.pixelSize: 12
                                elide: Text.ElideRight
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 7
                                Components.StatusPill {
                                    text: root.stateLabel(historyCard.modelData)
                                    tone: root.stateTone(String(
                                              historyCard.modelData.state || ""))
                                }
                                Components.StatusPill {
                                    visible: root.provenanceLabel(String(
                                                 historyCard.modelData.provenance
                                                 || "")).length > 0
                                    text: root.provenanceLabel(String(
                                              historyCard.modelData.provenance
                                              || ""))
                                    tone: "neutral"
                                }
                                Text {
                                    visible: historyCard.modelData.progress !== undefined
                                             && historyCard.modelData.state !== "completed"
                                    text: Math.round(Number(
                                              historyCard.modelData.progress) * 100)
                                          + "%"
                                    color: App.Theme.textMuted
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: 12
                                }
                                Text {
                                    visible: String(historyCard.modelData.costLabel
                                                    || "").length > 0
                                    text: String(historyCard.modelData.costLabel || "")
                                    color: App.Theme.textMuted
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Item { Layout.fillWidth: true }
                            }
                        }

                        ColumnLayout {
                            spacing: 7
                            Components.AppButton {
                                visible: String(historyCard.modelData.primaryOutput
                                                || "").length > 0
                                         || historyCard.modelData.state === "completed"
                                text: qsTranslate("App", "Abrir")
                                compact: true
                                onClicked: root.callBackend(
                                               "openHistoryOutput",
                                               [historyCard.modelData.id])
                            }
                            Components.AppButton {
                                visible: historyCard.modelData.state === "failed"
                                         || historyCard.modelData.state === "paused"
                                         || historyCard.modelData.state === "cancelled"
                                text: qsTranslate("App", "Retomar")
                                compact: true
                                onClicked: root.callBackend(
                                               "resumeTranscription",
                                               [historyCard.modelData.id])
                            }
                            Components.AppButton {
                                text: qsTranslate("App", "Mostrar detalhes")
                                variant: "ghost"
                                compact: true
                                onClicked: root.callBackend(
                                               "showHistoryDetails",
                                               [historyCard.modelData.id])
                            }
                        }
                    }
                }

                footer: Item {
                    width: historyList.width
                    height: 28
                    objectName: "historyEndMarker"
                }
            }

            ColumnLayout {
                visible: root.filteredItems.length === 0
                anchors.centerIn: parent
                width: Math.min(440, parent.width - 48)
                spacing: 10

                Components.Icon {
                    Layout.alignment: Qt.AlignHCenter
                    name: "history"
                    iconSize: 34
                    iconColor: App.Theme.textSoft
                }
                Text {
                    Layout.fillWidth: true
                    text: root.historyItems.length === 0
                          ? qsTranslate("App", "Nenhuma transcrição ainda")
                          : qsTranslate("App", "Nenhum item corresponde à busca")
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 19
                    font.weight: Font.Medium
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                Text {
                    Layout.fillWidth: true
                    text: root.historyItems.length === 0
                          ? qsTranslate("App", "Quando você iniciar uma tarefa, o progresso e os resultados aparecerão aqui.")
                          : qsTranslate("App", "Experimente remover o filtro ou buscar outro termo.")
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    horizontalAlignment: Text.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                Components.AppButton {
                    visible: root.historyItems.length === 0
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTranslate("App", "Transcrever agora")
                    onClicked: {
                        if (root.shell)
                            root.shell.navigate("transcribe")
                    }
                }
            }
        }
    }

    Connections {
        target: root.shell ? root.shell.backend : null
        function onInterfaceLanguageAboutToChange() {
            root.savedStateFilter = String(stateFilter.currentValue || "all")
        }
        function onInterfaceLanguageChanged() {
            Qt.callLater(function() {
                stateFilter.currentIndex = Math.max(0, stateFilter.indexOfValue(root.savedStateFilter))
            })
        }
        ignoreUnknownSignals: true
        function onHistoryChanged() {
            root.refreshHistory()
        }
    }
}
