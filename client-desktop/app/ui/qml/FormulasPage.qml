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
            title: "Формулы модели M/M/1"
            subtitle: "Формулы будут загружаться с FastAPI-сервера через API-клиент desktop-приложения."
        }

        Rectangle {
            Layout.fillWidth: true
            radius: 22
            color: root.paletteObject.surface
            border.color: root.paletteObject.border
            implicitHeight: 260

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 12

                Text {
                    text: "Базовые формулы"
                    color: root.paletteObject.text
                    font.pixelSize: 18
                    font.bold: true
                }

                Text {
                    text: "ρ = λ / μ"
                    color: root.paletteObject.text
                    font.pixelSize: 16
                }

                Text {
                    text: "L = λ / (μ - λ)"
                    color: root.paletteObject.text
                    font.pixelSize: 16
                }

                Text {
                    text: "Wq = λ / (μ × (μ - λ))"
                    color: root.paletteObject.text
                    font.pixelSize: 16
                }

                Text {
                    text: "W = 1 / (μ - λ)"
                    color: root.paletteObject.text
                    font.pixelSize: 16
                }
            }
        }
    }
}
