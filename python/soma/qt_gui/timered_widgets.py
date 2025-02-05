# -*- coding: utf-8 -*-

#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
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
QLineEditModificationTimer and TimeredQLineEdit classes associate a
QtCore.QTimer to a QtGui.QLineEdit in order to signal user
modification only after an inactivity period.

* author: Yann Cointepas
* organization: NeuroSpin
* license: `CeCILL B <http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html>`_
'''
__docformat__ = "restructuredtext en"

from soma.qt_gui.qt_backend import QtCore, QtGui, Qt
import weakref

#-------------------------------------------------------------------------


class QLineEditModificationTimer(QtCore.QObject):

    '''
    A QLineEditModificationTimer instance is accociated to a
    QtGui.QLineEdit instance, it listens all user modification (Qt
    signal 'textChanged( const QString & )') and emits a
    signal 'userModification()' when timerInterval milliseconds passed
    since the last user modification.
    '''
    # Default timer interval in milliseconds
    defaultTimerInterval = 2000
    userModification = QtCore.Signal()

    def __init__(self, qLineEdit, timerInterval=None):
        '''
        .. seealso:: :class:`TimeredQLineEdit`

        Parameters
        ----------
        qLineEdit: (QtGui.QLineEdit instance)
            widget associated with this QLineEditModificationTimer.
        timerInterval: (milliseconds)
            minimum inactivity period before emitting
            userModification signal. Default value is
            QLineEditModificationTimer.defaultTimerInterval

        '''

        QtCore.QObject.__init__(self)
        # QLineEdit<qt.QLineEdit> instance associated with this
        # QLineEditModificationTimer
        self.qLineEdit = weakref.proxy(qLineEdit)
        if timerInterval is None:
            self.timerInterval = self.defaultTimerInterval
        else:
            # minimum inactivity period before emitting C{userModification}
            # signal.
            self.timerInterval = timerInterval
        self.__timer = QtCore.QTimer(self)
        self.__timer.setSingleShot(True)
        self.__internalModification = False
        self.qLineEdit.textChanged.connect(self._userModification)
        # self.qLineEdit.lostFocus.connect(self._noMoreUserModification)
        self.qLineEdit.editingFinished.connect(self._noMoreUserModification)
        self.__timer.timeout.connect(self.modificationTimeout)

    def close(self):
        self.stop()
        self.qLineEdit.textChanged.disconnect(self._userModification)
        # self.qLineEdit.lostFocus.disconnect(self._noMoreUserModification)
        self.qLineEdit.editingFinished.disconnect(self._noMoreUserModification)
        self.__timer.timeout.disconnect(self.modificationTimeout)

    def _userModification(self, value):
        if not self.__internalModification:
            self.__timer.start(self.timerInterval)

    def modificationTimeout(self):
        self.userModification.emit()  # self.qLineEdit.text())

    def _noMoreUserModification(self):
        if self.__timer.isActive():
            self.__timer.stop()
            self.userModification.emit()  # self.qLineEdit.text())

    def stopInternalModification(self):
        '''
        Stop emitting ``userModification`` signal when associated
        :pyqt:`QLineEdit <QtGui/QLineEdit.html>` is modified.

        .. seealso:: :meth:`startInternalModification`
        '''
        self.__internalModification = False

    def startInternalModification(self):
        '''
        Restart emitting C{userModification} signal when associated
        :pyqt:`QLineEdit <QtGui/QLineEdit.html>` is modified.

        .. seealso:: :meth:`stopInternalModification`
        '''
        self.__internalModification = True

    def stop(self):
        '''
        Stop the timer if it is active.
        '''
        self.__timer.stop()

    def isActive(self):
        '''
        Returns True if the timer is active, or False otherwise.
        '''
        return self.__timer.isActive()


#-------------------------------------------------------------------------
class TimeredQLineEdit(Qt.QLineEdit):

    '''
    Create a QLineEdit instance that has an private attribute
    containing a QLineEditModificationTimer associated to self. Whenever
    the internal QLineEditModificationTimer emits a userModification
    signal, this signal is also emited by the TimeredQLineEdit instance.
    '''

    userModification = QtCore.Signal()

    def __init__(self, *args, **kwargs):
        '''
        All non keyword parameters of the constructor are passed to
        :pyqt:`QLineEdit <QtGui/QLineEdit.html>` constructor. An optional
        *timerInterval* keyword parameter can be given, it is passed to
        :class:`QLineEditModificationTimer` constructor. At the time this class
        was created, :pyqt:`QLineEdit <QtGui/QLineEdit.html>` constructor did
        not accept keyword parameters.
        '''
        timerInterval = kwargs.pop('timerInterval', None)
        if kwargs:
            Qt.QLineEdit.__init__(self, *args, **kwargs)
        else:
            Qt.QLineEdit.__init__(self, *args)
        self.__timer = QLineEditModificationTimer(self,
                                                  timerInterval=timerInterval)
        self.__timer.userModification.connect(self.userModification)

    def stopInternalModification(self):
        '''
        .. seealso:: :meth:`QLineEditModificationTimer.stopInternalModification`
        '''
        self.__timer.stopInternalModification()

    def startInternalModification(self):
        '''
        .. seealso:: :meth:`QLineEditModificationTimer.startInternalModification`
        '''
        self.__timer.startInternalModification()

    def close(self):
        self.__timer.close()
        super(TimeredQLineEdit, self).close()
