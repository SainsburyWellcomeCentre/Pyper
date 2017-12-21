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
    color: theme.background
    
    property string points
    onPointsChanged: {
        setPath(points);
    }
    onWidthChanged: {
        setPath(points);
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
        var minY = Math.min.apply(null, ys);
        var maxY = Math.max.apply(null, ys);
        var scalingY = (50 - 10) / (maxY - minY);  // the graph height in pixels  // FIXME: use height
        var scalingX = graph.width / (maxX - minX);  // FIXME: use width - prograsbarlabel.width
        
        for (var i=0; i < ys.length; i++) {
            ys[i] -= minY;
            ys[i] *= scalingY;
            ys[i] +=5; // FIXME:
            
            //                xs[i] -= minX;
            xs[i] *= scalingX;
        }
    }
    
    Canvas {
        id: graphCanvas
        
        anchors.fill: parent
        
        property color drawingColor: 'lightBlue'
        
        visible: parent.visible
        
        property real lastX
        property real lastY
        
        property var path: []
        
        function resetPath() {
            graphCanvas.path = [];
        }
        function drawPath() {
            var currentPoint = path[0];
            lastX = currentPoint.x;
            lastY = currentPoint.y;
            
            var ctx = getContext('2d');
            ctx.lineWidth = 3;
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
