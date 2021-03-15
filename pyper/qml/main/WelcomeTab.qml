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
        x: 18
        y: 175
        width: 604
        height: 238

        text: qsTr("This program is is designed to track the path of an object of interest in a live feed from a camera or a recorded video.

Different functionalities are available through the tabs on the left. You can get more information on each tab by pression ctrl+H. Alternatively, follow the tutorial or select the help menu in the top bar.

To get started, please select an existing video using the file menu (ctrl+O) or proceed to record or calibration.")
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
