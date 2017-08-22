import QtQuick 2.3
import QtQuick.Controls 1.2

import "../basic_types"
import "../style"

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
        color: theme.frameBackground
        radius: 9
        border.width: 3
        border.color: theme.frameBorder

        Column{
            width: parent.width - 2*10
            height: parent.height - 2*10

            anchors.margins: 10
            anchors.left: parent.left
            anchors.top: parent.top

            enabled: parent.enabled

            spacing: 10

            Grid {
                id: grid
                width: parent.width
                height: parent.height * 0.7

                anchors.left: parent.left
                anchors.right: parent.right

                enabled: parent.enabled

                columns: 2
                rows: 3
                spacing: 3
                CustomButton {
                    iconSource: "../../../resources/icons/play.png"
                    pressedSource: "../../../resources/icons/play_pressed.png"
                    enabled: parent.enabled
                    tooltip: "Starts the video playback"
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.playClicked() }
                }
                CustomButton {
                    iconSource: "../../../resources/icons/pause.png"
                    pressedSource: "../../../resources/icons/pause_pressed.png"
                    tooltip: "Pause playback"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.pauseClicked() }
                }
                CustomButton {
                    iconSource: "../../../resources/icons/backward.png"
                    pressedSource: "../../../resources/icons/backward_pressed.png"
                    tooltip: "Fast rewind"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.backwardClicked(slider.value) }
                }
                CustomButton {
                    iconSource: "../../../resources/icons/forward.png"
                    pressedSource: "../../../resources/icons/forward_pressed.png"
                    tooltip: "Fast forward"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.forwardClicked(slider.value) }
                }
                CustomButton {
                    iconSource: "../../../resources/icons/jump_backward.png"
                    pressedSource: "../../../resources/icons/jump_backward_pressed.png"
                    tooltip: "Go to start"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.startClicked() }
                }
                CustomButton {
                    iconSource: "../../../resources/icons/jump_forward.png"
                    pressedSource: "../../../resources/icons/jump_forward_pressed.png"
                    tooltip: "Go to end"
                    enabled: parent.enabled
                    width: parent.width/2 - parent.spacing/2
                    height: parent.height/3
                    onClicked: { controls.endClicked() }
                }
            }
            LabeledSlider{
                id: slider
                height: parent.height * 0.3

                anchors.left: parent.left
                anchors.right: parent.right
            }
        }
    }
}
