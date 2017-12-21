import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Private 1.0 // For Tooltip

import "../basic_types"
import "../style"


Item {
    id: root

    property alias source: previewImage.source
    property alias value: progressBar.value
    property alias maximumValue: progressBar.maximumValue
    property alias img: previewImage

    property alias imgWidth: previewImage.width
    property alias imgHeight: previewImage.height

    property alias progressBarWidth: progressBar.width

    signal progressPressed(real xPosition, real yPosition)
    signal progressReleased(real xPosition, real yPosition)
    signal progressClicked(int frameId)
    signal progressWheel(int angleDelta)

    property bool showProgressBar: true
    onShowProgressBarChanged: {
        if (showProgressBar) {
            pBar.height = 20;
        } else {
            pBar.height = 0;
        }
    }

    function reload(){
        previewImage.reload();
    }

    signal sizeChanged
    onWidthChanged: { sizeChanged(); }
    onHeightChanged: { sizeChanged(); }

    Column {
        anchors.fill: parent
        spacing: 5
        Image {
            id: previewImage
            width: parent.width
            height: parent.height - (progressBar.height + progressBar.anchors.topMargin)

            source: "image://provider/img"
            sourceSize.width: width
            sourceSize.height: height
            cache: false

            function reload() {
                var oldSource = source;
                source = "";
                source = oldSource;
            }
        }
        Row {
            id: pBar
            height: 20
            anchors.left: previewImage.left
            anchors.right: previewImage.right
            ProgressBar {
                id: progressBar

                width: previewImage.width - pBarLabel.width
                minimumValue: 0

                enabled: root.enabled

                signal pressed(real xPosition, real yPosition)
                signal released(real xPosition, real yPosition)
                signal clicked(real xPosition, real yPosition)
                signal positionChanged(real xPosition, real yPosition)
                signal exited()
                signal wheel(point angleDelta)

                onPressed: root.progressPressed(behavior.mouseX, behavior.mouseY)
                onReleased: root.progressReleased(behavior.mouseX, behavior.mouseY)
                onClicked: {
                    var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
                    root.progressClicked(hoveredFrame)
                }
                onPositionChanged: {
                    var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
                    Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), hoveredFrame);
                }
                onExited: {
                    Tooltip.hideText();
                }
                onWheel: {
                    root.progressWheel(angleDelta.y)
                }

                MouseArea{
                    id: behavior
                    anchors.fill: parent
                    hoverEnabled: true
                    enabled: parent.enabled

                    onPressed: parent.pressed(mouse.x, mouse.y)
                    onReleased: parent.released(mouse.x, mouse.y)
                    onClicked: parent.clicked(mouse.x, mouse.y)
                    onPositionChanged: parent.positionChanged(mouse.x, mouse.y)
                    onExited: parent.exited()
                    onWheel: parent.wheel(wheel.angleDelta)
                }
            }
            Label {
                id: pBarLabel
                width: contentWidth + 10
                anchors.top: parent.top
                anchors.bottom: parent.bottom
                text: progressBar.value
                font.family: theme.defaultFont
                color: theme.text
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                font.pointSize: 10
            }
        }
    }
}
