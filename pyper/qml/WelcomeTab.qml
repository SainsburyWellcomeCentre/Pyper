import QtQuick 2.3
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3

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

    TextArea {
        id: text1
        x: 196
        y: 246
        width: 397
        height: 142

        text: qsTr("Please select an existing video using the file menu or proceed to record or calibration")
        font.family: "Verdana"
        readOnly: true
        horizontalAlignment: Text.AlignHCenter
        font.pixelSize: 18
        style: TextAreaStyle{
            backgroundColor: "#666666"
            textColor: "white"
            selectionColor: "steelblue"
            selectedTextColor: "cyan"
        }
    }
}
