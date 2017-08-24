import QtQuick 2.3
import QtQml 2.0
import QtQuick.Controls 1.2

import "popup_messages"
import "basic_types"
import "video"
import "roi"

Rectangle {
    color: "#3B3B3B"
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

    Rectangle {
        id: controls
        x: 5
        y: 10
        width: 120
        height: row1.height + 20

        color: "#4c4c4c"
        radius: 9
        border.width: 3
        border.color: "#7d7d7d"

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
                        py_tracker.set_roi(mouseRoi.width, mouseRoi.height, mouseRoi.roiX, mouseRoi.roiY, mouseRoi.roiWidth, mouseRoi.roiHeight);
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

    Text {
        id: vidTitle
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.horizontalCenter: trackerDisplay.horizontalCenter

        color: "#ffffff"
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
        x: 152
        y: 60

        anchors.margins: 10
        anchors.left: controls.right
        anchors.right: parent.right
        anchors.top: vidTitle.bottom
        anchors.bottom: parent.bottom
        width: 640
        height: 480

        source: "image://trackerprovider/img"        

        RoiFactory {
            id: mouseRoi

            width: parent.imgWidth
            height: parent.imgHeight

            anchors.top: parent.top
            anchors.left: parent.left

            source: "roi/EllipseRoi.qml"

            roiActive: roiManager.trackingRoiActive
            drawingColor: roiManager.trackingRoiColor
            drawingMode: roiManager.drawingMode
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
        }
    }
    Rectangle{
        id: frameSetterContainer
        width: 120
        height: col.height + 20
        anchors.top: controls.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: controls.horizontalCenter

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
                readOnly: false
                text: py_iface.get_bg_frame_idx()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_bg_frame_idx(text);
                        reload();
                    }
                }
                function reload(){ text = py_iface.get_bg_frame_idx() }
            }
            IntLabel {
                width: parent.width
                label: "Start"
                tooltip: "Select the first data frame"
                readOnly: false
                text: py_iface.get_start_frame_idx()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_start_frame_idx(text);
                        reload();
                    }
                }
                function reload(){ text = py_iface.get_start_frame_idx() }
            }
            IntLabel {
                width: parent.width
                label: "End"
                tooltip: "Select the last data frame"
                readOnly: false
                text: py_iface.get_end_frame_idx()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_end_frame_idx(text);
                        reload();
                    }
                }
                function reload(){ text = py_iface.get_end_frame_idx() }
            }
        }
    }
    Rectangle{
        id: referenceTreatmentSettings
        width: 120
        height: col2.height + 20
        anchors.top: frameSetterContainer.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: frameSetterContainer.horizontalCenter

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
                readOnly: false
                text: py_iface.get_n_bg_frames()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_n_bg_frames(text);
                    }
                }
                function reload() {text = py_iface.get_n_bg_frames() }
            }
            IntLabel{
                width: parent.width
                label: "Sds"
                tooltip: "Number of standard deviations above average"
                readOnly: false
                text: py_iface.get_n_sds()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_n_sds(text);
                    }
                }
                function reload() {text = py_iface.get_n_sds() }
            }
        }
    }
    Rectangle{
        id: detectionParamsSetterContainer
        width: 120
        height: col3.height + 20
        anchors.top: referenceTreatmentSettings.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: referenceTreatmentSettings.horizontalCenter

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
                readOnly: false
                text: py_iface.get_detection_threshold()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_detection_threshold(text);
                    }
                }
                function reload() {text = py_iface.get_detection_threshold() }
            }
            IntLabel {
                width: parent.width
                label: "Min"
                tooltip: "Minimum object area"
                readOnly: false
                text: py_iface.get_min_area()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_min_area(text);
                    }
                }
                function reload() { py_iface.get_min_area() }
            }
            IntLabel {
                width: parent.width
                label: "Max"
                tooltip: "Maximum object area"
                readOnly: false
                text: py_iface.get_max_area()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_max_area(text);
                    }
                }
                function reload() { py_iface.get_max_area() }
            }
            IntLabel{
                width: parent.width
                label: "Mvmt"
                tooltip: "Maximum displacement (between frames) threshold"
                readOnly: false
                text: py_iface.get_max_movement()
                onTextChanged: {
                    if (validateInt()) {
                        py_iface.set_max_movement(text);
                    }
                }
                function reload() { py_iface.get_max_movement() }
            }
        }
    }
    Rectangle{
        id: boolSetterContainer
        width: 120
        height: col4.height + 20
        anchors.top: detectionParamsSetterContainer.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: detectionParamsSetterContainer.horizontalCenter

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
        id: comboBox1
        anchors.top: boolSetterContainer.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: boolSetterContainer.Center
        model: ["Raw", "Diff", "Mask"]
        onCurrentTextChanged:{
            py_tracker.set_frame_type(currentText)
        }
    }

    CustomButton {
        id: roiManagerBtn

        width: 50
        height: width

        anchors.margins: 10
        anchors.top: comboBox1.bottom
        anchors.horizontalCenter: comboBox1.horizontalCenter

        iconSource: "../../../resources/icons/roi.png"

        tooltip: "Open ROI manager"
        onClicked: {
            roiManager.visible = !roiManager.visible;
        }
    }
    RoiManager {
        id: roiManager
        pythonObject: py_iface
        visible: false
        function setRoiOnTop(topRoi, bottomRoi) {  // FIOXME: unnecessary with enabled changed
            bottomRoi.z = 9;
            topRoi.z = 10;
            // FIXME: enabled should be sufficient
        }

        onDrawCallback: {
            setRoiOnTop(mouseRoi, restrictionRoi);
        }
        onDrawRestriction: {
            setRoiOnTop(restrictionRoi, mouseRoi);
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
            changeRoiClass(mouseRoi, trackingRoiShape);
        }
        onRestrictionRoiShapeChanged: {
            changeRoiClass(restrictionRoi, restrictionRoiShape);
        }
    }
}
