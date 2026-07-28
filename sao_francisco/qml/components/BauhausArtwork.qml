import QtQuick
import ".." as App

Rectangle {
    id: root

    property url source: Qt.resolvedUrl(
                             "../../assets/branding/sao-francisco-bauhaus.png")
    property string accessibleName: "Ilustração Bauhaus de São Francisco"

    implicitWidth: 320
    implicitHeight: 220
    radius: App.Theme.radiusLarge
    color: App.Theme.background
    clip: true
    Accessible.name: accessibleName
    Accessible.role: Accessible.Graphic

    Image {
        anchors.fill: parent
        source: root.source
        fillMode: Image.PreserveAspectFit
        asynchronous: true
        cache: true
        mipmap: true
    }
}
