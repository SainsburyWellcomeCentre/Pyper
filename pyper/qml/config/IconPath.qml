pragma Singleton
import QtQuick 2.0

Item {
    id: root
    visible: false

    Image {
        id: img
        visible: false
    }

    QtObject {  // For private properties
        id: pathSources
        property string iconDir: '../../../resources/icons/'
        property string iconDir2: '../../resources/icons/'
        function imageExists(imagePath) {
            try {
                img.source = imagePath;
                img.source = "";
                return true;
            } catch(error) {
                console.log("Image not found")
                img.source = "";
                return false;
            }
        }
    }
    function getPath(imageName) {
        if (pathSources.imageExists(pathSources.iconDir + imageName)) {
            return pathSources.iconDir + imageName;
        } else if (pathSources.imageExists(pathSources.iconDir2 + imageName)) {
            return pathSources.iconDir2 + imageName;
        } else {
            return "";
        }
    }
}
