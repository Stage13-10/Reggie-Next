#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie Next - New Super Mario Bros. Wii Level Editor
# Milestone 4
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC, AboodXD, John10v10, TheGrop, CLF78,
# Zementblock, Danster64

# This file is part of Reggie Next.

# Reggie Next is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie Next is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie Next.  If not, see <http://www.gnu.org/licenses/>.


# spritelib.py
# Contains general code to render sprite images in the editor UI


################################################################
################################################################

# Imports
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt

OutlineColor = None
OutlinePen = None
OutlineBrush = None
ImageCache = {}
Tiles = {}
SpriteImagesLoaded = set()

SpritesFolders = []
RealViewEnabled = False
Area = None


################################################################
################################################################
################################################################
########################## Functions ###########################

def main():
    """
    Resets Sprites.py to its original settings
    """
    global OutlineColor, OutlinePen, OutlineBrush, ImageCache, SpritesFolders
    OutlinePen = QtGui.QPen(OutlineColor, 4)
    OutlineBrush = QtGui.QBrush(OutlineColor)

    for i in range(256):
        Tiles[i] = None

    # Don't make a new dict instance for ImageCache because sprites.py
    # won't receive it, which causes bugs.
    ImageCache.clear()
    SpriteImagesLoaded.clear()

    SpritesFolders = []


def GetImg(imgname, image=False):
    """
    Returns the image as a QImage from the PNG filename 'imgname' from the first
    matching sprite image folder. If 'image' is False, a QPixmap of this image
    is returned. If the image could not be found, None is returned and a warning
    is printed.
    """
    imgname = str(imgname)

    # Try to find the best path
    path = os.path.join('reggiedata', 'sprites', imgname)

    for folder in reversed(SpritesFolders):  # find the most recent copy
        tryPath = os.path.join(folder, imgname)
        if os.path.isfile(tryPath):
            path = tryPath
            break

    # Return the appropriate object
    if os.path.isfile(path):
        if image:
            return QtGui.QImage(path)
        else:
            return QtGui.QPixmap(path)

    print("[Warning] Could not load sprite image (%s)!" % imgname)

def GetTile(tile_id):
    """
    Returns the corresponding tile image if a tile is loaded. Otherwise, it
    returns the "unknown tile" override.
    """
    tile = Tiles[tile_id]

    if tile is None:
        tile = Tiles[4 * 0x200 + 64]  # The "Unknown Tile" override

    return tile.main

def loadIfNotInImageCache(name, filename):
    """
    If name is not in ImageCache, loads the image
    referenced by 'filename' and puts it there
    """
    if name not in ImageCache:
        ImageCache[name] = GetImg(filename)


def MapPositionToZoneID(zones, x, y, get_id=False):
    """
    Returns the index of the zone containing or nearest the specified position
    by default. Set 'get_id' to True to get the actual zone id. Returns -1 on
    failure.
    """
    minimumdist = match_index = -1

    for i, zone in enumerate(zones):
        rect = zone.ZoneRect
        if rect.contains(x, y):
            match_index = i
            break

        dist = 0
        l, t, r, b = rect.getCoords()

        if x < l: dist += (l - x) ** 2
        elif x > r: dist += (x - r) ** 2

        if y < t: dist += (t - y) ** 2
        elif y > b: dist += (y - b) ** 2

        if dist < minimumdist or minimumdist == -1:
            minimumdist = dist
            match_index = i

    if match_index == -1:
        return -1

    return zones[match_index].id if get_id else match_index


################################################################
################################################################
################################################################
##################### SpriteImage Classes ######################

class SpriteImage:
    """
    Class that contains information about a sprite image
    """

    def __init__(self, parent, scale=1.5):
        """
        Intializes the sprite image
        """
        self.parent = parent

        self.alpha = 1.0
        self.image = None
        self.spritebox = Spritebox(scale)
        self.dimensions = 0, 0, 16, 16
        self.scale = scale
        self.aux = []

    @staticmethod
    def loadImages():
        """
        Loads all images needed by the sprite
        """
        pass

    def dataChanged(self):
        """
        Called whenever the sprite data changes
        """
        pass

    def positionChanged(self):
        """
        Called whenever the sprite position changes
        """
        pass

    def paint(self, painter):
        """
        Paints the sprite
        """
        pass

    def remove(self):
        """
        Called whenever the parent is removed
        """
        pass

    # Offset property
    def getOffset(self):
        return (self.xOffset, self.yOffset)

    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]

    def delOffset(self):
        self.xOffset, self.yOffset = 0, 0

    offset = property(
        getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple',
    )

    # Size property
    def getSize(self):
        return (self.width, self.height)

    def setSize(self, new):
        self.width, self.height = new[0], new[1]

    def delSize(self):
        self.width, self.height = 16, 16

    size = property(
        getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple',
    )

    # Dimensions property
    def getDimensions(self):
        return (self.xOffset, self.yOffset, self.width, self.height)

    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]

    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = 0, 0, 16, 16

    dimensions = property(
        getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one tuple',
    )


