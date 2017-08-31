import QtQuick 2.3
import QtQuick.Controls 1.2

import "../basic_types"

Column {
    id: root

    property variant py_interface
    property variant parent_py_obj
    property alias visualisationOptions: cmbBox.model
    function reload() {
        frameSetterContainer.reload();
        referenceTreatmentSettings.reload();
        detectionParamsSetterContainer.reload();
        boolSetterContainer.reload();
    }

    Frame {
        id: frameSetterContainer
        height: col.height + 20

        function reload(){
            col.reload()
        }

        CustomColumn {
            id: col

            IntLabel {
                width: parent.width
                label: "Ref"
                tooltip: "Select the reference frame"
                value: root.py_interface.get_bg_frame_idx()
                onEdited: {
                    root.py_interface.set_bg_frame_idx(value);
                    reload();
                }
                function reload(){ value = root.py_interface.get_bg_frame_idx() }
            }
            IntLabel {
                width: parent.width
                label: "Start"
                tooltip: "Select the first data frame"
                value: root.py_interface.get_start_frame_idx()
                onEdited: {
                    root.py_interface.set_start_frame_idx(value);
                    reload();
                }
                function reload(){ value = root.py_interface.get_start_frame_idx() }
            }
            IntLabel {
                width: parent.width
                label: "End"
                tooltip: "Select the last data frame"
                value: root.py_interface.get_end_frame_idx()
                onEdited: {
                    root.py_interface.set_end_frame_idx(value);
                    reload();
                }
                function reload(){ value = root.py_interface.get_end_frame_idx() }
            }
        }
    }
    Frame {
        id: referenceTreatmentSettings
        height: col2.height + 20

        function reload(){ col2.reload() }

        CustomColumn {
            id: col2

            IntLabel{
                width: parent.width
                label: "n"
                tooltip: "Number of frames for background"
                value: root.py_interface.get_n_bg_frames()
                onEdited: { root.py_interface.set_n_bg_frames(value); }
                function reload() {value = root.py_interface.get_n_bg_frames() }
            }
            IntLabel{
                width: parent.width
                label: "Sds"
                tooltip: "Number of standard deviations above average"
                value: root.py_interface.get_n_sds()
                onEdited: { root.py_interface.set_n_sds(value); }
                function reload() {value = root.py_interface.get_n_sds() }
            }
        }
    }
    Frame {
        id: detectionParamsSetterContainer
        height: col3.height + 20

        function reload(){ col3.reload() }

        CustomColumn {
            id: col3

            IntLabel {
                width: parent.width
                label: "Thrsh"
                tooltip: "Detection threshold"
                value: root.py_interface.get_detection_threshold()
                onEdited: { root.py_interface.set_detection_threshold(value); }
                function reload() {value = root.py_interface.get_detection_threshold() }
            }
            IntLabel {
                width: parent.width
                label: "Min"
                tooltip: "Minimum object area"
                value: root.py_interface.get_min_area()
                onEdited: { root.py_interface.set_min_area(value); }
                function reload() { root.py_interface.get_min_area() }
            }
            IntLabel {
                width: parent.width
                label: "Max"
                tooltip: "Maximum object area"
                value: root.py_interface.get_max_area()
                onEdited: { root.py_interface.set_max_area(value); }
                function reload() { root.py_interface.get_max_area() }
            }
            IntLabel{
                width: parent.width
                label: "Mvmt"
                tooltip: "Maximum displacement (between frames) threshold"
                value: root.py_interface.get_max_movement()
                onEdited: { root.py_interface.set_max_movement(value); }
                function reload() { root.py_interface.get_max_movement() }
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
                checked: root.py_interface.get_clear_borders()
                onClicked: root.py_interface.set_clear_borders(checked)
                function reload() { checked = root.py_interface.get_clear_borders() }
            }
            BoolLabel {
                label: "Norm."
                tooltip: "Normalise frames intensity"
                checked: root.py_interface.get_normalise()
                onClicked: root.py_interface.set_normalise(checked)
                function reload() { checked = root.py_interface.get_normalise() }
            }
            BoolLabel{
                label: "Extract"
                tooltip: "Extract the arena as an ROI"
                checked: root.py_interface.get_extract_arena()
                onClicked: root.py_interface.set_extract_arena(checked)
                function reload() { checked = root.py_interface.get_extract_arena() }
            }
        }
    }

    ComboBox {
        id: cmbBox
        model: ["Raw", "Diff"]
        onCurrentTextChanged:{
            root.parent_py_obj.set_frame_type(currentText)
        }
    }
}
