import QtQuick 2.3
import QtQuick.Controls 1.2

import "popup_messages"
import "basic_types"
import "video"
import "roi"
import "style"
import "config"

Rectangle {
    color: theme.background
    anchors.fill: parent

    function reload(){
        trackingControls.reload();
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

                    iconSource: iconHandler.getPath("play.png")
                    pressedSource: iconHandler.getPath("play_pressed.png")
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

                    iconSource: iconHandler.getPath("stop.png")
                    pressedSource: iconHandler.getPath("stop_pressed.png")
                    tooltip: "Stop tracking"

                    onClicked: py_tracker.stop()
                }
            }
        }
        TrackingControls {
            id: trackingControls
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: parent.spacing

            py_interface: py_iface
            parent_py_obj: py_tracker

            visualisationOptions: ["Raw", "Diff", "Mask"]
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

                iconSource: iconHandler.getPath("roi.png")
                pressedSource: iconHandler.getPath("roi_pressed.png")
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

                iconSource: iconHandler.getPath("roi.png")
                pressedSource: iconHandler.getPath("roi_pressed.png")
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
