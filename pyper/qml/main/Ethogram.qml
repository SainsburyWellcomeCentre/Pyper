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
        if (height != defaultHeight) {
            height = defaultHeight;
        }
    }
    onWidthChanged: {
        setPath(points);
    }

    Rectangle {
        id: redBar

        visible: false
        width: 2
        height: parent.height
        color: 'red'
        x: 0
        y: 0
        z: 10
    }

    function highlightPoint(idx) {
        var x = idx / graphCanvas.path.length * width;
        redBar.x = Math.round(x - redBar.width/2.0);
    }
    
    function setPath(pointsString) {
        graphCanvas.resetPath();
        var pts = pointsString.split(";");
        var tmp;
        var behaviour;
        for (var i=0; i < pts.length; i++) {
            tmp = pts[i];
            behaviour = parseInt(tmp);
//            if (behaviour !== 0) {
//                console.log(behaviour);
//            }
            graphCanvas.path.push(behaviour);
        }
        graphCanvas.drawPath();
    }
    
    Canvas {
        id: graphCanvas
        
        anchors.fill: parent
        
        visible: parent.visible

        renderStrategy: Canvas.Cooperative
        renderTarget: Canvas.FramebufferObject

        property bool curveSet: false
        
        property var path: []
        
        function resetPath() {
            graphCanvas.path = [];
        }

        function drawPath() {
            if (available) {
                var currentPoint = path[0];

                var x = 0;

                redBar.x = x;
                redBar.visible = true;

                var ctx = getContext('2d');
                ctx.lineWidth = width / path.length;
                var defaultColor = "#000000";
                var currentColor;

                for (var i=1; i < path.length; i++) {
                    x = i / path.length * width;

                    currentPoint = path[i];
                    currentColor = Theme.ethogramColours[currentPoint];
                    ctx.strokeStyle = currentColor;
                    if (currentColor != defaultColor) {
                        ctx.stroke();
                        ctx.beginPath();
                    }

                    ctx.moveTo(x, 0);
                    ctx.lineTo(x, defaultHeight);
                }
                ctx.stroke();
                curveSet = true;
            }
            requestPaint();
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
