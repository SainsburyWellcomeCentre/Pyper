import QtQuick 2.3
import QtQuick.Controls 1.2


Item {
    id: labelWTooltip
    width: 145
    height: 30
    property alias text: labelObj.text
    property alias help: tooltip.tooltip
    property alias fontSize: labelObj.font.pointSize

    Label {
        id: labelObj
        color: "white"
        text: "Label"
        anchors.fill: parent
        antialiasing: true
    }
    ToolTip{
        id: tooltip
        tooltip: "No help yet"
        anchors.fill: parent
    }
}

