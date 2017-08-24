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
            if (target.isDrawn) {  // FIXME: part that changes + need pythonObject
                if (target.isActive) {
                    py_tracker.set_tracking_region_roi(target.width, target.height, target.roiX, target.roiY, target.roiWidth, target.roiHeight)
                } else {
                    py_tracker.remove_tracking_region_roi();
                    target.eraseRoi();
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
