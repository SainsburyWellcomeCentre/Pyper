import QtQuick 2.3
import QtQuick.Controls 1.2

Roi {
    id: root
    property alias roiX: roi.x
    property alias roiY: roi.y
    property alias roiWidth: roi.width
    property alias roiHeight: roi.height
    property color drawingColor: 'Yellow'
    property alias points: canvas.path

    function setRoiPosition(xPosition, yPosition){
        roi.mouseX = xPosition;
        roi.mouseY = yPosition;
        canvas.lastX = xPosition;
        canvas.lastY = yPosition;
        canvas.clearCanvas();
    }

    function resizeRoi(xPosition, yPosition){
        roi.mouseX = xPosition;
        roi.mouseY = yPosition;
        canvas.requestPaint();
    }

    function releasedCallback() {
        canvas.path = canvas.path.slice(1, canvas.path.length);
        var coords = getMinMaxCoords();
        root.roiX = coords[0];
        root.roiY = coords[1];
        root.roiWidth = coords[2] - coords[0];
        root.roiHeight = coords[3] - coords[1];
    }
    function getMinMaxCoords() {
        var minX = 1000000;
        var minY = 1000000;
        var maxX = 0;
        var maxY = 0;

        var pt;
        var curX;
        var curY

        var idx;
        for (idx in canvas.path) {
            pt = canvas.path[idx];
            curX = pt.x;
            curY = pt.y;
            if (curX < minX) {
                minX = curX;
            }
            if (curY < minY) {
                minY = curY;
            }
            if (curX > maxX) {
                maxX = curX;
            }
            if (curY > maxY) {
                maxY = curY;
            }
        }
        return [minX, minY, maxX, maxY];
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
            } else {
                canvas.drawingColor = 'transparent';
                canvas.clearCanvas();
            }
        }

        property real mouseX
        property real mouseY
    }
    Canvas {
        id: canvas
        property color drawingColor: 'transparent'
        anchors.fill: parent

        property real lastX
        property real lastY

        property var path: []

        onPaint: {
            var ctx = getContext('2d')
            ctx.lineWidth = 3
            ctx.strokeStyle = canvas.drawingColor
            ctx.beginPath()

            ctx.moveTo(lastX, lastY)
            ctx.lineTo(roi.mouseX, roi.mouseY)
            lastX = roi.mouseX
            lastY = roi.mouseY
            canvas.path.push(Qt.point(lastX, lastY))

            ctx.stroke()
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



