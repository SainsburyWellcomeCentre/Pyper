import QtQuick 2.5
import QtQuick.Controls 1.4

import "../style"

Roi {
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width
    property alias roiHeight: roi.height

    function _getVector(xPosition, yPosition){
        var xDist = xPosition - roi.startPosX;
        var yDist = yPosition - roi.startPosY;
        return Math.sqrt(xDist*xDist + yDist*yDist);
    }

    function setRoiPosition(xPosition, yPosition){
        var startPosX = xPosition - roi.width / 2.0;
        var startPosY = yPosition - roi.width / 2.0;
        roi.startPosX = startPosX;
        roi.startPosY = startPosY;
        roi.x = startPosX;
        roi.y = startPosY;
    }

    function resizeRoi(xPosition, yPosition){
        roi.width = _getVector(xPosition, yPosition);
        roi.x = roi.startPosX;
        roi.y = roi.startPosY;
    }

    Rectangle {  //Actually a circle (see radius property)
        id: roi

        width: 60
        height: width
        radius: width/2

        visible: false
        color: "transparent"
        border.color: Theme.roiDefault
        border.width: 3

        property real startPosX
        property real startPosY
    }
}
