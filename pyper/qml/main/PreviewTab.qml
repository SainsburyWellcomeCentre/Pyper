import QtQuick 2.5
import QtQuick.Controls 1.4

import "../popup_messages"
import "../basic_types"
import "../video"
import "../roi"
import "../style"

Rectangle {
    color: Theme.background
    anchors.fill: parent

    property bool loaded: false

    function reload(){
        frameControls.reload()
        vidTitle.reload()
    }

    function disableControls() {
        vidControl.enabled = false;
    }

    onVisibleChanged: {
        if (visible){
            reload()
        }
    }

    CustomLabeledButton {
        id: loadBtn
        x: 30
        y: 20
        label: "Load"
        tooltip: "Loads compressed video"
        onPressed:{
            splash.visible = true;
        }
        onReleased:{
            py_viewer.load();
            previewImage.enabled = true;
            splash.visible = false;
            vidControl.enabled = true;
            frameControls.enabled = true;
        }
    }

    Text {
        id: vidTitle
        anchors.top: parent.top
        anchors.topMargin: 10
        anchors.horizontalCenter: previewImage.horizontalCenter
        height: 20

        color: Theme.text
        text: py_iface.get_file_name()
        function reload() {
            text = py_iface.get_file_name();
        }

        style: Text.Raised
        font.bold: true
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 14
    }

    Video {
        id: previewImage
        objectName: "preview"

        width: 640
        height: 480

        anchors.margins: 10
        anchors.left: controlsLayout.right
        anchors.right: parent.right
        anchors.top: vidTitle.bottom
        anchors.bottom: parent.bottom

        enabled: false

        source: "image://viewerprovider/img"
        onProgressClicked: py_viewer.seek_to(frameId)
        onProgressWheel: {
            angleDelta /= 120
            var stepSize = vidControl.sliderValue * angleDelta
            py_viewer.move(stepSize)
        }
        Roi{
            anchors.fill: parent.previewImage
            onReleased: {
                py_tracker.set_roi(roiX, roiY, roiWidth)
            }
        }
    }

    SplashScreen{
        id: splash
        objectName: "splash"
        width: 400
        height: 200
        text: "Loading, please wait."
        z: 1
        visible: false
        anchors.centerIn: previewImage
    }
    ErrorScreen{
        id: videoErrorScreen
        objectName: "viewerVideoLoadingErrorScreen"

        anchors.centerIn: previewImage
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

    Column {
        id: controlsLayout

        anchors.top: loadBtn.bottom
        anchors.topMargin: 100
        anchors.leftMargin: 5
        anchors.left: parent.left

        width: 140

        spacing: 10

        VideoControls {
            id: vidControl
            objectName: "previewVidControls"

            anchors.left: parent.left
            anchors.right: parent.right

            enabled: false

            onPlayClicked: { py_viewer.play() }
            onPauseClicked: { py_viewer.pause() }
            onForwardClicked: { py_viewer.move(sliderValue) }
            onBackwardClicked: { py_viewer.move(-sliderValue) }
            onStartClicked: { py_viewer.seek_to(0) }
            onEndClicked: { py_viewer.seek_to(py_viewer.get_n_frames() - 1) }
        }
        Frame {
            id: frameControls
            objectName: "viewerFrameControls"
            height: col.height + 20

            enabled: false
            function reload(){ col.reload() }

            CustomColumn {
                id: col

                IntButton {
                    width: parent.width
                    enabled: parent.enabled
                    label: "Ref"
                    tooltip: "Select the reference frame"
                    text: py_iface.get_bg_frame_idx()
                    onTextChanged: {
                        py_iface.set_bg_frame_idx(text);
                        reload();
                    }
                    onClicked: { text = py_viewer.get_frame_idx() }
                    onEnabledChanged: reload()
                    function reload(){ text = py_iface.get_bg_frame_idx() }
                }
                IntButton {
                    width: parent.width
                    enabled: parent.enabled
                    label: "Start"
                    tooltip: "Select the first data frame"
                    text: py_iface.get_start_frame_idx()
                    onTextChanged: {
                        py_iface.set_start_frame_idx(text);
                        reload();
                    }
                    onClicked: { text = py_viewer.get_frame_idx() }
                    onEnabledChanged: reload()
                    function reload(){ text = py_iface.get_start_frame_idx() }
                }
                IntButton {
                    width: parent.width
                    enabled: parent.enabled
                    label: "End"
                    tooltip: "Select the last data frame"
                    text: py_iface.get_end_frame_idx()
                    onTextChanged: {
                        py_iface.set_end_frame_idx(text);
                        reload();
                    }
                    onClicked: { text = py_viewer.get_frame_idx() }
                    onEnabledChanged: reload()
                    function reload(){ text = py_iface.get_end_frame_idx() }
                }
            }
        }
    }
}
