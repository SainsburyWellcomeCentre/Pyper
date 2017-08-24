import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Private 1.0 // For Tooltip

import "../basic_types"


Item {
    property alias source: previewImage.source
    property alias value: progressBar.value
    property alias maximumValue: progressBar.maximumValue
    property alias img: previewImage

    property alias imgWidth: previewImage.width
    property alias imgHeight: previewImage.height

    signal progressPressed(real xPosition, real yPosition)
    signal progressReleased(real xPosition, real yPosition)
    signal progressClicked(int frameId)
    signal progressWheel(int angleDelta)

    function reload(){
        previewImage.reload();
    }

    Column {
        anchors.fill: parent
        spacing: 5
//        width: parent.width
//        height: parent.height
//        Layout.minimumWidth: 640
//        Layout.minimumHeight: 480
//        Layout.preferredWidth: 640
//        Layout.preferredHeight: 480
//        Layout.maximumWidth: 1280
//        Layout.maximumHeight: 1024
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
        ProgressBar {
            id: progressBar
            x: previewImage.x

            width: previewImage.width
            height: 20
            minimumValue: 0

            enabled: parent.parent.enabled

            signal pressed(real xPosition, real yPosition)
            signal released(real xPosition, real yPosition)
            signal clicked(real xPosition, real yPosition)
            signal positionChanged(real xPosition, real yPosition)
            signal exited()
            signal wheel(point angleDelta)

            onPressed: parent.parent.progressPressed(behavior.mouseX, behavior.mouseY)
            onReleased: parent.parent.progressReleased(behavior.mouseX, behavior.mouseY)
            onClicked: {
                var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
                parent.parent.progressClicked(hoveredFrame)
            }
            onPositionChanged: {
                var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
                Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), hoveredFrame);
            }
            onExited: {
                Tooltip.hideText();
            }
            onWheel: {
                parent.parent.progressWheel(angleDelta.y)
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
    }
}
