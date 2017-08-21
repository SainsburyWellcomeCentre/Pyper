import QtQuick 2.3
import QtQuick.Window 2.2
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.2

import "basic_types"
import "roi"
import "popup_messages"

ApplicationWindow {
    id: roiWin
    width: 210
    height: 500
    title: "ROI Manager"

    // FIXME: onClosed exit ROI mode, pythonObject.restore_cursor()
    onClosing: {
        pythonObject.restore_cursor();
        infoScreen.visible = false;
        roiShapeWin.visible = false;
        callbackRoi.checked = false;
        restrictionRoi.checked = false;
    }

    property variant pythonObject
    property variant mouseRoi // FIXME
    property variant restrictionRoi  // FIXME: clash (and only for x/z)

    property alias mouseRoiActive: callbackRoi.roiActive
    property alias restrictionRoiActive: restrictionRoi.roiActive // FIXME:

    property alias trackingRoiColor: callbackRoi.drawingColor
    trackingRoiColor: 'Yellow'  // Default
    property alias restrictionRoiColor: restrictionRoi.drawingColor
    restrictionRoiColor: 'Red'  // Default does not seem to work maybe because of roiCologDialog default

    ApplicationWindow {
        id: roiShapeWin

        flags: Qt.FramelessWindowHint
        color: "transparent"

        property string shape: "ellipse"

        onShapeChanged: {
            if (callbackRoi.checked) {  // FIXME: work with current instead
                callbackRoi.drawingType = shape;
            } else if (restrictionRoi.checked) {
                restrictionRoi.drawingType = shape;
            }
        }

        visible: false
        Column {
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/ellipse.png"  // FIXME: resize
                onClicked: {
                    roiShapeWin.shape = 'ellipse';
                    roiShapeWin.close();
                }
            }
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/rectangle.png"  // FIXME: resize
                onClicked: {
                    roiShapeWin.shape = 'rectangle';
                    roiShapeWin.close();
                }
            }
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/freehand.png"  // FIXME: resize
                onClicked: {
                    roiShapeWin.shape = 'freehand';
                    roiShapeWin.close();
                }
            }
        }

    }

    Rectangle {
        id: controls
        anchors.fill: parent
        color: "#3B3B3B"

        ColorDialog {
            id: roiColorDialog
            title: "Please pick ROI color"

            color: 'Yellow'
            showAlphaChannel: false

            onAccepted: {
                if (callbackRoi.checked) {
                    callbackRoi.drawingColor = roiColorDialog.color;
                } else if (restrictionRoi.checked) {
                    restrictionRoi.drawingColor = roiColorDialog.color;
                }  // FIXME: add freehand

                visible = false;
            }
            Component.onCompleted: visible = false
        }

        ExclusiveGroup {
            id: currentRoiExclusiveGroup
        }

        Column {
            anchors.topMargin: 10
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 10

            RoiControls {
                id: callbackRoi
                name: "Callback ROI"

                pythonObject: roiWin.pythonObject
                infoScreen: infoScreen
                roiColorDialog: roiColorDialog
                exclusiveGroup: currentRoiExclusiveGroup
                checked: true

                onPressed: {
                    roiWin.mouseRoi.z = 10;  // FIXME:
                    roiWin.restrictionRoi.z = 9;
                }
                onShapeRequest: {
                    var coordsInWin = shapeBtn.mapToItem(controls, 0, 0);
                    roiShapeWin.y = roiWin.y + coordsInWin.y;
                    roiShapeWin.x = roiWin.x + coordsInWin.x;
                    roiShapeWin.visible = true;
                }
    //            property alias roiActive: roiActive.checked
            }
            RoiControls {
                id: restrictionRoi
                name: "Restriction ROI"

                pythonObject: roiWin.pythonObject
                infoScreen: infoScreen
                roiColorDialog: roiColorDialog
                exclusiveGroup: currentRoiExclusiveGroup
                checked: false

                drawingType: 'rectangle'
                onPressed: {
                    roiWin.mouseRoi.z = 9;  // FIXME:
                    roiWin.restrictionRoi.z = 10;
                }
                onShapeRequest: {
                    var coordsInWin = shapeBtn.mapToItem(controls, 0, 0);
                    roiShapeWin.y = roiWin.y + coordsInWin.y;
                    roiShapeWin.x = roiWin.x + coordsInWin.x;
                    roiShapeWin.visible = true;
                }
    //            property alias roiActive: roiActive.checked
            }

        }
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
}
