#
# SOMA - Copyright (C) CEA, 2015
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
#

# System import
import logging
from functools import partial
import sys

# Define the logger
logger = logging.getLogger(__name__)

# Soma import
from soma.qt_gui.qt_backend import QtGui, QtCore
from soma.utils.functiontools import SomaPartial
from soma.qt_gui.controller_widget import weak_proxy
import traits.api as traits

if sys.version_info[0] >= 3:
    unicode = str


class EnumControlWidget(object):

    """ Control to select a value from a list.
    """

    @staticmethod
    def is_valid(control_instance, *args, **kwargs):
        """ Method to check if the new control value is correct.

        Parameters
        ----------
        control_instance: QComboBox (mandatory)
            the control widget we want to validate

        Returns
        -------
        out: bool
            always True since the control value is always valid
        """
        return True

    @classmethod
    def check(cls, control_instance):
        """ Check if a controller widget control is filled correctly.

        Parameters
        ----------
        cls: EnumControlWidget (mandatory)
            an EnumControlWidget control
        control_instance: QComboBox (mandatory)
            the control widget we want to validate
        """
        # Hook: function that will be called to check for typo
        # when a 'textEdited' qt signal is emited
        widget_callback = partial(cls.is_valid, weak_proxy(control_instance))

        # Execute manually the first time the control check method
        widget_callback()

        # When a qt 'editTextChanged' signal is emited, check if the new
        # user value is correct
        control_instance.editTextChanged.connect(widget_callback)

    @staticmethod
    def add_callback(callback, control_instance):
        """ Method to add a callback to the control instance when a 'editTextChanged'
        signal is emited.

        Parameters
        ----------
        callback: @function (mandatory)
            the function that will be called when a 'editTextChanged' signal is
            emited.
        control_instance: QComboBox (mandatory)
            the control widget we want to validate
        """
        control_instance.editTextChanged.connect(callback)

    @staticmethod
    def create_widget(parent, control_name, control_value, trait,
                      label_class=None):
        """ Method to create the widget.

        Parameters
        ----------
        parent: QWidget (mandatory)
            the parent widget
        control_name: str (mandatory)
            the name of the control we want to create
        control_value: str (mandatory)
            the default control value, here the enum values
        trait: Tait (mandatory)
            the trait associated to the control
        label_class: Qt widget class (optional, default: None)
            the label widget will be an instance of this class. Its constructor
            will be called using 2 arguments: the label string and the parent
            widget.

        Returns
        -------
        out: 2-uplet
            a two element tuple of the form (control widget: QComboBox,
            associated label: QLabel)
        """
        # Create the widget that will be used to select a value
        widget = QtGui.QComboBox(parent)

        # Save the possible choices
        widget._choices = trait.handler.values

        # Add a parameter to tell us if the widget is optional
        widget.optional = trait.optional

        # Set the enum list items to the widget
        for item in widget._choices:
            widget.addItem(unicode(item))

        # Select the default value
        # If the default value is not in the enum list, pick the first item
        # of the enum list
        if control_value not in widget._choices:
            widget.setCurrentIndex(0)
        else:
            widget.setCurrentIndex(widget._choices.index(control_value))

        # Create the label associated with the enum widget
        control_label = trait.label
        if control_label is None:
            control_label = control_name
        if label_class is None:
            label_class = QtGui.QLabel
        if control_label is not None:
            label = label_class(control_label, parent)
        else:
            label = None

        return (widget, label)

    @staticmethod
    def update_controller(controller_widget, control_name,
                          control_instance, *args, **kwargs):
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
        control_instance: StrControlWidget (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        if EnumControlWidget.is_valid(control_instance):
            new_trait_value = control_instance._choices[
                control_instance.currentIndex()]
            setattr(controller_widget.controller, control_name,
                    new_trait_value)
            logger.debug(
                "'EnumControlWidget' associated controller trait '{0}' "
                " has been updated with value '{1}'.".format(
                    control_name, new_trait_value))

    @staticmethod
    def update_controller_widget(controller_widget, control_name,
                                 control_instance):
        """ Update one element of the controller widget.

        At the end the controller widget user editable parameter with the
        name 'control_name' will match the controller trait value with the same
        name.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: StrControlWidget (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        # Get the controller trait value
        new_controller_value = getattr(
            controller_widget.controller, control_name, None)

        # If the controller value is not empty, update the controller widget
        # associated control
        if new_controller_value not in (None, traits.Undefined):
            control_instance.setCurrentIndex(
                control_instance._choices.index(new_controller_value))
        logger.debug("'EnumControlWidget' has been updated with value "
                     "'{0}'.".format(new_controller_value))

    @classmethod
    def connect(cls, controller_widget, control_name, control_instance):
        """ Connect an 'Enum' controller trait and an 'EnumControlWidget'
        controller widget control.

        Parameters
        ----------
        cls: EnumControlWidget (mandatory)
            an EnumControlWidget control
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str (mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QComboBox (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        # Update one element of the controller.
        # Hook: function that will be called to update a specific
        # controller trait when an 'activated' qt signal is emited
        widget_hook = partial(cls.update_controller,
                              weak_proxy(controller_widget),
                              control_name, weak_proxy(control_instance))

        # When a qt 'activated' signal is emited, update the
        # 'control_name' controller trait value
        control_instance.activated.connect(widget_hook)

        # Update one element of the controller widget.
        # Hook: function that will be called to update the specific widget
        # when a trait event is detected.
        controller_hook = SomaPartial(
            cls.update_controller_widget, weak_proxy(controller_widget),
            control_name, weak_proxy(control_instance))

        # When the 'control_name' controller trait value is modified, update
        # the corresponding control
        controller_widget.controller.on_trait_change(
            controller_hook, name=control_name, dispatch='ui')

        # Store the trait - control connection we just build
        control_instance._controller_connections = (
            widget_hook, controller_hook)
        logger.debug("Add 'Enum' connection: {0}.".format(
            control_instance._controller_connections))

    @staticmethod
    def disconnect(controller_widget, control_name, control_instance):
        """ Disconnect an 'Enum' controller trait and an 'EnumControlWidget'
        controller widget control.

        Parameters
        ----------
        controller_widget: ControllerWidget (mandatory)
            a controller widget that contains the controller we want to update
        control_name: str(mandatory)
            the name of the controller widget control we want to synchronize
            with the controller
        control_instance: QComboBox (mandatory)
            the instance of the controller widget control we want to
            synchronize with the controller
        """
        # Get the stored widget and controller hooks
        (widget_hook,
         controller_hook) = control_instance._controller_connections

        # Remove the controller hook from the 'control_name' trait
        controller_widget.controller.on_trait_change(
            controller_hook, name=control_name, remove=True)

        # Remove the widget hook associated with the qt 'activated'
        # signal
        control_instance.activated.disconnect(widget_hook)

        # Delete the trait - control connection we just remove
        del control_instance._controller_connections
