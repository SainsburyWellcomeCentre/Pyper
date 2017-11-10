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

    onRoiHeightChanged: {
        console.log("Roi height changed");  // DEBUG
    }

    property variant tracker_py_iface

    property string roiType

    function endsWith(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
    }

    function save() {
        console.log("Saving ROI");
        tracker_py_iface.save_roi(roiType);
    }

    function load() {
        console.log("Loading ROI");
        var roiData = tracker_py_iface.load_roi(roiType);
        if (roiData === -1){
            return;
        } else if (roiData === undefined){
            return;
        } else {
            roiType = roiData[0];
            source = roiData[1];
            roiX = roiData[2];
            roiY= roiData[3];
            roiWidth = roiData[4];
            roiHeight = roiData[5];
            var points;
            if (getType() === "freehand") {
                for (var i=0; i < roiData.length(); i++) {  // FIXME: simplyify syntax
                    if (i > 5) {
                        points[i-5] = roiData[i];
                    }
                }
            }
        }
    }

    function getTypeFromString(src) {
        if (endsWith(src, "EllipseRoi.qml")) {
            return 'ellipse';
        } else if (endsWith(src, "RectangleRoi.qml")) {
            return 'rectangle';
        } else if (endsWith(src, "FreehandRoi.qml")) {
            return 'freehand';
        } else {
            console.log("Unrecognised source: " + source);
        }
    }

    function getType() {
        return getTypeFromString(String(source));
    }

    function setPyIfaceRoi() {
        var type = getType();
        if (type === 'ellipse' || type === 'rectangle') {
            tracker_py_iface.set_roi(roiType, type, root.width, root.height, root.roiX, root.roiY, root.roiWidth, root.roiHeight);
        } else if (type === 'freehand') {
            tracker_py_iface.set_roi_from_points(roiType, root.width, root.height, pointsToString(roi.item.points));
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
    function finalise() {
        tracker_py_iface.set_tracker_rois();
    }

    onRoiActiveChanged: {
        if (roiActive == false) {
            unsetPyIfaceRoi();
        }
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
