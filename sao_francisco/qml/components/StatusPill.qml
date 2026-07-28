import QtQuick
import ".." as App

Rectangle {
    id: root

    property string text: ""
    property string tone: "neutral"

    implicitWidth: label.implicitWidth + 18
    implicitHeight: 25
    radius: 13
    color: {
        if (tone === "success")
            return App.Theme.successSoft
        if (tone === "warning")
            return App.Theme.warningSoft
        if (tone === "danger")
            return App.Theme.dangerSoft
        if (tone === "accent")
            return App.Theme.secondarySoft
        return App.Theme.surfaceMuted
    }

    Text {
        id: label
        anchors.centerIn: parent
        text: root.text
        color: {
            if (root.tone === "success")
                return App.Theme.success
            if (root.tone === "warning")
                return App.Theme.warning
            if (root.tone === "danger")
                return App.Theme.danger
            if (root.tone === "accent")
                return App.Theme.secondary
            return App.Theme.textMuted
        }
        font.family: App.Theme.uiFont
        font.pixelSize: 11
        font.weight: Font.DemiBold
    }
}
