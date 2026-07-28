import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as App
import "../components" as Components

Item {
    id: root

    property var shell: null

    function backendValue(name, fallbackValue) {
        return shell ? shell.backendValue(name, fallbackValue) : fallbackValue
    }

    function callBackend(name, args, fallbackValue) {
        return shell ? shell.callBackend(name, args, fallbackValue) : fallbackValue
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

    Rectangle {
        anchors.fill: parent
        color: App.Theme.surfaceRaised
    }

    Flickable {
        id: aboutScroll

        objectName: "aboutPageScroll"
        anchors.fill: parent
        clip: true
        contentWidth: width
        contentHeight: body.implicitHeight + 64
        flickableDirection: Flickable.VerticalFlick
        boundsBehavior: Flickable.StopAtBounds
        activeFocusOnTab: true
        Accessible.name: "Conteúdo da tela Sobre"
        Keys.onPressed: event => root.handleScrollKey(event, aboutScroll)

        Rectangle {
            parent: aboutScroll
            anchors.fill: parent
            color: "transparent"
            border.width: aboutScroll.activeFocus ? 2 : 0
            border.color: App.Theme.focus
            z: 1000
        }

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AsNeeded
            interactive: true
        }

        ColumnLayout {
            id: body
            width: Math.min(820, aboutScroll.width - 64)
            x: Math.max(32, (aboutScroll.width - width) / 2)
            y: 36
            spacing: 22

            Components.AppCard {
                Layout.fillWidth: true
                padding: 26
                spacing: 0
                cardColor: App.Theme.background

                GridLayout {
                    Layout.fillWidth: true
                    columns: width < 650 ? 1 : 2
                    columnSpacing: 30
                    rowSpacing: 22

                    Components.BauhausArtwork {
                        Layout.fillWidth: parent.width < 650
                        Layout.preferredWidth: parent.width < 650 ? 360 : 260
                        Layout.preferredHeight: 230
                        Layout.alignment: Qt.AlignHCenter
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Text {
                            Layout.fillWidth: true
                            text: "São Francisco"
                            color: App.Theme.text
                            font.family: App.Theme.displayFont
                            font.pixelSize: 30
                            font.weight: Font.Medium
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Transcrição cuidadosa para áudio e vídeo de qualquer duração."
                            color: App.Theme.primary
                            font.family: App.Theme.displayFont
                            font.pixelSize: 18
                            font.weight: Font.Medium
                            lineHeight: 1.25
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "O aplicativo prepara a mídia com FFmpeg, divide conteúdos longos em partes seguras e reúne o resultado em documentos e legendas."
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: 14
                            lineHeight: 1.4
                            wrapMode: Text.WordWrap
                        }
                        Components.StatusPill {
                            text: "Versão " + String(root.backendValue(
                                                       "appVersion",
                                                       Qt.application.version
                                                       || "1.0.0"))
                            tone: "accent"
                        }
                    }
                }
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                spacing: 12

                Text {
                    Layout.fillWidth: true
                    text: "Criado por Pedro Duarte Blanco"
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 20
                    font.weight: Font.Medium
                    wrapMode: Text.WordWrap
                }
                Text {
                    Layout.fillWidth: true
                    text: "Conheça outros projetos, livros e trabalhos no site do autor."
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    lineHeight: 1.4
                    wrapMode: Text.WordWrap
                }
                Components.AppButton {
                    Layout.alignment: Qt.AlignLeft
                    text: "Visitar pedblan.github.io"
                    variant: "secondary"
                    onClicked: root.callBackend(
                                   "openExternalUrl",
                                   ["https://pedblan.github.io"])
                }
            }

            Components.AppCard {
                Layout.fillWidth: true
                padding: 22
                spacing: 10

                Text {
                    Layout.fillWidth: true
                    text: "Software e licenças"
                    color: App.Theme.text
                    font.family: App.Theme.displayFont
                    font.pixelSize: 19
                    font.weight: Font.Medium
                }
                Text {
                    Layout.fillWidth: true
                    text: "São Francisco é software de código aberto sob licença MIT. O aplicativo usa Qt 6/PySide6, FFmpeg e bibliotecas de terceiros sob suas respectivas licenças."
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    lineHeight: 1.42
                    wrapMode: Text.WordWrap
                }
                Text {
                    Layout.fillWidth: true
                    text: "Jost e Source Sans 3 acompanham a identidade visual sob a SIL Open Font License."
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    lineHeight: 1.42
                    wrapMode: Text.WordWrap
                }
                Components.AppButton {
                    text: "Ver avisos de terceiros"
                    variant: "ghost"
                    compact: true
                    Layout.alignment: Qt.AlignLeft
                    onClicked: root.callBackend("openThirdPartyNotices", [])
                }
            }

            Item {
                objectName: "aboutEndMarker"
                Layout.fillWidth: true
                Layout.preferredHeight: 1
            }
        }
    }
}
