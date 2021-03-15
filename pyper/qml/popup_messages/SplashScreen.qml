import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Window 2.2

import "../style"

InfoScreen {
    color: Theme.splashScreenFrameBackground
    border.color: Theme.splashScreenFrameBorder

    BusyIndicator {
        id: indicator
        running: parent.visible
        anchors.centerIn: parent
    }
}
