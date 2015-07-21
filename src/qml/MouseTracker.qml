import QtQuick 2.3
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Window 2.2
import QtQuick.Layouts 1.1

ApplicationWindow {
    id: main
    title: "Pyper"
    width: 880
    height: 700

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem {
                text: qsTr("&Open")
                shortcut: "Ctrl+O"
                onTriggered: {
                    py_iface.openVideo();
                    infoScreen.flash(2000);
                }
            }
            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    Rectangle{
        id: mainMenuBar
        width: 70
        height: parent.height

        Timer {
            id: timer
        }
        function checkPathLoaded(idx){
            if (py_iface.isPathSelected()){
                tabs.currentIndex = idx;
            } else {
                errorScreen.flash(2000);
            }
        }

        Image{
           anchors.fill: parent
           source: "../../resources/images/menu_bar.png"
        }

        CustomToolButton{
            id: welcomeTabBtn
            x: 10
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: width * 1.25

            active: welcomeTab.visible

            text: "Welcome"
            tooltip: "Switch to welcome mode"
            iconSource: "../../resources/icons/welcome.png"
            onClicked: tabs.currentIndex = 0
        }

        CustomToolButton{
            id: previewTabBtn
            anchors.top: welcomeTabBtn.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: width * 1.25

            active: previewTab.visible

            text: "Preview"
            tooltip: "Switch to preview mode"
            iconSource: "../../resources/icons/preview.png"
            onClicked: { parent.checkPathLoaded(1) }
        }
        CustomToolButton{
            id: trackTabBtn
            anchors.top: previewTabBtn.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: width * 1.25

            active: trackTab.visible

            text: "Track"
            tooltip: "Switch to tracking mode"
            iconSource: "../../resources/icons/track.png"

            onClicked: { parent.checkPathLoaded(2) }
        }
        CustomToolButton{
            id: recordTabBtn
            anchors.top: trackTabBtn.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: width * 1.25

            active: recordTab.visible

            text: "Record"
            tooltip: "Switch to recording mode"
            iconSource: "../../resources/icons/camera.png"

            onClicked: { tabs.currentIndex = 3 }
        }
        CustomToolButton{
            id: analysisBtn
            anchors.top: recordTabBtn.bottom
            anchors.topMargin: 15
            anchors.horizontalCenter: parent.horizontalCenter
            width: parent.width
            height: width * 1.25

            active: analysisTab.visible

            text: "Analyse"
            tooltip: "Switch to analysis mode"
            iconSource: "../../resources/icons/analyse.png"

            onClicked: { tabs.currentIndex = 4 }
        }
    }
    Rectangle{
        id: mainUi
        color: "#3B3B3B"
        width: parent.width - mainMenuBar.width
        x: mainMenuBar.width
        height: parent.height - log.height

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

        ErrorScreen{
            id: errorScreen
            width: 400
            height: 200
            text: "No video selected"
            visible: false
            z: 1
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.verticalCenter
        }

        TabView {
            id: tabs
            tabsVisible: false
            frameVisible: false
            anchors.fill: parent
            Tab {
                id: welcomeTab
                title: "Welcome"
                WelcomeTab {
                    id: welcomeWindow
                }
            }
            Tab {
                id: previewTab
                title: "Preview"
                PreviewTab {
                    id: previewWindow
                    objectName: "previewWindow"
                }
            }
            Tab {
                id: trackTab
                title: "Track"
                TrackerTab {
                    id: trackerWindow
                    objectName: "Tracker"
                }
            }
            Tab {
                id: recordTab
                title: "Record"
                RecorderTab{
                    id: recorderWindow
                }
            }
            Tab {
                id: analysisTab
                title: "Analyse"
                AnalysisTab{
                    id: analysisWindow
                }
            }

            Tab {
                title: "Transcode"
            }
        }
    }
    TextArea {
        id: log
        objectName: "log"
//        text: ">>>"
        height: 50
        width: parent.width - mainMenuBar.width
        anchors.left:mainMenuBar.right
        anchors.top: mainUi.bottom
        style: TextAreaStyle{
            backgroundColor: "#666666"
            textColor: "#ffffff"
            selectionColor: "steelblue"
            selectedTextColor: "cyan"
        }
    }
}
