import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.2

Item {
    id: root
    height: 25
    width: 130

    property alias label: label.text
    property alias tooltip: label.help

    property alias value: spinBox.value
    property alias minimumValue: spinBox.minimumValue
    property alias maximumValue: spinBox.maximumValue
    property alias stepSize: spinBox.stepSize
    property alias suffix: spinBox.suffix

    signal edited()

    Row {
        anchors.fill: parent
        spacing: width - (label.width + spinBox.width)

        LabelWTooltip {
            id: label
//            width: (parent.width -5) /2
            width: contentWidth + 5
            height: parent.height
            text: "Label"
        }
        SpinBox {
            id: spinBox
            minimumValue: -1
            maximumValue: 1000000
            stepSize: 1
            value: 0
            style: SpinBoxStyle {
                background: Rectangle {
                    anchors.fill: parent
                    implicitWidth: 80
                    implicitHeight: 20
                    color: 'Gray'
                    radius: 2
                }
                textColor: 'white'
            }
            onEditingFinished: {
                root.edited();
            }
        }
    }
}
