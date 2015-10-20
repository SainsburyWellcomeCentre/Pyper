import QtQuick 2.3
import QtQuick.Controls 1.2

Column {
    enabled: parent.enabled
    anchors.centerIn: parent
    spacing: 5
    width: parent.width - 20
    height: calculateHeight()

    function reload() {
        for(var i=0; i < nChildren; i+=1){
            children[i].reload()
        }
    }

    property int nChildren
    nChildren: children.length

    function calculateHeight(){
        var childrenHeight = 0;
        for (var i=0; i < nChildren; i+=1) {
            childrenHeight += children[i].height;
        }
        return (childrenHeight + spacing * (nChildren -1));
    }
}
