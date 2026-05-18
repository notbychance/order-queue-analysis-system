import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    id: root

    required property var paletteObject

    property bool hasResult: false
    property real lambdaRate: 0
    property real muRate: 0
    property string metricKey: "L"

    radius: 18
    color: root.paletteObject.surfaceMuted
    border.color: root.paletteObject.border

    onMetricKeyChanged: chart.requestPaint()
    onHasResultChanged: chart.requestPaint()
    onLambdaRateChanged: chart.requestPaint()
    onMuRateChanged: chart.requestPaint()

    function metricTitle(key) {
        if (key === "L") return "Среднее число заказов L"
        if (key === "Wq") return "Ожидание Wq, ч"
        return "Время в системе W, ч"
    }

    function metricHint(key) {
        if (key === "L") return "L = λ / (μ - λ)"
        if (key === "Wq") return "Wq = λ / (μ × (μ - λ)) × 24"
        return "W = 1 / (μ - λ) × 24"
    }

    function calculateMetric(lambdaValue, muValue, key) {
        if (muValue <= 0 || lambdaValue >= muValue) {
            return null
        }

        if (key === "L") {
            return lambdaValue / (muValue - lambdaValue)
        }

        if (key === "Wq") {
            return (lambdaValue / (muValue * (muValue - lambdaValue))) * 24
        }

        return (1 / (muValue - lambdaValue)) * 24
    }

    function formatAxisValue(value) {
        if (!isFinite(value)) return "—"

        if (value >= 100) return value.toFixed(0)
        if (value >= 10) return value.toFixed(1)
        return value.toFixed(2)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 18
        spacing: 12

        RowLayout {
            Layout.fillWidth: true
            spacing: 12

            ColumnLayout {
                Layout.fillWidth: true
                spacing: 4

                Text {
                    text: root.metricTitle(root.metricKey)
                    color: root.paletteObject.text
                    font.pixelSize: 16
                    font.bold: true
                }

                Text {
                    Layout.fillWidth: true
                    text: root.metricHint(root.metricKey)
                    color: root.paletteObject.mutedText
                    font.pixelSize: 12
                    elide: Text.ElideRight
                }
            }

            RowLayout {
                spacing: 6

                Repeater {
                    model: [
                        { key: "L", title: "L" },
                        { key: "Wq", title: "Wq" },
                        { key: "W", title: "W" }
                    ]

                    delegate: Button {
                        required property var modelData

                        text: modelData.title
                        checkable: true
                        checked: root.metricKey === modelData.key
                        onClicked: root.metricKey = modelData.key

                        contentItem: Text {
                            text: parent.text
                            color: parent.checked ? "white" : root.paletteObject.text
                            font.pixelSize: 12
                            font.bold: parent.checked
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }

                        background: Rectangle {
                            radius: 10
                            color: parent.checked ? root.paletteObject.primary : "transparent"
                            border.color: parent.checked ? root.paletteObject.primary : root.paletteObject.border
                        }
                    }
                }
            }
        }

        Canvas {
            id: chart

            Layout.fillWidth: true
            Layout.fillHeight: true
            antialiasing: true

            onPaint: {
                const ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)

                const w = width
                const h = height
                const padLeft = 58
                const padRight = 24
                const padTop = 22
                const padBottom = 42
                const chartWidth = w - padLeft - padRight
                const chartHeight = h - padTop - padBottom

                ctx.fillStyle = root.paletteObject.surfaceMuted
                ctx.fillRect(0, 0, w, h)

                if (chartWidth <= 0 || chartHeight <= 0) {
                    return
                }

                ctx.strokeStyle = root.paletteObject.border
                ctx.lineWidth = 1

                // Grid
                ctx.beginPath()
                for (let i = 0; i <= 4; i++) {
                    const y = padTop + chartHeight * i / 4
                    ctx.moveTo(padLeft, y)
                    ctx.lineTo(w - padRight, y)
                }

                for (let j = 0; j <= 5; j++) {
                    const x = padLeft + chartWidth * j / 5
                    ctx.moveTo(x, padTop)
                    ctx.lineTo(x, h - padBottom)
                }
                ctx.stroke()

                // Axes
                ctx.strokeStyle = root.paletteObject.mutedText
                ctx.lineWidth = 1.4
                ctx.beginPath()
                ctx.moveTo(padLeft, padTop)
                ctx.lineTo(padLeft, h - padBottom)
                ctx.lineTo(w - padRight, h - padBottom)
                ctx.stroke()

                if (!root.hasResult || root.muRate <= 0) {
                    ctx.fillStyle = root.paletteObject.mutedText
                    ctx.font = "14px sans-serif"
                    ctx.textAlign = "center"
                    ctx.fillText("Выполните расчет, чтобы построить график", w / 2, h / 2)
                    return
                }

                const mu = root.muRate
                const maxLambda = mu * 0.95
                const points = []
                let maxY = 0

                for (let i = 0; i <= 80; i++) {
                    const lambdaValue = maxLambda * i / 80
                    const metricValue = root.calculateMetric(lambdaValue, mu, root.metricKey)

                    if (metricValue === null || !isFinite(metricValue)) {
                        continue
                    }

                    points.push({
                        lambdaValue: lambdaValue,
                        metricValue: metricValue
                    })

                    if (metricValue > maxY) {
                        maxY = metricValue
                    }
                }

                if (points.length === 0 || maxY <= 0) {
                    ctx.fillStyle = root.paletteObject.mutedText
                    ctx.font = "14px sans-serif"
                    ctx.textAlign = "center"
                    ctx.fillText("Недостаточно данных для построения графика", w / 2, h / 2)
                    return
                }

                maxY = maxY * 1.08

                // Y labels
                ctx.fillStyle = root.paletteObject.mutedText
                ctx.font = "11px sans-serif"
                ctx.textAlign = "right"
                ctx.textBaseline = "middle"

                for (let yIndex = 0; yIndex <= 4; yIndex++) {
                    const ratio = yIndex / 4
                    const value = maxY * (1 - ratio)
                    const y = padTop + chartHeight * ratio
                    ctx.fillText(root.formatAxisValue(value), padLeft - 8, y)
                }

                // X labels
                ctx.textAlign = "center"
                ctx.textBaseline = "top"

                for (let xIndex = 0; xIndex <= 5; xIndex++) {
                    const lambdaLabel = maxLambda * xIndex / 5
                    const x = padLeft + chartWidth * xIndex / 5
                    ctx.fillText(root.formatAxisValue(lambdaLabel), x, h - padBottom + 10)
                }

                // Axis titles
                ctx.textAlign = "left"
                ctx.textBaseline = "top"
                ctx.fillText(root.metricKey, 10, padTop)

                ctx.textAlign = "right"
                ctx.fillText("λ", w - 10, h - 18)

                // Curve fill
                const firstPoint = points[0]
                const lastPoint = points[points.length - 1]

                const firstX = padLeft + (firstPoint.lambdaValue / maxLambda) * chartWidth
                const lastX = padLeft + (lastPoint.lambdaValue / maxLambda) * chartWidth
                const bottomY = h - padBottom

                const gradient = ctx.createLinearGradient(0, padTop, 0, bottomY)
                gradient.addColorStop(0, Qt.rgba(37 / 255, 99 / 255, 235 / 255, 0.24))
                gradient.addColorStop(1, Qt.rgba(37 / 255, 99 / 255, 235 / 255, 0.02))

                ctx.beginPath()
                ctx.moveTo(firstX, bottomY)

                for (let pIndex = 0; pIndex < points.length; pIndex++) {
                    const p = points[pIndex]
                    const x = padLeft + (p.lambdaValue / maxLambda) * chartWidth
                    const y = bottomY - (p.metricValue / maxY) * chartHeight
                    ctx.lineTo(x, y)
                }

                ctx.lineTo(lastX, bottomY)
                ctx.closePath()
                ctx.fillStyle = gradient
                ctx.fill()

                // Curve stroke
                ctx.strokeStyle = root.paletteObject.primary
                ctx.lineWidth = 3
                ctx.beginPath()

                for (let lineIndex = 0; lineIndex < points.length; lineIndex++) {
                    const p = points[lineIndex]
                    const x = padLeft + (p.lambdaValue / maxLambda) * chartWidth
                    const y = bottomY - (p.metricValue / maxY) * chartHeight

                    if (lineIndex === 0) {
                        ctx.moveTo(x, y)
                    } else {
                        ctx.lineTo(x, y)
                    }
                }

                ctx.stroke()

                // Critical line near μ
                ctx.strokeStyle = root.paletteObject.warning
                ctx.setLineDash([6, 6])
                ctx.beginPath()
                ctx.moveTo(w - padRight, padTop)
                ctx.lineTo(w - padRight, bottomY)
                ctx.stroke()
                ctx.setLineDash([])

                ctx.fillStyle = root.paletteObject.warning
                ctx.font = "11px sans-serif"
                ctx.textAlign = "right"
                ctx.textBaseline = "bottom"
                ctx.fillText("λ → μ", w - padRight - 4, padTop + 16)

                // Current point
                if (root.lambdaRate >= 0 && root.lambdaRate < mu) {
                    const currentMetric = root.calculateMetric(root.lambdaRate, mu, root.metricKey)

                    if (currentMetric !== null && isFinite(currentMetric)) {
                        const currentLambdaForX = Math.min(root.lambdaRate, maxLambda)
                        const currentX = padLeft + (currentLambdaForX / maxLambda) * chartWidth
                        const currentY = bottomY - Math.min(currentMetric / maxY, 1) * chartHeight

                        ctx.strokeStyle = root.paletteObject.danger
                        ctx.lineWidth = 1.4
                        ctx.setLineDash([4, 4])
                        ctx.beginPath()
                        ctx.moveTo(currentX, padTop)
                        ctx.lineTo(currentX, bottomY)
                        ctx.stroke()
                        ctx.setLineDash([])

                        ctx.fillStyle = root.paletteObject.danger
                        ctx.beginPath()
                        ctx.arc(currentX, currentY, 6, 0, Math.PI * 2)
                        ctx.fill()

                        ctx.fillStyle = root.paletteObject.text
                        ctx.font = "12px sans-serif"
                        ctx.textAlign = currentX > w * 0.72 ? "right" : "left"
                        ctx.textBaseline = "bottom"
                        ctx.fillText(
                            "текущий расчет: " + root.formatAxisValue(currentMetric),
                            currentX + (currentX > w * 0.72 ? -10 : 10),
                            Math.max(currentY - 8, padTop + 16)
                        )
                    }
                } else if (root.lambdaRate >= mu) {
                    ctx.fillStyle = root.paletteObject.danger
                    ctx.font = "13px sans-serif"
                    ctx.textAlign = "center"
                    ctx.textBaseline = "middle"
                    ctx.fillText("Текущая система неустойчива: λ ≥ μ", w / 2, padTop + 20)
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 10

            Rectangle {
                Layout.preferredWidth: 10
                Layout.preferredHeight: 10
                radius: 5
                color: root.paletteObject.primary
            }

            Text {
                Layout.fillWidth: true
                text: "Кривая резко растет при приближении λ к μ: чем выше загрузка, тем быстрее увеличивается очередь и время ожидания."
                color: root.paletteObject.mutedText
                font.pixelSize: 12
                wrapMode: Text.WordWrap
            }
        }
    }
}
