# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from .keybindingSystem import keyBindingData
from .KeyBoardFormat import GetKeyBoardFormat

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()
compFactory = clientApi.GetEngineCompFactory()
levelId = clientApi.GetLevelId()

class keybindingUI(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        compFactory.CreateGame(levelId).SimulateTouchWithMouse(False)
        self.selectorIndex = 0 # 左侧选项当前选择索引
        self.nowSelectButton = None
        self.nowInputKeys = []

    def KeyPressedEvent(self, pressedKeys):
        if not self.nowSelectButton:
            return
        if pressedKeys not in self.nowInputKeys:
            self.nowInputKeys.append(pressedKeys)
        bindings = self.nowSelectButton[1]
        nowInputKeys = tuple(self.nowInputKeys)
        bindings.keys = nowInputKeys
        self.UpdateScreen(True)
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        # 保存玩家设置
        data = compFactory.CreateConfigClient(levelId).GetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), True) or {}
        key = str(bindings.default_keys) + str(bindings.description)
        data[key] = nowInputKeys
        compFactory.CreateConfigClient(levelId).SetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), data, True)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#arrisKeyBindingResetClick")
    def KeyBindingResetClick(self, args):
        index = args["#collection_index"]
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        bindings = modKeyBinding.Bindings[index]
        bindings.keys = bindings.default_keys
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.UpdateScreen(True)
        # 保存玩家设置
        data = compFactory.CreateConfigClient(levelId).GetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), True) or {}
        key = str(bindings.default_keys) + str(bindings.description)
        data[key] = bindings.default_keys
        compFactory.CreateConfigClient(levelId).SetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), data, True)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#arrisKeyBindingLeftClick")
    def KeyBindingLeftClick(self, args):
        path = args["ButtonPath"]
        controlList = path.split("/")
        newPath = ""
        for controlName in controlList[1:]:
            newPath += "/" + controlName

        index = args["#collection_index"]
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        modName = modKeyBinding.ModName
        self.nowSelectButton = (modName, modKeyBinding.Bindings[index])
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#arrisKeyBindingRightClick")
    def KeyBindingRightClick(self, args):
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#selectorStackGrid.item_count")
    def SetSelectorStackGridCount(self):
        return len(keyBindingData.KeyMapping)

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#arrisKeybindingGrid.item_count")
    def SetKeybindingGridCount(self):
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        return len(modKeyBinding.Bindings)

    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#arrisKeyBindingSelectorToggle")
    def SelectorToggleToggleChanged(self, args):
        self.selectorIndex = args["index"]
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "arrisKeybindingGrid", "#keybinding.description")
    def SetKeybindingItemDescription(self, index):
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        if index >= len(modKeyBinding.Bindings):
            return ""
        return modKeyBinding.Bindings[index].description

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "arrisKeybindingGrid", "#keybinding.keys")
    def SetKeybindingItemKeys(self, index):
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        formatText = ""
        if index >= len(modKeyBinding.Bindings):
            return ""
        keys = modKeyBinding.Bindings[index].keys
        # 拼接中文格式化按键
        for i, keyEnum in enumerate(keys):
            keyName = GetKeyBoardFormat(keyEnum)
            formatText += keyName
            if i < len(keys) - 1:
                formatText += " + "

        conflictList = []
        # 检测按键冲突
        for modKeyBindingCls in keyBindingData.KeyMapping:
            for binding in modKeyBindingCls.Bindings:
                if binding.keys == keys:
                    conflictList.append((modKeyBindingCls.ModName, keys))
                if len(conflictList) > 1:
                    formatText = "§c{}".format(formatText)
        # 设置选中样式
        if (modKeyBinding.ModName, modKeyBinding.Bindings[index]) == self.nowSelectButton:
            formatText = "§e> §2{}§e <".format(formatText)

        return formatText

    @ViewBinder.binding_collection(ViewBinder.BF_BindBool, "arrisKeybindingGrid", "#key_binding.enabled")
    def SetKeybindingItemEnabled(self, index):
        modKeyBinding = keyBindingData.KeyMapping[self.selectorIndex]
        if index >= len(modKeyBinding.Bindings):
            return True
        return modKeyBinding.Bindings[index].allow_modify

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "selectorStackGrid", "#selector.text")
    def SetSelectorItemName(self, index):
        return keyBindingData.KeyMapping[index].ModName

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "selectorStackGrid", "#icon.texture")
    def SetSelectorItemIcon(self, index):
        return keyBindingData.KeyMapping[index].ModIconPath

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#CloseKeyBindingScreen")
    def CloseScreen(self, _):
        clientApi.PopScreen()