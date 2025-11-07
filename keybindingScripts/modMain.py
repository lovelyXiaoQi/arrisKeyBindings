# -*- coding: utf-8 -*-
from mod.common.mod import Mod
import mod.client.extraClientApi as clientApi

@Mod.Binding(name="keybindingScripts", version="0.0.1")
class keybindingScripts(object):
    def __init__(self):
        pass

    @Mod.InitClient()
    def keybindingClientInit(self):
        clientApi.RegisterSystem("keybinding", "keybindingSystem", "keybindingScripts.keybindingSystem.keybindingSystem")
