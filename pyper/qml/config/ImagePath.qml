pragma Singleton
import QtQuick 2.3

Item {
    id: root
    visible: false

    Image {
        id: img
        visible: false
    }

    QtObject {  // For private properties
        id: pathSources
        property string iconDir: '../../../resources/images/'
    }
    function getPath(imageName) {
        return pathSources.iconDir + imageName;
    }
}
