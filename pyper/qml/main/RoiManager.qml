import QtQuick 2.3
import QtQuick.Window 2.2
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1
import QtQuick.Dialogs 1.2

import "../basic_types"
import "../roi"
import "../popup_messages"
import "../style"

ApplicationWindow {
    id: root
    width: 210
    height: 700
    title: "ROI Manager"

    property variant pythonObject

    property bool drawingMode: false

    property list<RoiControlsModel> roisControlsModelsList

    signal drawRois(int idx)

    function getCurrentRoi() {
        var idx = getCurrentRoiIndex();
        return roiListRepeater.itemAt(idx);
    }
    function getCurrentRoiIndex() {
        for (var i=0; i < roiListRepeater.count; i++) {
            var currentRoi = roiListRepeater.itemAt(i);
            if (currentRoi.checked) {
                return i;
            }
        }
    }
    onDrawRois: {
        for (var i=0; i < roiListRepeater.count; i++) {
            var roiControl = roiListRepeater.itemAt(i);
            if (i === idx) {
                roiControl.sourceRoi.z = 10;
            } else {
                roiControl.sourceRoi.z = 10 - (i + 1);
            }
        }
    }

    onClosing: {
        pythonObject.restore_cursor();
        infoScreen.visible = false;
        roiShapeWin.visible = false;
        for (var i=0; i < roiListRepeater.count; i++) {
            var roiControl = roiListRepeater.itemAt(i);
            roiControl.checked = false;
        }
    }

    RoiShapeWin {
        id: roiShapeWin
        root: root
    }

    Rectangle {
        id: controls
        anchors.fill: parent
        color: theme.background

        ColorDialog {
            id: colorDialog
            title: "Please pick ROI color"

            color: theme.roiDefault
            showAlphaChannel: false

            onAccepted: {
                var currentRoi = root.getCurrentRoi();
                currentRoi.drawingColor = colorDialog.color;
                visible = false;
            }
            visible: false
        }

        ExclusiveGroup {
            id: currentRoiExclusiveGroup
        }

        Column {
            id: col

            anchors.topMargin: 10
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 10

            Repeater {
                id: roiListRepeater
                model: root.roisControlsModelsList

                RoiControls {
                    name: modelData.name
                    drawingColor: modelData.drawingColor
                    drawingType: modelData.drawingType

                    idx: index

                    sourceRoi: modelData.sourceRoi

                    parentWindow: root
                    pythonObject: root.pythonObject
                    roiColorDialog: colorDialog

                    exclusiveGroup: currentRoiExclusiveGroup
                    checked: modelData.checked

                    onPressed: { root.drawRois(idx); }
                    onShapeRequest: {
                        var coordsInWin = shapeBtn.mapToItem(controls, 0, 0);  // FIXME: pass controls and can use embeded
                        roiShapeWin.popup(coordsInWin);
                    }
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
