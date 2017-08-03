import QtQuick 2.3
import QtQuick.Controls 1.2

Roi {
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width
    property alias roiHeight: roi.height

    function setRoiPosition(xPosition, yPosition) {
        roi.startPosX = xPosition;
        roi.startPosY = yPosition;
        roi.x = xPosition;
        roi.y = yPosition;
    }

    function expandRoi(xPosition, yPosition) {
        roi.width = xPosition - roi.startPosX;
        roi.height = yPosition - roi.startPosY;
        roi.x = roi.startPosX;
        roi.y = roi.startPosY;
    }

    Rectangle {
        id: roi

        height: 40
        width: 60

        visible: false
        color: "transparent"
        border.color: "red"
        border.width: 3

        property real startPosX
        property real startPosY
    }
}
