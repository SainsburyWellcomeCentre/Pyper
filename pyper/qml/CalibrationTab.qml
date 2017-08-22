import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Layouts 1.1

import "popup_messages"
import "basic_types"
import "video"

Rectangle {
    id: rectangle1
    color: "#3B3B3B"
    anchors.fill: parent

    SplashScreen{
        id: splash
        objectName: "splash"
        width: 400
        height: 200
        text: "Calibrating, please wait."
        z: 1
        visible: false
        anchors.centerIn: calibrateImage
    }

    Row {
        id: loadControls

        anchors.left: calibrateImage.left
        anchors.leftMargin: 30

        spacing: 5
        CustomButton {
            id: pathBtn
            width: 40
            height: width
            anchors.top: parent.top
            anchors.topMargin: 10

            iconSource: "../../../resources/icons/document-open.png"

            tooltip: "Select folder with the calibration images"
            onClicked: {
                pathTextField.text = py_calibration.get_folder_path();
                calibrateBtn.enabled = true;
            }
        }
        TextField{
            id: pathTextField
            width: 400
            anchors.verticalCenter: pathBtn.verticalCenter
            text: "..."
        }
    }
    Video {
        id: calibrateImage

        width: 640
        height: 480

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.right: parent.right
        anchors.top: loadControls.bottom
        anchors.topMargin: 20
        anchors.bottom: parent.bottom

        objectName: "calibrationDisplay"

        source: "image://calibrationprovider/img"
    }

    Column {
        id: controlsLayout
        width: 140

        anchors.margins: 5
        anchors.top: parent.top
        anchors.left: parent.left

        spacing: 10
        CustomLabeledButton {
            id: calibrateBtn

            anchors.horizontalCenter: parent.horizontalCenter

            label: "Calibrate"
            tooltip: "Calibrate the camera"
            enabled: false
            onPressed:{
                splash.visible = true;
            }
            onReleased:{
                py_calibration.calibrate();
                splash.visible = false;
                vidControls.enabled = true;
                displayControls.enabled = true;
                matrixControls.enabled = true;
            }
        }
        Rectangle{
            id: chessBoardGeometry
            height: col1.height + 15

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){ col1.reload() }

            CustomColumn {
                id: col1
                LabelWTooltip {
                    id: col1Label
                    text: "Pattern:"
                    help: "Geometry of the calibration pattern"
                }
                IntLabel{
                    width: parent.width
                    label: "Rows"
                    tooltip: "Number of rows in pattern"
                    value: py_calibration.get_n_rows()
                    onEdited: { py_calibration.set_n_rows(value); }
                    function reload() {value = py_calibration.get_n_rows() }
                }
                IntLabel{
                    width: parent.width
                    label: "Columns"
                    tooltip: "Number of columns in pattern"
                    value: py_calibration.get_n_columns()
                    onEdited: { py_calibration.set_n_columns(value); }
                    function reload() {value = py_calibration.get_n_columns() }
                }
            }
        }

        VideoControls {
            id: vidControls
            objectName: "previewVidControls"

            anchors.left: parent.left
            anchors.right: parent.right

            enabled: false

            onPlayClicked: { py_calibration.play() }
            onPauseClicked: { py_calibration.pause() }
            onForwardClicked: { py_calibration.move(1) }
            onBackwardClicked: { py_calibration.move(-1) }
            onStartClicked: { py_calibration.seek_to(-1) }
            onEndClicked: { py_calibration.seek_to(py_calibration.get_n_frames()) }
        }

        Rectangle{
            id: displayControls
            height: col2.height + 15

            anchors.left: parent.left
            anchors.right: parent.right

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"
            enabled: false

            function reload(){ col2.reload() }

            CustomColumn {
                id: col2
                LabelWTooltip {
                    id: col2Label
                    text: "Display:"
                    help: "Select the source of images to display"
                }
                ComboBox {
                    id: comboBox1
                    width: parent.width - 20
                    anchors.topMargin: 10
                    anchors.horizontalCenter: displayControls.Center
                    model: ["Source", "Detected", "Corrected"]
                    onCurrentTextChanged:{
                        if (enabled){
                            py_calibration.set_frame_type(currentText);
                        }
                    }
                }
            }
        }
        Rectangle{
            id: matrixControls
            height: col3.height + 15

            anchors.left: parent.left
            anchors.right: parent.right

            enabled: false

            color: "#4c4c4c"
            radius: 9
            border.width: 3
            border.color: "#7d7d7d"

            function reload(){ col3.reload() }

            CustomColumn {
                id: col3
                LabelWTooltip {
                    id: col3Label
                    text: "Matrix:"
                    help: "Save the camera matrix"
                }
                CustomRow{
                    height: 25
                    ComboBox {
                        id: comboBox2
                        width: parent.parent.width - 20

                        model: ["Normal", "Optimized"]
                        onCurrentTextChanged:{
                            py_calibration.set_matrix_type(currentText);
                        }
                    }
                    CustomButton {
                        id: save
                        width: 25
                        height: width

                        iconSource: "../../../resources/icons/document-save-as.png"

                        tooltip: "Select the destination of the camera matrix"
                        onClicked: {
                            pathTextField.text = py_calibration.save_camera_matrix();
                        }
                    }
                }
            }
        }
    }
}
