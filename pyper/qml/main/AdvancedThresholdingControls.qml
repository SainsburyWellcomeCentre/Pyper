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

    onNameChanged: {
        // console.log("Updating ", oldName, " to ", name);
        pythonObject.rename_structure(oldName, name);
        oldName = name;
        oldName = oldName;  // bind to itself to break the binding
    }

    property int idx
    property bool finished: false  // completed

    property variant pythonObject

    property variant parentWindow

    property alias thresholdSelected: thresholdSelected.checked

    signal deleteTriggered()
    property bool checked: false

    property ExclusiveGroup exclusiveGroup: null

    function finalise() {
        // console.log("Registering " + name);
        pythonObject.set_advanced_thresholding(name);
        root.finished = true;
        thresholdMin.update();
        thresholdMax.update();
        minArea.update();
        maxArea.update();
        nStructures.update();
        if (idx == 0) {
            thresholdSelected.checked = true;
        }
        thresholdMin.isBlackAndWhite = false;  // Hack to force disable controls at the beginning
        thresholdMin.isBlackAndWhite = true;
        thresholdMax.isBlackAndWhite = false;
        thresholdMax.isBlackAndWhite = true;
        pythonObject.register_structure_ctrl(root.name, root);
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

        Item {  // FIXME: just to shift itemName downwards
            height: 5
            width: 10
        }

        Row {
            spacing: 5
            anchors.horizontalCenter: parent.horizontalCenter
            TextInput {
                id: itemName
                width: contentWidth
                height: thresholdSelected.height
                verticalAlignment: Text.AlignVCenter
                color: Theme.text
                // help: a callback function will be triggered when the object enters this ROI
            }
            CheckBox {
                id: thresholdSelected
                text: ""
                onCheckedChanged: {
                    pythonObject.set_enabled(itemName.text, checked);
                    if (checked) {
                        pythonObject.set_object_name(itemName.text);
                    }
                }
            }
            Item {
                height:itemName.height
                width: 200
            }
            CustomLabeledButton {
                width: height
                label: "X"
                onClicked: {
                    root.deleteTriggered();
                }
            }
        }
        Row {
            height: 30
            spacing: 5
            ComboBox {
                width: 170
                height: 25
                id: thresholdingMethods
                model: ListModel {
                    id: cbItems
                    ListElement { text: "B&W" }
                    ListElement { text: "BGR" }
                    ListElement { text: "HSV" }
                    ListElement { text: "RGB" }
                }
                function has_item(elementName) {
                    console.log(elementName);
                    if (elementName == "DEFAULT") {
                        return true;
                    }

                    for (var i = 0; i < model.count; ++i) {
                        var item = cbItems.get(i)
                        if ((item.text == elementName) || (item.text.toLowerCase() == elementName)) {
                            return true;
                        }
                    }
                    return false
                }
                style: ComboBoxStyle {
                    background: Frame {
                        width: parent.width
                        height: parent.height
                        color: Theme.spinBoxBackground
                    }
                    textColor: Theme.text
                    selectedTextColor: 'steelblue'
                    selectionColor: Theme.darkBackground
                }

                onCurrentIndexChanged: {
                    var currentItem = cbItems.get(currentIndex);
                    console.log("Changing item ", currentItem.text);
                    if (currentItem != undefined) {
                        if (root.parentWindow.visible) {
                            pythonObject.set_thresholding_type(root.name, currentItem.text);
                            thresholdMin.colorMode = currentItem.text;
                            thresholdMax.colorMode = currentItem.text;
                        }
                    }
                }
            }
            CustomLabeledButton {
                width: 120
                height: 25
                label: "Update plugins"
                tooltip: "Add a custom tracking method"
                onClicked: {
                    py_editor.scrape_plugins_dir();
                    var plugin_names = py_editor.get_plugin_names().split(";");
                    for (var i=0; i < plugin_names.length; i++) {
                        var plugin_name = plugin_names[i].toUpperCase()
                        if (! (thresholdingMethods.has_item(plugin_name))) {
                            cbItems.append({text: plugin_name});  // FIXME: avoid duplicates (case insensitive)
                        }
                    }
                }
            }
        }
        IntInput {
            id: nStructures
            label: "Nb structs"
            width: 200
            minimumValue: 1
            onValueChanged: {
                if (root.finished) {
                    pythonObject.set_n_structures_max(root.name, value);
                }
            }
            tooltip: "The maximum simultaneous nb of objects with these parameters"
            function update() {
                value = pythonObject.get_n_structures_max(root.name);
            }
        }


        ColorThresholdCtrl {
            id: thresholdMin
            objectName: "thresholdMin"
            label: "Threshold min"
            structureName: root.name
            pythonObj: pythonObject
            thresholdType: "min"
        }
        ColorThresholdCtrl {
            id: thresholdMax
            objectName: "thresholdMax"
            label: "Threshold max"
            structureName: root.name
            pythonObj: pythonObject
            thresholdType: "max"
        }
        Row {
            spacing: 10
            IntInput {
                id: minArea
                label: "Min area"
                width: 200
                minimumValue: 0
                onValueChanged: pythonObject.set_min_area(root.name, value)
                tooltip: "The minimum area of the object in pixels"
                function update() {
                    value = pythonObject.get_min_area(root.name);
                }
            }
            IntInput {
                id: maxArea
                label: "Max area"
                width: 180
                onValueChanged: pythonObject.set_max_area(root.name, value)
                tooltip: "The maximum area of the object in pixels"
                function update() {
                    value = pythonObject.get_max_area(root.name);
                }
            }
        }

//        Row {
//            spacing: 10
//            IntInput {
//                id: movement
//                label: "Max move"
//                width: 200
//                minimumValue: 0
//                onValueChanged: pythonObject.set_max_move(root.name, value)
//                tooltip: "The maximum displacement between subsequent frames in pixels"
//                function update() {
//                    value = pythonObject.get_max_move(root.name);
//                }
//            }
//            IntInput {
//                id: erosion
//                label: "n erosions"
//                width: 180
//                onValueChanged: pythonObject.set_n_erosions(root.name, value)
//                tooltip: "The number of erosion cycles to clean the mask"
//                function update() {
//                    value = pythonObject.get_n_erosions(root.name);
//                }
//            }
//        }
    }
}

/*##^##
Designer {
    D{i:0;autoSize:true;height:480;width:640}
}
##^##*/
