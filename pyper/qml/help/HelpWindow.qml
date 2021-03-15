import QtQuick 2.5
import QtQuick.Controls 1.4


ApplicationWindow {
    id: root
    title: "Help"
    width: 640
    height: 480

    property string url: "http://pyper.readthedocs.io/en/latest/"

    visible: false

    Binding {
        id: b1

        property: "url"
        value: root.url
    }


    Loader {
        id: webview
        anchors.fill: parent
        source: "WebKitHelpWindow.qml"

        onStatusChanged: {
            if (webview.progress == 1) {
                if (webview.status == Loader.Error) {  // Finished loading but failed
                    source = "WebEngineHelpWindow.qml";  // try webengine instead
                }
            }
        }
        onLoaded: {
            b1.target = webview.item;
        }
    }
}
