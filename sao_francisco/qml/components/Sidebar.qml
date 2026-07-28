pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import ".." as App

Rectangle {
    id: root

    property bool collapsed: false
    property string activeRoute: "transcribe"
    property string versionLabel: ""
    signal navigate(string route)
    signal toggleCollapse()

    width: collapsed ? 64 : 224
    color: "#E9DFCF"
    border.width: 0

    Behavior on width {
        NumberAnimation { duration: 150; easing.type: Easing.OutCubic }
    }

    readonly property var workItems: [
        { "label": "Transcrever", "route": "transcribe", "icon": "transcribe" },
        { "label": "Histórico", "route": "history", "icon": "history" }
    ]
    readonly property var supportItems: [
        { "label": "Configurações", "route": "settings", "icon": "settings" },
        { "label": "Ajuda", "route": "help", "icon": "help" },
        { "label": "Sobre", "route": "about", "icon": "info" }
    ]

    component NavigationButton: Button {
        id: navigationButton

        required property var entry
        readonly property bool selected: root.activeRoute === entry.route

        Layout.fillWidth: true
        implicitHeight: 40
        hoverEnabled: true
        padding: 0
        activeFocusOnTab: true
        Accessible.name: entry.label
        Accessible.description: selected ? "Página atual" : "Abrir " + entry.label
        ToolTip.visible: root.collapsed && hovered
        ToolTip.text: entry.label
        onClicked: root.navigate(entry.route)

        contentItem: RowLayout {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.leftMargin: 11
            anchors.rightMargin: 11
            spacing: 11

            Icon {
                Layout.preferredWidth: 19
                Layout.preferredHeight: 19
                name: navigationButton.entry.icon
                iconSize: 19
                iconColor: navigationButton.selected
                           ? App.Theme.primary
                           : App.Theme.textMuted
            }

            Text {
                visible: !root.collapsed
                Layout.fillWidth: true
                text: navigationButton.entry.label
                color: navigationButton.selected
                       ? App.Theme.text
                       : App.Theme.textMuted
                font.family: App.Theme.uiFont
                font.pixelSize: App.Theme.bodySize
                font.weight: navigationButton.selected
                             ? Font.DemiBold
                             : Font.Medium
                elide: Text.ElideRight
            }
        }

        background: Rectangle {
            radius: App.Theme.radius
            color: navigationButton.selected
                   ? App.Theme.surface
                   : navigationButton.hovered
                     ? "#DFD3C1"
                     : "transparent"
            border.width: navigationButton.activeFocus ? 2
                         : (navigationButton.selected ? 1 : 0)
            border.color: navigationButton.activeFocus
                          ? App.Theme.focus
                          : App.Theme.border
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 4

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 58

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 6
                anchors.rightMargin: 4
                spacing: 10

                Image {
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    source: Qt.resolvedUrl("../../assets/branding/sao-francisco-bauhaus.svg")
                    fillMode: Image.PreserveAspectFit
                    mipmap: true
                    Accessible.name: "Símbolo Bauhaus de São Francisco"
                    Accessible.role: Accessible.Graphic
                }

                ColumnLayout {
                    visible: !root.collapsed
                    Layout.fillWidth: true
                    spacing: -1

                    Text {
                        Layout.fillWidth: true
                        text: "São Francisco"
                        color: App.Theme.text
                        font.family: App.Theme.displayFont
                        font.pixelSize: 18
                        font.weight: Font.Medium
                        elide: Text.ElideRight
                    }
                    Text {
                        Layout.fillWidth: true
                        text: "Escutar. Transcrever."
                        color: App.Theme.textMuted
                        font.family: App.Theme.uiFont
                        font.pixelSize: 10
                        elide: Text.ElideRight
                    }
                }
            }
        }

        Text {
            visible: !root.collapsed
            text: "TRABALHO"
            color: App.Theme.textSoft
            font.family: App.Theme.uiFont
            font.pixelSize: 9
            font.weight: Font.DemiBold
            font.letterSpacing: 1.0
            Layout.leftMargin: 10
            Layout.topMargin: 8
            Layout.bottomMargin: 4
        }

        Repeater {
            model: root.workItems
            delegate: NavigationButton {
                required property var modelData
                entry: modelData
            }
        }

        Item { Layout.fillHeight: true }

        Repeater {
            model: root.supportItems
            delegate: NavigationButton {
                required property var modelData
                entry: modelData
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.topMargin: 8
            implicitHeight: 1
            color: App.Theme.border
        }

        Button {
            id: collapseButton

            Layout.fillWidth: true
            implicitHeight: 40
            hoverEnabled: true
            padding: 0
            Accessible.name: root.collapsed
                             ? "Mostrar barra lateral"
                             : "Recolher barra lateral"
            ToolTip.visible: root.collapsed && hovered
            ToolTip.text: Accessible.name
            onClicked: root.toggleCollapse()

            contentItem: RowLayout {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.leftMargin: 11
                spacing: 11

                Icon {
                    name: root.collapsed ? "expand" : "collapse"
                    iconSize: 19
                    iconColor: App.Theme.textMuted
                }

                Text {
                    visible: !root.collapsed
                    text: "Recolher"
                    color: App.Theme.textMuted
                    font.family: App.Theme.uiFont
                    font.pixelSize: App.Theme.bodySize
                }
            }

            background: Rectangle {
                radius: App.Theme.radius
                color: collapseButton.hovered ? "#DFD3C1" : "transparent"
                border.width: collapseButton.activeFocus ? 2 : 0
                border.color: App.Theme.focus
            }
        }

        Text {
            visible: !root.collapsed && root.versionLabel.length > 0
            Layout.alignment: Qt.AlignHCenter
            Layout.bottomMargin: 2
            text: root.versionLabel
            color: App.Theme.textSoft
            font.family: App.Theme.uiFont
            font.pixelSize: 10
        }
    }
}
