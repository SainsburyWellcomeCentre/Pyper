import QtQuick 2.3
import QtQuick.Controls 1.2

import "popup_messages"
import "basic_types"
import "video"
import "roi"
import "style"

Rectangle {
    color: theme.background
    anchors.fill: parent

    function reload(){
        frameSetterContainer.reload();
        referenceTreatmentSettings.reload();
        detectionParamsSetterContainer.reload();
        boolSetterContainer.reload();
        vidTitle.reload();
    }

    onVisibleChanged: { if (visible){ reload() } }

    SplashScreen{
        id: splash
        width: 400
        height: 200
        text: "Loading, please wait."
        z: 1
        visible: false
        anchors.centerIn: trackerDisplay
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
    ErrorScreen{
        id: videoErrorScreen
        objectName: "videoLoadingErrorScreen"

        anchors.centerIn: trackerDisplay
        width: 400
        height: 200

        text: "Loading video failed"
        visible: false
        z: 1
        onDoFlashChanged: {
            if (doFlash) {
                flash(3000)
            }
            doFlash = false
        }
    }

    Text {
        id: vidTitle
        anchors.topMargin: 10
        anchors.top: parent.top
        anchors.horizontalCenter: trackerDisplay.horizontalCenter

        color: theme.text
        text: py_iface.get_file_name()
        function reload(){
            text = py_iface.get_file_name();
        }

        style: Text.Raised
        font.bold: true
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 14
    }
    Video {
        id: trackerDisplay
        objectName: "trackerDisplay"

        anchors.margins: 10
        anchors.left: controlsColumn.right
        anchors.right: parent.right
        anchors.top: vidTitle.bottom
        anchors.bottom: parent.bottom
        width: 640
        height: 480

        source: "image://trackerprovider/img"

        onWidthChanged: {
            mouseRoi.width = img.width;
            restrictionRoi.width = img.width;
        }
        onHeightChanged: {
            mouseRoi.height = img.height;
            restrictionRoi.height = img.height;
        }
        CircleRoi {
            id: mouseRoi

            anchors.top: parent.top
            anchors.left: parent.left
            isActive: roiButton.isDown

            onReleased: {
                if (isDrawn) {
                    if (isActive){
                        py_tracker.set_roi(width, height, roiX, roiY, roiWidth);
                    } else {
                        py_tracker.remove_roi();
                        eraseRoi();
                    }
                }
            }
        }
        RectangleRoi {
            id: restrictionRoi

            anchors.top: parent.top
            anchors.left: parent.left
            isActive: restrictionRoiButton.isDown
            onReleased: {
                if (isDrawn) {
                    if (isActive) {
                        py_tracker.set_tracking_region_roi(width, height, roiX, roiY, roiWidth, roiHeight)
                    } else {
                        py_tracker.remove_tracking_region_roi();
                        eraseRoi();
                    }
                }
            }
        }
    }

    Column {
        id: controlsColumn
        width: 140
        anchors.margins: 5
        anchors.left: parent.left
        anchors.top: parent.top
        // TODO: use SplitView

        spacing: 10

        Frame {
            id: controls
            height: row1.height + 20

            Row{
                id: row1

                anchors.centerIn: controls
                width: children[0].width *2 + spacing
                height: children[0].height
                spacing: 10

                CustomButton {
                    id: startTrackBtn

                    width: 45
                    height: width

                    iconSource: "../../../resources/icons/play.png"
                    pressedSource: "../../../resources/icons/play_pressed.png"
                    tooltip: "Start tracking"

                    onPressed:{
                        splash.visible = true;
                    }
                    onClicked: {
                        if (mouseRoi.isDrawn){
                            py_tracker.set_roi(mouseRoi.width, mouseRoi.height, mouseRoi.roiX, mouseRoi.roiY, mouseRoi.roiWidth);
                        }
                        py_tracker.start()
                    }
                    onReleased:{
                        py_tracker.load();
                        splash.visible = false;
                    }
                }
                CustomButton {
                    id: stopTrackBtn

                    width: startTrackBtn.width
                    height: width

                    iconSource: "../../../resources/icons/stop.png"
                    pressedSource: "../../../resources/icons/stop_pressed.png"
                    tooltip: "Stop tracking"

                    onClicked: py_tracker.stop()
                }
            }
        }
        Frame {
            id: frameSetterContainer
            height: col.height + 20

            function reload(){ col.reload() }

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
                        console.log(value);
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
        Frame {
            id: referenceTreatmentSettings
            height: col2.height + 20

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
        Frame {
            id: detectionParamsSetterContainer
            height: col3.height + 20

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
        Frame {
            id: boolSetterContainer
            height: col4.height + 20

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
            model: ["Raw", "Diff", "Mask"]
            onCurrentTextChanged:{
                py_tracker.set_frame_type(currentText)
            }
        }
        Row {
            CustomButton {
                id: roiButton

                property bool isDown
                isDown: false
                property string oldSource
                oldSource: iconSource

                width: startTrackBtn.width
                height: width

                iconSource: "../../../resources/icons/roi.png"
                pressedSource: "../../../resources/icons/roi_pressed.png"
                tooltip: "Draw ROI"

                onPressed: {}
                onReleased: {}

                onClicked: {
                    if (isDown) { // already active -> revert
                        py_iface.restore_cursor();
                        iconSource = oldSource;
                        isDown = false;
                        infoScreen.visible = false;
                    } else {  // activate
                        py_iface.chg_cursor();
                        oldSource = iconSource;
                        iconSource = pressedSource;
                        isDown = true;
                        infoScreen.visible = true;
                        mouseRoi.z = 10;
                        restrictionRoi.z = 9;
                    }
                }
            }
            CustomButton {
                id: restrictionRoiButton

                property bool isDown
                isDown: false
                property string oldSource
                oldSource: iconSource

                width: startTrackBtn.width
                height: width

                iconSource: "../../../resources/icons/roi.png"
                pressedSource: "../../../resources/icons/roi_pressed.png"
                tooltip: "Draw tracking area ROI"

                onPressed: {}
                onReleased: {}

                onClicked: {
                    if (isDown) { // already active -> revert
                        py_iface.restore_cursor();
                        iconSource = oldSource;
                        isDown = false;
                        infoScreen.visible = false;
                    } else { // activate
                        py_iface.chg_cursor();
                        oldSource = iconSource;
                        iconSource = pressedSource;
                        isDown = true;
                        infoScreen.visible = true;
                        restrictionRoi.z = 10;
                        mouseRoi.z = 9;
                    }
                }
            }
        }
    }
}
