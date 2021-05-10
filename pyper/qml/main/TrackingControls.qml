import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Controls.Styles 1.3


import "../basic_types"
import "../style"

Column {
    id: root

    property variant py_params_iface
    property variant py_tracking_iface
    property alias visualisationOptions: cmbBox.model
    function reload() {
        frameSetterContainer.reload();
        referenceTreatmentSettings.reload();
        detectionParamsSetterContainer.reload();
        boolSetterContainer.reload();
    }

    function updateTracker() {
        py_tracking_iface.set_tracker_params();
    }
    signal advancedThresholdingSelected;

    Frame {
        id: frameSetterContainer
        height: col.height + 20

        function reload(){
            col.reload()
        }

        CustomColumn {
            id: col

            IntInput {
                id: refFrameInput
                width: parent.width
                label: "Ref"
                tooltip: "Select the reference frame"
                value: root.py_params_iface.bg_frame_idx
                minimumValue: 0
                maximumValue: startFrameInput.value - nBgFramesInput.value
                onEdited: {
                    root.py_params_iface.bg_frame_idx = value;
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.bg_frame_idx;
                    root.updateTracker();
                }
            }
            IntInput {
                id: startFrameInput
                width: parent.width
                label: "Start"
                tooltip: "Select the first data frame"
                value: root.py_params_iface.start_frame_idx
                minimumValue: refFrameInput.value + nBgFramesInput.value
                onEdited: {
                    root.py_params_iface.start_frame_idx = value;
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.start_frame_idx;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "End"
                tooltip: "Select the last data frame"
                value: root.py_params_iface.end_frame_idx
//                minimumValue: startFrameInput.value
                minimumValue: -1  // means to the end
                onEdited: {
                    root.py_params_iface.end_frame_idx = value;
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.end_frame_idx;
                    root.updateTracker();
                }
            }
        }
    }
    Frame {
        id: referenceTreatmentSettings
        height: col2.height + 20

        function reload(){ col2.reload() }

        CustomColumn {
            id: col2

            IntInput {
                id: nBgFramesInput
                width: parent.width
                label: "n"
                tooltip: "Number of frames for background"
                value: root.py_params_iface.n_bg_frames
                onEdited: {
                    root.py_params_iface.n_bg_frames = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.n_bg_frames;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "Sds"
                tooltip: "Number of standard deviations above average"
                value: root.py_params_iface.n_sds
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.n_sds = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.n_sds;
                    root.updateTracker();
                }
            }
        }
    }
    Frame {
        id: detectionParamsSetterContainer
        height: col3.height + 20

        function reload(){ col3.reload() }

        CustomColumn {
            id: col3

            BoolLabel {
                id: advancedThresholding
                label: "Advanced"
                width: parent.width
                tooltip: "Advanced (e.g. color) thresholding options."
                checked: false;
                onClicked: {
                    root.advancedThresholdingSelected(checked);
                    // root.updateTracker();
                }
                function reload() {
                    checked = false;
                    // root.updateTracker();
                }
            }

            IntInput {
                width: parent.width
                enabled: !advancedThresholding.checked
                label: "Thrsh"
                tooltip: "Detection threshold"
                value: root.py_params_iface.detection_threshold
                minimumValue: 1
                maximumValue: 255
                onEdited: {
                    root.py_params_iface.detection_threshold = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.detection_threshold;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                enabled: !advancedThresholding.checked
                label: "Min"
                tooltip: "Minimum object area"
                value: root.py_params_iface.min_area
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.min_area = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.min_area;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                enabled: !advancedThresholding.checked
                label: "Max"
                tooltip: "Maximum object area"
                value: root.py_params_iface.max_area
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.max_area = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.max_area;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
//                enabled: !advancedThresholding.checked
                label: "Mvmt"
                tooltip: "Maximum displacement (between frames) threshold"
                value: root.py_params_iface.max_movement
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.max_movement = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.max_movement;
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
//                enabled: !advancedThresholding.checked
                label: "Erosions"
                tooltip: "Number of erosions to perform on the mask"
                value: root.py_params_iface.n_erosions
                minimumValue: 0
                onEdited: {
                    root.py_params_iface.n_erosions = value;
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.n_erosions;
                    root.updateTracker();
                }
            }
        }
    }
    Frame {
        id: boolSetterContainer
        height: col4.height + 20

        function reload(){ col4.reload() }

        CustomColumn {
            id: col4

            BoolLabel {
                label: "Clear"
                tooltip: "Clear objects touching the borders of the image"
                checked: root.py_params_iface.clear_borders
                onClicked: {
                    root.py_params_iface.clear_borders = checked;
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.clear_borders;
                    root.updateTracker();
                }
            }
            BoolLabel {
                label: "Norm."
                tooltip: "Normalise frames intensity"
                checked: root.py_params_iface.normalise
                onClicked: {
                    root.py_params_iface.normalise = checked;
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.normalise;
                    root.updateTracker();
                }
            }
            BoolLabel{
                label: "Extract"
                tooltip: "Extract the arena as an ROI"
                checked: root.py_params_iface.extract_arena
                onClicked: {
                    root.py_params_iface.extract_arena = checked;
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.extract_arena;
                    root.updateTracker();
                }
            }
            BoolLabel {
                label: "Infer"
                tooltip: "Infers that the object is still at the\nlast know location in case tracking is lost."
                checked: root.py_params_iface.infer_location;
                onClicked: {
                    root.py_params_iface.infer_location = checked;
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.infer_location;
                    root.updateTracker();
                }
            }
        }
    }

    ComboBox {
        id: cmbBox
        model: ["Raw", "Diff"]
        height: 25
        width: boolSetterContainer.width
        style: ComboBoxStyle {
            background: Frame {
                width: parent.width
                height: parent.height
                color: Theme.spinBoxBackground
            }
            textColor: Theme.darkBackground
            selectedTextColor: 'steelblue'
            selectionColor: Theme.darkBackground
        }
        onCurrentTextChanged:{
            root.py_tracking_iface.set_frame_type(currentText)
        }
    }
}
