import QtQuick 2.3
import QtQuick.Controls 1.2

import "../popup_messages"
import "../basic_types"
import "../video"
import "../roi"
import "../style"
import "../config"

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
    InfoScreen{
        id: infoScreen

        anchors.right: parent.right
        anchors.bottom: parent.bottom
        width: 100
        height: 75

        text: "Roi mode"
        visible: false
        z: 1
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
                    x: 20
                    width: 45
                    height: width

                    tooltip: "Starts video recording"
                    iconSource: iconHandler.getPath("record.png")

                    enabled: false
                    onClicked:{
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
                    iconSource: iconHandler.getPath("stop.png")

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
            id: roiButton

            property bool isDown
            isDown: false
            property string oldSource
            oldSource: iconSource

            width: recordBtn.width
            height: width

            iconSource: iconHandler.getPath("roi.png")
            pressedSource: iconHandler.getPath("roi_pressed.png")
            tooltip:
                "Draw ROI
When pressed, this will open the ROI manager."

            onPressed: {}
            onReleased: {}

            onClicked: {
                if (isDown){
                    py_iface.restore_cursor();
                    iconSource = oldSource;
                    isDown = false;
                    infoScreen.visible = false;
                } else {
                    py_iface.chg_cursor();
                    oldSource = iconSource;
                    iconSource = pressedSource;
                    isDown = true;
                    infoScreen.visible = true;
                }
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

            iconSource: iconHandler.getPath("document-save-as.png")

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

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.right: parent.right
        anchors.top: pathLayout.bottom
        anchors.bottom: parent.bottom
        width: 640
        height: 480

        source: "image://recorderprovider/img"

        onWidthChanged: {roi.width = img.width; }
        onHeightChanged: {roi.height = img.height; }

        CircleRoi {
            id: roi
            anchors.top: parent.top
            anchors.left: parent.left
            isActive: roiButton.isDown

            onReleased: {
                if (isDrawn) {
                    if (isActive){
                        py_recorder.set_roi(width, height, roiX, roiY, roiWidth);
                    } else {
                        py_recorder.remove_roi();
                        eraseRoi();
                    }
                }
            }
        }
    }
}
