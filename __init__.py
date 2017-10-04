# -*- coding: utf-8 -*-
"""A widget library for Python and PyQt

Copyright (C) 2017 Radomir Matveev, GPL 3.0+

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = "0.1"

# --------------------------------------------------------------------------- #
# Import libraries
# --------------------------------------------------------------------------- #
import logging

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QModelIndex


# --------------------------------------------------------------------------- #
# Define classes
# --------------------------------------------------------------------------- #
class QNotice(QtWidgets.QWidget):
    """Implements an interactive notice container widget.
    """
    def __init__(self, widget, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self._widget = widget
        self._fixedX = False
        self._fixedY = False
        self._fixedWidth = False
        self._fixedHeight = False
        # create layout
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)

    def widget(self):
        """Returns the widget of this notice."""
        return self._widget

    def fixedX(self):
        return self._fixedX
    def setFixedX(self, val):
        self._fixedX = val

    def fixedY(self):
        return self._fixedY
    def setFixedY(self, val):
        self._fixedY = val

    def fixedWidth(self):
        return self._fixedWidth
    def setFixedWidth(self, val):
        self._fixedWidth = val

    def fixedHeight(self):
        return self._fixedHeight
    def setFixedHeight(self, val):
        self._fixedHeight = val

    def fixedGeometry(self):
        return (self._fixedX and self.fixedY and self.fixedWidth and
                self.fixedHeight)
    def setFixedGeometry(self, val):
        self._fixedX = self.fixedY = self.fixedWidth = self.fixedHeight = val

    def refGeometry(self):
        """Returns the reference geometry for this notice."""
        board = self.parent()
        layout = board.layout()
        return layout.referenceGeometry(self)
    def setRefGeometry(self, geometry):
        """Updates the reference geometry for this notice."""
        board = self.parent()
        layout = board.layout()
        layout.setReferenceGeometry(self, geometry)

    def nid(self):
        """Return the notice id."""
        return id(self._widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setFocus()
        event.ignore()

    def keyPressEvent(self, event):
        geom = list(self.refGeometry().getRect())
        if event.modifiers() & Qt.ShiftModifier:
            step = 10  # this should be an even number (2, 4, 6, ...)
        else:
            step = 2  # this should be an even number (2, 4, 6, ...)
        if event.modifiers() & Qt.ControlModifier:  # resize notice
            resize = True
            if self._fixedX is False and event.key() == Qt.Key_Left:
                geom[2] -= step  # shrink width
                geom[0] += int(step / 2)
            elif self._fixedX is False and event.key() == Qt.Key_Right:
                geom[2] += step  # increase width
                geom[0] -= int(step / 2)
            elif self._fixedY is False and event.key() == Qt.Key_Up:
                geom[3] -= step  # shrink height
                geom[1] += int(step / 2)
            elif self._fixedY is False and event.key() == Qt.Key_Down:
                geom[3] += step  # increase height
                geom[1] -= int(step / 2)
            else:
                resize = False
            if resize is True:
                self.setRefGeometry(QtCore.QRect(*geom))
        else:  # move notice
            move = True
            if (self._fixedWidth is False and
                event.key() == Qt.Key_Left):
                geom[0] -= step
            elif (self._fixedWidth is False and
                  event.key() == Qt.Key_Right):
                geom[0] += step
            elif (self._fixedHeight is False and
                  event.key() == Qt.Key_Up):
                geom[1] -= step
            elif (self._fixedHeight is False and
                  event.key() == Qt.Key_Down):
                geom[1] += step
            else:
                move = False
            if move is True:
                self.setRefGeometry(QtCore.QRect(*geom))


class QScalingNoticeBoard(QtWidgets.QWidget):
    """Implements a notice board using the scaling layout.
    """
    def __init__(self, referencewidth=400, referenceheight=300, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.notices = {}
        self.background = QPixmapLabel()
#        self.background.setGeometry(0, 0, referencewidth, referenceheight)
        # create layout
        layout = QScalingLayout(referencewidth, referenceheight)
        layout.addWidget(self.background)
        self.setLayout(layout)
        # configure widgets
        pixmap = QtGui.QPixmap(referencewidth, referenceheight)
        pixmap.fill(Qt.transparent)
        self.setPixmap(pixmap)

    def setReferenceSize(self, width, height):
        """Sets the reference size, which is used to calculate the scale."""
        layout = self.layout()
        layout.removeWidget(self.background)
        layout.setReferenceSize(width, height)
        self.background.setGeometry(0, 0, width, height)
        layout.addWidget(self.background)

    def setPixmap(self, pixmap):
        """Changes the background of the widget to pixmap."""
        referencewidth = pixmap.width()
        referenceheight = pixmap.height()
        # update reference size
        self.setReferenceSize(referencewidth, referenceheight)
        # display pixmap
        self.background.setPixmap(pixmap)
#        # remove current layout
#        clearLayout(self.layout())
#        QtWidgets.QWidget().setLayout(self.layout())
#        # add new layout
#        self.background.setGeometry(0, 0, referencewidth, referenceheight)
#        layout = QScalingLayout(referencewidth, referenceheight)
#        layout.addWidget(self.background)
#        self.setLayout(layout)

    def sizeHint(self):
        return self.layout().sizeHint()

    def minimumSizeHint(self):
        return self.background.minimumSizeHint()

    def clear(self):
        """Remove all notices from this board."""
        layout = self.layout()
        for notice in self.notices.values():
            layout.removeWidget(notice)
            notice.setParent(None)
        self.notices = {}

    def notice(self, nid):
        """Returns the notice with the specified widget id."""
        return self.notices[nid]

    def noticeWidgets(self):
        """Returns a list of the widgets of all notices."""
        return [notice.widget() for notice in self.notices.values()]

    def addNotice(self, widget):
        """Anchors the widget at the given widget coords and resizes it."""
        log.info("Add notice %s", widget)
        notice = QNotice(widget)
        notice.setGeometry(widget.geometry())
        self.notices[id(widget)] = notice
        self.layout().addWidget(notice)
        return notice

    def removeNotice(self, nid):
        """Removes the notice with the specified widget id."""
        # remove notice from notices dict
        notice = self.notices.pop(nid)
        # remove widget from the layout list
        layout = self.layout()
        layout.removeWidget(notice)
        # remove it from the gui
        notice.setParent(None)


class QScalingLayout(QtWidgets.QLayout):
    """Arranges items in a composition that scales on parent widget resize.

    The layout has a reference size. The inital size and position of each
    item relative to the reference size is determined by the geometry of the
    item when it is added to the layout.
    When the layout size changes the geometry of each item is rescaled
    proportionally.

    Further infos: section 'How to Write a Custom Layout Manager' at
        http://doc.qt.io/qt-5/layout.html
    """
    def __init__(self, referencewidth, referenceheight):
        QtWidgets.QLayout.__init__(self)
        self.refrect = None  # a QtCore.QRect instance
        self.currect = None  # a QtCore.QRect instance
        self.items = []
        self.itemgeom = {}  # stores the reference geometry of layout items
        self.setReferenceSize(referencewidth, referenceheight)

    def __del__(self):
        self.items = []
        self.itemgeom = {}
        # QtWidgets.QLayout.__del__(self)  # __del__ not implemented in QLayout
        # TODO maybe we also have to del each item separately
        # TODO or maybe this whole method is unnecessary

    def count(self):
        return len(self.items)

    def itemAt(self, idx):
        if idx < 0:
            # negative indices are not supported in Qt
            # we should mimic that behaviour
            return None
        try:
            return self.items[idx]
        except IndexError:
            return None

    def takeAt(self, idx):
        return self.items.pop(idx)

    def addItem(self, item):
        self.items.append(item)
        if item.widget() != 0:
            # set the reference geometry for the widget
            # in this item to the item's geometry
            self.setReferenceGeometry(item.widget(), item.geometry())
        else:
            raise NotImplementedError

    def setGeometry(self, rect):
        # determine the scale of the new geometry and the limiting dimension
        scale, limdim = calculateScale(self.refrect, rect)
        # adjust the size of the current rect
        self.currect.setWidth(round(self.refrect.width() * scale))
        self.currect.setHeight(round(self.refrect.height() * scale))
        # calculate item position based on the limiting dimension
        if limdim == "width":
            xoff = 0
            yoff = round((rect.height() - self.currect.height()) / 2)
        else:
            xoff = round((rect.width() - self.currect.width()) / 2)
            yoff = 0
        # update item geometries
        for item in self.items:
            # retrieve reference item geometry
            refgeom = self.itemgeom[id(item)]
            # calculate new item geometry
            newgeom = [round(c * scale) for c in refgeom.getRect()]
            # adjust for excess space
            newgeom[0] = newgeom[0] + xoff
            newgeom[1] = newgeom[1] + yoff
            # TODO check if we need QLayoutItem.isEmpty to support hidden items
            # update item geometry
            item.setGeometry(QtCore.QRect(*newgeom))

    def sizeHint(self):
        left = [self.refrect.left()]
        right = [self.refrect.left() + self.refrect.width()]
        top = [self.refrect.top()]
        bottom = [self.refrect.top() + self.refrect.height()]
        for item in self.items:
            # retrieve reference item geometry
            refgeom = self.itemgeom[id(item)]
            left.append(refgeom.left())
            right.append(refgeom.left() + refgeom.width())
            top.append(refgeom.top())
            bottom.append(refgeom.top() + refgeom.height())
        width = max(right) - min(left)
        height = max(bottom) - min(top)
        return QtCore.QSize(width, height)

    def setReferenceSize(self, width, height):
        """Sets the reference size, which is used to calculate the scale."""
        width = int(width)
        height = int(height)
        if width <= 0:
            raise ValueError("reference width must be bigger than 0")
        if height <= 0:
            raise ValueError("reference height must be bigger than 0")
        self.refrect = QtCore.QRect(0, 0, width, height)
        self.currect = QtCore.QRect(0, 0, width, height)

    def referenceGeometry(self, notice):
        """Returns the reference geometry for this notice."""
        item = self.itemAt(self.indexOf(notice))
        return self.itemgeom[id(item)]

    def setReferenceGeometry(self, notice, geometry):
        """Sets the reference geometry for this notice."""
        # ensure geometry is a QRect
        if not isinstance(geometry, QtCore.QRect):
            raise TypeError("geometry must be a QtCore.QRect, not %s"
                            % type(geometry))
        # fetch the layout item for this notice...
        item = self.itemAt(self.indexOf(notice))
        # ...and raise an error if the layout does not find it
        if item is None:
            raise KeyError("Widget %s is not part of layout %s"
                           % (notice, self))
        # store the reference geometry for this notice
        self.itemgeom[id(item)] = geometry
        # if this layout has been set on a widget, update this layout to
        # account for the new geometry of one of it's layout items
        if self.parentWidget() is not None:
            self.update()

    def widgetToReference(self, point):
        """Translates local widget coordinates to reference coordinates."""
        widget = self.parentWidget()
        left, top = getCoords(point)
        scale = self.scale()
        # factor in scale
        left = left / scale
        top = top / scale
        # translate from widget coordinates to reference coordinates
        widgetwidth = widget.width() / scale
        widgetheight = widget.height() / scale
        left -= (widgetwidth - self.refrect.width()) / 2
        top -= (widgetheight - self.refrect.height()) / 2
        return QtCore.QPoint(round(left), round(top))

    def scale(self):
        """Returns the current scale of the layout."""
        return self.currect.width() / self.refrect.width()


class QPixmapLabel(QtWidgets.QLabel):
    """A label used to display pictures with dynamic resizing.

    Preserves aspect ratio.

    Based on:
    http://stackoverflow.com/questions/5653114/
            display-image-in-qt-to-fit-label-size
    """
    @classmethod
    def fitPixmapIntoRect(cls, rect, pixmap, sourcepixmap=None,
                          mode=Qt.SmoothTransformation):
        # check input
        if sourcepixmap is None:
            sourcepixmap = pixmap
        if pixmap.isNull():
            return pixmap
        if rect.width() == 0 or rect.height() == 0:
            raise ValueError("Can not fit a pixmap into a rect with zero " +
                             "width or height: %s" % rect)
        # calculate new scale of pixmap
        scale, limiter = calculateScale(sourcepixmap.rect(), rect)
        # resize pixmap
        if limiter == "width":
            width = round(sourcepixmap.width() * scale)
            pixmap = sourcepixmap.scaledToWidth(width, mode)
        else:
            height = round(sourcepixmap.height() * scale)
            pixmap = sourcepixmap.scaledToHeight(height, mode)
        return pixmap

    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self, *args, **kwargs)
        self.mode = kwargs.get("mode", Qt.SmoothTransformation)
        pixmap = QtGui.QPixmap(50, 50)
        pixmap.fill(QtGui.QColor("magenta"))
        # preserve the original, so multiple resize events
        # won't break the quality
        self.source = pixmap  # original pixmap
        self.current = pixmap  # current pixmap
        # any size is useful, but the bigger the widget the better
        QSPol = QtWidgets.QSizePolicy
        self.setSizePolicy(QSPol(QSPol.Expanding, QSPol.Expanding))

    def resizePixmap(self, size):
        """Resizes the pixmap so it fits into size.

        The caller is responsible for handling the results of this resize,
        like notifying the layout about the geometry update.
        """
        if size.width() == 0 or size.height() == 0:
            self.current = QtGui.QPixmap()
            msg = "QPixmapLabel is invisible because width or height are 0"
            log.warning(msg)
        else:
            self.current = self.fitPixmapIntoRect(size, self.current,
                                                  sourcepixmap=self.source,
                                                  mode=self.mode)

    def resizeEvent(self, event):
        # resize pixmap to fit into new size
        self.resizePixmap(event.size())
        # resize widget
        QtWidgets.QLabel.resizeEvent(self, event)

    def paintEvent(self, event):
        if self.source is None:  # no image was set, don't draw anything
            return
        QtWidgets.QLabel.paintEvent(self, event)
        # fit the pixmap into the current widget size
        self.resizePixmap(self.rect())
        # determine the widget coords for the top left corner of the pixmap
        x = round((self.width() - self.current.width()) / 2)
        y = round((self.height() - self.current.height()) / 2)
        # draw the pixmap
        painter = QtGui.QPainter(self)
        painter.drawPixmap(x, y, self.current)

    def sizeHint(self):
        if self.current is not None:
            w = self.source.width()
            h = self.source.height()
            return QtCore.QSize(w, h)
        else:
            return QtWidgets.QLabel.sizeHint(self)

    def setPixmap(self, pixmap):
        """Sets a new source image for this label."""
        if pixmap.isNull():
            log.error("Setting emtpy pixmap, using default instead")
            self.clear()
        else:
            self.source = self.current = pixmap
            self.update()
        # notify layout about size hint change
        self.updateGeometry()

    def clear(self, emptycolor=QtGui.QColor("magenta")):
        """Replace current pixmap with colored rectangle of the same size."""
        width = self.current.width()
        height = self.current.height()
        QtWidgets.QLabel.clear(self)
        pixmap = QtGui.QPixmap(width, height)
        pixmap.fill(emptycolor)
        self.setPixmap(pixmap)

    def scale(self):
        """The ratio of the current pixmap size to that of the source."""
        return float(self.current.width() / self.source.width())

    def imageAt(self, pos):
        """Returns True if these widget coordinates are over the image."""
        return self.currentRect().contains(pos)

    def mapWidgetToCurrent(self, point):
        """Maps the local widget coordinates to the current image.

        The target origin is the top left corner of the current image.
        """
        x = round(point.x() - (self.width() - self.current.width()) / 2)
        y = round(point.y() - (self.height() - self.current.height()) / 2)
        return QtCore.QPoint(x, y)

    def mapCurrentToSource(self, point):
        """Maps the QPoint on the current image to source image coordinates."""
        scale = self.scale()
        x = round(point.x() / scale)
        y = round(point.y() / scale)
        return QtCore.QPoint(x, y)

    def currentRect(self):
        """Return a QRect for the local coordinates of the current image.

        The origin is the top left corner of this widget.
        """
        imgw = self.current.width()
        imgh = self.current.height()
        left = round((self.width() - imgw) / 2)
        top = round((self.height() - imgh) / 2)
        return QtCore.QRect(left, top, imgw, imgh)

    def currentGlobalRect(self):
        """Return a QRect for the global coordinates of the current image."""
        local = self.currentRect()
        topleft = self.mapToGlobal(local.topLeft())
        return QtCore.QRect(topleft, local.size())

    def currentTopLeft(self):
        """Return local coords for the left top corner of the current image."""
        return self.currentRect().topLeft()


class QTableItem(object):
    default_flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def __init__(self, datamap=None, flags=None):
        if datamap is None:
            self.datamap = {Qt.DisplayRole: ""}  # maps roles to values
        else:
            self.datamap = datamap  # TODO: validity check?
        if flags is None:
            self.flags = self.default_flags
        else:
            self.flags = flags

    def data(self, role=Qt.DisplayRole):
        return self.datamap.get(role, QtCore.QVariant())

    def setData(self, value, role=Qt.DisplayRole):
        # TODO: validity check?
        self.datamap[role] = value


class QTableModel(QtCore.QAbstractTableModel):
    """A simple model for table views.

    Might also be useful as base class when implementing more complex
    table models.
    """
    def __init__(self, column_headers, row_headers=None, parent=None):
        super().__init__(parent)
        self.colhead = []
        self.rowhead = []
        self.datamap = {}  # maps model key to item

        # add headers
        for text in column_headers:
            self.colhead.append(self.createHeaderItem({Qt.DisplayRole: text}))
        if row_headers is not None:
            for text in row_headers:
                item = self.createHeaderItem({Qt.DisplayRole: text})
                self.rowhead.append(item)

    def createHeaderItem(self, datamap=None, flags=None):
        return QTableItem(datamap, flags)

    def createKey(self, index):
        """Converts a model index to a (row, column) tuple."""
        return (index.row(), index.column())

    createItem = createHeaderItem

#    def index(self, row, column, parent=QModelIndex()):
#        return self.createIndex(row, column)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            # see http://doc.qt.io/qt-5/qabstractitemmodel.html#rowCount
            return 0
        else:
            return len(self.rowhead)  # TODO: check the meaning of parent

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self.colhead)

    def data(self, index, role=Qt.DisplayRole):
        key = self.createKey(index)
        if key in self.datamap:
            return self.datamap[key].data(role)
        # if we have no data for that role or index, we return an
        # invalid QVariant; why return that?
        # see: http://doc.qt.io/qt-5/qabstractitemmodel.html#data
        return QtCore.QVariant()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal:
            header = self.colhead
        elif orientation == Qt.Vertical:
            header = self.rowhead
        else:
            raise ValueError("Not a valid Qt orientation: %s" % orientation)
        try:
            return header[section].data(role)
        except IndexError:
            pass  # no data available for this section
        # if we have no data for that role or section, we return an
        # invalid QVariant; why do that?
        # so that the behaviour is similar to self.data
        return QtCore.QVariant()

    def flags(self, index):
        key = self.createKey(index)
        try:
            return self.datamap[key].flags
        except KeyError:
            return Qt.NoItemFlags


class QEditableTableModel(QTableModel):
    """An editable model for table views.
    """
    def __init__(self, column_headers, row_headers=None, parent=None):
        super().__init__(column_headers, row_headers, parent)

    def createItem(self, datamap=None, flags=None):
        item = super().createItem(datamap, flags)
        item.flags = item.flags | Qt.ItemIsEditable
        return item

    def setData(self, index, value, role=Qt.EditRole):
        key = self.createKey(index)
        item = self.datamap.get(key, self.createItem(*key))
        item.setData(value, role)
        self.datamap[key] = item
        self.dataChanged.emit(index, index, [role])
        return True


# --------------------------------------------------------------------------- #
# Define functions
# --------------------------------------------------------------------------- #
def clearLayout(layout):
    """Remove all widgets from a layout and delete them.

    http://stackoverflow.com/questions/4528347/
        clear-all-widgets-in-a-layout-in-pyqt
    """
    for idx in reversed(range(layout.count())):
        widget = layout.itemAt(idx).widget()
        # remove it from the layout list
        layout.removeWidget(widget)
        # remove it from the gui
        widget.setParent(None)


def calculateScale(scalingrect, framingrect):
    """Return the scaling factor and the limiting dimension.

    Multiplying the scaling factor with the width and height of scalingrect
    resizes it so it fits optimally into framingrect while preserving the
    aspect ratio of scalingrect.
    The returned limiting dimension is either 'width' or 'height'.
    """
    scw = scalingrect.width()
    sch = scalingrect.height()
    frw = framingrect.width()
    frh = framingrect.height()
    # determine which dimension requires the bigger shrink or smaller expansion
    wratio = frw / scw
    hratio = frh / sch
    if wratio < hratio:
        return (wratio, "width")
    # since both wratio and hratio are floats, the chance of them
    # being equal is very small and we don't care
    return (hratio, "height")


def getCoords(obj):
    """Takes a position, size or rect and returns a tuple.

    Conversion:
        QPoint -> (x, y)
        QSize  -> (width, height)
        QRect  -> (x, y, width, height)
    """
    # see if it behaves like a QPoint
    try:
        return (obj.x(), obj.y())
    except AttributeError:
        pass
    # see if it behaves like a QSize
    try:
        return (obj.width(), obj.height())
    except AttributeError:
        pass
    # see if it behaves like a QRect
    try:
        return (obj.x(), obj.y(), obj.width(), obj.height())
    except AttributeError:
        pass
    # handle invalid object
    msg = "This object is not a valid input for getCoords: %s"
    raise ValueError(msg % obj)


# --------------------------------------------------------------------------- #
# Declare module globals
# --------------------------------------------------------------------------- #
log = logging.getLogger(__name__)
