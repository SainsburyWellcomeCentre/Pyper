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

    function set_tracker_py_iface_roi() {
        tracker_py_iface.set_roi(roi.item.width, roi.item.height, roi.item.roiX, roi.item.roiY, roi.item.roiWidth, roi.item.roiHeight);
    }

    function set_tracker_py_iface_restriction_roi() {

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
                if (target.isActive) {
                    tracker_py_iface.set_tracking_region_roi(target.width, target.height, target.roiX, target.roiY, target.roiWidth, target.roiHeight); // FIXME: part that changes
                } else {
                    tracker_py_iface.remove_tracking_region_roi();
                    target.eraseRoi();
                }
                root.roiX = target.roiX;
                root.roiY = target.roiY;
                root.roiWidth = target.roiWidth;
                root.roiHeight = target.roiHeight;
                console.log(root.roiX, root.roiY, root.roiWidth, root.roiHeight);
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
