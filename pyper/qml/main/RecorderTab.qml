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
    anchors.fill: parent

    function reload(){
        trackingControls.reload();
    }

    onVisibleChanged: { if (visible) { reload() } }

    ErrorScreen {
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
            height: row1.height + vidSpeed.height + 20

            CustomColumn {
                enabled: parent.enabled
                anchors.centerIn: parent
                spacing: 5
                width: parent.width - 20
                height: parent.height - 20

                Row {
                    id: row1
                    anchors.horizontalCenter: parent.horizontalCenter

                    width: (children[0].width * 2) + spacing
                    height: children[0].height
                    spacing: 10

                    CustomButton {
                        id: recordBtn

                        width: 45
                        height: width

                        iconSource: IconHandler.getPath("record.png")
                        pressedSource: IconHandler.getPath("record_pressed.png")
                        tooltip: "Starts video recording"

                        enabled: false
                        onClicked: {  // FIXME: should have both ROIs and probably embed in factory
                            if (py_recorder.cam_detected(0)){
                                if (trackingRoi.isDrawn){
                                    py_recorder.set_roi(trackingRoi.width, trackingRoi.height, trackingRoi.roiX, trackingRoi.roiY, trackingRoi.roiWidth);
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
                        iconSource: IconHandler.getPath("stop.png")
                        pressedSource: IconHandler.getPath("stop_pressed.png")

                        enabled: false
                        onClicked:{
                            py_recorder.stop()
                            recordBtn.enabled = true;
                            enabled = false;
                        }
                    }
                }
                IntInput {
                    id: vidSpeed

                    width: parent.width
                    enabled: parent.enabled

                    label: "Spd."
                    tooltip: "Acqusition frame period in ms (1/FPS)"
                    value: py_iface.timer_period
                    minimumValue: 8  // > 120 FPS
                    onEdited: {
                        py_iface.timer_period = value;
                        reload();
                    }
                    function reload(){
                        value = py_iface.timer_period;
                        //root.updateTracker();
                    }
                }
            }
        }
        TrackingControls {
            id: trackingControls
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: parent.spacing

            py_params_iface: py_iface
            py_tracking_iface: py_recorder

            visualisationOptions: ["Raw", "Diff"]
        }
        CustomButton {
            id: roiManagerBtn

            width: 50
            height: width

            anchors.horizontalCenter: parent.horizontalCenter

            iconSource: IconHandler.getPath("roi.png")
            pressedSource: IconHandler.getPath("roi_pressed.png")

            tooltip: "Open ROI manager"
            onClicked: {
                roiManager.visible = !roiManager.visible;
            }
        }
    }

    Row {
        id: pathLayout

        anchors.margins: 10
        anchors.top: parent.top
        anchors.left: recordImage.left
        spacing: 5

        function updatePath() {
            if (py_recorder.cam_detected(0)){
                recordBtn.enabled = true;
            } else {
                errorScreen.flash(3000);
            }
        }

        CustomButton {
            id: pathBtn
            width: 40
            height: width

            iconSource: IconHandler.getPath("document-save-as.png")

            tooltip: "Select video destination (before recording)"
            onClicked: {
                pathTextField.text = py_iface.set_save_path("");
                pathLayout.updatePath();
            }
        }
        TextField{
            id: pathTextField
            width: 400
            anchors.verticalCenter: pathBtn.verticalCenter
            text: "..."

            onTextChanged: {
                py_iface.set_save_path(text);
                pathLayout.updatePath();
            }
        }

        ComboBox {
            id: camSelect
            width: 100
            anchors.verticalCenter: pathBtn.verticalCenter
            model: ListModel {
                id: model
            }
            Component.onCompleted: {
                if (py_iface.kinect_cam_available()) {
                    model.append("kinect");
                } else {
                    console.log("Kinect unavailable")
                }

                var i = 0;
                while (true) {
                    console.log("Checking camera " + i);
                    var camDetected = py_recorder.cam_detected(i);
                    console.log(camDetected);
                    if (camDetected) {
                        model.append({text: "usb"+i});
                    } else {
                        console.log("USB cam " + i + " unavailable");
                        break;
                    }
                    i += 1;
                }

            }

            onCurrentTextChanged:{
                py_recorder.set_camera(currentText);
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

            source: "../roi/EllipseRoi.qml"

            drawingMode: roiManager.drawingMode

            tracker_py_iface: py_recorder
            roiType: 'tracking'
        }
        RoiFactory {
            id: restrictionRoi

            width: parent.imgWidth
            height: parent.imgHeight

            anchors.top: parent.top
            anchors.left: parent.left

            source: "../roi/RectangleRoi.qml"

            drawingMode: roiManager.drawingMode

            tracker_py_iface: py_recorder
            roiType: 'restriction'
        }
    }

    RoiManager {
        id: roiManager
        pythonObject: py_iface
        visible: false

        roisControlsModelsList: [
            RoiControlsModel { sourceRoi: trackingRoi; name: "Callback ROI"; drawingType: "ellipse"; drawingColor: Theme.roiDefault; checked: true},
            RoiControlsModel { sourceRoi: restrictionRoi; name: "Restriction ROI"; drawingType: "rectangle"; drawingColor: 'red'}
        ]
    }
}
