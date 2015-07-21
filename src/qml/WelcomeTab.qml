import QtQuick 2.3
import QtQuick.Controls 1.2

Rectangle {
    id: background
    color: "#3B3B3B"
    anchors.fill: parent

    InfoScreen{
        id: infoScreen
        width: 400
        height: 200
        text: "Video selected\n Please proceed to preview or tracking"
        visible: false
        z: 1
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.verticalCenter
    }

    Label{
        id: welcomeMsg
        x: 60
        y: 100
        text: "Welcome to Pyper"
        color: "white"
        styleColor: "#222222"
        textFormat: Text.AutoText
        font.pointSize: 16
        font.bold: true
        style: Text.Raised
        font.family: "Verdana"
    }

    Button {
        id: loadButton
        x: 80
        anchors.top: welcomeMsg.bottom
        anchors.topMargin: 100
        text: "Select video"
        tooltip: "Select the video for 'preview' and 'track'"

        onClicked: {
            py_iface.openVideo();
            infoScreen.flash(2000);
        }
    }
}
//    Button {
//        id: recordButton
//        x: 220
//        anchors.top: welcomeMsg.bottom
//        anchors.topMargin: 100
//        text: "Record"
//    }
