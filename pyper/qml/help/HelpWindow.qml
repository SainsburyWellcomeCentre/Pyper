import QtQuick 2.5
import QtQuick.Controls 1.4
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
