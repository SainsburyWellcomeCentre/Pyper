import QtQuick 2.5
import QtQuick.Controls 1.4

import "../popup_messages"
import "../basic_types"
import "../style"

Rectangle {
    id: background
    color: Theme.background
    anchors.fill: parent

    Label{
        id: mainLabel
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top

        text: "Tracking results"
        styleColor: Theme.darkBackground
        color: Theme.text
        textFormat: Text.AutoText
        font.pointSize: 16
        font.bold: true
        style: Text.Raised
        font.family: Theme.defaultFont
    }
    Row {
        id: referenceLayout
        anchors.margins: 5
        anchors.left: parent.left
        anchors.top: mainLabel.bottom
        anchors.topMargin: 20
        height: 30
        BoolLabel {
            id: trackingLabel
            height: parent.height
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
        BoolLabel {
            id: recordingLabel
            height: parent.height
            width: 210
            label: "Recording"
            fontSize: 12
            onCheckedChanged: {
                if (checked){
                    trackingLabel.checked = false;
                }
            }
        }
    }

    SplitView {
        anchors.margins: 10
        anchors.top: referenceLayout.bottom
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        anchors.right: parent.right

        orientation: Qt.Horizontal

        Column {
            id: controlsLayout

            anchors.left:parent.left
            anchors.topMargin: 20
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            spacing: 10

            Grid {
                id: trackingControlsGrid
                anchors.left: parent.left

                columns: 3
                rows: 2
                spacing: 10
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
                    label: "Save"
                    onClicked: {
                        if (trackingLabel.checked){
                            py_tracker.save(py_iface.get_path())
                        } else if (recordingLabel.checked){
                            py_recorder.save(py_iface.get_dest_path())
                        }
                    }
                }
                CustomLabeledButton{
                    width: 80
                    height: 30
                    label: "Angles"
                    onClicked: {
                        if (trackingLabel.checked){
                            py_tracker.analyse_angles();
                        } else if (recordingLabel.checked){
                            py_recorder.analyse_angles();
                        }
                        analysisImage.reload();
                    }
                }
                CustomLabeledButton{
                    width: 80
                    height: 30
                    label: "Distances"
                    onClicked: {
                        if (trackingLabel.checked){
                            py_tracker.analyse_distances();
                        } else if (recordingLabel.checked){
                            py_recorder.analyse_distances();
                        }
                        analysisImage2.reload();
                    }
                }
                CustomLabeledButton{
                    width: 80
                    height: 30
                    label: "Times"
                    onClicked: {
                        if (trackingLabel.checked){
                            py_tracker.analyse_times();
                        } else if (recordingLabel.checked){
                            py_recorder.analyse_times();
                        }
                        analysisImage.reload();
                        analysisImage2.reload();
                    }
                }
            }
            AnalysisResultsView {
                id: positionsView

                anchors.left: parent.left
                anchors.right: parent.right

                height: parent.height - trackingControlsGrid.height - parent.spacing - 10  // x for parent.margin

                function getRow(iface, idx){
                    if (iface === "tracker"){
                        return py_tracker.get_row(idx);
                    } else if (iface === "recorder"){
                        return py_recorder.get_row(idx);
                    }
                }
            }
        }
        Column{
            id: imageLayout

            width: 512  // default width and height seem necessary for CvImageProvider
            height: 512

            anchors.top: parent.top
            anchors.bottom: parent.bottom
            anchors.left: controlsLayout.right
            anchors.right: parent.right

            Image {
                id: analysisImage

                width: parent.width
                height: parent.height/2

                source: "image://analysisprovider/img";
                signal rightClicked()

                onRightClicked:{
                    if (trackingLabel.checked){
                        py_tracker.save_angles_fig();
                    } else if (recordingLabel.checked){
                        py_recorder.save_angles_fig();
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

                width: parent.width
                height: parent.height/2

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
    }
}
