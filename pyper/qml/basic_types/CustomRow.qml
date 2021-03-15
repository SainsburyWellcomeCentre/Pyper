import QtQuick 2.5
import QtQuick.Controls 1.4

Row {
    enabled: parent.enabled
    spacing: 2
    height: parent.height - 20
    width: calculateWidth()

    function reload() {
        for(var i=0; i < nChildren; i+=1){
            children[i].reload()
        }
    }

    property int nChildren
    nChildren: children.length

    function calculateWidth(){
        var childWidth = 0;
        for (var i=0; i < nChildren; i+=1) {
            childWidth += children[i].width;
        }
        return (childWidth + spacing * (nChildren -1));
    }
}
