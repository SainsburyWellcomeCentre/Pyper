import QtQuick 2.3
import QtQuick.Controls 1.3
import QtWebKit 3.0


ApplicationWindow {
    id: root
    title: "Help"
    width: 640
    height: 480

    property alias url: webview.url

    visible: false

    WebView {
        id: webview

        anchors.fill: parent

        url: 'http://pyper.readthedocs.io/en/latest/'
    }
}
