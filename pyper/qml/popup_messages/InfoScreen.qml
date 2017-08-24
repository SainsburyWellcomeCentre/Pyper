import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Window 2.2

import "../style"


Rectangle{
    property alias text: label.text
    property alias fontSize: label.font.pixelSize

    property alias labelAnchors: label.anchors
    property alias labelWidth: label.width

    property bool doFlash: false

    width: 200
    height: 100
    radius: 10
    color: theme.infoScreenFrameBackground
    border.color: theme.infoScreenFrameBorder
    border.width: 2

    function flash(duration) {
        visible = true;
        delay(duration, hide)
    }
    function hide(){
        visible = false
    }
    function delay(interval, routine) {
        timer.interval = interval;
        timer.repeat = false;
        timer.triggered.connect(routine);
        timer.start();
    }

    Label{
        id: label
        width: parent.width * 0.8
        height: parent.height * 0.8
        anchors.centerIn: parent

        font.pixelSize: 15
        color: theme.text
        verticalAlignment: Text.AlignVCenter
        horizontalAlignment: Text.AlignHCenter
        font.bold: true

        visible: parent.visible
    }
}
