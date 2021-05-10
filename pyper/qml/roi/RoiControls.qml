import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2

import "../basic_types"
import "../style"
import "../config"

Frame {
    id: roiLayout
    height: roiLayoutColumn.height + anchors.margins *2

    anchors.margins: 5

    property string name

    property int idx

    property variant pythonObject
    property variant roiColorDialog

    property variant parentWindow

    property alias drawingColor: roi.drawingColor
    property alias drawingType: roi.drawingType

    property alias roiActive: roiActive.checked
    property alias shapeBtn: shapeBtn

    property var sourceRoi

    signal pressed()
    signal shapeRequest()
    property bool checked: false

    property ExclusiveGroup exclusiveGroup: null

    onDrawingTypeChanged: {
        shapeBtn.iconSource = "../../resources/icons/" + drawingType + ".png";  // different folder root
//        shapeBtn.iconSource = IconHandler.getPath(drawingType + ".png");
        changeRoiClass(sourceRoi, drawingType);
    }
    onDrawingColorChanged: {
        sourceRoi.drawingColor = drawingColor;
    }

    function changeRoiClass(roi, roiShape) {
        if (roiShape === "ellipse") {
            roi.source = "EllipseRoi.qml";
        } else if (roiShape === 'rectangle') {
            roi.source = "RectangleRoi.qml";
        } else if (roiShape === 'freehand') {
            roi.source = "FreehandRoi.qml";
        } else {
            console.log("Unrecognised drawing mode: " + roiShape);
        }
    }

    onExclusiveGroupChanged: {
        if (exclusiveGroup)
            exclusiveGroup.bindCheckable(roiLayout)
    }

    Column {
        id: roiLayoutColumn
        anchors.margins: 10
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 10

        Row {
            spacing: 5
            anchors.horizontalCenter: parent.horizontalCenter
            Label {
                width: contentWidth
                height: roiActive.height

                text: roiLayout.name
                verticalAlignment: Text.AlignVCenter
                color: Theme.text
                // help: a callback function will be triggered when the object enters this ROI
            }
            CheckBox {
                id: roiActive
                text: ""
                onCheckedChanged: {
                    roiLayout.sourceRoi.roiActive = checked;
                }
            }
        }

        Row {
            id: roi
            spacing: 5

            property int btnsWidth: 50

            property color drawingColor: Theme.roiDefault
            onDrawingColorChanged: {
                colorBtn.paint();
            }

            property string drawingType: 'ellipse'

            CustomButton {
                id: colorBtn
                width: parent.btnsWidth
                height: width

                tooltip: "Select ROI color"

//                iconSource: "../../../resources/icons/pick_color.png"  // FIXME: change upon selection
                iconSource: IconHandler.getPath("pick_color.png");  // FIXME: change upon selection

                function paint() {
                    canvas.requestPaint();
                }

                onClicked: {
                    roiLayout.checked = true;
                    roiActive.checked = true;
                    roiColorDialog.visible = true;
                }
                Canvas {
                    id: canvas
                    anchors.margins: 10
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.right: parent.right
                    onPaint: {
                        var ctx = getContext('2d');
                        ctx.fillStyle = roi.drawingColor;
                        ctx.fillRect(0, 0, parent.width - 20, parent.height - 20);
                    }
                }
            }
            CustomButton {
                id: shapeBtn

                width: parent.btnsWidth
                height: width
                label: ""

//                iconSource: "../../resources/icons/ellipse.png"
                iconSource: IconHandler.getPath("ellipse.png");

                onClicked: {
                    roiLayout.checked = true;
                    roiActive.checked = true;
                    roiLayout.shapeRequest();
                }
            }
            CustomLabeledButton {
                id: drawBtn
                width: 60
                height: 30

                anchors.verticalCenter: parent.verticalCenter

                label: "Draw"
                property bool isDown: false

                onClicked: {
                    roiLayout.checked = true;
                    roiActive.checked = true;
                    if (isDown) { // already active -> revert
                        roiLayout.pythonObject.restore_cursor();
                        isDown = false;
                        sourceRoi.finalise();
                    } else {  // activate
                        roiLayout.pythonObject.chg_cursor("cross");
                        isDown = true;
                        roiLayout.pressed();
                    }
                    roiLayout.parentWindow.drawingMode = isDown;
                }
            }
        }
        Grid {
            anchors.left: parent.left
            anchors.right: parent.right

            columns: 2
            rows: 2

            spacing: 5
            IntInput {
                label: "x:"
                width: 85
                boxWidth: 65
                tooltip: "Set roi x position"
                value: sourceRoi.roiX
                decimals: 1
                onValueChanged: sourceRoi.roiX = value
            }
            IntInput {
                label: "y:"
                width: 85
                boxWidth: 65
                tooltip: "Set roi x position"
                value: sourceRoi.roiY
                decimals: 1
                onValueChanged: sourceRoi.roiY = value
            }
            IntInput {
                label: "w:"
                width: 85
                boxWidth: 65
                tooltip: "Set roi width"
                value: sourceRoi.roiWidth
                decimals: 1
                onValueChanged: sourceRoi.roiWidth = value
            }
            IntInput {
                label: "h:"
                width: 85
                boxWidth: 65
                tooltip: "Set roi height"
                value: sourceRoi.roiHeight
                decimals: 1
                onValueChanged: sourceRoi.roiHeight = value
            }
        }
        Row {
//            spacing: 5
            property int btnsWidth: 40
            CustomButton {
                id: saveRoiBtn

                width: parent.btnsWidth
                height: width
                anchors.verticalCenter: parent.verticalCenter

//                iconSource: "../../../resources/icons/document-save-as.png"
                iconSource: IconHandler.getPath("document-save-as.png");
                tooltip: "Save ROI"

                onClicked: sourceRoi.save();
            }
            CustomButton {
                id: loadRoiBtn

                width: parent.btnsWidth
                height: width
                anchors.verticalCenter: parent.verticalCenter

//                iconSource: "../../../resources/icons/document-open.png"
                iconSource: IconHandler.getPath("document-open.png");
                tooltip: "Load ROI"

                onClicked: sourceRoi.load();
            }
            CustomButton {
                id: storeRoiBtn

                width: parent.btnsWidth
                height: width
                anchors.verticalCenter: parent.verticalCenter

//                iconSource: "../../../resources/icons/ram.png"
                iconSource: IconHandler.getPath("ram.png");
                tooltip: "Store the ROI in memory"

                onClicked: {
                    var uuid = sourceRoi.store()
                    cbItems.append({text: uuid})
                }
            }
            Column {
                property int btnsWidth: 55
                property int btnsHeight: 25
                CustomLabeledButton {
                    id: loadRoiBatchBtn  // make menu?

                    width: parent.btnsWidth
                    height: parent.btnsHeight

                    label: "load all"
                    tooltip: "Load batch of ROI from file to memory"

                    onClicked: {
                        sourceRoi.loadRoisBatch();
                        while (true) {
                            var uuid = sourceRoi.retrieveNext();
                            if (uuid == undefined) {
                                break;
                            } else if (uuid === -1) {
                                break;
                            } else {
                                cbItems.append({text: uuid})
                            }
                        }
                    }
                }
                CustomLabeledButton {
                    id: saveRoiBatchBtn  // make menu?

                    width: parent.btnsWidth
                    height: parent.btnsHeight

                    label: "save all"
                    tooltip: "Save all ROIs in manager to memory"

                    onClicked: {
                        sourceRoi.saveRoisBatch();
                    }
                }
            }
        }
        ComboBox {
            model: ListModel {
                id: cbItems
            }
            width: 170
            height: 25
            style: ComboBoxStyle {
                background: Frame {
                    width: parent.width
                    height: parent.height
                }
                textColor: Theme.text
            }
            onCurrentIndexChanged: {
                var currentItem = cbItems.get(currentIndex);
                if (currentItem != undefined) {
                    var uuid = currentItem.text;
                    sourceRoi.retrieve(uuid);
                }
            }
        }
    }
}
