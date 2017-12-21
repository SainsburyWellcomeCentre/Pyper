import QtQuick 2.3
import QtQuick.Window 2.2
import QtQuick.Controls 1.3
import QtQuick.Controls.Styles 1.3
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2
import QtQuick.Dialogs 1.2

import "../basic_types"
import "../roi"
import "../popup_messages"
import "../style"

ApplicationWindow {
    id: roiShapeWin

    property variant root
    
    flags: Qt.FramelessWindowHint
    color: "transparent"
    visible: false
    
    signal shapeSelected(string newShape)
    onShapeSelected: {
        var currentRoi = root.getCurrentRoi();
        currentRoi.drawingType = newShape;
        close();
    }
    
    function popup(btnCoordsInWin) {
        x = root.x + btnCoordsInWin.x;
        y = root.y + btnCoordsInWin.y;
        visible = true;
    }
    
    Column {
        CustomButton {
            width: 50
            height: width
            iconSource: "../../../resources/icons/ellipse.png"
            onClicked: { roiShapeWin.shapeSelected('ellipse'); }
        }
        CustomButton {
            width: 50
            height: width
            iconSource: "../../../resources/icons/rectangle.png"
            onClicked: { roiShapeWin.shapeSelected('rectangle'); }
        }
        CustomButton {
            width: 50
            height: width
            iconSource: "../../../resources/icons/freehand.png"
            onClicked: { roiShapeWin.shapeSelected('freehand'); }
        }
    }
    
}
