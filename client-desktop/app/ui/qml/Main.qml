import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root

    width: 1180
    height: 760
    minimumWidth: 980
    minimumHeight: 640
    visible: true
    title: appName

    property bool darkMode: themeViewModel.isDark
    property string currentPage: "analysis"

    QtObject {
        id: palette

        readonly property color background: root.darkMode ? "#101827" : "#f4f7fb"
        readonly property color surface: root.darkMode ? "#172033" : "#ffffff"
        readonly property color surfaceMuted: root.darkMode ? "#202b43" : "#edf2f7"
        readonly property color border: root.darkMode ? "#2c3956" : "#d9e2ef"
        readonly property color text: root.darkMode ? "#f8fafc" : "#172033"
        readonly property color mutedText: root.darkMode ? "#a8b3c7" : "#64748b"
        readonly property color primary: "#2563eb"
        readonly property color primaryHover: "#1d4ed8"
        readonly property color success: "#16a34a"
        readonly property color warning: "#f59e0b"
        readonly property color danger: "#dc2626"
    }

    Connections {
        target: historyViewModel

        function onRepeatRequested(lambdaRate, muRate) {
            root.currentPage = "analysis"
            analysisPage.setInputValues(lambdaRate, muRate)
        }
    }

    background: Rectangle {
        color: palette.background
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 68
            color: palette.surface
            border.color: palette.border
            border.width: 1

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 24
                anchors.rightMargin: 24
                spacing: 16

                Rectangle {
                    Layout.preferredWidth: 38
                    Layout.preferredHeight: 38
                    radius: 12
                    color: palette.primary

                    Text {
                        anchors.centerIn: parent
                        text: "λ"
                        color: "white"
                        font.pixelSize: 22
                        font.bold: true
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: appName
                        color: palette.text
                        font.pixelSize: 20
                        font.bold: true
                    }

                    Text {
                        text: "Desktop-клиент анализа одноканальной системы массового обслуживания"
                        color: palette.mutedText
                        font.pixelSize: 12
                    }
                }

                Text {
                    text: "Тема:"
                    color: palette.mutedText
                    font.pixelSize: 12
                }

                ComboBox {
                    id: themeModeSelect

                    Layout.preferredWidth: 150
                    model: themeViewModel.themeOptions
                    textRole: "title"
                    valueRole: "value"
                    currentIndex: themeViewModel.themeIndex

                    onActivated: themeViewModel.setThemeMode(currentValue)

                    contentItem: Text {
                        text: themeModeSelect.displayText
                        color: palette.text
                        font.pixelSize: 13
                        verticalAlignment: Text.AlignVCenter
                        leftPadding: 10
                    }

                    background: Rectangle {
                        radius: 12
                        color: palette.surfaceMuted
                        border.color: palette.border
                    }
                }

                Button {
                    id: themeButton

                    text: themeViewModel.themeButtonText
                    flat: true
                    onClicked: themeViewModel.toggleTheme()

                    contentItem: Text {
                        text: themeButton.text
                        color: palette.text
                        font.pixelSize: 13
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                    }

                    background: Rectangle {
                        radius: 12
                        color: themeButton.hovered ? palette.surfaceMuted : "transparent"
                        border.color: palette.border
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.preferredWidth: 250
                Layout.fillHeight: true
                color: palette.surface
                border.color: palette.border

                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: 16
                    spacing: 10

                    Text {
                        text: "Разделы"
                        color: palette.mutedText
                        font.pixelSize: 12
                        font.bold: true
                    }

                    SidebarButton {
                        text: "Анализ системы"
                        selected: root.currentPage === "analysis"
                        paletteObject: palette
                        onClicked: root.currentPage = "analysis"
                    }

                    SidebarButton {
                        text: "История расчетов"
                        selected: root.currentPage === "history"
                        paletteObject: palette
                        onClicked: {
                            root.currentPage = "history"
                            historyViewModel.loadHistory()
                        }
                    }

                    SidebarButton {
                        text: "Формулы модели"
                        selected: root.currentPage === "formulas"
                        paletteObject: palette
                        onClicked: {
                            root.currentPage = "formulas"
                            formulasViewModel.loadFormulas()
                        }
                    }

                    SidebarButton {
                        text: "О приложении"
                        selected: root.currentPage === "about"
                        paletteObject: palette
                        onClicked: root.currentPage = "about"
                    }

                    Item {
                        Layout.fillHeight: true
                    }

                    Rectangle {
                        Layout.fillWidth: true
                        radius: 16
                        color: palette.surfaceMuted
                        border.color: palette.border

                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 6

                            Text {
                                text: "Локальная история"
                                color: palette.text
                                font.pixelSize: 13
                                font.bold: true
                            }

                            Text {
                                Layout.fillWidth: true
                                text: "Расчеты desktop-клиента сохраняются в SQLite на стороне клиента."
                                color: palette.mutedText
                                font.pixelSize: 12
                                wrapMode: Text.WordWrap
                            }

                            Text {
                                text: "Записей: " + historyViewModel.historyCount
                                color: palette.mutedText
                                font.pixelSize: 12
                            }

                            Text {
                                text: "Тема: " + themeViewModel.themeTitle
                                color: palette.mutedText
                                font.pixelSize: 12
                            }
                        }
                    }
                }
            }

            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: {
                    if (root.currentPage === "analysis") return 0
                    if (root.currentPage === "history") return 1
                    if (root.currentPage === "formulas") return 2
                    return 3
                }

                AnalysisPage {
                    id: analysisPage
                    paletteObject: palette
                }

                HistoryPage {
                    paletteObject: palette
                }

                FormulasPage {
                    paletteObject: palette
                }

                AboutPage {
                    paletteObject: palette
                }
            }
        }
    }

    Component.onCompleted: {
        historyViewModel.loadHistory()
        formulasViewModel.loadFormulas()
    }
}
