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
    objectName: "ethogramControlManager"
    width: 430  // FIXME: put in config
    height: 700
    title: "Ethogram"

    signal selected

    property variant pythonObject
    property variant pythonParams

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
    function addBehaviour(behaviourVars) {  // creates and appends
        if (behaviourVars === undefined) {  // FIXME: check
            behaviourVars = pythonObject.add_behaviour();
        }
        behaviourVars = behaviourVars.split(";");

        var component = Qt.createComponent("../basic_types/EthogramControlsModel.qml");
        if (component.status === Component.Ready) {
            var newBehaviour = component.createObject(root);
            newBehaviour.name = behaviourVars[0];
            newBehaviour.numericalId = parseInt(behaviourVars[1]);
            var col = behaviourVars[2];
            var qColor = Qt.rgba(col[0], col[1], col[2], col[3]);
            newBehaviour.key = behaviourVars[3];
            behaviourListRepeater.model.append(newBehaviour);
        }
    }
    function appendBehaviour(behaviourVars) {  // appends from existing python
        addBehaviour(behaviourVars);
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
                    //ListElement { name: "idle"; numericalId: 1; colour: 'orange'; key: "Ctrl+r"}
                    //ListElement { name: "nesting"; numericalId: 2; colour: 'green'; key: "Ctrl+t"}
                    //ListElement { name: "grooming"; numericalId: 4; colour: 'purple'; key: "Ctrl+g"}
                }

                delegate: EthogramControls {
                    name: model.name
                    idx: index
                    parentWindow: root
                    pythonObject: root.pythonParams

                    // exclusiveGroup: currentBehaviourExclusiveGroup
                    numericalId: model.numericalId
                    colour: Theme.ethogramColours[model.numericalId]
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
                    root.addBehaviour();
                }
            }
        }
    }
}
