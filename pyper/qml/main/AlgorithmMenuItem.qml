import QtQuick.Controls 1.4

MenuItem {
    text: qsTr("Unknown algorithm")
    property string className
    property variant pythonObject
    checkable: true

    property bool objectSet: false
    onPythonObjectChanged: {
        objectSet = true;
    }

    onTriggered: {
        if (objectSet) {
            pythonObject.set_tracker_type(className);
        }
    }
}
