import QtQuick
import QtQuick.Layouts
import ".." as App

ColumnLayout {
    id: root

    property string title: ""
    property string description: ""

    spacing: 7

    Text {
        Layout.fillWidth: true
        text: root.title
        color: App.Theme.text
        font.family: App.Theme.displayFont
        font.pixelSize: App.Theme.titleSize
        font.weight: Font.Medium
        wrapMode: Text.WordWrap
    }

    Text {
        visible: root.description.length > 0
        Layout.fillWidth: true
        text: root.description
        color: App.Theme.textMuted
        font.family: App.Theme.uiFont
        font.pixelSize: 15
        lineHeight: 1.35
        wrapMode: Text.WordWrap
    }
}
