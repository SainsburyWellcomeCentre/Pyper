import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Window 2.2

InfoScreen {
    color: "steelblue"
    border.color: "#49afff"

    BusyIndicator {
        id: indicator
        running: parent.visible
        anchors.centerIn: parent
    }
}
