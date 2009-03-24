# -*- coding: iso-8859-1 -*-

#  This software and supporting documentation were developed by
#  NeuroSpin and IFR 49
#
# This software is governed by the CeCILL license version 2 under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the
# terms of the CeCILL license version 2 as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info".
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license version 2 and that you accept its terms.

'''
Toolboxes to create
U{Qt 4<http://www.trolltech.com/products/qt/qt4>} widgets (requires
U{PyQt v4<http://www.riverbankcomputing.co.uk/pyqt>} to be installed).

This module gather together several public items defined in various submodules:
  - From L{soma.qt4gui.designer}:
    - L{createWidget}
    - L{WidgetFactory}
    - L{CustomizedQWidgetFactory}
  - From L{soma.qt4gui.automatic}:
    - L{ApplicationQt4GUI}
    - L{Qt4GUI}
    - L{WidgetGeometryUpdater}
  - Other items:
    - L{EditableTreeWidget}
    - L{getPixmap}
    - L{ObservableListWidget}
    - L{QFileDialogWithSignals}
    - L{QLineEditModificationTimer}
    - L{QtThreadCall}, L{FakeQtThreadCall}
    - L{TimeredQLineEdit}
    - L{TreeListWidget}
    - L{VScrollFrame}
@author: Yann Cointepas
@organization: U{NeuroSpin<http://www.neurospin.org>} and U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''
__docformat__ = "epytext en"

#: Default size for icons
defaultIconSize = ( 16, 16 )
largeIconSize = ( 22, 22 )

from soma.qt4gui.automatic import ApplicationQt4GUI, Qt4GUI, WidgetGeometryUpdater
from soma.qt4gui.timered_widgets import QLineEditModificationTimer, TimeredQLineEdit
#from soma.qt4gui.vscrollframe import VScrollFrame
from soma.qt4gui.list_tree_widgets import ObservableListWidget, EditableTreeWidget, TreeListWidget
from soma.qt4gui.qtThread import QtThreadCall, FakeQtThreadCall
#from soma.qt4gui.file_dialog import QFileDialogWithSignals
from soma.qt4gui.icons import getPixmap
from soma.qt4gui.text import TextEditWithSearch, TextBrowserWithSearch