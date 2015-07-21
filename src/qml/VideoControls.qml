import QtQuick 2.3
import QtQuick.Controls 1.2

Item{
    id: controls
    width: 120
    height: 230

    property int sliderValue: slider.value

    signal playClicked()
    signal pauseClicked()
    signal forwardClicked(int step)
    signal backwardClicked(int step)
    signal startClicked()
    signal endClicked()

    Rectangle{
        anchors.fill: parent

        enabled: parent.enabled
        color: "#4c4c4c"
        radius: 9
        border.width: 3
        border.color: "#7d7d7d"

        Rectangle{
            width: parent.width - 2*10
            anchors.left: parent.left
            anchors.leftMargin: 10

            height: parent.height - 2*10
            anchors.top: parent.top
            anchors.topMargin: 10

            color: "transparent"

            enabled: parent.enabled

            LabeledSlider{
                id: slider
                x: grid.x
                anchors.top: grid.bottom
                anchors.topMargin: 10
                anchors.bottom: parent.bottom
                width: parent.width
                height: parent.height * 0.3
            }
            Grid {
                id: grid
                width: parent.width
                height: parent.height * 0.7

                enabled: parent.enabled

                columns: 2
                rows: 3
                spacing: 3
                CustomButton {
                    iconSource: "../../resources/icons/play.png"
                    pressedSource: "../../resources/icons/play_pressed.png"
                    enabled: parent.enabled
                    tooltip: "Starts the video playback"
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.playClicked() }
                }
                CustomButton {
                    iconSource: "../../resources/icons/pause.png"
                    pressedSource: "../../resources/icons/pause_pressed.png"
                    tooltip: "Pause playback"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.pauseClicked() }
                }
                CustomButton {
                    iconSource: "../../resources/icons/backward.png"
                    pressedSource: "../../resources/icons/backward_pressed.png"
                    tooltip: "Fast rewind"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.backwardClicked(slider.value) }
                }
                CustomButton {
                    iconSource: "../../resources/icons/forward.png"
                    pressedSource: "../../resources/icons/forward_pressed.png"
                    tooltip: "Fast forward"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.forwardClicked(slider.value) }
                }
                CustomButton {
                    iconSource: "../../resources/icons/jump_backward.png"
                    pressedSource: "../../resources/icons/jump_backward_pressed.png"
                    tooltip: "Go to start"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.startClicked() }
                }
                CustomButton {
                    iconSource: "../../resources/icons/jump_forward.png"
                    pressedSource: "../../resources/icons/jump_forward_pressed.png"
                    tooltip: "Go to end"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.endClicked() }
                }
            }
        }
    }
}
