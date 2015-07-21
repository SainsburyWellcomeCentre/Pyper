import QtQuick 2.3
import QtQuick.Controls 1.2

Rectangle {
    id: background
    color: "#3B3B3B"
    anchors.fill: parent

    Label{
        id: mainLabel
        x: 85
        y: 0
        text: "Mouse coordinates"
        styleColor: "#222222"
        color: "white"
        textFormat: Text.AutoText
        font.pointSize: 16
        font.bold: true
        style: Text.Raised
        font.family: "Verdana"
    }
    BoolLabel {
        id: recordingLabel
        width: 210
        anchors.top: mainLabel.bottom
        anchors.topMargin: 20
        anchors.left: trackingLabel.right
        anchors.leftMargin: 20
        label: "Recording"
        fontSize: 12
        onCheckedChanged: {
            if (checked){
                trackingLabel.checked = false;
            }
        }
    }
    BoolLabel {
        id: trackingLabel
        x: 5
        height: 30
        anchors.top: mainLabel.bottom
        anchors.topMargin: 20
        width: 210
        label: "Tracking"
        fontSize: 12
        Component.onCompleted: { checked = true;}
        onCheckedChanged: {
            if (checked){
                recordingLabel.checked = false;
            }
        }
    }
    Grid{
        id: trackingControlsGrid
        spacing: 10
        anchors.top: trackingLabel.bottom
        anchors.topMargin: 20
        anchors.horizontalCenter: trackingLabel.horizontalCenter
        columns: 2
        rows: 2
        CustomLabeledButton{
            width: 80
            height: 30
            label: "Save"
            onClicked: {
                if (trackingLabel.checked){
                    py_tracker.save()
                } else if (recordingLabel.checked){
                    py_recorder.save()
                }
            }
        }
        CustomLabeledButton{
            width: 80
            height: 30
            label: "Update"
            onClicked: {
                if (trackingLabel.checked){
                    positionsView.getData("tracker")
                } else if (recordingLabel.checked){
                    positionsView.getData("recorder")
                }
            }
        }
        CustomLabeledButton{
            width: 80
            height: 30
            label: "Angles"
            onClicked: {
                if (trackingLabel.checked){
                    py_tracker.analyseAngles();
                    analysisImage.reload();
                } else if (recordingLabel.checked){
                    py_recorder.analyseAngles();
                    analysisImage.reload();
                }
            }
        }
        CustomLabeledButton{
            width: 80
            height: 30
            label: "Distances"
            onClicked: {
                if (trackingLabel.checked){
                    py_tracker.analyseDistances();
                    analysisImage2.reload();
                } else if (recordingLabel.checked){
                    py_recorder.analyseDistances();
                    analysisImage2.reload();
                }
            }
        }
    }
    PositionsView {
        id: positionsView
        anchors.top: trackingControlsGrid.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: trackingControlsGrid.horizontalCenter
        function getRow(iface, idx){
            if (iface === "tracker"){
                return py_tracker.getRow(idx);
            } else if (iface === "recorder"){
                return py_recorder.getRow(idx);
            }
        }
    }
    Image {
        id: analysisImage
        x: 235
        y: 85
        width: 512
        height: 256
        source: "image://analysisprovider/img";
        signal rightClicked()

        onRightClicked:{
            if (trackingLabel.checked){
                py_tracker.saveAnglesFig();
            } else if (recordingLabel.checked){
                py_recorder.saveAnglesFig();
            }
        }
        function reload() {
            var oldSource = source;
            source = "";
            source = oldSource;
        }
        sourceSize.width: width
        sourceSize.height: height
        cache: false
        MouseArea{
            anchors.fill: parent
            acceptedButtons: Qt.LeftButton | Qt.RightButton
            onClicked: {
                if (mouse.button == Qt.RightButton){
                    parent.rightClicked()
                }
            }
        }
    }
    Image {
        id: analysisImage2
        x: 235
        y: 333
        width: 512
        height: 256
        source: "image://analysisprovider2/img";
        function reload() {
            var oldSource = source;
            source = "";
            source = oldSource;
        }
        sourceSize.height: height
        sourceSize.width: width
        cache: false
    }
}
