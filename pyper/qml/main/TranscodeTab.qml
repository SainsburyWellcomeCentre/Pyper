import QtQuick 2.3
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Dialogs 1.0

import "../popup_messages"
import "../style"
import "../basic_types"
import "../config"
import "../roi"
import "../video"

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
            id: controls
            height: row1.height + 20

            Row {
                id: row1

                anchors.centerIn: controls
                width: children[0].width *2 + spacing
                height: children[0].height
                spacing: 10

                CustomButton {
                    id: startTranscodeBtn

                    width: 45
                    height: width

                    iconSource: iconHandler.getPath("play.png")
                    pressedSource: iconHandler.getPath("play_pressed.png")
                    tooltip: "Start transcoding"

//                    onPressed:{ splash.visible = true; }
                    onClicked: { py_transcoder.start() }
                    onReleased:{
                        py_transcoder.load();
//                        splash.visible = false;
                    }
                }
                CustomButton {
                    id: stopTrackBtn

                    width: startTranscodeBtn.width
                    height: width

                    iconSource: iconHandler.getPath("stop.png")
                    pressedSource: iconHandler.getPath("stop_pressed.png")
                    tooltip: "Stop transcoding"

                    onClicked: py_transcoder.stop()
                }
            }
        }
        Frame {
            height: col.height + 20
            id: frameControls
            function reload(){ col.reload() }
            CustomColumn {
                id: col

                IntInput {
                    width: parent.width
                    enabled: parent.enabled
                    label: "Start"
                    tooltip: "Select the first data frame"
                    value: py_transcoder.get_start_frame_idx()
                    onEdited: {
                        py_transcoder.set_start_frame_idx(value);
                        reload();
                    }
                    onEnabledChanged: reload()
                    function reload(){ value = py_transcoder.get_start_frame_idx() }
                }
                IntInput {
                    width: parent.width
                    enabled: parent.enabled
                    label: "End"
                    tooltip: "Select the last data frame"
                    value: py_transcoder.get_end_frame_idx()
                    onEdited: {
                        py_transcoder.set_end_frame_idx(value);
                        reload();
                    }
                    onEnabledChanged: reload()
                    function reload(){ value = py_transcoder.get_end_frame_idx() }
                }
            }
        }
        Frame {
            height: col.height + 20
            id: scaleControls
            function reload(){ col.reload() }
            CustomColumn {
                id: col1

                IntInput {
                    width: parent.width
                    enabled: parent.enabled
                    label: "x scale"
                    tooltip: "Select the Horizontal scaling factor"
                    stepSize: 0.1
                    minimumValue: 0.1
                    maximumValue: 1
                    value: 1
                    onEdited: {
                        py_transcoder.set_x_scale(value);
                    }
                }
                IntInput {
                    width: parent.width
                    enabled: parent.enabled
                    label: "y scale"
                    tooltip: "Select the Vertical scaling factor"
                    stepSize: 0.1
                    minimumValue: 0.1
                    maximumValue: 1
                    value: 1
                    onEdited: {
                        py_transcoder.set_y_scale(value);
                    }
                }
            }
        }
        ComboBox {
            id: codecSelector
            anchors.left: parent.left
            anchors.right: parent.right
            model: [ "MPG4", "X264", "THEO", "DIVX","XVID", "WMV2", "WMV1" ]
            onCurrentTextChanged: { py_transcoder.set_codec(currentText); }
        }

        CustomButton {
            id: roiManagerBtn

            width: 50
            height: width

            anchors.horizontalCenter: parent.horizontalCenter

            iconSource: iconHandler.getPath("roi.png")

            tooltip: "Open ROI manager"
            onClicked: {
                roiManager.visible = !roiManager.visible;
            }
        }
    }

    Column {
        id: pathControls
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

            CustomButton {
                id: pathBtn
                width: 40
                height: width

                iconSource: iconHandler.getPath("document-open.png")

                tooltip: "Select video to transcode"
                onClicked: {
                    inPathDialog.visible = true;
                }
                FileDialog {
                    id: inPathDialog
                    title: "Please select the path of the video to transcode"
//                    folder: shortcuts.home
                    onAccepted: {
                        visible = false;
                        py_transcoder.set_source_path(fileUrl);
                    }
                }
            }
            TextField{
                id: pathTextField
                width: 400
                anchors.verticalCenter: pathBtn.verticalCenter
                text: inPathDialog.fileUrl
            }
        }
        Row {
            id: outPathLayout

            anchors.margins: 10
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 5


            CustomButton {
                id: outPathBtn
                width: 40
                height: width

                iconSource: iconHandler.getPath("document-save-as.png")

                tooltip: "Select the destination path"
                onClicked: {
                    outPathDialog.visible = true;
                }
                FileDialog {
                    id: outPathDialog
                    title: "Please select the path to save the video"
                    selectExisting: false
//                    selectedNameFilter:
//                    folder: shortcuts.home
                    onAccepted: {
                        visible = false;
                        py_transcoder.set_save_path(fileUrl);
                    }
                }
            }
            TextField{
                id: outPathTextField
                width: 400
                anchors.verticalCenter: outPathBtn.verticalCenter
                text: outPathDialog.fileUrl
            }
        }
    }
    Video {
        id: preview
        objectName: "transcodingDisplay"

        width: 640
        height: 480

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.right: parent.right
        anchors.top: pathControls.bottom
        anchors.bottom: parent.bottom

        source: "image://transcoderprovider/img"

        RoiFactory {
            id: restrictionRoi

            anchors.fill: parent

            source: "../roi/RectangleRoi.qml"

            drawingMode: roiManager.drawingMode

            tracker_py_iface: py_transcoder
            roiType: 'restriction'
        }
    }

    RoiManager {
        id: roiManager
        pythonObject: py_iface
        visible: false

        // FIXME: Force rectangle ROI because other shapes do not make sense
        roisControlsModelsList: [
            RoiControlsModel { sourceRoi: restrictionRoi; name: "Restriction ROI"; drawingType: "rectangle"; drawingColor: 'red'}
        ]
    }
}
