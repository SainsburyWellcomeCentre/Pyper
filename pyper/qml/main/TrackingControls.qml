import QtQuick 2.3
import QtQuick.Controls 1.2

import "../basic_types"

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
                value: root.py_params_iface.get_bg_frame_idx()
                minimumValue: 0
                maximumValue: startFrameInput.value - nBgFramesInput.value
                onEdited: {
                    root.py_params_iface.set_bg_frame_idx(value);
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.get_bg_frame_idx();
                    root.updateTracker();
                }
            }
            IntInput {
                id: startFrameInput
                width: parent.width
                label: "Start"
                tooltip: "Select the first data frame"
                value: root.py_params_iface.get_start_frame_idx()
                minimumValue: refFrameInput.value + nBgFramesInput.value
                onEdited: {
                    root.py_params_iface.set_start_frame_idx(value);
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.get_start_frame_idx();
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "End"
                tooltip: "Select the last data frame"
                value: root.py_params_iface.get_end_frame_idx()
//                minimumValue: startFrameInput.value
                minimumValue: -1  // means to the end
                onEdited: {
                    root.py_params_iface.set_end_frame_idx(value);
                    reload();
                }
                function reload(){
                    value = root.py_params_iface.get_end_frame_idx();
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
                value: root.py_params_iface.get_n_bg_frames()
                onEdited: {
                    root.py_params_iface.set_n_bg_frames(value);
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.get_n_bg_frames();
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "Sds"
                tooltip: "Number of standard deviations above average"
                value: root.py_params_iface.get_n_sds()
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.set_n_sds(value);
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.get_n_sds();
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

            IntInput {
                width: parent.width
                label: "Thrsh"
                tooltip: "Detection threshold"
                value: root.py_params_iface.get_detection_threshold()
                minimumValue: 1
                maximumValue: 255
                onEdited: {
                    root.py_params_iface.set_detection_threshold(value);
                    root.updateTracker();
                }
                function reload() {
                    value = root.py_params_iface.get_detection_threshold();
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "Min"
                tooltip: "Minimum object area"
                value: root.py_params_iface.get_min_area()
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.set_min_area(value);
                    root.updateTracker();
                }
                function reload() {
                    root.py_params_iface.get_min_area();
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "Max"
                tooltip: "Maximum object area"
                value: root.py_params_iface.get_max_area()
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.set_max_area(value);
                    root.updateTracker();
                }
                function reload() {
                    root.py_params_iface.get_max_area();
                    root.updateTracker();
                }
            }
            IntInput {
                width: parent.width
                label: "Mvmt"
                tooltip: "Maximum displacement (between frames) threshold"
                value: root.py_params_iface.get_max_movement()
                minimumValue: 1
                onEdited: {
                    root.py_params_iface.set_max_movement(value);
                    root.updateTracker();
                }
                function reload() {
                    root.py_params_iface.get_max_movement();
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
                checked: root.py_params_iface.get_clear_borders()
                onClicked: {
                    root.py_params_iface.set_clear_borders(checked);
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.get_clear_borders();
                    root.updateTracker();
                }
            }
            BoolLabel {
                label: "Norm."
                tooltip: "Normalise frames intensity"
                checked: root.py_params_iface.get_normalise()
                onClicked: {
                    root.py_params_iface.set_normalise(checked);
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.get_normalise();
                    root.updateTracker();
                }
            }
            BoolLabel{
                label: "Extract"
                tooltip: "Extract the arena as an ROI"
                checked: root.py_params_iface.get_extract_arena()
                onClicked: {
                    root.py_params_iface.set_extract_arena(checked);
                    root.updateTracker();
                }
                function reload() {
                    checked = root.py_params_iface.get_extract_arena();
                    root.updateTracker();
                }
            }
        }
    }

    ComboBox {
        id: cmbBox
        model: ["Raw", "Diff"]
        onCurrentTextChanged:{
            root.py_tracking_iface.set_frame_type(currentText)
        }
    }
}
