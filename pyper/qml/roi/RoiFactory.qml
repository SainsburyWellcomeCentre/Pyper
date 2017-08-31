import QtQuick 2.3


Item {
    id: root

    anchors.top: parent.top
    anchors.left: parent.left
    width: parent.imgWidth
    height: parent.imgHeight

    property alias source: roi.source

    property bool roiActive: false
    property bool drawingMode: false
    property string drawingColor: "Yellow"

    property real roiX: 0
    property real roiY: 0
    property real roiWidth: 0
    property real roiHeight: 0

    property variant tracker_py_iface

    property string roiType

    function endsWith(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
    }

    function setPyIfaceRoi() {
//        console.log("Setting ROI " + roiType + " to: " + source + ", size:  " + roi.item.width + ", " + roi.item.height);
        var src = String(source);
        if (endsWith(src, "EllipseRoi.qml") || endsWith(src, "RectangleRoi.qml")) {
            tracker_py_iface.set_roi(roiType, source, root.width, root.height, root.roiX, root.roiY, root.roiWidth, root.roiHeight);
        } else if (endsWith(src, "FreehandRoi.qml")) {
            tracker_py_iface.set_roi_from_points(roiType, root.width, root.height, pointsToString(roi.item.points));
        } else {
            console.log("Unrecognised source: " + source);
        }
    }
    function unsetPyIfaceRoi() {
        tracker_py_iface.remove_roi(roiType);
        roi.item.eraseRoi();
    }
    function pointsToString(points) {
        var pts = [];
        var pt;
        for (var i=0; i < points.length; i++) {
            pt = points[i];
            pts[i] = "(" + pt.x + "," + pt.y + ")"
        }
        return String(pts);
    }

    Loader {
        id: roi

        anchors.fill: parent

        source: "EllipseRoi.qml"
        onLoaded: {
            binding1.target = roi.item;
            binding2.target = roi.item;
            binding3.target = roi.item;
            connections.target = roi.item;
        }
    }
    Connections {
        id: connections
        target: roi.item

        onReleased: {
            if (target.isDrawn) {
                root.roiX = target.roiX;
                root.roiY = target.roiY;
                root.roiWidth = target.roiWidth;
                root.roiHeight = target.roiHeight;
                if (target.isActive) {
                     setPyIfaceRoi();
                } else {
                    unsetPyIfaceRoi();
                }
            }
        }
    }
    Binding {
        id: binding1

        property: "isActive"
        value: root.roiActive
    }
    Binding {
        id: binding2

        property: "drawingColor"
        value: root.drawingColor
    }
    Binding {
        id: binding3

        property: "drawingMode"
        value: root.drawingMode
    }
}
