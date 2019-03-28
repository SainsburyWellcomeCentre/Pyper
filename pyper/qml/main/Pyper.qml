import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3
import QtQuick.Window 2.2
import QtQuick.Layouts 1.2
import QtQml.Models 2.2
import QtGraphicalEffects 1.0
import QtQuick.Dialogs 1.2

import "../popup_messages"
import "../basic_types"
import "../help"
import "../style"
import "../config"


ApplicationWindow {
    id: main
    title: "Pyper"
    width: 880
    height: 750

    menuBar: MenuBar {
        id: pyperTopMenuBar

        Menu {
            title: qsTr("&File")
            MenuItem {
                text: qsTr("&Open")
                shortcut: "Ctrl+O"
                onTriggered: {
                    if (py_iface.open_video()) {
                        infoScreen.flash(2000);
                        if (tabs){
                            if (previewTab) {
                                if (previewTab.wasLoaded) {
                                    previewTab.children[0].reload(); // Using children[0] because direct call doesn't work
                                    previewTab.children[0].disableControls();
                                }
                            }
                            if (trackTab) {
                                if (trackTab.wasLoaded) {
                                    trackTab.children[0].reload(); // Using children[0] because direct call doesn't work
                                }
                            }
                        }
                    }
                }
            }
            MenuItem {
                text: qsTr("Save config to defaults")
                onTriggered: py_iface.write_defaults();
            }
            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
        Menu {
            id: trackingAlgorithmMenu
            objectName: "trackingAlgorithmMenu"
            title: qsTr("Tracking &Method")
            onPopupVisibleChanged: {
                algo1.pythonObject = py_iface;  // Needs to be put here to remove warnings as it does not exist on init
                algo2.pythonObject = py_iface;  // Needs to be put here to remove warnings
                py_editor.scrape_plugins_dir();
            }

            property string lastAddedEndtry
            onLastAddedEndtryChanged: {
                var menuComponent = Qt.createComponent("AlgorithmMenuItem.qml");
                if(menuComponent.status === Component.Ready) {
                    if (lastAddedEndtry == "") {  // skip missing
                        return
                    } // skip if already exists
                    menuComponent.className = lastAddedEndtry;
                    var menuItem = menuComponent.createObject(main);
                    menuItem.className = lastAddedEndtry;
                    menuItem.text = lastAddedEndtry;
                    menuItem.exclusiveGroup = trackingAlgorithmExclusiveGroup;
                    menuItem.checked = false;
                    menuItem.pythonObject = py_iface;
                    insertItem(3, menuItem);
                } else {
                    console.log("Tracking menu item error, status:", menuComponent.status, menuComponent.errorString());
                }

            }

            AlgorithmMenuItem { id: algo1; checked:true; text: "Open field"; className: "GuiTracker"; exclusiveGroup: trackingAlgorithmExclusiveGroup}
            AlgorithmMenuItem { id: algo2; text: "Pupil tracking"; className: "PupilGuiTracker"; exclusiveGroup: trackingAlgorithmExclusiveGroup}

            MenuSeparator { }  // For plugins
            MenuSeparator { }
            MenuItem {
                text: qsTr("Add custom")
                onTriggered: {
                    var codeWindow = Qt.createComponent("CodeWindow.qml");
                    if(codeWindow.status === Component.Ready) {
                        var win = codeWindow.createObject(main);
                        win.algorithmsMenu = trackingAlgorithmMenu;
                        win.algorithmsExclusiveGroup = trackingAlgorithmExclusiveGroup;
                        win.pythonObject = py_iface;
                        win.show();
                    } else {
                        console.log("Code Window error, Status:", codeWindow.status, codeWindow.errorString());
                    }
                }
            }
            MenuSeparator { }
        }
        Menu {
            title: qsTr("&Reference")
            MenuItem {
                text: qsTr("Load")
                onTriggered: { loadRefDialog.visible = true; }
            }
            MenuItem {
                text: qsTr("Save")
                shortcut: "Ctrl+Shift+S"
                onTriggered: { saveRefDialog.visible = true; }
            }
        }

        Menu {
            title: qsTr("&Help")
            MenuItem {
                text: qsTr("Program documentation")
                onTriggered: {
                    helpWindow.url = "http://pyper.readthedocs.io/en/latest/";
                    helpWindow.visible = true;
                }
            }
            MenuItem {
                text: qsTr("Help on current tab")
                shortcut: "Ctrl+h"
                onTriggered: {
                    var currentTab = tabs.getTab(tabs.currentIndex).title;
                    if (currentTab === "Welcome") {
                        helpWindow.url = "http://pyper.readthedocs.io/en/latest/";
                    } else {
                        helpWindow.url = "http://pyper.readthedocs.io/en/latest/usage.html#the-" + currentTab.toLowerCase() + "-tab";
                    }
                    helpWindow.visible = true;
                }
            }
        }
    }
    ExclusiveGroup {
        id: trackingAlgorithmExclusiveGroup
    }

    Row {
        id: allControls
        anchors.fill: parent

        Rectangle {
            id: mainMenuBar
            width: 70
            anchors.top: parent.top
            anchors.bottom: parent.bottom
    //        RadialGradient {
    //            anchors.fill: parent
    //            verticalRadius: parent.height * 2
    //            horizontalRadius: parent.width
    //            gradient: Gradient {
    //                GradientStop {
    //                    position: 0.0;
    //                    color: Theme.background;
    //                }
    //                GradientStop {
    //                    position: 0.5;
    //                    color: Theme.frameBorder;
    //                }
    //            }
    //        }

            Timer {
                id: timer
            }
            function checkPathLoaded(idx){
                if (py_iface.is_path_selected()){
                    tabs.currentIndex = idx;
                } else {
                    errorScreen.flash(2000);
                }
            }

            Image{
               anchors.fill: parent
               source: ImageHandler.getPath("menu_bar.png")
            }
            Column {
                spacing: 15
                anchors.fill: parent
                CustomToolButton{
                    id: welcomeTabBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: welcomeTab.visible

                    text: "Welcome"
                    tooltip: "Switch to welcome mode"
                    iconSource: IconHandler.getPath("welcome.png")
                    onClicked: tabs.currentIndex = 0
                }

                CustomToolButton{
                    id: previewTabBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: previewTab.visible

                    text: "Preview"
                    tooltip: "Switch to preview mode"
                    iconSource: IconHandler.getPath("preview.png")
                    onClicked: { mainMenuBar.checkPathLoaded(1) }
                }
                CustomToolButton{
                    id: trackTabBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: trackTab.visible

                    text: "Track"
                    tooltip: "Switch to tracking mode"
                    iconSource: IconHandler.getPath("track.png")

                    onClicked: { mainMenuBar.checkPathLoaded(2) }
                }
                CustomToolButton{
                    id: recordTabBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: recordTab.visible

                    text: "Record"
                    tooltip: "Switch to recording mode"
                    iconSource: IconHandler.getPath("camera.png")

                    onClicked: { tabs.currentIndex = 3 }
                }
                CustomToolButton{
                    id: calibrationBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: calibrationTab.visible

                    text: "Calibration"
                    tooltip: "Switch to camera calibration mode"
                    iconSource: IconHandler.getPath("calibration.png")

                    onClicked: { tabs.currentIndex = 4 }
                }
                CustomToolButton{
                    id: analysisBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: analysisTab.visible

                    text: "Analyse"
                    tooltip: "Switch to analysis mode"
                    iconSource: IconHandler.getPath("analyse.png")

                    onClicked: { tabs.currentIndex = 5 }
                }
                CustomToolButton{
                    id: transcodeBtn
                    anchors.left: parent.left
                    anchors.right: parent.right
                    height: width * 1.25

                    active: transcodeTab.visible

                    text: "Transcode"
                    tooltip: "Switch to transcode mode\nSelect a video and crop/convert/scale..."
                    iconSource: IconHandler.getPath("transcode.png")

                    onClicked: { tabs.currentIndex = 6 }
                }
            }
        }

        Column {
            anchors.top: parent.top
            anchors.bottom: parent.bottom
            width: parent.width - mainMenuBar.width
            Rectangle {
                id: mainUi
                color: Theme.background
                anchors.left: parent.left
                anchors.right: parent.right

                height: parent.height - log.height

                InfoScreen {
                    id: infoScreen
                    width: 400
                    height: 200
                    text: "Video selected\n Please proceed to preview or tracking"
                    visible: false
                    z: 1
                    anchors.horizontalCenter: parent.horizontalCenter
                    anchors.top: parent.verticalCenter
                }

                ErrorScreen {
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
                        property bool wasLoaded
                        onLoaded: {
                            console.log("Loading preview");
                            wasLoaded = true;
                        }
                    }
                    Tab {
                        id: trackTab
                        title: "Track"
                        TrackerTab {
                            id: trackerWindow
                            objectName: "Tracker"
                        }
                        property bool wasLoaded
                        onLoaded: {wasLoaded = true}
                    }
                    Tab {
                        id: recordTab
                        title: "Record"
                        RecorderTab {
                            id: recorderWindow
                        }
                    }
                    Tab {
                        id: calibrationTab
                        title: "Calibrate"
                        CalibrationTab {
                            id: calibrationWindow
                        }
                    }
                    Tab {
                        id: analysisTab
                        title: "Analyse"
                        AnalysisTab {
                            id: analysisWindow
                        }
                    }

                    Tab {
                        id: transcodeTab
                        title: "Transcode"
                        TranscodeTab {
                            id: transcodeWindow
                        }
                    }
                }
            }
            TextArea {
                id: log
                objectName: "log"
                height: 50
                anchors.left: parent.left
                anchors.right: parent.right
                style: TextAreaStyle{
                    backgroundColor: Theme.textBackground
                    textColor: Theme.text
                    selectionColor: Theme.terminalSelection
                    selectedTextColor: Theme.terminalSelectedText
                }
            }
        }
    }
    FileDialog {
        id: loadRefDialog
        title: "Select reference image"

        selectExisting: true

        nameFilters: [ "Image files (*.jpg *.png)", "All files (*)" ]
        onAccepted: {
            py_iface.set_ref_source(fileUrl);
            visible = false;  // TODO: see if necessary
        }
        onRejected: { }
    }
    FileDialog {
        id: saveRefDialog
        title: "Select reference image"

        selectExisting: false

        nameFilters: [ "Image files (*.jpg *.png)", "All files (*)" ]
        function startsWith(str, prefix) {
            return str.indexOf(prefix, 0) !== -1;
        }
        onAccepted: {
            var currentTabName = tabs.getTab(tabs.currentIndex).title;
            if (startsWith(currentTabName, "Track")) {
                py_tracker.save_ref_source(fileUrl);
            } else if (startsWith(currentTabName, "Record")) {
                py_recorder.save_ref_source(fileUrl);
            } else if (startsWith(currentTabName, "Preview")) {
                py_viewer.save_ref_source(fileUrl);
            } else {
                console.error("Unknown tab " + currentTabName); // FIXME: handle preview
            }

            visible = false;  // TODO: see if necessary
        }
        onRejected: {
            console.log("Save aborted");
        }
    }
    HelpWindow {
        id: helpWindow
    }
}
