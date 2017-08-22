import QtQuick 2.3
import QtQuick.Controls 1.2

import "popup_messages"
import "basic_types"
import "video"
import "roi"

Rectangle {
    id: rectangle1
    color: "#3B3B3B"
    anchors.fill: parent

    onVisibleChanged: reload()

    function reload(){
        frameSetterContainer.reload();
        referenceTreatmentSettings.reload();
        detectionParamsSetterContainer.reload();
        boolSetterContainer.reload();
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

        Rectangle {
            id: controls
            height: row1.height + 20

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

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
                    iconSource: "../../../resources/icons/record.png"

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
        Rectangle{
            id: frameSetterContainer
            height: col.height + 20

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){
                col.reload()
            }

            CustomColumn {
                id: col

                IntLabel {
                    width: parent.width
                    label: "Ref"
                    tooltip: "Select the reference frame"
                    value: py_iface.get_bg_frame_idx()
                    onEdited: {
                        py_iface.set_bg_frame_idx(value);
                        reload();
                    }
                    function reload(){ value = py_iface.get_bg_frame_idx() }
                }
                IntLabel {
                    width: parent.width
                    label: "Start"
                    tooltip: "Select the first data frame"
                    value: py_iface.get_start_frame_idx()
                    onEdited: {
                        py_iface.set_start_frame_idx(value);
                        reload();
                    }
                    function reload(){ value = py_iface.get_start_frame_idx() }
                }
                IntLabel {
                    width: parent.width
                    label: "End"
                    tooltip: "Select the last data frame"
                    value: py_iface.get_end_frame_idx()
                    onEdited: {
                        py_iface.set_end_frame_idx(value);
                        reload();
                    }
                    function reload(){ value = py_iface.get_end_frame_idx() }
                }
            }
        }
        Rectangle{
            id: referenceTreatmentSettings
            height: col2.height + 20

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){ col2.reload() }

            CustomColumn {
                id: col2

                IntLabel{
                    width: parent.width
                    label: "n"
                    tooltip: "Number of frames for background"
                    value: py_iface.get_n_bg_frames()
                    onEdited: { py_iface.set_n_bg_frames(value); }
                    function reload() {value = py_iface.get_n_bg_frames() }
                }
                IntLabel{
                    width: parent.width
                    label: "Sds"
                    tooltip: "Number of standard deviations above average"
                    value: py_iface.get_n_sds()
                    onEdited: { py_iface.set_n_sds(value); }
                    function reload() {value = py_iface.get_n_sds() }
                }
            }
        }
        Rectangle{
            id: detectionParamsSetterContainer
            height: col3.height + 20

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){ col3.reload() }

            CustomColumn {
                id: col3

                IntLabel {
                    width: parent.width
                    label: "Thrsh"
                    tooltip: "Detection threshold"
                    value: py_iface.get_detection_threshold()
                    onEdited: { py_iface.set_detection_threshold(value); }
                    function reload() {value = py_iface.get_detection_threshold() }
                }
                IntLabel {
                    width: parent.width
                    label: "Min"
                    tooltip: "Minimum object area"
                    value: py_iface.get_min_area()
                    onEdited: { py_iface.set_min_area(value); }
                    function reload() { py_iface.get_min_area() }
                }
                IntLabel {
                    width: parent.width
                    label: "Max"
                    tooltip: "Maximum object area"
                    value: py_iface.get_max_area()
                    onEdited: { py_iface.set_max_area(value); }
                    function reload() { py_iface.get_max_area() }
                }
                IntLabel{
                    width: parent.width
                    label: "Mvmt"
                    tooltip: "Maximum displacement (between frames) threshold"
                    value: py_iface.get_max_movement()
                    onEdited: { py_iface.set_max_movement(value); }
                    function reload() { py_iface.get_max_movement() }
                }
            }
        }
        Rectangle{
            id: boolSetterContainer
            height: col4.height + 20

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){ col4.reload() }

            CustomColumn {
                id: col4

                BoolLabel {
                    label: "Clear"
                    tooltip: "Clear objects touching the borders of the image"
                    checked: py_iface.get_clear_borders()
                    onClicked: py_iface.set_clear_borders(checked)
                    function reload() { checked = py_iface.get_clear_borders() }
                }
                BoolLabel {
                    label: "Norm."
                    tooltip: "Normalise frames intensity"
                    checked: py_iface.get_normalise()
                    onClicked: py_iface.set_normalise(checked)
                    function reload() { checked = py_iface.get_normalise() }
                }
                BoolLabel{
                    label: "Extract"
                    tooltip: "Extract the arena as an ROI"
                    checked: py_iface.get_extract_arena()
                    onClicked: py_iface.set_extract_arena(checked)
                    function reload() { checked = py_iface.get_extract_arena() }
                }
            }
        }

        ComboBox {
            model: ["Raw", "Diff"]
            onCurrentTextChanged:{
                py_recorder.set_frame_type(currentText)
            }
        }
        CustomButton {
            id: roiButton

            property bool isDown
            isDown: false
            property string oldSource
            oldSource: iconSource

            width: recordBtn.width
            height: width

            iconSource: "../../../resources/icons/roi.png"
            pressedSource: "../../../resources/icons/roi_pressed.png"
            tooltip: "Draw ROI"

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
