import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: window
    required property QtObject controller
    readonly property color paper: "#fcf4e9"
    readonly property color ink: "#3d1835"
    readonly property color plum: "#692d70"
    readonly property color muted: "#765d70"
    readonly property color lilac: "#f1def3"
    readonly property color card: "#fff9f0"
    readonly property color edge: "#c4a995"
    readonly property color leaf: "#aaba7c"
    readonly property color green: "#dce5ba"
    readonly property color rose: "#af5264"
    readonly property string uiFont: "Malgun Gothic"
    property string selectedDifficulty: ""
    readonly property string drawDifficulty: controller.availableDifficulties.includes(selectedDifficulty)
        ? selectedDifficulty : (controller.availableDifficulties[0] || "")

    width: 490
    height: 602
    minimumWidth: 390
    minimumHeight: 480
    visible: true
    title: "하루 랜덤 미션"
    color: paper
    font.family: uiFont

    component InkText: Text {
        color: window.ink
        font.family: window.uiFont
        font.pixelSize: 14
        verticalAlignment: Text.AlignVCenter
    }

    component PaperButton: Button {
        id: button
        property color fill: window.plum
        property color textColor: "white"
        implicitHeight: 45
        padding: 9
        font.family: window.uiFont
        font.pixelSize: 15
        font.bold: true
        hoverEnabled: true
        contentItem: InkText {
            text: button.text
            font: button.font
            color: button.enabled ? button.textColor : window.muted
            horizontalAlignment: Text.AlignHCenter
        }
        background: Rectangle {
            radius: 9
            color: button.enabled ? button.down ? Qt.darker(button.fill, 1.14)
                : button.hovered ? Qt.darker(button.fill, 1.06) : button.fill : window.green
            border.color: button.visualFocus ? window.ink : "transparent"
            border.width: 2
        }
    }

    component PaperHeading: Item {
        id: heading
        property string title
        implicitWidth: caption.implicitWidth + 86
        implicitHeight: 39
        Doodle {
            anchors.fill: parent
            kind: "heading"
        }
        InkText {
            id: caption
            anchors.centerIn: parent
            text: heading.title
            font.pixelSize: 21
            font.bold: true
        }
    }

    component PageScroll: ScrollView {
        contentWidth: availableWidth
        clip: true
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    }

    Dialog {
        id: missionEditor
        objectName: "missionEditor"
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(405, window.width - 38)
        modal: true
        title: missionId ? "미션 수정" : "미션 추가"
        property string missionId: ""

        function openFor(entry) {
            missionId = entry ? entry.missionId : ""
            contentField.text = entry ? entry.content : ""
            difficultyField.currentIndex = entry ? controller.difficulties.indexOf(entry.difficulty) : 0
            activeField.checked = entry ? entry.active : true
            editError.text = ""
            open()
        }

        onOpened: contentField.forceActiveFocus()
        background: Rectangle { color: window.card; radius: 12; border.color: window.edge }
        contentItem: ColumnLayout {
            spacing: 9
            InkText { text: "미션 내용"; font.bold: true }
            TextField {
                id: contentField
                objectName: "missionContentField"
                Layout.fillWidth: true
                placeholderText: "예: 10분 산책하기"
                maximumLength: 120
                selectByMouse: true
                Accessible.name: "미션 내용"
            }
            InkText { text: "난이도"; font.bold: true }
            ComboBox {
                id: difficultyField
                objectName: "missionDifficultyField"
                Layout.fillWidth: true
                model: controller.difficulties
                Accessible.name: "난이도"
            }
            Switch {
                id: activeField
                objectName: "missionActiveSwitch"
                visible: missionEditor.missionId.length > 0
                text: checked ? "활성화" : "비활성화"
                Accessible.name: "미션 활성화"
            }
            InkText {
                id: editError
                visible: text.length > 0
                Layout.fillWidth: true
                color: window.rose
                wrapMode: Text.Wrap
            }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                PaperButton { text: "취소"; fill: window.lilac; textColor: window.ink; onClicked: missionEditor.close() }
                PaperButton {
                    objectName: "saveMissionButton"
                    text: "저장"
                    enabled: contentField.text.trim().length > 0
                    onClicked: {
                        editError.text = controller.saveMission(
                            missionEditor.missionId, contentField.text, difficultyField.currentText, activeField.checked
                        )
                        if (!editError.text)
                            missionEditor.close()
                    }
                }
            }
        }
    }

    Dialog {
        id: deleteDialog
        objectName: "deleteMissionDialog"
        parent: Overlay.overlay
        anchors.centerIn: parent
        width: Math.min(405, window.width - 38)
        modal: true
        title: "미션 삭제"
        property string missionId: ""
        property string missionContent: ""

        function openFor(entry) {
            missionId = entry.missionId
            missionContent = entry.content
            deleteError.text = ""
            open()
        }

        background: Rectangle { color: window.card; radius: 12; border.color: window.edge }
        contentItem: ColumnLayout {
            spacing: 11
            InkText {
                Layout.fillWidth: true
                text: "‘" + deleteDialog.missionContent + "’ 미션을 삭제할까요?"
                wrapMode: Text.Wrap
                font.bold: true
            }
            InkText {
                Layout.fillWidth: true
                text: "이미 저장된 추첨과 완료 기록은 유지됩니다."
                wrapMode: Text.Wrap
                color: window.muted
            }
            InkText {
                id: deleteError
                visible: text.length > 0
                Layout.fillWidth: true
                wrapMode: Text.Wrap
                color: window.rose
            }
            RowLayout {
                Layout.alignment: Qt.AlignRight
                PaperButton { text: "취소"; fill: window.lilac; textColor: window.ink; onClicked: deleteDialog.close() }
                PaperButton {
                    objectName: "confirmDeleteButton"
                    text: "삭제"
                    fill: window.rose
                    onClicked: {
                        deleteError.text = controller.deleteMission(deleteDialog.missionId)
                        if (!deleteError.text)
                            deleteDialog.close()
                    }
                }
            }
        }
    }

    Timer {
        interval: 15000
        repeat: true
        running: true
        onTriggered: controller.checkDate()
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 120

            Row {
                id: brand
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: 17
                spacing: 6
                InkText {
                    text: "하루 랜덤 미션"
                    height: 49
                    font.pixelSize: 31
                    font.bold: true
                    font.letterSpacing: -0.6
                    Doodle {
                        width: 148
                        height: 9
                        anchors.top: parent.bottom
                        kind: "underline"
                    }
                }
                Doodle { width: 55; height: 53; kind: "dice" }
            }

            Item {
                width: 146
                height: 29
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.bottom: parent.bottom
                anchors.bottomMargin: 11
                Doodle { anchors.fill: parent; kind: "tape" }
                InkText {
                    anchors.centerIn: parent
                    text: controller.today
                    font.pixelSize: 13
                    font.bold: true
                }
            }

            Doodle {
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.bottom: parent.bottom
                height: 7
                kind: "seam"
            }
        }

        TabBar {
            id: tabs
            Layout.fillWidth: true
            Layout.leftMargin: 21
            Layout.rightMargin: 21
            Layout.topMargin: 8
            spacing: 5
            background: Item {}
            onCurrentIndexChanged: controller.refresh()

            Repeater {
                model: ["오늘의 미션", "미션관리", "기록"]
                delegate: TabButton {
                    id: tab
                    required property string modelData
                    required property int index
                    objectName: ["todayTab", "catalogTab", "historyTab"][index]
                    text: modelData
                    implicitHeight: 39
                    font.pixelSize: 14
                    font.bold: true
                    contentItem: InkText {
                        text: tab.text
                        font: tab.font
                        color: tab.checked ? "white" : window.ink
                        horizontalAlignment: Text.AlignHCenter
                    }
                    background: Rectangle {
                        radius: 7
                        color: tab.checked ? window.plum : window.lilac
                        border.color: tab.visualFocus ? window.ink : "transparent"
                        border.width: 2
                    }
                }
            }
        }

        RowLayout {
            visible: controller.error.length > 0
            Layout.fillWidth: true
            Layout.margins: 13
            InkText {
                Layout.fillWidth: true
                text: controller.error
                wrapMode: Text.WordWrap
                color: window.rose
            }
            PaperButton { text: "다시 시도"; onClicked: controller.refresh() }
        }

        StackLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 21
            Layout.topMargin: 16
            currentIndex: tabs.currentIndex

            PageScroll {
                objectName: "todayPage"
                ColumnLayout {
                    width: parent.width
                    spacing: 10

                    PaperHeading {
                        Layout.alignment: Qt.AlignHCenter
                        title: controller.daily.missionId ? "오늘의 미션" : "난이도 선택"
                    }

                    ColumnLayout {
                        visible: !controller.daily.missionId
                        Layout.fillWidth: true
                        spacing: 8
                        ButtonGroup { id: difficultyGroup }

                        Repeater {
                            model: controller.difficulties
                            delegate: RadioButton {
                                id: option
                                required property string modelData
                                required property int index
                                objectName: "difficulty" + index
                                ButtonGroup.group: difficultyGroup
                                Layout.fillWidth: true
                                text: modelData
                                enabled: controller.availableDifficulties.includes(modelData)
                                checked: window.drawDifficulty === modelData
                                onClicked: window.selectedDifficulty = modelData
                                implicitHeight: 52
                                leftPadding: 16
                                font.pixelSize: 17
                                font.bold: true
                                indicator: Rectangle {
                                    x: option.leftPadding
                                    y: (option.height - height) / 2
                                    width: 18
                                    height: width
                                    radius: width / 2
                                    color: "transparent"
                                    border.width: 1.7
                                    border.color: option.checked ? "#903fa3" : window.muted
                                    Rectangle {
                                        anchors.centerIn: parent
                                        width: 10
                                        height: width
                                        radius: width / 2
                                        color: "#903fa3"
                                        visible: option.checked
                                    }
                                }
                                contentItem: InkText {
                                    text: option.text
                                    font: option.font
                                    color: option.enabled ? window.ink : window.muted
                                    leftPadding: 31
                                }
                                background: Rectangle {
                                    radius: 8
                                    color: option.checked ? window.lilac : window.card
                                    border.color: option.checked || option.visualFocus ? "#9f55ac" : window.edge
                                    border.width: option.checked || option.visualFocus ? 1.5 : 1
                                }
                            }
                        }

                        PaperButton {
                            objectName: "drawButton"
                            Layout.fillWidth: true
                            Layout.topMargin: 6
                            implicitHeight: 51
                            font.pixelSize: 17
                            text: "오늘의 미션 뽑기"
                            enabled: window.drawDifficulty.length > 0
                            onClicked: controller.pick(window.drawDifficulty)
                        }
                        InkText {
                            Layout.fillWidth: true
                            visible: !window.drawDifficulty
                            text: "추첨할 수 있는 활성 미션이 없어요. 미션관리에서 추가하거나 활성화해 주세요."
                            wrapMode: Text.Wrap
                            color: window.muted
                        }
                    }

                    ColumnLayout {
                        visible: !!controller.daily.missionId
                        Layout.fillWidth: true
                        spacing: 9

                        Rectangle {
                            Layout.fillWidth: true
                            implicitHeight: result.implicitHeight + 32
                            radius: 12
                            color: window.card
                            border.color: window.edge
                            ColumnLayout {
                                id: result
                                width: parent.width - 28
                                anchors.centerIn: parent
                                spacing: 6

                                Doodle {
                                    Layout.alignment: Qt.AlignHCenter
                                    Layout.preferredWidth: 116
                                    Layout.preferredHeight: 101
                                    kind: controller.daily.missionId === "basic-01" ? "water" : "dice"
                                }
                                Rectangle {
                                    Layout.alignment: Qt.AlignHCenter
                                    implicitWidth: difficultyText.implicitWidth + 27
                                    implicitHeight: 27
                                    radius: 7
                                    color: window.green
                                    InkText {
                                        id: difficultyText
                                        anchors.centerIn: parent
                                        text: controller.daily.difficulty || ""
                                        font.bold: true
                                    }
                                }
                                InkText {
                                    objectName: "missionText"
                                    Layout.fillWidth: true
                                    text: controller.daily.content || ""
                                    horizontalAlignment: Text.AlignHCenter
                                    wrapMode: Text.Wrap
                                    font.pixelSize: 25
                                    font.bold: true
                                }
                            }
                        }

                        PaperButton {
                            objectName: "completeButton"
                            Layout.alignment: Qt.AlignHCenter
                            text: controller.daily.completed ? "완료됨" : "미션 완료"
                            enabled: !controller.daily.completed
                            onClicked: controller.complete()
                        }

                        InkText {
                            Layout.alignment: Qt.AlignHCenter
                            text: controller.daily.completed ? "완료 도장이 찍혔어요!" : "오늘의 미션이 저장됐어요."
                            color: window.muted
                        }
                    }
                }
            }

            PageScroll {
                objectName: "catalogPage"
                ColumnLayout {
                    width: parent.width
                    spacing: 9
                    PaperHeading {
                        Layout.alignment: Qt.AlignHCenter
                        title: "미션 관리"
                    }
                    PaperButton {
                        objectName: "addMissionButton"
                        Layout.alignment: Qt.AlignRight
                        text: "미션 추가"
                        onClicked: missionEditor.openFor(null)
                    }
                    InkText {
                        visible: controller.catalog.length === 0
                        Layout.alignment: Qt.AlignHCenter
                        text: "등록된 미션이 없어요."
                        color: window.muted
                    }
                    Repeater {
                        model: controller.catalog
                        delegate: Rectangle {
                            id: entry
                            required property var modelData
                            Layout.fillWidth: true
                            implicitHeight: entryRow.implicitHeight + 18
                            color: window.card
                            border.color: window.edge
                            radius: 9

                            RowLayout {
                                id: entryRow
                                width: parent.width - 20
                                anchors.centerIn: parent
                                spacing: 6
                                ColumnLayout {
                                    Layout.fillWidth: true
                                    spacing: 3
                                    InkText {
                                        Layout.fillWidth: true
                                        text: entry.modelData.content
                                        wrapMode: Text.Wrap
                                        font.bold: true
                                    }
                                    InkText {
                                        text: entry.modelData.difficulty + (entry.modelData.active ? " · 활성" : " · 비활성")
                                        color: entry.modelData.active ? window.plum : window.muted
                                        font.pixelSize: 12
                                    }
                                }
                                PaperButton {
                                    objectName: "edit-" + entry.modelData.missionId
                                    text: "수정"
                                    implicitHeight: 34
                                    fill: window.lilac
                                    textColor: window.ink
                                    onClicked: missionEditor.openFor(entry.modelData)
                                }
                                PaperButton {
                                    objectName: "delete-" + entry.modelData.missionId
                                    text: "삭제"
                                    implicitHeight: 34
                                    fill: window.lilac
                                    textColor: window.rose
                                    onClicked: deleteDialog.openFor(entry.modelData)
                                }
                            }
                        }
                    }
                }
            }

            PageScroll {
                objectName: "historyPage"
                ColumnLayout {
                    width: parent.width
                    spacing: 10
                    PaperHeading {
                        Layout.alignment: Qt.AlignHCenter
                        title: "날짜별 미션 기록"
                    }

                    Rectangle {
                        objectName: "historyCalendar"
                        Layout.fillWidth: true
                        implicitHeight: calendarBody.implicitHeight + 18
                        color: window.card
                        border.color: window.edge
                        radius: 10

                        ColumnLayout {
                            id: calendarBody
                            width: parent.width - 22
                            anchors.centerIn: parent
                            spacing: 4
                            RowLayout {
                                Layout.fillWidth: true
                                PaperButton {
                                    objectName: "previousMonth"
                                    Layout.preferredWidth: 36
                                    implicitHeight: 33
                                    text: "‹"
                                    fill: window.lilac
                                    textColor: window.ink
                                    Accessible.name: "이전 달"
                                    onClicked: controller.changeMonth(-1)
                                }
                                InkText {
                                    Layout.fillWidth: true
                                    text: controller.monthTitle
                                    font.bold: true
                                    horizontalAlignment: Text.AlignHCenter
                                }
                                PaperButton {
                                    objectName: "nextMonth"
                                    Layout.preferredWidth: 36
                                    implicitHeight: 33
                                    text: "›"
                                    fill: window.lilac
                                    textColor: window.ink
                                    Accessible.name: "다음 달"
                                    onClicked: controller.changeMonth(1)
                                }
                            }
                            GridLayout {
                                Layout.fillWidth: true
                                columns: 7
                                columnSpacing: 3
                                rowSpacing: 2
                                Repeater {
                                    model: "월화수목금토일".split("")
                                    delegate: InkText {
                                        required property string modelData
                                        Layout.fillWidth: true
                                        Layout.preferredWidth: 1
                                        text: modelData
                                        color: window.muted
                                        font.pixelSize: 11
                                        horizontalAlignment: Text.AlignHCenter
                                    }
                                }
                                Repeater {
                                    model: controller.calendarDays
                                    delegate: Rectangle {
                                        id: dayCell
                                        required property var modelData
                                        Layout.fillWidth: true
                                        Layout.preferredWidth: 1
                                        Layout.preferredHeight: 24
                                        radius: 4
                                        color: modelData.today ? window.lilac : "transparent"

                                        InkText {
                                            anchors.centerIn: parent
                                            text: dayCell.modelData.number
                                                ? dayCell.modelData.number + (dayCell.modelData.completed ? " ✓" : "") : ""
                                            font.pixelSize: 12
                                            font.bold: dayCell.modelData.today || dayCell.modelData.completed
                                            color: dayCell.modelData.completed ? window.rose : window.ink
                                        }
                                    }
                                }
                            }
                        }
                    }

                    InkText {
                        Layout.alignment: Qt.AlignHCenter
                        visible: controller.records.length === 0
                        text: "아직 추첨한 미션이 없어요."
                        color: window.muted
                    }

                    RowLayout {
                        visible: controller.records.length > 0
                        Layout.fillWidth: true
                        spacing: 9
                        ListView {
                            id: recordList
                            objectName: "recordList"
                            Layout.preferredWidth: 146
                            Layout.preferredHeight: 108
                            clip: true
                            spacing: 3
                            model: controller.records
                            delegate: PaperButton {
                                required property var modelData
                                required property int index
                                width: ListView.view.width
                                implicitHeight: 32
                                font.pixelSize: 11
                                text: modelData.date + (modelData.completed ? "  완료" : "  미완료")
                                fill: recordList.currentIndex === index ? window.plum : window.lilac
                                textColor: recordList.currentIndex === index ? "white" : window.ink
                                onClicked: recordList.currentIndex = index
                            }
                            ScrollBar.vertical: ScrollBar {}
                        }
                        Rectangle {
                            id: recordDetail
                            readonly property var entry: controller.records[recordList.currentIndex] || controller.records[0]
                            Layout.fillWidth: true
                            Layout.minimumHeight: 108
                            radius: 9
                            color: window.card
                            border.color: window.edge
                            ColumnLayout {
                                width: parent.width - 20
                                anchors.centerIn: parent
                                spacing: 4
                                InkText {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: recordDetail.entry ? recordDetail.entry.date : ""
                                    color: window.muted
                                    font.pixelSize: 12
                                }
                                InkText {
                                    objectName: "historyDetail"
                                    Layout.fillWidth: true
                                    text: recordDetail.entry ? recordDetail.entry.content : ""
                                    wrapMode: Text.Wrap
                                    horizontalAlignment: Text.AlignHCenter
                                    font.bold: true
                                }
                                InkText {
                                    Layout.alignment: Qt.AlignHCenter
                                    text: recordDetail.entry
                                        ? recordDetail.entry.difficulty + " · " + (recordDetail.entry.completed ? "완료" : "미완료") : ""
                                    color: window.plum
                                    font.pixelSize: 12
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
