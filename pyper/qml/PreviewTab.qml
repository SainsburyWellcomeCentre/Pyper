import QtQuick 2.3
import QtQuick.Controls 1.2

Rectangle {
    color: "#3B3B3B"
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
        anchors.bottom: previewImage.top
        anchors.bottomMargin: 20
        anchors.horizontalCenter: previewImage.horizontalCenter

        color: "#ffffff"
        text: py_iface.getFileName()
        function reload() {
            text = py_iface.getFileName();
        }

        style: Text.Raised
        font.bold: true
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 14
    }

    Video {
        id: previewImage
        x: 152
        y: 60
        objectName: "preview"
        width: 640
        height: 480

        enabled: false

        source: "image://viewerprovider/img"
        onProgressClicked: py_viewer.seekTo(frameId)
        onProgressWheel: {
            angleDelta /= 120
            var stepSize = vidControl.sliderValue * angleDelta
            py_viewer.move(stepSize)
        }
        Roi{
            anchors.fill: parent
            onReleased: {
                py_tracker.setRoi(roiX, roiY, roiWidth)
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

    VideoControls {
        id: vidControl
        objectName: "previewVidControls"

        anchors.horizontalCenter: loadBtn.horizontalCenter
        y: 100

        enabled: false

        onPlayClicked: { py_viewer.play() }
        onPauseClicked: { py_viewer.pause() }
        onForwardClicked: { py_viewer.move(sliderValue) }
        onBackwardClicked: { py_viewer.move(-sliderValue) }
        onStartClicked: { py_viewer.seekTo(-1) }
        onEndClicked: { py_viewer.seekTo(py_viewer.getNFrames()) }
    }
    Rectangle{
        id: frameControls
        objectName: "viewerFrameControls"
        width: vidControl.width
        height: col.height + 20
        anchors.top: vidControl.bottom
        anchors.topMargin: 10
        anchors.horizontalCenter: vidControl.horizontalCenter

        enabled: false
        function reload(){
            col.reload()
        }

        color: "#4c4c4c"
        radius: 9
        border.width: 3
        border.color: "#7d7d7d"

        CustomColumn {
            id: col

            IntButton {
                width: parent.width
                enabled: parent.enabled
                label: "Ref"
                tooltip: "Select the reference frame"
                text: py_iface.getBgFrameIdx()
                onTextChanged: {
                    py_iface.setBgFrameIdx(text);
                    reload();
                }
                onClicked: { text = py_viewer.getFrameIdx() }
                onEnabledChanged: reload()
                function reload(){ text = py_iface.getBgFrameIdx() }
            }
            IntButton {
                width: parent.width
                enabled: parent.enabled
                label: "Start"
                tooltip: "Select the first data frame"
                text: py_iface.getStartFrameIdx()
                onTextChanged: {
                    py_iface.setStartFrameIdx(text);
                    reload();
                }
                onClicked: { text = py_viewer.getFrameIdx() }
                onEnabledChanged: reload()
                function reload(){ text = py_iface.getStartFrameIdx() }
            }
            IntButton {
                width: parent.width
                enabled: parent.enabled
                label: "End"
                tooltip: "Select the last data frame"
                text: py_iface.getEndFrameIdx()
                onTextChanged: {
                    py_iface.setEndFrameIdx(text);
                    reload();
                }
                onClicked: { text = py_viewer.getFrameIdx() }
                onEnabledChanged: reload()
                function reload(){ text = py_iface.getEndFrameIdx() }
            }
        }
    }
}
