import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

import "components"

Page {
    id: root

    required property var paletteObject

    function setInputValues(lambdaRate, muRate) {
        lambdaInput.text = lambdaRate
        muInput.text = muRate
    }

    background: Rectangle {
        color: root.paletteObject.background
    }

    Connections {
        target: analysisViewModel

        function onResultChanged() {
            historyViewModel.loadHistory()
        }
    }

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: root.width
            spacing: 22

            Item {
                Layout.preferredHeight: 1
            }

            PageTitle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                paletteObject: root.paletteObject
                title: "Анализ системы"
                subtitle: "Введите интенсивность поступления заказов λ и интенсивность обслуживания μ. Расчет выполняется на FastAPI-сервере, а история сохраняется локально в SQLite."
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                radius: 22
                color: root.paletteObject.surface
                border.color: root.paletteObject.border

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 18

                    Text {
                        text: "Параметры расчета"
                        color: root.paletteObject.text
                        font.pixelSize: 18
                        font.bold: true
                    }

                    GridLayout {
                        Layout.fillWidth: true
                        columns: 2
                        columnSpacing: 16
                        rowSpacing: 12

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "λ — поступление заказов"
                                color: root.paletteObject.mutedText
                                font.pixelSize: 13
                            }

                            TextField {
                                id: lambdaInput

                                Layout.fillWidth: true
                                placeholderText: "Например: 6"
                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                color: root.paletteObject.text
                                selectedTextColor: "white"
                                selectionColor: root.paletteObject.primary
                            }
                        }

                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: 6

                            Text {
                                text: "μ — обслуживание заказов"
                                color: root.paletteObject.mutedText
                                font.pixelSize: 13
                            }

                            TextField {
                                id: muInput

                                Layout.fillWidth: true
                                placeholderText: "Например: 8"
                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                color: root.paletteObject.text
                                selectedTextColor: "white"
                                selectionColor: root.paletteObject.primary
                            }
                        }
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        visible: analysisViewModel.errorMessage.length > 0
                        radius: 14
                        color: Qt.rgba(220 / 255, 38 / 255, 38 / 255, 0.10)
                        border.color: root.paletteObject.danger

                        Text {
                            anchors.fill: parent
                            anchors.margins: 12
                            text: analysisViewModel.errorMessage
                            color: root.paletteObject.danger
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                        }

                        implicitHeight: visible ? Math.max(48, children[0].implicitHeight + 24) : 0
                    }

                    RowLayout {
                        Layout.fillWidth: true

                        Button {
                            text: analysisViewModel.isLoading ? "Расчет..." : "Рассчитать"
                            enabled: !analysisViewModel.isLoading
                            onClicked: analysisViewModel.analyze(lambdaInput.text, muInput.text)
                        }

                        Button {
                            text: "Очистить"
                            flat: true
                            enabled: !analysisViewModel.isLoading
                            onClicked: {
                                lambdaInput.text = ""
                                muInput.text = ""
                                analysisViewModel.clearResult()
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                        }

                        Text {
                            text: "Единицы: заказов/день"
                            color: root.paletteObject.mutedText
                            font.pixelSize: 12
                        }
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                columns: 3
                columnSpacing: 16
                rowSpacing: 16

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Загрузка клерка"
                    value: analysisViewModel.utilizationPercentText
                    hint: "ρ = λ / μ"
                }

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Среднее число заказов"
                    value: analysisViewModel.averageOrdersText
                    hint: "L = λ / (μ - λ)"
                }

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Время в системе"
                    value: analysisViewModel.averageTimeInSystemText
                    hint: "W = 1 / (μ - λ)"
                }

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Ожидание начала обработки"
                    value: analysisViewModel.averageWaitingTimeText
                    hint: "Wq = λ / (μ × (μ - λ))"
                }

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Состояние системы"
                    value: analysisViewModel.stabilityText
                    hint: "Условие устойчивости: λ < μ"
                }

                MetricCard {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Входные параметры"
                    value: "λ=" + analysisViewModel.lambdaRateText + ", μ=" + analysisViewModel.muRateText
                    hint: "Последний выполненный расчет"
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                radius: 22
                color: root.paletteObject.surface
                border.color: root.paletteObject.border
                implicitHeight: conclusionText.implicitHeight + 52

                Text {
                    id: conclusionText

                    anchors.fill: parent
                    anchors.margins: 22
                    text: analysisViewModel.conclusionText
                    color: root.paletteObject.text
                    font.pixelSize: 14
                    wrapMode: Text.WordWrap
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                Layout.preferredHeight: 390
                radius: 22
                color: root.paletteObject.surface
                border.color: root.paletteObject.border

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 14

                    Text {
                        text: "График чувствительности"
                        color: root.paletteObject.text
                        font.pixelSize: 18
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Переключайте показатель, чтобы увидеть, как очередь и время ожидания изменяются при росте интенсивности поступления заказов."
                        color: root.paletteObject.mutedText
                        font.pixelSize: 12
                        wrapMode: Text.WordWrap
                    }

                    SensitivityChart {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        paletteObject: root.paletteObject
                        hasResult: analysisViewModel.hasResult
                        lambdaRate: analysisViewModel.lambdaRate
                        muRate: analysisViewModel.muRate
                    }
                }
            }

            Item {
                Layout.preferredHeight: 24
            }
        }
    }
}
