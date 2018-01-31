import QtQuick 2.5
import QtQuick.Controls 1.4
import QtWebKit 3.0
//import QtWebEngine 1.5


ApplicationWindow {
    id: root
    title: "Help"
    width: 640
    height: 480

    property alias url: webview.url

    visible: false

    WebView {
//    WebEngineView {
        id: webview

        anchors.fill: parent

        url: 'http://pyper.readthedocs.io/en/latest/'
    }
}
