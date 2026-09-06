pragma Singleton

import QtQuick

QtObject {
    readonly property string displayFont: "Jost"
    readonly property string uiFont: "Source Sans 3"

    // Terra Franciscana
    readonly property color background: "#F4EDDF"
    readonly property color surface: "#FFF9EF"
    readonly property color surfaceRaised: "#FFFCF6"
    readonly property color surfaceMuted: "#EDE3D3"
    readonly property color text: "#1B2520"
    readonly property color textMuted: "#526058"
    readonly property color textSoft: "#59645D"
    readonly property color border: "#D8C8B0"
    readonly property color borderStrong: "#BDA98D"
    readonly property color primary: "#3F684C"
    readonly property color primaryHover: "#34583F"
    readonly property color primaryPressed: "#2A4934"
    readonly property color primarySoft: "#DCE8DD"
    readonly property color secondary: "#8E4D31"
    readonly property color secondaryHover: "#783F28"
    readonly property color secondarySoft: "#F0DDD2"
    readonly property color accent: "#D09A3A"
    readonly property color accentSoft: "#F5E6BF"
    readonly property color success: "#3F684C"
    readonly property color successSoft: "#DCE8DD"
    readonly property color warning: "#825B16"
    readonly property color warningSoft: "#F5E6BF"
    readonly property color danger: "#9B4339"
    readonly property color dangerSoft: "#F2D9D3"
    readonly property color focus: "#6F9279"
    readonly property color shadow: "#241A100F"

    readonly property int radiusSmall: 6
    readonly property int radius: 8
    readonly property int radiusLarge: 12
    readonly property int controlHeight: 36
    readonly property int bodySize: 14
    readonly property int captionSize: 12
    readonly property int sectionSize: 17
    readonly property int titleSize: 28

    function routeTitle(route) {
        const titles = {
            "transcribe": qsTranslate("App", "Transcrever"),
            "history": qsTranslate("App", "Histórico"),
            "settings": qsTranslate("App", "Configurações"),
            "help": qsTranslate("App", "Ajuda"),
            "about": qsTranslate("App", "Sobre")
        }
        return titles[route] || "São Francisco"
    }
}
