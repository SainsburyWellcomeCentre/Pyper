import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Private 1.0

CustomLabeledButton{
    width: 60
    height: 70

    property string iconSource
    property string pressedSource
    pressedSource: iconSource

    onPressed: {
        toolButtonIcon.oldSource = iconSource;
        iconSource = pressedSource;
    }
    onReleased: {
        iconSource = toolButtonIcon.oldSource;
    }

    color: "#00000000"
    label: ""

    Image {
        id: toolButtonIcon
        source: parent.iconSource
        antialiasing: true
        anchors.fill: parent

        property string oldSource
        property bool enabled
        enabled: parent.enabled

        function setOpacity(){ opacity = (0.5 + enabled*0.5)}
        opacity: setOpacity()
        onEnabledChanged: setOpacity()
    }
}
