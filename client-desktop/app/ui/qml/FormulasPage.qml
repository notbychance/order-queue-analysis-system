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

    Component.onCompleted: formulasViewModel.loadFormulas()

    ScrollView {
        anchors.fill: parent
        clip: true

        ColumnLayout {
            width: root.width
            spacing: 18

            Item {
                Layout.preferredHeight: 1
            }

            RowLayout {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28

                PageTitle {
                    Layout.fillWidth: true
                    paletteObject: root.paletteObject
                    title: "Формулы модели " + formulasViewModel.modelName
                    subtitle: formulasViewModel.description
                }

                Button {
                    text: formulasViewModel.isLoading ? "Загрузка..." : "Обновить"
                    enabled: !formulasViewModel.isLoading
                    onClicked: formulasViewModel.loadFormulas()
                }
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                visible: formulasViewModel.errorMessage.length > 0
                radius: 14
                color: Qt.rgba(220 / 255, 38 / 255, 38 / 255, 0.10)
                border.color: root.paletteObject.danger

                Text {
                    anchors.fill: parent
                    anchors.margins: 12
                    text: formulasViewModel.errorMessage
                    color: root.paletteObject.danger
                    font.pixelSize: 13
                    wrapMode: Text.WordWrap
                }

                implicitHeight: visible ? Math.max(48, children[0].implicitHeight + 24) : 0
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.leftMargin: 28
                Layout.rightMargin: 28
                radius: 22
                color: root.paletteObject.surface
                border.color: root.paletteObject.border
                implicitHeight: 138

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 22
                    spacing: 8

                    Text {
                        text: "Условие устойчивости"
                        color: root.paletteObject.mutedText
                        font.pixelSize: 13
                        font.bold: true
                    }

                    Text {
                        text: formulasViewModel.stabilityCondition
                        color: root.paletteObject.primary
                        font.pixelSize: 32
                        font.bold: true
                    }

                    Text {
                        Layout.fillWidth: true
                        text: "Если условие не выполняется, очередь будет расти неограниченно, и стационарные показатели системы не рассчитываются."
                        color: root.paletteObject.mutedText
                        font.pixelSize: 13
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Repeater {
                model: formulasViewModel.formulaItems

                delegate: Rectangle {
                    Layout.fillWidth: true
                    Layout.leftMargin: 28
                    Layout.rightMargin: 28
                    radius: 22
                    color: root.paletteObject.surface
                    border.color: root.paletteObject.border
                    implicitHeight: formulaLayout.implicitHeight + 44

                    ColumnLayout {
                        id: formulaLayout

                        anchors.fill: parent
                        anchors.margins: 22
                        spacing: 10

                        Text {
                            text: modelData.title
                            color: root.paletteObject.text
                            font.pixelSize: 18
                            font.bold: true
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            radius: 16
                            color: root.paletteObject.surfaceMuted
                            border.color: root.paletteObject.border
                            implicitHeight: 64

                            Text {
                                anchors.centerIn: parent
                                text: modelData.formula
                                color: root.paletteObject.primary
                                font.pixelSize: 24
                                font.bold: true
                            }
                        }

                        Text {
                            Layout.fillWidth: true
                            text: modelData.hint
                            color: root.paletteObject.mutedText
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
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
