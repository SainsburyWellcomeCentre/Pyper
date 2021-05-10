import QtQuick 2.0
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3

import "../style"

SpinBox {
    value: 0
    minimumValue: 0
    maximumValue: 255
    stepSize: 1
    style: SpinBoxStyle {
        background: Rectangle {
            anchors.fill: parent
            implicitWidth: 80
            implicitHeight: 20
            color: Theme.spinBoxBackground
            radius: 2
        }
        textColor: Theme.text
    }
}
