import QtQml 2.2
import QtQuick 2.5
import QtQuick.Controls 1.4

import "../popup_messages"
import "../basic_types"
import "../video"
import "../roi"
import "../style"
import "../config"

Rectangle {    
    color: Theme.background

    property alias displayed: graphCanvas.curveSet
    
    property string points

    property int defaultHeight: 50

    onPointsChanged: {
        setPath(points);
    }
    onWidthChanged: {
        setPath(points);
    }

    Rectangle {
        id: redDot

        visible: false
        width: 7
        height: width
        radius: width/2
        color: 'red'
        x: 0
        y: 0
        z: 10
    }

    function highlightPoint(idx) {
        var currentPoint = graphCanvas.path[idx];
        if (currentPoint !== undefined) {
            // console.log(currentPoint);
            redDot.x = Math.round(currentPoint.x - redDot.width/2.0);
            redDot.y = Math.round(currentPoint.y - redDot.height/2.0);
        }
    }
    
    function setPath(points) {
        graphCanvas.resetPath();
        var pointsString = points.split(";");
        var ptString;
        var x;
        var y;
        var ys = [];
        var xs = [];
        for (var i=0; i < pointsString.length; i++) {
            ptString = pointsString[i];
            y = parseFloat(ptString);
            ys.push(y);
            xs.push(i);
        }
        scalePath(xs, ys);
        for (var i=0; i < ys.length; i++) {
            x = xs[i];
            y = ys[i];
            graphCanvas.path.push(Qt.point(x, y));
        }
        graphCanvas.drawPath();
    }
    function scalePath(xs, ys) {
        var minX = Math.min.apply(null, xs);
        var maxX = Math.max.apply(null, xs);
        var scalingX = graph.width / (maxX - minX);  // FIXME: use width - prograsbarlabel.width

        var minY = Math.min.apply(null, ys);
        var maxY = Math.max.apply(null, ys);
        var scalingY = (defaultHeight - 10) / (maxY - minY);  // the graph height in pixels  // FIXME: use height
        
        for (var i=0; i < ys.length; i++) {
            ys[i] -= minY;
            ys[i] *= -scalingY;
            ys[i] += defaultHeight; //  canvas is top left w/ inverted y axis compared to graph
            
            xs[i] *= scalingX;
        }
    }
    
    Canvas {
        id: graphCanvas
        
        anchors.fill: parent
        
        property color drawingColor: Theme.graphCurve
        
        visible: parent.visible
        
        property real lastX
        property real lastY

        property bool curveSet: false
        
        property var path: []
        
        function resetPath() {
            graphCanvas.path = [];
        }

        function drawPath() {
            if (available) {
                var currentPoint = path[0];
                lastX = currentPoint.x;
                lastY = currentPoint.y;

                redDot.x = lastX;
                redDot.y = lastY;
                redDot.visible = true;

                var ctx = getContext('2d');
                ctx.lineWidth = 3.0;
                ctx.strokeStyle = drawingColor;
                ctx.beginPath();

                for (var i=1; i < path.length; i++) {
                    currentPoint = path[i];

                    ctx.moveTo(lastX, lastY);
                    ctx.lineTo(currentPoint.x, currentPoint.y);

                    lastX = currentPoint.x;
                    lastY = currentPoint.y;
                }
                ctx.stroke();
                curveSet = true;
            }
        }
        function clearCanvas() {
            var ctx = getContext("2d");
            try {
                ctx.reset();
            } catch (err) {
                console.log("Canvas reset failed");
            }
        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
