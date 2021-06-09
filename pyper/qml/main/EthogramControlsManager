import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2

import "../basic_types"
import "../popup_messages"
import "../style"

ApplicationWindow {
    id: root
    width: 430  // FIXME: put in config
    height: 700
    title: "Advanced thresholding"

    property variant pythonObject

    property bool drawingMode: false

//    property list<ThresholdingControlsModel> thresholdingControlsModelsList

    function getCurrentStructure() {
        var idx = getCurrentStructureIndex();
        return structureListRepeater.itemAt(idx);
    }
    function getCurrentStructureIndex() {  // WARNING: returns the first checked item
        for (var i=0; i < structureListRepeater.count; i++) {
            var currentStructure = structureListRepeater.itemAt(i);
            if (currentStructure.checked) {
                return i;
            }
        }
    }

    onClosing: {
    }

    Rectangle {
        id: controls
        anchors.fill: parent
        color: Theme.background

        ExclusiveGroup {
            id: currentStructureExclusiveGroup
        }

        Column {
            id: col

            anchors.topMargin: 10
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            spacing: 10

            Repeater {
                id: structureListRepeater
                model: ListModel {
                    ListElement { name: "mouse"; checked: true}
                    ListElement { name: "cotton"; checked: false}
                }

                onItemAdded:{
                    pythonObject.set_advanced_thresholding
                }
                delegate: AdvancedThresholdingControls {
                    name: model.name  // FIXME: binding
                    idx: index
                    parentWindow: root
                    pythonObject: root.pythonObject

                    exclusiveGroup: currentStructureExclusiveGroup
                    checked: model.checked
                    onDeleteTriggered: {
                        pythonObject.remove_structure(name);
                        structureListRepeater.model.remove(idx);//, 1);
                    }
                }
            }
            CustomLabeledButton {
                label: "+"
                onClicked: {
                    var component = Qt.createComponent("../basic_types/ThresholdingControlsModel.qml");
                    if (component.status == Component.Ready) {
                        var newStructure = component.createObject(root);
                        newStructure.name = "Structure"+structureListRepeater.count;  // FIXME: may colide
                        newStructure.checked = false;
                        structureListRepeater.model.append(newStructure);
                    }
                }
            }
        }
    }
}
