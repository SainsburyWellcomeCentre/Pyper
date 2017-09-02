import QtQuick 2.3
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3

import "../popup_messages"
import "../style"
import "../basic_types"
import "../config"
import "../roi"

Rectangle {
    id: background
    color: theme.background
    anchors.fill: parent

    Column {
        id: controlsLayout
        width: 140

        anchors.left: parent.left
        anchors.top: parent.top
        anchors.margins: 10

        spacing: 10


        Frame {
            height: col.height + 20
            id: frameControls
            function reload(){ col.reload() }
            CustomColumn {
                id: col

//                IntButton {
//                    width: parent.width
//                    enabled: parent.enabled
//                    label: "Ref"
//                    tooltip: "Select the reference frame"
//                    text: py_iface.get_bg_frame_idx()
//                    onTextChanged: {
//                        py_iface.set_bg_frame_idx(text);
//                        reload();
//                    }
//                    onClicked: { text = py_viewer.get_frame_idx() }
//                    onEnabledChanged: reload()
//                    function reload(){ text = py_iface.get_bg_frame_idx() }
//                }
                IntButton {
                    width: parent.width
                    enabled: parent.enabled
                    label: "Start"
                    tooltip: "Select the first data frame"
//                    text: py_iface.get_start_frame_idx()
                    onTextChanged: {
//                        py_iface.set_start_frame_idx(text);
//                        reload();
                    }
//                    onClicked: { text = py_viewer.get_frame_idx() }
//                    onEnabledChanged: reload()
//                    function reload(){ text = py_iface.get_start_frame_idx() }
                }
                IntButton {
                    width: parent.width
                    enabled: parent.enabled
                    label: "End"
                    tooltip: "Select the last data frame"
//                    text: py_iface.get_end_frame_idx()
                    onTextChanged: {
//                        py_iface.set_end_frame_idx(text);
//                        reload();
                    }
//                    onClicked: { text = py_viewer.get_frame_idx() }
//                    onEnabledChanged: reload()
//                    function reload(){ text = py_iface.get_end_frame_idx() }
                }
            }
        }
    }

    Column {
        spacing: 10

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.top: parent.top
        Row {
            id: pathLayout

            anchors.margins: 10
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 5

            function updatePath() {
//                if (py_recorder.cam_detected()){
//                    recordBtn.enabled = true;
//                } else {
//                    errorScreen.flash(3000);
//                }
            }

            CustomButton {
                id: pathBtn
                width: 40
                height: width

                iconSource: iconHandler.getPath("document-open.png")

                tooltip: "Select video to transcode"
                onClicked: {
//                    pathTextField.text = py_iface.set_save_path("");
//                    pathLayout.updatePath();
                }
            }
            TextField{
                id: pathTextField
                width: 400
                anchors.verticalCenter: pathBtn.verticalCenter
                text: "..."

                onTextChanged: {
//                    py_iface.set_save_path(text);
//                    pathLayout.updatePath();
                }
            }
        }
        Row {
            id: outPathLayout

            anchors.margins: 10
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 5

            function updatePath() {
                if (py_recorder.cam_detected()){
                    recordBtn.enabled = true;
                } else {
                    errorScreen.flash(3000);
                }
            }

            CustomButton {
                id: outPathBtn
                width: 40
                height: width

                iconSource: iconHandler.getPath("document-save-as.png")

                tooltip: "Select video to transcode"
                onClicked: {
//                    pathTextField.text = py_iface.set_save_path("");
//                    pathLayout.updatePath();
                }
            }
            TextField{
                id: outPathTextField
                width: 400
                anchors.verticalCenter: outPathBtn.verticalCenter
                text: "..."

                onTextChanged: {
//                    py_iface.set_save_path(text);
//                    pathLayout.updatePath();
                }
            }
        }
        Image {
            id: preview

            width: 640
            height: 480

            RoiFactory {
                id: restrictionRoi

                anchors.fill: parent

                source: "../roi/RectangleRoi.qml"

                drawingMode: roiManager.drawingMode

//                tracker_py_iface: py_recorder
                roiType: 'restriction'
            }
        }

        RoiManager {
            id: roiManager
//            pythonObject: py_iface
            visible: false

            roisControlsModelsList: [
                RoiControlsModel { sourceRoi: restrictionRoi; name: "Restriction ROI"; drawingType: "rectangle"; drawingColor: 'red'}
            ]
        }
    }
}
