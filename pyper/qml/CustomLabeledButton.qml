import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Private 1.0

Rectangle{
    width: 70
    height: 30
    radius: 5
    antialiasing: true

    property color gradientStart
    gradientStart: "white"
    property color gradientStop
    gradientStop: "black"
    gradient: Gradient {
                GradientStop { position: 0.0; color: gradientStart }
                GradientStop { position: 1.0; color: gradientStop}
            }

    function setOpacity(){ opacity = (0.5 + enabled*0.5)}
    opacity: setOpacity()
    onEnabledChanged: setOpacity()

    property string label
    label: "Button"
    property string tooltip

    signal pressed(real xPosition, real yPosition)
    signal released(real xPosition, real yPosition)
    signal clicked(real xPosition, real yPosition)

    Text{
        id: buttonLabel
        anchors.centerIn: parent
        width: parent.width * 0.8
        height: parent.height * 0.8

        function setOpacity(){ opacity = (0.5 + enabled*0.5) }
        enabled: parent.enabled
        opacity: setOpacity()
        onEnabledChanged: setOpacity()

        font.pixelSize: parent.height * 0.5
        style: Text.Sunken
        color: "white"
        text: parent.label
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        styleColor: "black"
    }

    MouseArea{
        id: behavior
        anchors.fill: parent
        hoverEnabled: true
        enabled: parent.enabled
        onPressed: parent.pressed(mouse.x, mouse.y)
        onReleased: parent.released(mouse.x, mouse.y)
        onClicked: parent.clicked(mouse.x, mouse.y)
        property string tooltip
        tooltip: parent.tooltip
        onExited: Tooltip.hideText()
        onCanceled: Tooltip.hideText()

        Timer {
            interval: 1000
            property string tooltip
            tooltip: parent.tooltip
            running: behavior.containsMouse && tooltip.length
            onTriggered: Tooltip.showText(behavior, Qt.point(behavior.mouseX, behavior.mouseY), tooltip)
        }
    }
}
