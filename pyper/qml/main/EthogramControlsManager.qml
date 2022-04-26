import QtQuick 2.5
import QtQuick.Window 2.2
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2

import "../basic_types"
import "../popup_messages"
import "../style"

Window {
    id: root
    width: 430  // FIXME: put in config
    height: 700
    title: "Ethogram"

    signal selected

    property variant pythonObject

    property bool drawingMode: false

    function getCurrentBehaviour() {
        var idx = getCurrentBehaviourIndex();
        return behaviourListRepeater.itemAt(idx);
    }
    function getCurrentBehaviourIndex() {  // WARNING: returns the first checked item
        for (var i=0; i < behaviourListRepeater.count; i++) {
            var currentBehaviour = behaviourListRepeater.itemAt(i);
            if (currentBehaviour.checked) {
                return i;
            }
        }
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

            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                CustomLabeledButton {
                    label: "Create empty"
                    width: 110
                    onClicked: {
                        py_viewer.create_empty_ethogram("viewerEthogram");  // FIXME: hard coded
                    }
                }
                CustomLabeledButton {
                    label: "Save"
                    width: 110
                    onClicked: {
                        py_viewer.save_ethogram("viewerEthogram");  // FIXME: hard coded
                    }
                }
            }

            Repeater {
                id: behaviourListRepeater
                model: ListModel {
                    ListElement { name: "idle"; numericalId: 1; colour: 'orange'; key: "Ctrl+r"}
                    ListElement { name: "nesting"; numericalId: 2; colour: 'green'; key: "Ctrl+t"}
                    ListElement { name: "grooming"; numericalId: 4; colour: 'purple'; key: "Ctrl+g"}
                }

                delegate: EthogramControls {
                    name: model.name
                    idx: index
                    parentWindow: root
                    pythonObject: root.pythonObject

                    // exclusiveGroup: currentBehaviourExclusiveGroup
                    numericalId: model.numericalId
                    colour: model.colour
                    key: model.key

                    onDeleteTriggered: {
                        pythonObject.remove_behaviour(name, behaviourListRepeater.model.get(idx).numericalId);
                        behaviourListRepeater.model.remove(idx);
                    }
                }
            }
            CustomLabeledButton {
                label: "+"
                onClicked: {
                    var component = Qt.createComponent("../basic_types/EthogramControlsModel.qml");
                    if (component.status == Component.Ready) {
                        var newBehaviour = component.createObject(root);
                        newBehaviour.name = "Behaviour"+behaviourListRepeater.count;  // FIXME : may colide
                        newBehaviour.numericalId = Math.pow(2, behaviourListRepeater.count);
                        newBehaviour.colour = Theme.ethogramColours[behaviourListRepeater.count];
                        newBehaviour.key = toString(behaviourListRepeater.count + 1);
                        behaviourListRepeater.model.append(newBehaviour);
                        pythonObject.add_behaviour(newBehaviour.name, newBehaviour.numericalId);
                    }
                }
            }
        }
    }
}
