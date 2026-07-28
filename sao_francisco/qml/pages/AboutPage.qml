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
                            text: "Transforma gravações e vídeos longos em textos e legendas, com acompanhamento do início ao fim."
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
                padding: 24
                spacing: 0
                cardColor: App.Theme.surface

                GridLayout {
                    Layout.fillWidth: true
                    columns: width < 650 ? 1 : 2
                    columnSpacing: 24
                    rowSpacing: 20

                    Components.BauhausArtwork {
                        Layout.fillWidth: parent.width < 650
                        Layout.preferredWidth: parent.width < 650 ? 360 : 210
                        Layout.preferredHeight: 178
                        Layout.alignment: Qt.AlignHCenter
                        source: Qt.resolvedUrl(
                                    "../../assets/branding/sao-francisco-coffee-bauhaus.png")
                        accessibleName: "Ilustração Bauhaus de uma xícara de café com gesto de regência"
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 10

                        Components.StatusPill {
                            text: "SAIBA MAIS"
                            tone: "warning"
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "Conheça os livros e outros trabalhos"
                            color: App.Theme.text
                            font.family: App.Theme.displayFont
                            font.pixelSize: 24
                            font.weight: Font.Bold
                            wrapMode: Text.WordWrap
                        }
                        Text {
                            Layout.fillWidth: true
                            text: "São Francisco é software livre! Se você quiser valorizar o trabalho, leia os livros e conheça os outros projetos na minha página de autor."
                            color: App.Theme.textMuted
                            font.family: App.Theme.uiFont
                            font.pixelSize: App.Theme.bodySize
                            wrapMode: Text.WordWrap
                            lineHeight: 1.3
                        }
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.topMargin: 6
                            spacing: 18

                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 3

                                Text {
                                    text: "Autor e programador"
                                    color: App.Theme.textSoft
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: App.Theme.captionSize
                                    font.weight: Font.Medium
                                }
                                Text {
                                    text: "Pedro Duarte Blanco"
                                    color: App.Theme.text
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: 16
                                    font.weight: Font.Bold
                                }
                                Text {
                                    id: authorSite

                                    text: "pedblan.github.io"
                                    color: App.Theme.secondary
                                    font.family: App.Theme.uiFont
                                    font.pixelSize: App.Theme.bodySize
                                    font.weight: Font.DemiBold
                                    activeFocusOnTab: true
                                    Accessible.name: "Abrir pedblan.github.io"
                                    Accessible.role: Accessible.Link
                                    Keys.onReturnPressed: root.callBackend(
                                                              "openExternalUrl",
                                                              ["https://pedblan.github.io"])
                                    Keys.onEnterPressed: root.callBackend(
                                                             "openExternalUrl",
                                                             ["https://pedblan.github.io"])

                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: root.callBackend(
                                                       "openExternalUrl",
                                                       ["https://pedblan.github.io"])
                                    }
                                }
                            }
                            Components.AppButton {
                                text: "Clique para conhecer"
                                variant: "primary"
                                onClicked: root.callBackend(
                                               "openExternalUrl",
                                               ["https://pedblan.github.io"])
                            }
                        }
                    }
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
                    text: "São Francisco é software de código aberto sob licença MIT. Componentes e fontes de terceiros conservam suas próprias licenças."
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
                    onClicked: noticesDialog.open()
                }
            }

            Item {
                objectName: "aboutEndMarker"
                Layout.fillWidth: true
                Layout.preferredHeight: 1
            }
        }
    }

    Popup {
        id: noticesDialog

        objectName: "thirdPartyNoticesPopup"
        parent: Overlay.overlay
        x: parent ? Math.round((parent.width - width) / 2) : 0
        y: parent ? Math.round((parent.height - height) / 2) : 0
        width: parent ? Math.min(760, parent.width - 64) : 760
        height: parent ? Math.min(580, parent.height - 64) : 580
        padding: 0
        modal: true
        focus: true
        closePolicy: Popup.CloseOnEscape
        onOpened: noticeScroll.forceActiveFocus()

        background: Rectangle {
            radius: App.Theme.radiusLarge
            color: App.Theme.surfaceRaised
            border.width: 1
            border.color: App.Theme.borderStrong
        }

        contentItem: ColumnLayout {
            spacing: 0
            Accessible.name: "Avisos de terceiros"

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 64
                color: App.Theme.background
                radius: App.Theme.radiusLarge

                Rectangle {
                    anchors.left: parent.left
                    anchors.right: parent.right
                    anchors.bottom: parent.bottom
                    height: App.Theme.radiusLarge
                    color: parent.color
                }

                RowLayout {
                    anchors.fill: parent
                    anchors.leftMargin: 22
                    anchors.rightMargin: 14

                    Text {
                        Layout.fillWidth: true
                        text: "Avisos de terceiros"
                        color: App.Theme.text
                        font.family: App.Theme.displayFont
                        font.pixelSize: 21
                        font.weight: Font.Medium
                    }
                    Button {
                        id: noticesCloseIcon

                        objectName: "thirdPartyNoticesCloseIcon"
                        implicitWidth: 40
                        implicitHeight: 40
                        Accessible.name: "Fechar avisos de terceiros"
                        onClicked: noticesDialog.close()
                        contentItem: Components.Icon {
                            anchors.centerIn: parent
                            name: "close"
                            iconSize: 18
                            iconColor: App.Theme.textMuted
                        }
                        background: Rectangle {
                            radius: App.Theme.radius
                            color: noticesCloseIcon.hovered
                                   ? App.Theme.surfaceMuted
                                   : "transparent"
                            border.width: noticesCloseIcon.activeFocus ? 2 : 0
                            border.color: App.Theme.focus
                        }
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: App.Theme.border
            }

            Flickable {
                id: noticeScroll

                objectName: "thirdPartyNoticesScroll"
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                contentWidth: width
                contentHeight: noticesText.implicitHeight + 44
                boundsBehavior: Flickable.StopAtBounds
                activeFocusOnTab: true
                Accessible.name: "Conteúdo dos avisos de terceiros"
                Keys.onPressed: event => root.handleScrollKey(event, noticeScroll)

                Text {
                    id: noticesText

                    x: 22
                    y: 20
                    width: noticeScroll.width - 44
                    text: String(root.backendValue(
                                     "thirdPartyNoticesMarkdown",
                                     "# Avisos de terceiros\n\nConteúdo indisponível."))
                    textFormat: Text.MarkdownText
                    color: App.Theme.text
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                    lineHeight: 1.35
                    wrapMode: Text.WordWrap
                    linkColor: App.Theme.secondary
                    onLinkActivated: link => root.callBackend(
                                         "openExternalUrl", [link])
                }

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                    interactive: true
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 1
                color: App.Theme.border
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.margins: 14

                Item {
                    Layout.fillWidth: true
                }
                Components.AppButton {
                    objectName: "thirdPartyNoticesCloseButton"
                    text: "Fechar"
                    variant: "secondary"
                    onClicked: noticesDialog.close()
                }
            }
        }
    }
}
