#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 ~ 2015 Deepin, Inc.
#               2011 ~ 2015 Wang YaoHua
#
# Author:     Wang YaoHua <mr.asianwang@gmail.com>
# Maintainer: Wang YaoHua <mr.asianwang@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
from uuid import uuid4

from PyQt5.QtCore import QObject, pyqtProperty, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication
from PyQt5.QtDBus import QDBusConnection

from utils.i18n import _
from dbus_services import DeepinMoviePrivateServie, DBUS_PATH
from dbus_interfaces import RendererManagerInterface
from dbus_interfaces import RendererRendererDeviceInterface
from dbus_interfaces import RendererPushHostInterface
from dbus_interfaces import RendererMediaPlayerPlayerInterface

class Renderer(QObject):
    nameChanged = pyqtSignal()
    iconChanged = pyqtSignal()
    uuidChanged = pyqtSignal()

    def __init__(self, parent):
        super(Renderer, self).__init__(parent)

    @pyqtProperty(str, notify=nameChanged)
    def name(self):
        return self._device.FriendlyName

    @pyqtProperty(str, notify=iconChanged)
    def icon(self):
        return self._device.IconURL

    @pyqtProperty(str, notify=uuidChanged)
    def uuid(self):
        return self._device.UDN

    @pyqtProperty(str)
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value

        self._device = RendererRendererDeviceInterface(self._path)
        self._player = RendererMediaPlayerPlayerInterface(self._path)
        self._push_host = RendererPushHostInterface(self._path)

    @pyqtSlot(str)
    def playPath(self, path):
        uri = self._push_host.hostFile(path)
        self._player.openUri(uri)
        self._player.play()

    @pyqtSlot(str)
    def removePath(self, path):
        self._push_host.removeFile(path)

    @pyqtSlot()
    def stop(self):
        self._player.stop()

class RendererManager(QObject):
    foundRenderer = pyqtSignal("QVariant", arguments=["renderer"])
    lostRenderer = pyqtSignal(str, arguments=["path"])

    def __init__(self):
        super(RendererManager, self).__init__()
        self._renderers = []

        self._iface = RendererManagerInterface()
        self._iface.FoundRenderer.connect(self._rendererFound)
        self._iface.LostRenderer.connect(
            lambda x: self.lostRenderer.emit(x.path()))

    def _rendererFound(self, path):
        renderer = Renderer(self)
        renderer.path = path.path()
        self.foundRenderer.emit(renderer)

    @pyqtSlot(result="QVariant")
    def getRenderers(self):
        paths = self._iface.getRenderers()

        for _path in paths:
            renderer = Renderer(self)
            renderer.path = _path
            self._renderers.append(renderer)

        return self._renderers

    @pyqtSlot(result=str)
    def getVersion(self):
        return self._iface.getVersion()

class DLNAController(QObject):
    rendererName = _("Deepin Movie")
    foundRenderer = pyqtSignal("QVariant", arguments=["renderer"])
    lostRenderer = pyqtSignal(str, arguments=["path"])

    def __init__(self, asRenderer=False):
        super(DLNAController, self).__init__()
        self._dbus_name = None
        self._dbus_service = None
        self._daemon_pid = None
        self._daemon_uuid = None

        self._renderer_manager = RendererManager()
        self._renderer_manager.foundRenderer.connect(self.foundRenderer)
        self._renderer_manager.lostRenderer.connect(self.lostRenderer)

        self.setAsRenderer(asRenderer)

    def _initDaemon(self):
        if self._asRenderer:
            if not self._dbus_service:
                if not self._dbus_name:
                    self._daemon_uuid = str(uuid4()).replace("-", "_")
                    self._dbus_name = "com.deepin.private.DeepinMovie_%s" \
                                      % self._daemon_uuid
                app = QApplication.instance()
                self._dbus_service = DeepinMoviePrivateServie(app)

                bus = QDBusConnection.sessionBus()
                bus.registerService(self._dbus_name)
                bus.registerObject(DBUS_PATH, self._dbus_service)

            self._daemon_pid = subprocess.Popen(["deepin-dlna-renderer",
                "-f", self.rendererName,
                "-u", self._daemon_uuid,
                "--service-name", self._dbus_name])

    @pyqtSlot(bool)
    def setAsRenderer(self, asRenderer):
        self._asRenderer = asRenderer
        if asRenderer:
            if not self._daemon_pid:
                self._initDaemon()
        else:
            if self._daemon_pid:
                self._daemon_pid.kill()
                self._daemon_pid = None
                self._daemon_uuid = None

    @pyqtSlot(result="QVariant")
    def getRenderers(self):
        renderers = self._renderer_manager.getRenderers()
        filter_rule = lambda x: self._daemon_uuid not in x.uuid \
                                and x.name.encode("utf-8") != self.rendererName
        return filter(filter_rule, renderers)

    @pyqtSlot(result=str)
    def getVersion(self):
        return self._renderer_manager.getVersion()