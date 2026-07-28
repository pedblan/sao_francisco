import QtQuick
import ".." as App

Canvas {
    id: root

    property string name: ""
    property color iconColor: App.Theme.textMuted
    property int iconSize: 20

    implicitWidth: iconSize
    implicitHeight: iconSize
    width: iconSize
    height: iconSize
    Accessible.ignored: true

    onNameChanged: requestPaint()
    onIconColorChanged: requestPaint()
    onWidthChanged: requestPaint()
    onHeightChanged: requestPaint()

    onPaint: {
        const ctx = getContext("2d")
        ctx.clearRect(0, 0, width, height)
        ctx.save()
        const scale = Math.min(width, height) / 24
        ctx.scale(scale, scale)
        ctx.lineWidth = 1.8
        ctx.lineCap = "round"
        ctx.lineJoin = "round"
        ctx.strokeStyle = iconColor
        ctx.fillStyle = iconColor

        function line(x1, y1, x2, y2) {
            ctx.beginPath()
            ctx.moveTo(x1, y1)
            ctx.lineTo(x2, y2)
            ctx.stroke()
        }

        function circle(x, y, radius) {
            ctx.beginPath()
            ctx.arc(x, y, radius, 0, Math.PI * 2)
            ctx.stroke()
        }

        if (name === "transcribe" || name === "microphone") {
            ctx.beginPath()
            ctx.moveTo(12, 2.5)
            ctx.bezierCurveTo(9.8, 2.5, 8.5, 3.8, 8.5, 6)
            ctx.lineTo(8.5, 11)
            ctx.bezierCurveTo(8.5, 13.2, 9.8, 14.5, 12, 14.5)
            ctx.bezierCurveTo(14.2, 14.5, 15.5, 13.2, 15.5, 11)
            ctx.lineTo(15.5, 6)
            ctx.bezierCurveTo(15.5, 3.8, 14.2, 2.5, 12, 2.5)
            ctx.closePath()
            ctx.stroke()
            ctx.beginPath()
            ctx.arc(12, 11, 6.5, 0, Math.PI)
            ctx.stroke()
            line(12, 17.5, 12, 21)
            line(8.5, 21, 15.5, 21)
        } else if (name === "history") {
            circle(12, 12, 8.5)
            line(12, 7, 12, 12)
            line(12, 12, 16, 14)
            line(5.2, 5.5, 5.2, 9)
            line(5.2, 5.5, 8.5, 5.5)
        } else if (name === "settings") {
            circle(12, 12, 3.2)
            circle(12, 12, 7.2)
            for (let i = 0; i < 8; i++) {
                const a = i * Math.PI / 4
                line(12 + Math.cos(a) * 7.2, 12 + Math.sin(a) * 7.2,
                     12 + Math.cos(a) * 9.5, 12 + Math.sin(a) * 9.5)
            }
        } else if (name === "help") {
            circle(12, 12, 9)
            ctx.beginPath()
            ctx.moveTo(8.9,9.2)
            ctx.bezierCurveTo(9.2,6.8, 10.7,5.8, 12.5,5.8)
            ctx.bezierCurveTo(14.7,5.8, 16.1,7.1, 16.1,9)
            ctx.bezierCurveTo(16.1,10.6, 15.1,11.4, 13.7,12.3)
            ctx.bezierCurveTo(12.6,13, 12.1,13.7, 12.1,14.8)
            ctx.stroke()
            ctx.beginPath()
            ctx.arc(12.1, 18, 1, 0, Math.PI * 2)
            ctx.fill()
        } else if (name === "info") {
            circle(12, 12, 9)
            circle(12, 7.4, 0.8)
            line(12, 11, 12, 16.5)
        } else if (name === "collapse") {
            line(15, 5, 8, 12)
            line(8, 12, 15, 19)
        } else if (name === "expand") {
            line(9, 5, 16, 12)
            line(16, 12, 9, 19)
        } else if (name === "file") {
            ctx.beginPath()
            ctx.moveTo(6, 2.5)
            ctx.lineTo(14, 2.5)
            ctx.lineTo(19, 7.5)
            ctx.lineTo(19, 21.5)
            ctx.lineTo(6, 21.5)
            ctx.closePath()
            ctx.stroke()
            line(14, 2.5, 14, 8)
            line(14, 8, 19, 8)
            line(9, 13, 16, 13)
            line(9, 17, 16, 17)
        } else if (name === "link") {
            ctx.beginPath()
            ctx.arc(9, 12, 4.5, Math.PI * 0.35, Math.PI * 1.65)
            ctx.stroke()
            ctx.beginPath()
            ctx.arc(15, 12, 4.5, Math.PI * 1.35, Math.PI * 0.65)
            ctx.stroke()
            line(9.5, 12, 14.5, 12)
        } else if (name === "folder") {
            ctx.beginPath()
            ctx.moveTo(2.5, 7)
            ctx.lineTo(9, 7)
            ctx.lineTo(11, 9)
            ctx.lineTo(21.5, 9)
            ctx.lineTo(20, 20)
            ctx.lineTo(4, 20)
            ctx.closePath()
            ctx.stroke()
            ctx.beginPath()
            ctx.moveTo(3.5, 16)
            ctx.lineTo(4.2, 4)
            ctx.lineTo(10, 4)
            ctx.lineTo(12, 7)
            ctx.stroke()
        } else if (name === "check") {
            line(4.5, 12.5, 9.5, 17.5)
            line(9.5, 17.5, 19.5, 6.5)
        } else if (name === "play") {
            ctx.beginPath()
            ctx.moveTo(8, 5)
            ctx.lineTo(19, 12)
            ctx.lineTo(8, 19)
            ctx.closePath()
            ctx.fill()
        } else if (name === "download") {
            line(12, 3, 12, 15)
            line(7, 10, 12, 15)
            line(17, 10, 12, 15)
            ctx.beginPath()
            ctx.moveTo(4, 17)
            ctx.lineTo(4, 21)
            ctx.lineTo(20, 21)
            ctx.lineTo(20, 17)
            ctx.stroke()
        } else if (name === "key") {
            circle(8.5, 11, 4)
            line(12.5, 11, 21, 11)
            line(17, 11, 17, 14)
            line(20, 11, 20, 14)
        } else if (name === "external") {
            ctx.strokeRect(4, 6, 14, 14)
            line(11, 13, 21, 3)
            line(14, 3, 21, 3)
            line(21, 3, 21, 10)
        } else if (name === "close") {
            line(5, 5, 19, 19)
            line(19, 5, 5, 19)
        } else if (name === "search") {
            circle(10.5, 10.5, 6.5)
            line(15.5, 15.5, 21, 21)
        } else {
            circle(12, 12, 8)
        }
        ctx.restore()
    }
}
