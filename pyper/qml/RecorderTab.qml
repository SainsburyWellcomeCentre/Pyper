import QtQuick 2.3
import QtQuick.Controls 1.2

import "popup_messages"
import "basic_types"
import "video"
import "roi"
import "style"

Rectangle {
    id: rectangle1
    color: theme.background
    anchors.fill: parent

    onVisibleChanged: reload()

    function reload(){
        trackingControls.reload();
    }

    ErrorScreen{
        id: errorScreen
        width: 400
        height: 200
        text: "No camera detected.\n\nConnect one first."
        visible: false
        z: 1
        anchors.centerIn: parent
    }

    Column {
        id: controlsLayout
        width: 140

        anchors.margins: 5
        anchors.top: parent.top
        anchors.left: parent.left

        spacing: 10

        Frame {
            id: controls
            height: row1.height + 20

            Row {
                id: row1

                anchors.centerIn: parent
                width: (children[0].width * 2) + spacing
                height: children[0].height
                spacing: 10

                CustomButton {
                    id: recordBtn
                    x: 20  // FIXME: put anchor
                    width: 45
                    height: width

                    tooltip: "Starts video recording"
                    iconSource: "../../../resources/icons/record.png"

                    enabled: false
                    onClicked: {  // FIXME: should have both ROIs and probably embed in factory
                        if (py_recorder.cam_detected()){
                            if (roi.isDrawn){
                                py_recorder.set_roi(roi.width, roi.height, roi.roiX, roi.roiY, roi.roiWidth);
                            }
                            if (py_recorder.start()) {
                                enabled = false;
                                stopBtn.enabled = true;
                            }
                        } else {
                            errorScreen.flash(3000);
                        }
                    }
                }
                CustomButton {
                    id: stopBtn
                    width: recordBtn.width
                    height: width

                    tooltip: "Stops video recording"
                    iconSource: "../../../resources/icons/stop.png"

                    enabled: false
                    onClicked:{
                        py_recorder.stop()
                        recordBtn.enabled = true;
                        enabled = false;
                    }
                }
            }
        }
        TrackingControls {
            id: trackingControls
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: parent.spacing

            py_interface: py_iface
            parent_py_obj: py_recorder
        }

        CustomButton {
            id: roiManagerBtn

            width: 50
            height: width

            anchors.horizontalCenter: parent.horizontalCenter

            iconSource: "../../../resources/icons/roi.png"
//            pressedSource: "../../../resources/icons/roi_pressed.png"
//            property string oldSource: iconSource
//            property bool isDown: false

            tooltip: "Open ROI manager"
            onClicked: {
                roiManager.visible = !roiManager.visible;
            }
        }
        RoiManager {
            id: roiManager
            pythonObject: py_iface
            visible: false

            onDrawCallback: {
                setRoiOnTop(trackingRoi, restrictionRoi);
            }
            onDrawRestriction: {
                setRoiOnTop(restrictionRoi, trackingRoi);
            }

            function changeRoiClass(roi, roiShape) {
                if (roiShape === "ellipse") {
                    roi.source = "roi/EllipseRoi.qml";
                } else if (roiShape === 'rectangle') {
                    roi.source = "roi/RectangleRoi.qml"
                } else {
                    console.log("Unrecognised drawing mode: " + roiShape);
                }
            }
            onTrackingRoiShapeChanged: {
                changeRoiClass(trackingRoi, trackingRoiShape);
            }
            onRestrictionRoiShapeChanged: {
                changeRoiClass(restrictionRoi, restrictionRoiShape);
            }
        }
    }

    Row {
        id: pathLayout

        anchors.margins: 10
        anchors.top: parent.top
        anchors.left: recordImage.left
        spacing: 5

        CustomButton {
            id: pathBtn
            width: 40
            height: width

            iconSource: "../../../resources/icons/document-save-as.png"

            tooltip: "Select video destination (before recording)"
            onClicked: {
                pathTextField.text = py_iface.set_save_path("");
                if (py_recorder.cam_detected()){
                    recordBtn.enabled = true;
                } else {
                    errorScreen.flash(3000);
                }
            }
        }
        TextField{
            id: pathTextField
            width: 400
            anchors.verticalCenter: pathBtn.verticalCenter
            text: "..."

            onTextChanged: {
                py_iface.set_save_path(text);
                if (py_recorder.cam_detected()){
                    recordBtn.enabled = true;
                } else {
                    errorScreen.flash(3000);
                }
            }
        }
    }
    Video {
        id: recordImage
        objectName: "recording"

        width: 640
        height: 480

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.right: parent.right
        anchors.top: pathLayout.bottom
        anchors.bottom: parent.bottom

        source: "image://recorderprovider/img"


        RoiFactory {
            id: trackingRoi

            width: parent.imgWidth
            height: parent.imgHeight

            anchors.top: parent.top
            anchors.left: parent.left

            source: "roi/EllipseRoi.qml"

            roiActive: roiManager.trackingRoiActive
            drawingColor: roiManager.trackingRoiColor
            drawingMode: roiManager.drawingMode

            tracker_py_iface: py_recorder
        }
        RoiFactory {
            id: restrictionRoi

            width: parent.imgWidth
            height: parent.imgHeight

            anchors.top: parent.top
            anchors.left: parent.left

            source: "roi/RectangleRoi.qml"

            roiActive: roiManager.restrictionRoiActive
            drawingColor: roiManager.restrictionRoiColor
            drawingMode: roiManager.drawingMode

            tracker_py_iface: py_recorder
        }
    }
}
