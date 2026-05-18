import QtQuick
import QtQuick.Layouts

ColumnLayout {
    id: root

    required property var paletteObject
    property string title: ""
    property string subtitle: ""

    spacing: 6

    Text {
        text: root.title
        color: root.paletteObject.text
        font.pixelSize: 28
        font.bold: true
    }

    Text {
        Layout.fillWidth: true
        text: root.subtitle
        color: root.paletteObject.mutedText
        font.pixelSize: 14
        wrapMode: Text.WordWrap
    }
}
