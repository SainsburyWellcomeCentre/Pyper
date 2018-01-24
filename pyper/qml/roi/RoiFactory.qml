import QtQuick 2.5


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

    function redraw() {
        if (roiActive) {
            roiActive = false;
            roiActive = true;
        }
    }

    onRoiXChanged: { redraw(); }
    onRoiYChanged: { redraw(); }
    onRoiWidthChanged: { redraw(); }
    onRoiHeightChanged: { redraw(); }

    property variant tracker_py_iface

    property string roiType
    property string uuid

    // utils
    function endsWith(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
    }
    function getRandomUuid() {
        return tracker_py_iface.get_uuid();
    }
    function sourceFileFromString(srcString) {
        srcString = srcString.replace(/^\s+|\s+$/g, '');
        if (srcString === "ellipse") {
            return "EllipseRoi.qml";
        } else if (srcString === "rectangle") {
            return "RectangleRoi.qml";
        } else if (srcString === "freehand") {
            return ("FreehandRoi.qml");
        } else {
            console.log("Unknown ROI type: " + srcString);
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
            console.log("Unknown source: " + src);
        }
    }

    function getType() {
        return getTypeFromString(String(source));
    }

    // Store the ROI by uuid in a list
    function store() {
        var _uuid = getRandomUuid();
        uuid = _uuid;
        tracker_py_iface.store_roi(roiType, _uuid);  // FIXME: add
        return _uuid;
    }
    // Retrieve the ROI by uuid
    function retrieve(_uuid) {
        var roiData = tracker_py_iface.retrieve_roi(roiType, _uuid);
        uuid = _uuid;
        loadFromRoiData(roiData);
    }

    // Batch load/save
    function loadRoisBatch() {
        tracker_py_iface.load_roi_vault(roiType);
    }
    function retrieveNext() {
        var roiData = tracker_py_iface.retrieve_next(roiType);
        if (roiData === -1) {  // No next element
            return -1;
        } else {
            uuid = roiData[0];
            loadFromRoiData(roiData.slice(1));
            return uuid;
        }
    }
    function saveRoisBatch() {
        tracker_py_iface.save_roi_vault(roiType)
    }

    // Single load/save
    function save() {
        tracker_py_iface.save_roi(roiType);
    }
    function load() {
        var roiData = tracker_py_iface.load_roi(roiType);
        loadFromRoiData(roiData);
    }

    function scaleCoordinates(source_type, img_width, img_height, roi_x, roi_y, roi_width, roi_height) {
        var horizontal_scaling_factor = width / img_width;  // TODO: check if not contrary
        var vertical_scaling_factor = height / img_height;

        var scaled_width = roi_width * horizontal_scaling_factor;
        var scaled_height = roi_height * vertical_scaling_factor;

        var scaled_x = roi_x * horizontal_scaling_factor;
        var scaled_y = roi_y * vertical_scaling_factor;

        return [scaled_x, scaled_y, scaled_width, scaled_height];
    }
    function loadFromRoiData(roiData) {
        if (roiData === -1){
            return;
        } else if (roiData === undefined){
            return;
        } else {
            var img_width = parseFloat(roiData[0]);
            var img_height = parseFloat(roiData[1]);
            roi.source = sourceFileFromString(roiData[2]);
            var rawRoiX = parseFloat(roiData[3]);
            var rawRoiY = parseFloat(roiData[4]);
            var rawRoiWidth = parseFloat(roiData[5]);
            var rawRoiHeight = parseFloat(roiData[6]);

            var scaledCoords = scaleCoordinates(roiData[2], img_width, img_height, rawRoiX, rawRoiY, rawRoiWidth, rawRoiHeight);
            root.roiX = Math.round(scaledCoords[0]);
            root.roiY= Math.round(scaledCoords[1]);
            root.roiWidth = Math.round(scaledCoords[2]);
            root.roiHeight = Math.round(scaledCoords[3]);

            var points;
            if (getType() === "freehand") {
                for (var i=7; i < roiData.length(); i++) {
                    points[i-7] = roiData[i];  // FIXME:
                }
            }
        }
        if (roiActive) {
            tracker_py_iface.set_tracker_rois();
        }
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
            b4.target = roi.item;
            b5.target = roi.item;
            b6.target = roi.item;
            b7.target = roi.item;
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
    Binding {
        id: b4

        property: "roiX"
        value: root.roiX
    }
    Binding {
        id: b5

        property: "roiY"
        value: root.roiY
    }
    Binding {
        id: b6

        property: "roiWidth"
        value: root.roiWidth
    }
    Binding {
        id: b7

        property: "roiHeight"
        value: root.roiHeight
    }
}
