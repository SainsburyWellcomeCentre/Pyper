import QtQuick 2.5
import QtQuick.Controls 1.4

import "../style"

Item{
    id: root

    width: 80
    height: 40
    property alias value: slider.value
    property alias text: sliderLabel.text
    property bool showValue: true

    onShowValueChanged: {
        if (showValue) {
            valueLabel.width = valueLabel.contentWidth;
        } else {
            valueLabel.width = 0;
        }

        valueLabel.visible = showValue;
    }

    CustomColumn {
        anchors.fill: parent

        spacing: 5
        Label {
            id: sliderLabel

            height: contentHeight

            anchors.horizontalCenter: parent.horizontalCenter

            text: "Scroll speed"
            horizontalAlignment: Text.AlignHCenter
            font.pointSize: 10
            color: Theme.text
            wrapMode: Text.WordWrap
        }
        Row {
            height: sliderLabel.height

            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width

            spacing: 5
            Slider {
                id: slider

                width: parent.width - valueLabel.width - parent.spacing

                anchors.top: parent.top
                anchors.bottom: parent.bottom

                tickmarksEnabled: true
                value: 1
                stepSize: 1
                minimumValue: 1
                maximumValue: 100
            }
            Label {
                id: valueLabel
                anchors.top: parent.top
                anchors.bottom: parent.bottom

                text: slider.value
                width: contentWidth

                horizontalAlignment: Text.AlignHCenter
                font.pointSize: 10
                color: Theme.text
            }
        }
    }
}
