import QtQuick 2.5
import QtQuick.Controls 1.4

import "../style"

Item {
    implicitHeight: 25
    implicitWidth: 110

    property alias label: btn.text
    property alias tooltip: btn.tooltip
    property alias text: textField.text
    property alias readOnly: textField.readOnly

    signal clicked

    Row {
        anchors.fill: parent
        spacing: 5
        Button{
            id: btn
            width: (parent.width -5) /2
            height: parent.height
            text: "Button"
            enabled: parent.enabled

            onClicked: { parent.parent.clicked() }
        }

        TextEdit {
            id: textField
            width: (parent.width -5) /2
            height: parent.height
            enabled: parent.enabled

            color: theme.text
            horizontalAlignment: Text.AlignHCenter
            readOnly: true
        }
    }
}
