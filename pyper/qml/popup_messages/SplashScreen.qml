import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Window 2.2

import "../style"

InfoScreen {
    color: theme.splashScreenFrameBackground
    border.color: theme.splashScreenFrameBorder

    BusyIndicator {
        id: indicator
        running: parent.visible
        anchors.centerIn: parent
    }
}
