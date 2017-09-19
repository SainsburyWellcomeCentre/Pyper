import QtQuick 2.3
import QtQuick.Window 2.2
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.1

import "../style"

ApplicationWindow {
    width: 600
    height: 500
    title: "Pugin code"

    property variant algorithmsExclusiveGroup
    property variant algorithmsMenu
    property variant pythonObject

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem {
                text: qsTr("&Open")
                shortcut: "Ctrl+O"
                onTriggered: {
                    var txt = py_editor.open_plugin_code();
                    if (txt) {
                        document.text = txt;
                    } else {
                        console.log("Empty code, skipping");
                    }
                }
            }
            MenuItem {
                text: qsTr("&Save")
                shortcut: "Ctrl+S"
                onTriggered: {
                    py_editor.save_plugin_code(document.getText(0, document.text.length));
                }
            }
            MenuItem {
                text: qsTr("Export")
                onTriggered: {
                    var cls_name = py_editor.export_code_to_plugins(document.text);
                    var menuComponent = Qt.createComponent("AlgorithmMenuItem.qml");
                    if(menuComponent.status === Component.Ready) {
                        menuComponent.className = cls_name;
                        var menuItem = menuComponent.createObject(main);
                        menuItem.pythonObject = pythonObject;
                        menuItem.className = cls_name;
                        menuItem.text = cls_name;
                        menuItem.exclusiveGroup = algorithmsExclusiveGroup;
                        menuItem.checked = true;
                        algorithmsMenu.insertItem(algorithmsMenu.items.length, menuItem);
                    } else {
                        console.log("Tracking menu item error, status:", menuComponent.status, menuComponent.errorString());
                    }
                }
            }
            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        height: parent.height - 20
        width: parent.width
        color: theme.codeBackground

        TextArea {
            id: document
            anchors.fill: parent
            textFormat: Text.RichText
            wrapMode: TextEdit.Wrap
            text: py_editor.load_plugin_template();
            // FIXME: creates infinite loop
//            onTextChanged: {
//                text = py_editor.highlight_code(getText(0, text.length));
//            }
        }
    }
}
