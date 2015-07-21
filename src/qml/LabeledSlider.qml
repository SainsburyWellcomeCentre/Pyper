import QtQuick 2.3
import QtQuick.Controls 1.2

Item{
    width: 80
    height: 40
    property alias value: slider.value
    property alias text: sliderLabel.text

    Label {
        id: sliderLabel
        horizontalAlignment: Text.AlignHCenter
        anchors.horizontalCenter: parent.horizontalCenter
        width: parent.width
        height: parent.height/2 - 5

        text: "Scroll speed"
        font.pointSize: 10
        wrapMode: Text.WordWrap
    }
    Slider {
        id: slider
        width: parent.width
        height: parent.height/2 - 5
        anchors.top: sliderLabel.bottom
        anchors.topMargin: 10

        tickmarksEnabled: true
        value: 1
        stepSize: 1
        minimumValue: 1
        maximumValue: 100
    }
}
