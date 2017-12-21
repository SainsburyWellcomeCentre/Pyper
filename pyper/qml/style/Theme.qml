pragma Singleton
import QtQuick 2.5

QtObject {
    readonly property color text: "white"
    readonly property color background: "#3B3B3B"
    readonly property color darkBackground: "#222222"
    readonly property color frameBorder: "#7d7d7d"
    readonly property color frameBackground: "#4c4c4c"
    readonly property color roiDefault: 'Yellow'

    readonly property color textBackground: "#666666"

    readonly property color terminalSelection: "steelblue"
    readonly property color terminalSelectedText: "cyan"

    readonly property color codeBackground: "#202020"  // Same as code backgound from pygments 'native' template
    readonly property color codeTextColor: "white"

    readonly property color spinBoxBackground: 'Gray'

    readonly property color errorScreenFrameBackground: "pink"
    readonly property color errorScreenFrameBorder: "red"
    readonly property color infoScreenFrameBackground: "lightgreen"
    readonly property color infoScreenFrameBorder: "green"
    readonly property color splashScreenFrameBackground: "steelblue"
    readonly property color splashScreenFrameBorder: "#49afff"

    readonly property color labeledButtonGradientStart: "white"
    readonly property color labeledButtonGradientEnd: "black"

    readonly property color toolButtonText: "white"
    readonly property color toolButtonNegativeText: "Black"
    readonly property color toolButtonHoveredBackground: "#999999"
    readonly property color toolButtonActiveBackground: "#DBDBDB"

    readonly property string defaultFont: "Verdana"
}