class SpriteImage_Static(SpriteImage):
    """
    A simple class for drawing a static sprite image
    """

    def __init__(self, parent, scale=1.5, image=None, offset=None):
        super().__init__(parent, scale)
        self.image = image
        self.spritebox.shown = False

        if self.image is not None:
            self.width = (self.image.width() / self.scale) + 1
            self.height = (self.image.height() / self.scale) + 2
        if offset is not None:
            self.xOffset = offset[0]
            self.yOffset = offset[1]

    def dataChanged(self):
        super().dataChanged()

        if self.image is not None:
            self.size = (
                (self.image.width() / self.scale) + 1,
                (self.image.height() / self.scale) + 2,
            )
        else:
            del self.size

    def paint(self, painter):
        super().paint(painter)

        if self.image is None: return
        painter.save()
        painter.setOpacity(self.alpha)
        painter.scale(1.5 / self.scale, 1.5 / self.scale)  # rescale images not based on a 24x24 block size
        painter.setRenderHint(painter.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.image)
        painter.restore()


class SpriteImage_StaticMultiple(SpriteImage_Static):
    """
    A class that acts like a SpriteImage_Static but lets you change
    the image with the dataChanged() function
    """

    def __init__(self, parent, scale=1.5, image=None, offset=None):
        super().__init__(parent, scale, image, offset)
        # no other changes needed yet


################################################################
################################################################
################################################################
####################### Spritebox Class ########################

class Spritebox:
    """
    Contains size and other information for a spritebox
    """

    def __init__(self, scale=1.5):
        super().__init__()
        self.shown = True
        self.xOffset = 0
        self.yOffset = 0
        self.width = 16
        self.height = 16
        self.scale = scale

    # Offset property
    def getOffset(self):
        return self.xOffset, self.yOffset

    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]

    def delOffset(self):
        self.xOffset, self.yOffset = 0, 0

    offset = property(
        getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple',
    )

    # Size property
    def getSize(self):
        return self.width, self.height

    def setSize(self, new):
        self.width, self.height = new[0], new[1]

    def delSize(self):
        self.width, self.height = 16, 16

    size = property(
        getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple',
    )

    # Dimensions property
    def getDimensions(self):
        return self.xOffset, self.yOffset, self.width, self.height

    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]

    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = 0, 0, 16, 16

    dimensions = property(
        getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one '
        'tuple',
    )

    # RoundedRect property
    def getRR(self):
        return QtCore.QRectF(
            (self.xOffset * self.scale) + 1,
            (self.yOffset * self.scale) + 1,
            (self.width * self.scale) - 2,
            (self.height * self.scale) - 2,
        )

    def setRR(self, new):
        self.dimensions = (
            (new.x() / self.scale) - 1,
            (new.y() / self.scale) - 1,
            (new.width() / self.scale) + 2,
            (new.height() / self.scale) + 2,
        )

    def delRR(self):
        self.dimensions = 0, 0, 16, 16

    RoundedRect = property(
        getRR, setRR, delRR,
        'Property that contains the rounded rect for the spritebox',
    )

    # BoundingRect property
    def getBR(self):
        return QtCore.QRectF(
            self.xOffset * self.scale,
            self.yOffset * self.scale,
            self.width * self.scale,
            self.height * self.scale,
        )

    def setBR(self, new):
        self.dimensions = (
            new.x() * self.scale,
            new.y() * self.scale,
            new.width() * self.scale,
            new.height() * self.scale,
        )

    def delBR(self):
        self.dimensions = 0, 0, 16, 16

    BoundingRect = property(
        getBR, setBR, delBR,
        'Property that contains the bounding rect for the spritebox',
    )


################################################################
################################################################
################################################################
#################### AuxiliarySpriteItem Classes ###############


class AuxiliaryItem:
    """
    Base class for all auxiliary things
    """
    pass


class AuxiliarySpriteItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
    """
    Base class for auxiliary objects that accompany specific sprite types
    """

    def __init__(self, parent):
        """
        Generic constructor for auxiliary items
        """
        super().__init__(parent)
        self.parent = parent
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, True)
        self.setParentItem(parent)
        self.hover = False

        self.BoundingRect = QtCore.QRectF(0, 0, 24, 24)

    def setIsBehindSprite(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the sprite or in front of it. Default is for the item to
        be behind the sprite.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect


class AuxiliaryTrackObject(AuxiliarySpriteItem):
    """
    Track shown behind moving platforms to show where they can move
    """
    Horizontal = 1
    Vertical = 2

    def __init__(self, parent, width, height, direction):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.setPos(0, 0)
        self.width = width
        self.height = height
        self.direction = direction
        self.hover = False

    def setSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)

        if self.direction == self.Horizontal:
            lineY = self.height * 0.75
            painter.drawLine(20, lineY, (self.width * 1.5) - 20, lineY)
            painter.drawEllipse(8, lineY - 4, 8, 8)
            painter.drawEllipse((self.width * 1.5) - 16, lineY - 4, 8, 8)
        else:
            lineX = self.width * 0.75
            painter.drawLine(lineX, 20, lineX, (self.height * 1.5) - 20)
            painter.drawEllipse(lineX - 4, 8, 8, 8)
            painter.drawEllipse(lineX - 4, (self.height * 1.5) - 16, 8, 8)


class AuxiliaryCircleOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width, alignMode=Qt.AlignHCenter):
        """
        Constructor
        """
        super().__init__(parent)

        self.hover = False
        self.fillFlag = True
        self.alignMode = alignMode
        self.setSize(width)

    def setSize(self, width):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, width * 1.5)

        centerOffset = (8 - (width / 2)) * 1.5
        fullOffset = -(width * 1.5) + 24

        xval = 0
        if self.alignMode & Qt.AlignHCenter:
            xval = centerOffset
        elif self.alignMode & Qt.AlignRight:
            xval = fullOffset

        yval = 0
        if self.alignMode & Qt.AlignVCenter:
            yval = centerOffset
        elif self.alignMode & Qt.AlignBottom:
            yval = fullOffset

        self.setPos(xval, yval)
        self.width = width

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)

        if self.fillFlag:
            painter.setBrush(OutlineBrush)

        painter.drawEllipse(self.BoundingRect)


class AuxiliaryRotationAreaOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, width * 1.5)
        self.setPos((8 - (width / 2)) * 1.5, (8 - (width / 2)) * 1.5)
        self.width = width
        self.startAngle = 0
        self.spanAngle = 0
        self.hover = False

    def SetAngle(self, startAngle, spanAngle):
        self.startAngle = startAngle * 16
        self.spanAngle = spanAngle * 16

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawPie(self.BoundingRect, self.startAngle, self.spanAngle)


class AuxiliaryRectOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width, height, xoff=0, yoff=0):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)
        self.hover = False
        self.color = None
        self.fillFlag = True

    def setSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)

    def setColor(self, color):
        if color is None:
            self.color = None
        else:
            self.color = QtGui.QColor(color)

    def paint(self, painter, option, widget=None):
        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.color is None:
            painter.setPen(OutlinePen)
            if self.fillFlag:
                painter.setBrush(OutlineBrush)
        else:
            pen = QtGui.QPen(OutlinePen)
            self.color.setAlpha(pen.color().alpha())
            pen.setColor(self.color)
            painter.setPen(pen)

            if self.fillFlag:
                brush = QtGui.QBrush(OutlineBrush)
                self.color.setAlpha(brush.color().alpha())
                brush.setColor(self.color)
                painter.setBrush(brush)

        painter.drawRect(self.BoundingRect)


class AuxiliaryPainterPath(AuxiliarySpriteItem):
    def __init__(self, parent, path, width, height, xoff=0, yoff=0):
        """
        Constructor
        """
        super().__init__(parent)

        self.PainterPath = path
        self.setPos(xoff, yoff)
        self.fillFlag = True

        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.hover = False

    def setPath(self, path):
        self.PainterPath = path

    def setSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)
        if self.fillFlag: painter.setBrush(OutlineBrush)
        painter.drawPath(self.PainterPath)


class AuxiliaryImage(AuxiliarySpriteItem):
    def __init__(self, parent, width, height):
        """
        Constructor
        """
        super().__init__(parent)
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.width = width
        self.height = height
        self.image = None
        self.hover = True
        self.alpha = 1

    def setSize(self, width, height, xoff=0, yoff=0):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)

        if self.image is not None:
            painter.setOpacity(self.alpha)
            painter.drawPixmap(0, 0, self.image)
            painter.setOpacity(1)


