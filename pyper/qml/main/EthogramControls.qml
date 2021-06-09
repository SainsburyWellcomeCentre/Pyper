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
    id: root
    objectName: itemName.text  // Maybe useless
    height: layoutColumn.height + anchors.margins *2

    anchors.margins: 5

    property alias name: itemName.text
    property string oldName: ""
    property color colour
    property int numericalId
    property string key

    property int idx

    Shortcut {
        id: shortcut
        sequence: root.key
        context: Qt.ApplicationShortcut
        onActivated: {
            py_viewer.switch_ethogram_state("viewerEthogram", idx + 1);    // FIXME: hard coded // TODO: use numericalId + check if can parametrise object
        }
    }

    onNameChanged: {
        pythonObject.rename_structure(oldName, name);
        oldName = name;
        oldName = oldName;  // bind to itself to break the binding
    }

    property bool finished: false  // completed

    property variant pythonObject

    property variant parentWindow

    signal deleteTriggered()
    property bool checked: false

    property ExclusiveGroup exclusiveGroup: null

    function finalise() {
        root.finished = true;
//        if (idx == 0) {
//            itemSelected.checked = true;
//        }
    }

    Component.onCompleted: {
        finalise();
    }


    onExclusiveGroupChanged: {
        if (exclusiveGroup)
            exclusiveGroup.bindCheckable(root)
    }

    Column {
        id: layoutColumn
        anchors.topMargin: 20  // Does not work
        anchors.leftMargin: 10
        anchors.rightMargin: 10
        anchors.left: parent.left
        anchors.right: parent.right
        spacing: 10

        Item {  // spacer
            height: 5
            width: 10
        }

        ColorDialog {
            id: colorDialog
            title: "Please choose a color"
            property color lastColor
            onAccepted: {
                lastColor = colorDialog.color;
                root.colour = color;
                visible = false;
            }
            onRejected: {
                visible = false;
            }
            Component.onCompleted: visible = false;
        }

        Row {
            id: mainRow
            spacing: 5
            anchors.left: parent.left
            anchors.right: parent.right
            Text {
                width: contentWidth
                height: itemName.height
                color: Theme.text
                text: "Behaviour: "
            }

            TextInput {
                id: itemName
                width: 90
                height: 15
                color: Theme.text
                font.bold: true
            }

            Rectangle {
                color: root.colour
                height: itemName.height
                width: height
                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        colorDialog.visible = true;
                    }
                }
                onColorChanged: {
                    Theme.ethogramColours[root.idx + 1] = color
                }
            }
            Text {
                text: "Shortcut: '"
                width: contentWidth
                height: itemName.height
                color: Theme.text
            }
            TextInput {
                id: shortcutValue
                text: root.key
                width: contentWidth
                height: itemName.height
                color: Theme.text
                onTextChanged: {
                    shortcut.sequence = text;
                }
            }
            Text {
                text: "'"
                width: contentWidth
                height: itemName.height
                color: Theme.text
            }


            Item {  // spacer
                height:itemName.height
                width: 60
            }
            CustomLabeledButton {
                width: height
                label: "X"
                onClicked: {
                    root.deleteTriggered();
                }
            }
        }
    }
}
