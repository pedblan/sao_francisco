import QtQuick
import QtQuick.Controls
import ".." as App

Button {
    id: control

    property string variant: "primary"
    property bool compact: false

    implicitHeight: compact ? 32 : App.Theme.controlHeight
    implicitWidth: Math.max(compact ? 76 : 108, contentItem.implicitWidth + leftPadding + rightPadding)
    leftPadding: compact ? 12 : 16
    rightPadding: compact ? 12 : 16
    topPadding: 0
    bottomPadding: 0
    hoverEnabled: true
    font.family: App.Theme.uiFont
    font.pixelSize: App.Theme.bodySize
    font.weight: Font.DemiBold
    Accessible.name: text

    readonly property color normalBackground: {
        if (variant === "secondary")
            return App.Theme.surface
        if (variant === "ghost")
            return "transparent"
        if (variant === "danger")
            return App.Theme.danger
        return App.Theme.primary
    }

    readonly property color hoverBackground: {
        if (variant === "secondary" || variant === "ghost")
            return App.Theme.surfaceMuted
        if (variant === "danger")
            return "#84372F"
        return App.Theme.primaryHover
    }

    readonly property color foreground: {
        if (variant === "secondary" || variant === "ghost")
            return App.Theme.text
        return "#FFFFFF"
    }

    contentItem: Text {
        text: control.text
        color: control.enabled ? control.foreground : App.Theme.textSoft
        font: control.font
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    background: Rectangle {
        radius: App.Theme.radius
        color: !control.enabled
               ? App.Theme.surfaceMuted
               : control.down
                 ? (control.variant === "primary"
                    ? App.Theme.primaryPressed
                    : control.hoverBackground)
                 : control.hovered
                   ? control.hoverBackground
                   : control.normalBackground
        border.width: control.activeFocus ? 2
                     : (control.variant === "secondary" ? 1 : 0)
        border.color: control.activeFocus
                      ? App.Theme.focus
                      : App.Theme.borderStrong

        Behavior on color {
            ColorAnimation { duration: 130 }
        }
    }
}
