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

    Component.onCompleted: historyViewModel.loadHistory()

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 18

        RowLayout {
            Layout.fillWidth: true

            PageTitle {
                Layout.fillWidth: true
                paletteObject: root.paletteObject
                title: "История расчетов"
                subtitle: "Локальная история расчетов desktop-клиента хранится в SQLite."
            }

            Button {
                text: "Обновить"
                enabled: !historyViewModel.isLoading
                onClicked: historyViewModel.loadHistory()
            }

            Button {
                text: "Очистить"
                enabled: historyViewModel.hasHistory && !historyViewModel.isLoading
                onClicked: historyViewModel.clearHistory()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            visible: historyViewModel.errorMessage.length > 0
            radius: 14
            color: Qt.rgba(220 / 255, 38 / 255, 38 / 255, 0.10)
            border.color: root.paletteObject.danger

            Text {
                anchors.fill: parent
                anchors.margins: 12
                text: historyViewModel.errorMessage
                color: root.paletteObject.danger
                font.pixelSize: 13
                wrapMode: Text.WordWrap
            }

            implicitHeight: visible ? Math.max(48, children[0].implicitHeight + 24) : 0
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            radius: 22
            color: root.paletteObject.surface
            border.color: root.paletteObject.border

            Text {
                anchors.centerIn: parent
                visible: !historyViewModel.hasHistory && !historyViewModel.isLoading
                text: "История пока пуста"
                color: root.paletteObject.mutedText
                font.pixelSize: 15
            }

            Text {
                anchors.centerIn: parent
                visible: historyViewModel.isLoading
                text: "Загрузка истории..."
                color: root.paletteObject.mutedText
                font.pixelSize: 15
            }

            ScrollView {
                anchors.fill: parent
                anchors.margins: 18
                visible: historyViewModel.hasHistory
                clip: true

                ColumnLayout {
                    width: parent.width
                    spacing: 12

                    Repeater {
                        model: historyViewModel.historyItems

                        delegate: Rectangle {
                            Layout.fillWidth: true
                            radius: 18
                            color: root.paletteObject.surfaceMuted
                            border.color: root.paletteObject.border
                            implicitHeight: itemLayout.implicitHeight + 28

                            ColumnLayout {
                                id: itemLayout

                                anchors.fill: parent
                                anchors.margins: 14
                                spacing: 10

                                RowLayout {
                                    Layout.fillWidth: true

                                    ColumnLayout {
                                        Layout.fillWidth: true
                                        spacing: 4

                                        RowLayout {
                                            spacing: 8

                                            Text {
                                                text: "λ=" + modelData.lambdaRate + ", μ=" + modelData.muRate
                                                color: root.paletteObject.text
                                                font.pixelSize: 16
                                                font.bold: true
                                            }

                                            Rectangle {
                                                radius: 10
                                                color: modelData.isStable ? Qt.rgba(22 / 255, 163 / 255, 74 / 255, 0.15) : Qt.rgba(220 / 255, 38 / 255, 38 / 255, 0.15)
                                                border.color: modelData.isStable ? root.paletteObject.success : root.paletteObject.danger
                                                implicitWidth: stableText.implicitWidth + 18
                                                implicitHeight: 26

                                                Text {
                                                    id: stableText
                                                    anchors.centerIn: parent
                                                    text: modelData.stabilityText
                                                    color: modelData.isStable ? root.paletteObject.success : root.paletteObject.danger
                                                    font.pixelSize: 12
                                                    font.bold: true
                                                }
                                            }
                                        }

                                        Text {
                                            text: modelData.createdAt
                                            color: root.paletteObject.mutedText
                                            font.pixelSize: 12
                                        }
                                    }

                                    Button {
                                        text: "Повторить"
                                        onClicked: historyViewModel.repeatHistoryItem(modelData.id)
                                    }

                                    Button {
                                        text: "Удалить"
                                        flat: true
                                        onClicked: historyViewModel.deleteHistoryItem(modelData.id)
                                    }
                                }

                                GridLayout {
                                    Layout.fillWidth: true
                                    columns: 4
                                    columnSpacing: 12
                                    rowSpacing: 8

                                    Text {
                                        text: "Загрузка: " + modelData.utilizationPercent
                                        color: root.paletteObject.text
                                        font.pixelSize: 13
                                    }

                                    Text {
                                        text: "L: " + modelData.averageOrders
                                        color: root.paletteObject.text
                                        font.pixelSize: 13
                                    }

                                    Text {
                                        text: "Wq: " + modelData.averageWaitingTimeHours
                                        color: root.paletteObject.text
                                        font.pixelSize: 13
                                    }

                                    Text {
                                        text: "W: " + modelData.averageTimeInSystemHours
                                        color: root.paletteObject.text
                                        font.pixelSize: 13
                                    }
                                }

                                Text {
                                    Layout.fillWidth: true
                                    text: modelData.conclusion
                                    color: root.paletteObject.mutedText
                                    font.pixelSize: 12
                                    wrapMode: Text.WordWrap
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
