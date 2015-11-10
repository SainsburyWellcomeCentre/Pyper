import QtQuick 2.3
import QtQuick.Controls 1.2

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
            width: (children[0].width * 2) + spacing
            height: children[0].height
            spacing: 10

            CustomButton {
                id: recordBtn
                x: 20
                width: 45
                height: width

                tooltip: "Starts video recording"
                iconSource: "../../resources/icons/record.png"

                enabled: false
                onClicked:{
                    if (py_recorder.camDetected()){
                        if (roi.isDrawn){
                            py_recorder.setRoi(roi.width, roi.height, roi.roiX, roi.roiY, roi.roiWidth);
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
                iconSource: "../../resources/icons/stop.png"

                enabled: false
                onClicked:{
                    py_recorder.stop()
                    recordBtn.enabled = true;
                    enabled = false;
                }
            }
        }
    }

    CustomButton {
        id: pathBtn
        width: 40
        height: width
        anchors.left: recordImage.left
        anchors.bottom: recordImage.top
        anchors.bottomMargin: 10

        iconSource: "../../resources/icons/document-save-as.png"

        tooltip: "Select video destination (before recording)"
        onClicked: {
            pathTextField.text = py_iface.setSavePath("");
            if (py_recorder.camDetected()){
                recordBtn.enabled = true;
            } else {
                errorScreen.flash(3000);
            }
        }
    }
    TextField{
        id: pathTextField
        width: 400
        anchors.left: pathBtn.right
        anchors.leftMargin: 5
        anchors.verticalCenter: pathBtn.verticalCenter
        text: "..."

        onTextChanged: {
            py_iface.setSavePath(text);
            if (py_recorder.camDetected()){
                recordBtn.enabled = true;
            } else {
                errorScreen.flash(3000);
            }
        }
    }

    Video {
        id: recordImage
        x: 152
        y: 60
        objectName: "recording"
        width: 640
        height: 480

        source: "image://recorderprovider/img"

        Roi{
            id: roi
            anchors.fill: parent
            isActive: roiButton.isDown
            onReleased: {
                if (isDrawn) {
                    if (isActive){
                        py_recorder.setRoi(width, height, roiX, roiY, roiWidth);
                    } else {
                        py_recorder.removeRoi();
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
                text: py_iface.getBgFrameIdx()
                onTextChanged: {
                    py_iface.setBgFrameIdx(text);
                    reload();
                }
                function reload(){ text = py_iface.getBgFrameIdx() }
            }
            IntLabel {
                width: parent.width
                label: "Start"
                tooltip: "Select the first data frame"
                readOnly: false
                text: py_iface.getStartFrameIdx()
                onTextChanged: {
                    py_iface.setStartFrameIdx(text);
                    reload();
                }
                function reload(){ text = py_iface.getStartFrameIdx() }
            }
            IntLabel {
                width: parent.width
                label: "End"
                tooltip: "Select the last data frame"
                readOnly: false
                text: py_iface.getEndFrameIdx()
                onTextChanged: {
                    py_iface.setEndFrameIdx(text);
                    reload();
                }
                function reload(){ text = py_iface.getEndFrameIdx() }
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
                text: py_iface.getNBgFrames()
                onTextChanged: py_iface.setNBgFrames(text)
                function reload() {text = py_iface.getNBgFrames() }
            }
            IntLabel{
                width: parent.width
                label: "Sds"
                tooltip: "Number of standard deviations above average"
                readOnly: false
                text: py_iface.getNSds()
                onTextChanged: py_iface.setNSds(text)
                function reload() {text = py_iface.getNSds() }
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
                text: py_iface.getDetectionThreshold()
                onTextChanged: py_iface.setDetectionThreshold(text)
                function reload() {text = py_iface.getDetectionThreshold() }
            }
            IntLabel {
                width: parent.width
                label: "Min"
                tooltip: "Minimum object area"
                readOnly: false
                text: py_iface.getMinArea()
                onTextChanged: py_iface.setMinArea(text)
                function reload() { py_iface.getMinArea() }
            }
            IntLabel {
                width: parent.width
                label: "Max"
                tooltip: "Maximum object area"
                readOnly: false
                text: py_iface.getMaxArea()
                onTextChanged: py_iface.setMaxArea(text)
                function reload() { py_iface.getMaxArea() }
            }
            IntLabel{
                width: parent.width
                label: "Mvmt"
                tooltip: "Maximum displacement (between frames) threshold"
                readOnly: false
                text: py_iface.getMaxMovement()
                onTextChanged: py_iface.setMaxMovement(text)
                function reload() { py_iface.getMaxMovement() }
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
                checked: py_iface.getClearBorders()
                onClicked: py_iface.setClearBorders(checked)
                function reload() { checked = py_iface.getClearBorders() }
            }
            BoolLabel {
                label: "Norm."
                tooltip: "Normalise frames intensity"
                checked: py_iface.getNormalise()
                onClicked: py_iface.setNormalise(checked)
                function reload() { checked = py_iface.getNormalise() }
            }
            BoolLabel{
                label: "Extract"
                tooltip: "Extract the arena as an ROI"
                checked: py_iface.getExtractArena()
                onClicked: py_iface.setExtractArena(checked)
                function reload() { checked = py_iface.getExtractArena() }
            }
        }
    }

    ComboBox {
        id: comboBox1
        anchors.top: boolSetterContainer.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: boolSetterContainer.Center
        model: ["Raw", "Diff"]
        onCurrentTextChanged:{
            py_recorder.setFrameType(currentText)
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

        width: recordBtn.width
        height: width

        iconSource: "../../resources/icons/roi.png"
        pressedSource: "../../resources/icons/roi_pressed.png"
        tooltip: "Draw ROI"

        onPressed: {}
        onReleased: {}

        onClicked: {
            if (isDown){
                py_iface.restoreCursor();
                iconSource = oldSource;
                isDown = false;
                infoScreen.visible = false;
            } else {
                py_iface.chgCursor();
                oldSource = iconSource;
                iconSource = pressedSource;
                isDown = true;
                infoScreen.visible = true;
            }
        }
    }
}
