import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "components"

Page {
    id: root

    required property var paletteObject

    background: Rectangle {
        color: root.paletteObject.background
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 18

        PageTitle {
            Layout.fillWidth: true
            paletteObject: root.paletteObject
            title: "О приложении"
            subtitle: "Desktop-клиент клиент-серверной системы анализа очереди заказов."
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 22
            color: root.paletteObject.surface
            border.color: root.paletteObject.border
            implicitHeight: 280

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 10

                Text {
                    text: "Архитектура"
                    color: root.paletteObject.text
                    font.pixelSize: 18
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: "FastAPI-сервер выполняет расчет модели M/M/1. Desktop-клиент на PySide6/QML отправляет параметры на сервер, получает результат и сохраняет историю локально в SQLite через SQLAlchemy."
                    color: root.paletteObject.mutedText
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }

                Text {
                    Layout.fillWidth: true
                    text: "Глобальная база данных на сервере не используется."
                    color: root.paletteObject.mutedText
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }
            }
        }
    }
}
