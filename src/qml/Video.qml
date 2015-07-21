import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Private 1.0 // For Tooltip


Item {
    width: 640
    height: 480
    property alias source: previewImage.source
    property alias value: progressBar.value
    property alias maximumValue: progressBar.maximumValue

    signal progressPressed(real xPosition, real yPosition)
    signal progressReleased(real xPosition, real yPosition)
    signal progressClicked(int frameId)
    signal progressWheel(int angleDelta)

    function reload(){
        previewImage.reload();
    }

    Image {
        id: previewImage
        width: parent.width
        height: parent.height

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
        anchors.top: previewImage.bottom
        anchors.topMargin: 10

        width: previewImage.width
        height: 20
        minimumValue: 0

        signal pressed(real xPosition, real yPosition)
        signal released(real xPosition, real yPosition)
        signal clicked(real xPosition, real yPosition)
        signal positionChanged(real xPosition, real yPosition)
        signal exited()
        signal wheel(point angleDelta)

        onPressed: parent.progressPressed(behavior.mouseX, behavior.mouseY)
        onReleased: parent.progressReleased(behavior.mouseX, behavior.mouseY)
        onClicked: {
            var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
            parent.progressClicked(hoveredFrame)
        }
        onPositionChanged: {
            var hoveredFrame = Math.round((maximumValue - minimumValue) * (behavior.mouseX/width));
            Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), hoveredFrame);
        }
        onExited: {
            Tooltip.hideText();
        }
        onWheel: {
            parent.progressWheel(angleDelta.y)
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
