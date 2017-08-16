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

    CustomLabeledButton {
        id: loadBtn
        x: 30
        y: 20
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
                loadBtn.enabled = true;
            }
        }
        TextField{
            id: pathTextField
            width: 400
            anchors.verticalCenter: pathBtn.verticalCenter
            text: "..."
        }
    }

    Rectangle{
        id: chessBoardGeometry
        width: 120
        height: col1.height + 15
        anchors.top: loadBtn.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: loadBtn.horizontalCenter

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
                readOnly: false
                text: py_calibration.get_n_rows()
                onTextChanged: {
                    if (validateInt()) {
                        py_calibration.set_n_rows(text);
                    }
                }
                function reload() {text = py_calibration.get_n_rows() }
            }
            IntLabel{
                width: parent.width
                label: "Columns"
                tooltip: "Number of columns in pattern"
                readOnly: false
                text: py_calibration.get_n_columns()
                onTextChanged: {
                    if (validateInt()) {
                        py_calibration.set_n_columns(text);
                    }
                }
                function reload() {text = py_calibration.get_n_columns() }
            }
        }
    }

    VideoControls {
        id: vidControls
        objectName: "previewVidControls"

        anchors.horizontalCenter: chessBoardGeometry.horizontalCenter
        anchors.top: chessBoardGeometry.bottom
        anchors.topMargin: 10

        enabled: false

        onPlayClicked: { py_calibration.play() }
        onPauseClicked: { py_calibration.pause() }
        onForwardClicked: { py_calibration.move(1) }
        onBackwardClicked: { py_calibration.move(-1) }
        onStartClicked: { py_calibration.seek_to(-1) }
        onEndClicked: { py_calibration.seek_to(py_calibration.get_n_frames()) }
    }
    Video {
        id: calibrateImage
        x: 150
        y: 60
        anchors.margins: 10
        anchors.left: vidControls.right
        anchors.right: parent.right
        anchors.top: loadControls.bottom
        anchors.topMargin: 20
        anchors.bottom: parent.bottom
        width: 640
        height: 480
        objectName: "calibrationDisplay"

        source: "image://calibrationprovider/img"
    }

    Rectangle{
        id: displayControls
        width: 120
        height: col2.height + 15
        anchors.top: vidControls.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: vidControls.horizontalCenter

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
        width: 120
        height: col3.height + 15
        anchors.top: displayControls.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: displayControls.horizontalCenter

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
