import QtQuick 2.5
import QtQuick.Controls 1.4

import "../style"

Item {
    width: 145
    height: 30
    property alias lbl: labelObj.text
    property alias text: textField.text
    property alias help: tooltip.tooltip

    Label {
        id: labelObj
        height: parent.height
        color: theme.text
        text: "Label"
        anchors.left: textField.right
        anchors.leftMargin: 10
    }
    TextField {
        id: textField
        width: 50
        height: parent.height
        readOnly: true
        placeholderText: "Field"
        textColor: theme.text
    }
    ToolTip{
        id: tooltip
        tooltip: "No help yet"
        anchors.fill: parent
    }
}
