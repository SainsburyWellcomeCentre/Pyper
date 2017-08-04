import QtQuick.Controls 1.3

MenuItem {
    text: qsTr("Unknown algorithm")
    property string className
    property variant pythonObject
    checkable: true

    onTriggered: {
        pythonObject.set_tracker_type(className)
    }
}
