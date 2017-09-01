import QtQuick 2.3
import QtQuick.Controls 1.2

Roi {
    id: root
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width
    property alias roiHeight: roi.height
    property color drawingColor: 'Yellow'

    function setRoiPosition(xPosition, yPosition){
        var startPosX = xPosition - roi.width / 2.0;
        var startPosY = yPosition - roi.height / 2.0;
        roi.startPosX = startPosX;
        roi.startPosY = startPosY;
        roi.x = startPosX;
        roi.y = startPosY;
        canvas.clearCanvas();
        canvas.requestPaint();
    }

    function resizeRoi(xPosition, yPosition){
        roi.width = xPosition - roi.startPosX
        roi.height = yPosition - roi.startPosY
        roi.x = roi.startPosX;
        roi.y = roi.startPosY;
        canvas.clearCanvas();
        canvas.requestPaint();
    }

    Rectangle {
        id: roi

        width: 60
        height: width
        radius: width / 2

        visible: false
        color: "transparent"
        border.color: "transparent"
        border.width: 3

        onVisibleChanged: {
            if (visible) {
                canvas.drawingColor = root.drawingColor;
                canvas.requestPaint();
            } else {
                canvas.drawingColor = 'transparent';
                canvas.clearCanvas();
            }
        }

        property real startPosX
        property real startPosY
    }
    Canvas {
        id: canvas
        property color drawingColor: 'transparent'
        anchors.fill: parent

        visible: roi.visible

        onPaint: {
            var ctx = getContext('2d');
            ctx.lineWidth = 3;
            ctx.strokeStyle = canvas.drawingColor;
            ctx.beginPath();
            ctx.ellipse(roi.x, roi.y, roi.width, roi.height);
            ctx.stroke();
        }
        function clearCanvas() {
            var ctx = getContext("2d");
            try {
                ctx.reset();
            } catch (err) {
                //  FIXME:
            }
        }
    }
}



