import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3
import QtQuick.Controls.Private 1.0

Label {
    property string tooltip: "No help yet"

    MouseArea {
        id: behavior

        anchors.fill: parent
        hoverEnabled: true

        onExited: Tooltip.hideText()
        onCanceled: Tooltip.hideText()

        Timer {
            interval: 1000
            running: behavior.containsMouse && tooltip.length
            onTriggered: Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), tooltip)
        }
    }
}
