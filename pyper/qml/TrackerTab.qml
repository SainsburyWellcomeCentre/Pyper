import QtQuick 2.3
import QtQuick.Controls 1.2

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

                iconSource: "../../resources/icons/play.png"
                pressedSource: "../../resources/icons/play_pressed.png"
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

                iconSource: "../../resources/icons/stop.png"
                pressedSource: "../../resources/icons/stop_pressed.png"
                tooltip: "Stop tracking"

                onClicked: py_tracker.stop()
            }
        }
    }

    Text {
        id: vidTitle
        anchors.bottom: trackerDisplay.top
        anchors.bottomMargin: 20
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
        x: 152
        y: 60
        objectName: "trackerDisplay"
        width: 640
        height: 480

        source: "image://trackerprovider/img"

        CircleRoi {
            id: mouseRoi
            anchors.fill: parent
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
            anchors.fill: parent
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
        id: roiButton

        property bool isDown
        isDown: false
        property string oldSource
        oldSource: iconSource

        anchors.top: comboBox1.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: comboBox1.horizontalCenter

        width: startTrackBtn.width
        height: width

        iconSource: "../../resources/icons/roi.png"
        pressedSource: "../../resources/icons/roi_pressed.png"
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

        anchors.top: comboBox1.bottom
        anchors.topMargin: 10
        anchors.left: roiButton.right

        width: startTrackBtn.width
        height: width

        iconSource: "../../resources/icons/roi.png"
        pressedSource: "../../resources/icons/roi_pressed.png"
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
