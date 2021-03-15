import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3

import "../popup_messages"
import "../style"

Rectangle {
    id: background
    color: Theme.background
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
        color: Theme.text
        styleColor: Theme.background
        textFormat: Text.AutoText
        font.pointSize: 16
        font.bold: true
        style: Text.Raised
        font.family: Theme.defaultFont
    }

    TextArea {
        id: text1
        x: 196
        y: 246
        width: 397
        height: 142

        text: qsTr("Please select an existing video using the file menu or proceed to record or calibration")
        font.family: Theme.defaultFont
        readOnly: true
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 18
        style: TextAreaStyle{
            backgroundColor: Theme.textBackground
            textColor: Theme.text
        }
    }
}
