import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Private 1.0

import "../style"

// Used for the tab buttons
Rectangle {
    width: 60
    height: 70

    property string text
    property string textColor
    property string iconSource
    property string tooltip
    property bool active: false
    property bool hovered: false

    signal clicked(real xPosition, real yPosition)
    signal pressed(real xPosition, real yPosition)
    signal released(real xPosition, real yPosition)

    textColor: theme.text
    color: "transparent"

    onActiveChanged: setColor()
    onHoveredChanged: setColor()

    function setColor(){
        if (hovered){
            color = theme.toolButtonHoveredBackground
            textColor = theme.toolButtonText
        } else if (active) {
            color = theme.toolButtonActiveBackground
            textColor = theme.toolButtonNegativeText
        } else {
            color = "transparent"
            textColor = theme.toolButtonText
        }
    }

    Rectangle {
        width: parent.width * 0.8
        height: parent.height * 0.8
        anchors.centerIn: parent

        color: "transparent"

        Image {
            id: toolButtonIcon
            source: parent.parent.iconSource
            width: parent.width
            height: parent.height * 0.8
            anchors.top: parent.top
        }

        Text {
            width: parent.width
            height: parent.height * 0.2

            anchors.top: toolButtonIcon.bottom
            anchors.horizontalCenter: toolButtonIcon.horizontalCenter

            text: parent.parent.text
            horizontalAlignment: Text.AlignHCenter
            font.bold: true
            font.pointSize: 8
            color: parent.parent.textColor

            antialiasing: true
        }

        MouseArea {
            id: behavior
            anchors.fill: parent
            hoverEnabled: true
            onClicked: parent.parent.clicked(mouse.x, mouse.y)
            onPressed: parent.parent.pressed(mouse.x, mouse.y)
            onReleased: parent.parent.released(mouse.x, mouse.y)
            onExited: {
                parent.parent.hovered = false
                Tooltip.hideText()
            }
            onCanceled: Tooltip.hideText()
            onEntered: parent.parent.hovered = true

            Timer {
                interval: 1000
                running: behavior.containsMouse && tooltip.length
                onTriggered: Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), tooltip)
            }
        }
    }
}
