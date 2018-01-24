import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3

import "../style"

Item {
    id: root
    height: 25
    width: label.width + spinBox.width

    property alias label: label.text
    property alias tooltip: label.help

    property alias value: spinBox.text

    Row {
        anchors.fill: parent
        spacing: 5

        LabelWTooltip {
            id: label
            width: contentWidth + 5
            height: parent.height
            text: "Label"
        }
        Label {
            id: spinBox
            width: contentWidth + 5
            height: parent.height
            text: "0"
            color: theme.text
        }
    }
}
