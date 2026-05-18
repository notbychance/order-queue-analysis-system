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
            sensitivityChart.requestPaint()
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
                Layout.preferredHeight: 300
                radius: 22
                color: root.paletteObject.surface
                border.color: root.paletteObject.border

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 10

                    Text {
                        text: "График чувствительности"
                        color: root.paletteObject.text
                        font.pixelSize: 18
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Зависимость среднего числа заказов L от λ при текущем μ."
                        color: root.paletteObject.mutedText
                        font.pixelSize: 12
                    }

                    Canvas {
                        id: sensitivityChart

                        Layout.fillWidth: true
                        Layout.fillHeight: true

                        onPaint: {
                            const ctx = getContext("2d")
                            ctx.reset()

                            const w = width
                            const h = height
                            const pad = 38

                            ctx.fillStyle = root.paletteObject.surfaceMuted
                            ctx.fillRect(0, 0, w, h)

                            ctx.strokeStyle = root.paletteObject.border
                            ctx.lineWidth = 1
                            ctx.beginPath()
                            ctx.moveTo(pad, pad)
                            ctx.lineTo(pad, h - pad)
                            ctx.lineTo(w - pad, h - pad)
                            ctx.stroke()

                            if (!analysisViewModel.hasResult || analysisViewModel.muRate <= 0) {
                                ctx.fillStyle = root.paletteObject.mutedText
                                ctx.font = "14px sans-serif"
                                ctx.textAlign = "center"
                                ctx.fillText("Выполните расчет, чтобы построить график", w / 2, h / 2)
                                return
                            }

                            const mu = analysisViewModel.muRate
                            const maxLambda = mu * 0.95
                            const points = []

                            for (let i = 0; i <= 40; i++) {
                                const lambdaValue = maxLambda * i / 40
                                const lValue = lambdaValue / (mu - lambdaValue)
                                points.push({ lambdaValue, lValue })
                            }

                            const maxY = Math.max(...points.map(p => p.lValue), 1)

                            ctx.strokeStyle = root.paletteObject.primary
                            ctx.lineWidth = 3
                            ctx.beginPath()

                            for (let i = 0; i < points.length; i++) {
                                const p = points[i]
                                const x = pad + (p.lambdaValue / maxLambda) * (w - pad * 2)
                                const y = h - pad - (p.lValue / maxY) * (h - pad * 2)

                                if (i === 0) {
                                    ctx.moveTo(x, y)
                                } else {
                                    ctx.lineTo(x, y)
                                }
                            }

                            ctx.stroke()

                            if (analysisViewModel.lambdaRate < mu) {
                                const currentL = analysisViewModel.lambdaRate / (mu - analysisViewModel.lambdaRate)
                                const currentX = pad + (analysisViewModel.lambdaRate / maxLambda) * (w - pad * 2)
                                const currentY = h - pad - (currentL / maxY) * (h - pad * 2)

                                ctx.fillStyle = root.paletteObject.danger
                                ctx.beginPath()
                                ctx.arc(currentX, currentY, 6, 0, Math.PI * 2)
                                ctx.fill()
                            }

                            ctx.fillStyle = root.paletteObject.mutedText
                            ctx.font = "12px sans-serif"
                            ctx.textAlign = "left"
                            ctx.fillText("L", 12, pad)
                            ctx.textAlign = "right"
                            ctx.fillText("λ", w - 14, h - 10)
                        }
                    }
                }
            }

            Item {
                Layout.preferredHeight: 24
            }
        }
    }
}