class AuxiliaryImage_FollowsRect(AuxiliaryImage):
    def __init__(self, parent, width, height):
        """
        Constructor
        """
        super().__init__(parent, width, height)
        self.alignment = Qt.AlignTop | Qt.AlignLeft
        self.realwidth = self.width
        self.realheight = self.height
        self.realimage = None
        # Doing it this way may provide a slight speed boost?
        self.flagPresent = lambda flags, flag: flags | flag == flags

    def setSize(self, width, height):
        super().setSize(width, height)

        self.realwidth = width
        self.realheight = height

    def paint(self, painter, option, widget=None):

        if not RealViewEnabled: return
        super().paint(painter, option, widget)

        if self.realimage is None:
            try:
                self.realimage = self.image
            except:
                pass

    def move(self, x, y, w, h):
        """
        Repositions the auxiliary image
        """

        # This will be used later
        oldx, oldy = self.x(), self.y()

        # Decide on the height to use
        # This solves the problem of "what if
        # agument w is smaller than self.width?"
        self.width = self.realwidth
        self.height = self.realheight
        changedSize = False
        if w < self.width:
            self.width = w
            changedSize = True
        if h < self.height:
            self.height = h
            changedSize = True
        if self.realimage is not None:
            if changedSize:
                self.image = self.realimage.copy(0, 0, w, h)
            else:
                self.image = self.realimage

        # Find the absolute X-coord
        if self.flagPresent(self.alignment, Qt.AlignLeft):
            newx = x
        elif self.flagPresent(self.alignment, Qt.AlignRight):
            newx = x + w - self.width
        else:
            newx = x + (w / 2) - (self.width / 2)

        # Find the absolute Y-coord
        if self.flagPresent(self.alignment, Qt.AlignTop):
            newy = y
        elif self.flagPresent(self.alignment, Qt.AlignBottom):
            newy = y + h - self.height
        else:
            newy = y + (h / 2) - (self.height / 2)

        # Translate that to relative coords
        try:
            parent = self.parent
            newx = newx - parent.x()
            newy = newy - parent.y()
        except RuntimeError:
            # Must catch this error -> if parent is deleted
            return

        if newx == oldx and newy == oldy:
            # Don't set the position and update the scene if the item did not
            # move.
            return

        # Set the pos
        self.setPos(newx, newy)

        # Update the affected area of the scene
        if self.scene() is not None:
            self.scene().update(oldx + parent.x(), oldy + parent.y(), self.width, self.height)


class AuxiliaryZoneItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
    """
    An auxiliary item that can have a zone as its parent
    """

    def __init__(self, parent, imageObj):
        """
        Generic constructor for auxiliary zone items
        """
        super().__init__(parent)
        self.parent = parent
        self.imageObj = imageObj
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.setParentItem(parent)
        self.hover = False

        if parent is not None:
            parent.aux.add(self)

        self.BoundingRect = QtCore.QRectF(0, 0, 24, 24)

    def setIsBehindZone(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the zone or in front of it. Default is for the item to
        be in front of the zone.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def setZoneID(self, id):
        """
        Changes this aux item's parent to zone with the given id.
        Raises ValueError if no zone with this id exists.
        """

        if not hasattr(Area, 'zones'): return

        z = None
        for iterz in Area.zones:
            if iterz.id == id: z = iterz
        if z is None:
            raise ValueError('No zone with this ID exists.')

        if self.parent is not None:
            self.parent.aux.remove(self)
        self.setParentItem(z)
        self.parent = z
        z.aux.add(self)

    def alignToZone(self):
        """
        Resets the position and size of the AuxiliaryZoneItem to that of the zone
        """
        self.setPos(0, 0)
        if self.parent is not None:
            self.BoundingRect = QtCore.QRectF(self.parent.BoundingRect)
        else:
            self.BoundingRect = QtCore.QRectF(0, 0, 24, 24)

    @staticmethod
    def zoneRepositioned():
        """
        Called when the zone is repositioned or resized
        """
        pass

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect


class AuxiliaryLocationItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
    """
    An auxiliary item that can have a location as its parent
    """

    def __init__(self, parent, imageObj):
        """
        Generic constructor for auxiliary items
        """
        super().__init__(parent)
        self.parent = parent
        self.imageObj = imageObj
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.setParentItem(parent)
        self.hover = False

    def setIsBehindLocation(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the location or in front of it. Default is for the item to
        be in front of the location.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def alignToLocation(self):
        """
        Resets the position and size of the AuxiliaryLocationItem to that of the
        location.
        """
        self.setPos(0, 0)
        self.setSize(self.parent.width(), self.parent.height())

    def paint(self, painter, option, widget=None):
        """
        Paints the image, tiled to fill the bounding rect of the location it
        belongs to.
        """
        if self.imageObj is None:
            return

        painter.drawTiledPixmap(self.boundingRect(), self.imageObj)

    def remove(self):
        """
        Removes the auxiliary item.
        """
        # Detach this item from its parent so it gets deleted properly. This
        # causes the last reference to this item to be held by the sprite image
        # this is an auxiliary item to, which causes it to be deleted properly.
        self.setParentItem(None)

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.parent.DrawRect
