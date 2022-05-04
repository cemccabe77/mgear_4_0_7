import json

import pymel.core

from mgear.vendor.Qt import QtWidgets


def widget_get(widget):
    if isinstance(widget, QtWidgets.QDoubleSpinBox):
        return widget.value()
    if isinstance(widget, QtWidgets.QSpinBox):
        return widget.value()
    if isinstance(widget, QtWidgets.QLineEdit):
        return widget.text()
    if isinstance(widget, QtWidgets.QCheckBox):
        return widget.isChecked()
    if isinstance(widget, QtWidgets.QComboBox):
        return widget.currentIndex()

    return None


def widget_set(widget, value):
    if isinstance(widget, QtWidgets.QDoubleSpinBox):
        widget.setValue(value)
        return
    if isinstance(widget, QtWidgets.QSpinBox):
        widget.setValue(value)
        return
    if isinstance(widget, QtWidgets.QLineEdit):
        widget.setText(value)
        return
    if isinstance(widget, QtWidgets.QCheckBox):
        widget.setChecked(value)
        return
    if isinstance(widget, QtWidgets.QComboBox):
        widget.setCurrentIndex(value)
        return

    raise ValueError("Widget {0} was not recognized.".format(widget))


def import_settings_from_file(file_path, widget):
    settings = {}
    with open(file_path, "r") as f:
        settings = json.load(f)

    for attr, obj in widget.__dict__.iteritems():
        if attr not in settings.keys():
            continue

        widget_set(obj, settings[attr])


def get_settings_from_widget(widget):
    settings = {}
    for attr, obj in widget.__dict__.iteritems():
        value = widget_get(obj)
        if value is not None:
            settings[attr] = value

    return settings


def get_file_path(filter, mode):
    filemode = None
    if mode == "open":
        filemode = 1
    if mode == "save":
        filemode = 0

    file_path = pymel.core.fileDialog2(
        fileMode=filemode,
        fileFilter=filter
    )
    if not file_path:
        return None
    if not isinstance(file_path, basestring):
        file_path = file_path[0]

    return file_path


def get_edge_loop_from_selection():
    selection = pymel.core.selected(fl=1)
    if selection:
        edge_list = ""
        separator = ""
        for edge in selection:
            if isinstance(edge, pymel.core.MeshEdge):
                if edge_list:
                    separator = ","
                edge_list = edge_list + separator + str(edge)
        if not edge_list:
            pymel.core.displayWarning("Please select first the edge loop.")
        elif len(edge_list.split(",")) < 4:
            pymel.core.displayWarning("The minimun edge count is 4")
        else:
            return edge_list
    else:
        pymel.core.displayWarning("Please select first the edge loop.")
