import QtQuick 2.3
import QtQuick.Controls 1.2

Item{
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width


    signal released(real xPosition, real yPosition)

    MouseArea {
        id: behavior
        anchors.fill: parent

        function getVector(xPosition, yPosition){
            var xDist = xPosition - roi.startPosX;
            var yDist = yPosition - roi.startPosY;
            return Math.sqrt(xDist*xDist + yDist* yDist);
        }

        onReleased: parent.released(mouse.x, mouse.y)

        onPressed: {
            var startPosX = mouseX - roi.width / 2.0;
            var startPosY = mouseY - roi.width / 2.0;
            roi.startPosX = startPosX;
            roi.startPosY = startPosY;
            roi.x = startPosX;
            roi.y = startPosY;
            roi.visible = true;
        }
        onPositionChanged: {
            roi.width = getVector(mouseX, mouseY);
            roi.x = roi.startPosX;// - roi.width/2;
            roi.y = roi.startPosY;// - roi.height/2;
        }
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
