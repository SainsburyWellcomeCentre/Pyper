import QtQuick 2.3
import QtQuick.Controls 1.2
import QtQuick.Controls.Styles 1.3

TableView{
    x: 10
    y: 140
    width: 180
    height: 400
    alternatingRowColors: true
    sortIndicatorVisible : false

    function getRow(iface, idx){}

    function getData(iface){
        var idx=0;
        var result;
        mod.clear();
        while (true){
            result = getRow(iface, idx);
            if (result === -1){
                break;
            } else if (result === undefined){
                break;
            } else {
                mod.append({"frameId": parseInt(result[0]),
                            "time": result[1],
                            "x": result[2],
                            "y": result[3],
                            "area": result[4],
                            "centerDist": result[5],
                            "borderDist": result[6],
                            "measure": result[7],
                            "inRoi": result[8] == "True"
                           }
                           );
                idx += 1;
            }
        }
    }

    model: ListModel {
        id: mod
        ListElement{ // Necessary to create model with one item at beginnning otherwise all empty (type)
            frameId: 0  // uint
            time: "0.0"
            x: "0.0"  // unsigned float
            y: "0.0"
            area: "0.0"
            centerDist: "-1.0"  // signed float
            boderDist: "-1.0"
            measure: "-1.0"
            inRoi: false
        }
    }
    Component.onCompleted: {
        getData();
    }

    TableViewColumn{
        role: "frameId"
        title: "Frame"
        width: 60
    }
    TableViewColumn{
        role: "time"
        title: "Time"
        width: 60
    }
    TableViewColumn{
        role: "x"
        title: "X"
        width: 60
    }
    TableViewColumn{
        role: "y"
        title: "Y"
        width: 60
    }
    TableViewColumn{
        role: "area"
        title: "Area"
        width: 60
    }
    TableViewColumn{
        role: "centerDist"
        title: "to center"
        width: 60
    }
    TableViewColumn{
        role: "borderDist"
        title: "to border"
        width: 60
    }
    TableViewColumn{
        role: "measure"
        title: "measure"
        width: 60
    }
    TableViewColumn{
        role: "inRoi"
        title: "in roi"
        width: 60
    }
}
