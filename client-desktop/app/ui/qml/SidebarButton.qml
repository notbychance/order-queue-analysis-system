import QtQuick
import QtQuick.Controls

Button {
    id: control

    required property var paletteObject
    property bool selected: false

    height: 44
    flat: true

    contentItem: Text {
        text: control.text
        color: control.selected ? "white" : control.paletteObject.text
        font.pixelSize: 14
        font.bold: control.selected
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
        leftPadding: 14
    }

    background: Rectangle {
        radius: 14
        color: {
            if (control.selected) return control.paletteObject.primary
            if (control.hovered) return control.paletteObject.surfaceMuted
            return "transparent"
        }
        border.color: control.selected ? control.paletteObject.primary : control.paletteObject.border
        border.width: control.hovered || control.selected ? 1 : 0
    }
}
