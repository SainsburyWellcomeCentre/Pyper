import QtQuick 2.3
import QtQuick.Controls 1.2

Item {
    implicitHeight: 25
    implicitWidth: 110

    property alias label: label.text
    property alias tooltip: label.help
    property alias checked: checkBox.checked
    property alias fontSize: label.fontSize

    signal clicked

    Row {
        anchors.fill: parent
        spacing: 5

        LabelWTooltip{
            id: label
            width: (parent.width -5) /2
            height: parent.height
            text: "Label"
        }
        CheckBox{
            id: checkBox
            onClicked: parent.parent.clicked()
        }
    }
}
