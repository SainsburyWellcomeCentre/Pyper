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
import "style"

ApplicationWindow {
    id: root
    width: 210
    height: 500
    title: "ROI Manager"

    property variant pythonObject

    // FIXME: Do dictionnary
    property alias trackingRoiActive: callbackRoi.roiActive
    property alias restrictionRoiActive: restrictionRoi.roiActive
    property alias trackingRoiColor: callbackRoi.drawingColor
    property alias restrictionRoiColor: restrictionRoi.drawingColor
    property alias trackingRoiShape: callbackRoi.drawingType
    property alias restrictionRoiShape: restrictionRoi.drawingType

    property bool drawingMode: false

    signal drawCallback()
    signal drawRestriction()

    function setRoiOnTop(topRoi, bottomRoi) {  // FIXME: unnecessary with enabled changed
        bottomRoi.z = 9;
        topRoi.z = 10;
        // FIXME: enabled should be sufficient
    }

    onClosing: {
        pythonObject.restore_cursor();
        infoScreen.visible = false;
        roiShapeWin.visible = false;
        callbackRoi.checked = false;
        restrictionRoi.checked = false;
    }

    ApplicationWindow {
        id: roiShapeWin

        flags: Qt.FramelessWindowHint
        color: "transparent"
        visible: false

        function getCurrentRoi() {
            if (callbackRoi.checked) {
                return callbackRoi;
            } else if (restrictionRoi.checked) {
                return restrictionRoi;
            }
        }

        signal shapeSelected(string newShape)
        onShapeSelected: {
            var currentRoi = getCurrentRoi();
            currentRoi.drawingType = newShape;
            close();
        }

        function popup(btnCoordsInWin) {
            x = root.x + btnCoordsInWin.x;
            y = root.y + btnCoordsInWin.y;
            visible = true;
        }

        Column {
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/ellipse.png"
                onClicked: { roiShapeWin.shapeSelected('ellipse'); }
            }
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/rectangle.png"
                onClicked: { roiShapeWin.shapeSelected('rectangle'); }
            }
            CustomButton {
                width: 50
                height: width
                iconSource: "../../../resources/icons/freehand.png"
                onClicked: { roiShapeWin.shapeSelected('freehand'); }
            }
        }

    }

    Rectangle {
        id: controls
        anchors.fill: parent
        color: theme.background

        ColorDialog {
            id: roiColorDialog
            title: "Please pick ROI color"

            color: theme.roiDefault
            showAlphaChannel: false

            onAccepted: {
                if (callbackRoi.checked) {
                    callbackRoi.drawingColor = roiColorDialog.color;
                } else if (restrictionRoi.checked) {
                    restrictionRoi.drawingColor = roiColorDialog.color;
                }  // FIXME: add freehand
                visible = false;
            }
            Component.onCompleted: {
                restrictionRoi.drawingColor = 'red';
                visible = false;
            }
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

                pythonObject: root.pythonObject
                parentWindow: root
                roiColorDialog: roiColorDialog
                exclusiveGroup: currentRoiExclusiveGroup
                checked: true

                onPressed: { root.drawCallback(); }
                onShapeRequest: {
                    var coordsInWin = shapeBtn.mapToItem(controls, 0, 0);
                    roiShapeWin.popup(coordsInWin);
                }
            }
            RoiControls {
                id: restrictionRoi
                name: "Restriction ROI"

                pythonObject: root.pythonObject
                parentWindow: root
                roiColorDialog: roiColorDialog
                exclusiveGroup: currentRoiExclusiveGroup
                checked: false

                drawingType: 'rectangle'
                onPressed: { root.drawRestriction(); }
                onShapeRequest: {
                    var coordsInWin = shapeBtn.mapToItem(controls, 0, 0);
                    roiShapeWin.popup(coordsInWin);
                }
            }

        }
    }
    InfoScreen{
        id: infoScreen
        width: 100
        height: 75

        anchors.right: parent.right
        anchors.bottom: parent.bottom

        text: "Roi mode"
        visible: root.drawingMode
        z: 1
    }
}
