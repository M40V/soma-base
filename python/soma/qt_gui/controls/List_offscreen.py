#
# SOMA - Copyright (C) CEA, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
#

# System import
import os
import logging
from functools import partial
import six

# Define the logger
logger = logging.getLogger(__name__)

# Soma import
from soma.qt_gui.qt_backend import QtGui, QtCore
from soma.utils.functiontools import SomaPartial
from soma.controller import trait_ids
from soma.controller import Controller
from soma.qt_gui.controller_widget import ControllerWidget

from .List import ListControlWidget, ListController

# Qt import
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

QtCore.QResource.registerResource(os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'resources', 'widgets_icons.rcc'))


class OffscreenListControlWidget(object):

    """ Control to enter a list of items.
    """

    #
    # Public members
    #

    @staticmethod
    def is_valid(control_instance, *args, **kwargs):
        """ Method to check if the new control values are correct.

        If the new list controls values are not correct, the backroung
        color of each control in the list will be red.

        Parameters
        ----------
        control_instance: QFrame (mandatory)
            the control widget we want to validate

        Returns
        -------
        valid: bool
            True if the control values are valid,
            False otherwise
        """
        # Initilaized the output
        valid = True

        return valid

    @classmethod
    def check(cls, control_instance):
        """ Check if a controller widget list control is filled correctly.

        Parameters
        ----------
        cls: OffscreenListControlWidget (mandatory)
            an OffscreenListControlWidget control
        control_instance: QFrame (mandatory)
            the control widget we want to validate
        """
        pass

    @staticmethod
    def add_callback(callback, control_instance):
        """ Method to add a callback to the control instance when the list
        trait is modified

        Parameters
        ----------
        callback: @function (mandatory)
            the function that will be called when a 'textChanged' signal is
            emited.
        control_instance: QFrame (mandatory)
            the control widget we want to validate
        """
        pass

    @staticmethod
    def create_widget(parent, control_name, control_value, trait,
                      label_class=None):
        """ Method to create the list widget.

        Parameters
        ----------
        parent: QWidget (mandatory)
            the parent widget
        control_name: str (mandatory)
            the name of the control we want to create
        control_value: list of items (mandatory)
            the default control value
        trait: Tait (mandatory)
            the trait associated to the control
        label_class: Qt widget class (optional, default: None)
            the label widget will be an instance of this class. Its constructor
            will be called using 2 arguments: the label string and the parent
            widget.

        Returns
        -------
        out: 2-uplet
            a two element tuple of the form (control widget: ,
            associated labels: (a label QLabel, the tools QWidget))
        """
        # Get the inner trait: expect only one inner trait
        # note: trait.inner_traits might be a method (ListInt) or a tuple
        # (List), whereas trait.handler.inner_trait is always a method
        if len(trait.handler.inner_traits()) != 1:
            raise Exception(
                "Expect only one inner trait in List control. Trait '{0}' "
                "inner trait is '{1}'.".format(control_name,
                                               trait.handler.inner_traits()))
        inner_trait = trait.handler.inner_traits()[0]

        # Create the widget
        frame = QtGui.QFrame()
        frame.setFrameShape(QtGui.QFrame.StyledPanel)
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout)
        #item = QtGui.QLabel('&lt;list of %s&gt;'
                            #% str(inner_trait.trait_type.__class__.__name__))
        #item.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard |
                                     #QtCore.Qt.TextSelectableByMouse)
        #item.setFrameStyle(QtGui.QFrame.StyledPanel | QtGui.QFrame.Sunken)
        #layout.addWidget(item)

        # Create tools to interact with the list widget: expand or collapse -
        # add a list item - remove a list item
        tool_widget = QtGui.QWidget(parent)
        layout.addWidget(tool_widget)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        tool_widget.setLayout(layout)
        # Store some parameters in the list widget
        frame.inner_trait = inner_trait
        frame.trait = trait
        frame.connected = False
        frame.control_value = control_value
        frame.trait_name = control_name

        # Create the label associated with the list widget
        control_label = trait.label
        if control_label is None:
            control_label = control_name
        if label_class is None:
            label_class = QtGui.QLabel
        if control_label is not None:
            label = label_class(control_label, parent)
        else:
            label = None
        frame.label_class = label_class

        # view the model
        items = OffscreenListControlWidget.partial_view_widget(
            parent, frame, control_value)
        layout.addWidget(items)
        layout.addWidget(QtGui.QLabel('...'))
        frame.control_widget = items
        frame.controller = items.control_widget.controller
        frame.controller_widget = items.control_widget.controller_widget

        # Create the tool buttons
        edit_button = QtGui.QToolButton()
        layout.addWidget(edit_button)
        # Set the tool icons
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/soma_widgets_icons/add")),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        edit_button.setIcon(icon)
        edit_button.setFixedSize(30, 22)

        layout.addStretch(1)

        # Set some callback on the list control tools
        # Resize callback
        edit_hook = partial(
            OffscreenListControlWidget.edit_elements, parent, frame,
            edit_button)
        edit_button.clicked.connect(edit_hook)

        return (frame, label)

    @staticmethod
    def partial_view_widget(controller_widget, parent_frame, control_value):
        widget = QtGui.QTableWidget()
        widget.horizontalHeader().hide()
        widget.verticalHeader().hide()

        control_widget, control_label = ListControlWidget.create_widget(
            controller_widget, parent_frame.trait_name, control_value,
            parent_frame.trait, parent_frame.label_class)

        control_label[0].deleteLater()
        control_label[1].deleteLater()
        del control_label

        n = len(control_value)
        widget.setRowCount(1)
        widget.setColumnCount(n)
        clayout = control_widget.layout()
        maxheight = 0
        for i in range(n):
            litem = clayout.itemAtPosition(i + 1, 1)
            if litem is not None:
                item = litem.widget()
                widget.setCellWidget(0, i, item)
                maxheight = max(maxheight, item.height())

        height = maxheight + 5 \
            + widget.findChildren(QtGui.QScrollBar)[-1].height()
        #print('height:', height)
        #print('maxheight:', maxheight, widget.findChildren(QtGui.QScrollBar)[-1].height())
        #widget.setSizePolicy(QtGui.QSizePolicy.Preferred,
                             #QtGui.QSizePolicy.Maximum)
        #widget.resize(widget.sizeHint().width(), height - 20)

        widget.control_widget = control_widget
        control_widget.hide()

        return widget

    @staticmethod
    def update_controller(controller_widget, control_name, control_instance,
                          *args, **kwarg):
        """ Update one element of the controller.

        At the end the controller trait value with the name 'control_name'
        will match the controller widget user parameters defined in
        'control_instance'.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QFrame (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        return

    @classmethod
    def update_controller_widget(cls, controller_widget, control_name,
                                 control_instance):
        """ Update one element of the list controller widget.

        At the end the list controller widget user editable parameter with the
        name 'control_name' will match the controller trait value with the same
        name.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QFrame (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        return

    @classmethod
    def connect(cls, controller_widget, control_name, control_instance):
        """ Connect a 'List' controller trait and an
        'OffscreenListControlWidget' controller widget control.

        Parameters
        ----------
        cls: StrControlWidget (mandatory)
            a StrControlWidget control
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str (mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QFrame (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        # Check if the control is connected
        if not control_instance.connected:

            ListControlWidget.connect(
                #control_instance.control_widget.control_widget,
                controller_widget,
                control_instance.trait_name,
                control_instance)
            # Update the list control connection status
            control_instance.connected = True

    @staticmethod
    def disconnect(controller_widget, control_name, control_instance):
        """ Disconnect a 'List' controller trait and an
        'OffscreenListControlWidget' controller widget control.

        Parameters
        ----------
        cls: StrControlWidget (mandatory)
            a StrControlWidget control
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str (mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QFrame (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        # Check if the control is connected
        if control_instance.connected:

            ListControlWidget.disconnect(
                #control_instance.control_widget.control_widget,
                controller_widget,
                control_instance.trait_name,
                control_instance)

            ## Get the stored widget and controller hooks
            #(list_controller_hook,
             #controller_hook) = control_instance._controller_connections

            # Update the list control connection status
            control_instance.connected = False

    #
    # Callbacks
    #


    @staticmethod
    def edit_elements(controller_widget, control_instance, edit_button):
        """ Callback to view/edit a 'ListControlWidget'.

        Parameters
        ----------
        control_instance: QFrame (mandatory)
            the list widget item
        edit_button: QToolButton
            the signal sender
        """
        widget = QtGui.QDialog(controller_widget)
        widget.setModal(True)
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
        hlayout = QtGui.QHBoxLayout()
        layout.addLayout(hlayout)

        value = getattr(controller_widget.controller,
                        control_instance.trait_name)

        control_widget, control_label = ListControlWidget.create_widget(
            controller_widget, control_instance.trait_name, value,
            control_instance.trait, control_instance.label_class)

        ListControlWidget.connect(controller_widget,
                                  control_instance.trait_name,
                                  control_widget)

        hlayout.addWidget(control_label[0])
        hlayout.addWidget(control_label[1])
        layout.addWidget(control_widget)

        hlayout2 = QtGui.QHBoxLayout()
        layout.addLayout(hlayout2)
        hlayout2.addStretch(1)
        ok = QtGui.QPushButton('OK')
        cancel = QtGui.QPushButton('Cancel')
        hlayout2.addWidget(ok)
        hlayout2.addWidget(cancel)

        ok.pressed.connect(widget.accept)
        cancel.pressed.connect(widget.reject)

        if widget.exec_():

            new_trait_value = [
                getattr(control_widget.controller, str(i))
                for i in range(len(control_widget.controller.user_traits()))]

            setattr(controller_widget.controller,
                    control_instance.trait_name,
                    new_trait_value)

        ListControlWidget.disconnect(controller_widget,
                                     control_instance.trait_name,
                                     control_widget)

