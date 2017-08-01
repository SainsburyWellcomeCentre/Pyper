import QtQuick 2.3
import QtQuick.Controls 1.2

Item{
    property bool isActive
    property bool isDrawn
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width

    signal released(real xPosition, real yPosition)
    signal pressed(real xPosition, real yPosition)
    signal dragged(real xPosition, real yPosition)

    function drawRoi() {
        roi.visible = true;
        isDrawn = true;
    }
    function eraseRoi() {
        roi.visible = false;
        isDrawn = false;
    }

    function _getVector(xPosition, yPosition){
        var xDist = xPosition - roi.startPosX;
        var yDist = yPosition - roi.startPosY;
        return Math.sqrt(xDist*xDist + yDist* yDist);
    }

    function setRoiPosition(xPosition, yPosition){
        var startPosX = xPosition - roi.width / 2.0;
        var startPosY = yPosition - roi.width / 2.0;
        roi.startPosX = startPosX;
        roi.startPosY = startPosY;
        roi.x = startPosX;
        roi.y = startPosY;
    }

    function expandRoi(xPosition, yPosition){
        roi.width = _getVector(xPosition, yPosition);
        roi.x = roi.startPosX;
        roi.y = roi.startPosY;
    }


    onPressed: {
        if (isActive) {
            setRoiPosition(xPosition, yPosition);
            drawRoi();
        }
    }
    onDragged: {
        if (isActive) {
            expandRoi(xPosition, yPosition)
        }
    }

    MouseArea {
        id: behavior
        anchors.fill: parent

        onReleased: { parent.released(mouse.x, mouse.y) }
        onPressed: { parent.pressed(mouse.x, mouse.y) }
        onPositionChanged: { parent.dragged(mouse.x, mouse.y) }
    }

    Rectangle{//Actually a circle
        id: roi

        width: 60
        height: width
        radius: width/2

        visible: false
        color: "transparent"
        border.color: "yellow"
        border.width: 3

        property real startPosX
        property real startPosY
    }
}
