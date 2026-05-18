import QtQuick
import QtQuick.Layouts

Rectangle {
    id: root

    required property var paletteObject
    property string title: ""
    property string value: "—"
    property string hint: ""

    radius: 18
    color: root.paletteObject.surface
    border.color: root.paletteObject.border

    implicitHeight: 118

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 8

        Text {
            text: root.title
            color: root.paletteObject.mutedText
            font.pixelSize: 12
            font.bold: true
        }

        Text {
            text: root.value
            color: root.paletteObject.text
            font.pixelSize: 28
            font.bold: true
        }

        Text {
            Layout.fillWidth: true
            text: root.hint
            color: root.paletteObject.mutedText
            font.pixelSize: 12
            elide: Text.ElideRight
        }
    }
}
