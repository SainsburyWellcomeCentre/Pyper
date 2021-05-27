import QtQuick 2.5
import QtQuick.Controls 1.4

Row {
    id: root
    property variant pythonObj
    property string structureName
    property alias label: lbl.label
    property string thresholdType: "min"
    property string colorMode: "B&W"
    onColorModeChanged: {
        isBlackAndWhite = (colorMode == "B&W")
    }

    anchors.left: parent.left
    anchors.right: parent.right
    spacing: 5
    property bool isBlackAndWhite: true
    onIsBlackAndWhiteChanged: {
        children[1].enabled = !(isBlackAndWhite);
        children[2].enabled = !(isBlackAndWhite);
    }


    function set_value(a, b, c) {
        children[0].value = a;
        children[1].value = b;
        children[2].value = c;
        colorRect.update();
    }

    function send_data(idx) {
        if (root.thresholdType == "min") {
            pythonObj.set_min_threshold(structureName, idx, children[idx].value);  // FIXME: f(colormode)
        } else if (root.thresholdType == "max") {
            pythonObj.set_max_threshold(structureName, idx, children[idx].value);
        }
        colorRect.update();
    }
    function update() {
        var _val;
        if (root.thresholdType == "min") {
            _val = pythonObj.get_min_threshold(structureName);  // FIXME: use update functions
        } else if (root.thresholdType == "max") {
            _val = pythonObj.get_max_threshold(structureName);  // FIXME: use update functions
        }
        set_value(parseInt(_val[0]), parseInt(_val[1]), parseInt(_val[2]));
    }

    IntInput {
        id: lbl
        height: 15
        width: 200
        minimumValue: 0
        maximumValue: 255
        onValueChanged: parent.send_data(0)
    }
    ByteSpinBox {
        onValueChanged: parent.send_data(1)
    }
    ByteSpinBox {
        onValueChanged: parent.send_data(2)
    }
    Rectangle {
        id: colorRect
        height: parent.height
        width: height
        color: getColor();
        signal clicked
        onClicked:{
            pythonObj.chg_cursor("point_hand");
            if (root.thresholdType == "min") {
                pythonObj.set_picking_colour(structureName, true, "thresholdMin");
            } else if (root.thresholdType == "max") {
                pythonObj.set_picking_colour(structureName, true, "thresholdMax");
            }
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                parent.clicked();
            }
        }
        function getColor() {
            var _color;
            if (parent.colorMode == "B&W") {
                _color = Qt.rgba(parent.children[0].value/255, parent.children[0].value/255, parent.children[0].value/255, 1);
            } else if (parent.colorMode == "RGB") {
                _color = Qt.rgba(parent.children[0].value/255, parent.children[1].value/255, parent.children[2].value/255, 1);
            } else if  (parent.colorMode == "BGR") {
                _color = Qt.rgba(parent.children[2].value/255, parent.children[1].value/255, parent.children[0].value/255, 1);
            } else if (parent.colorMode == "HSV") {
                _color = Qt.hsva(parent.children[0].value/255, parent.children[1].value/255, parent.children[2].value/255, 1);
            } else {
                console.log("Unknown color mode " + parent.colorMode + " defaulting to RGB");
                _color = Qt.rgba(parent.children[0].value/255, parent.children[1].value/255, parent.children[2].value/255, 1);
            }
            return _color;
        }
        function update() {
            if (parent.isBlackAndWhite) {
            } else {
                color = getColor();
            }
        }
    }

}
