import QtQuick
import QtQuick.Layouts
import ".." as App

Rectangle {
    id: root

    default property alias content: body.data
    property int padding: 20
    property int spacing: 12
    property color cardColor: App.Theme.surface
    property color strokeColor: App.Theme.border

    implicitWidth: 320
    implicitHeight: body.implicitHeight + padding * 2
    radius: App.Theme.radiusLarge
    color: cardColor
    border.width: 1
    border.color: strokeColor

    ColumnLayout {
        id: body
        anchors.fill: parent
        anchors.margins: root.padding
        spacing: root.spacing
    }
}
