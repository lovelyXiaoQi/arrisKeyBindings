# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from .keybindingSystem import KeyBindingData
from .KeyBoardFormat import GetKeyBoardFormat

ScreenNode = clientApi.GetScreenNodeCls()
ViewBinder = clientApi.GetViewBinderCls()
compFactory = clientApi.GetEngineCompFactory()
levelId = clientApi.GetLevelId()

class keybindingUI(ScreenNode):
    def __init__(self, namespace, name, param):
        ScreenNode.__init__(self, namespace, name, param)
        self.selectorIndex = 0 # 左侧选项当前选择索引
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.keyBindingData = KeyBindingData.GetKeyMapping()

    def KeyPressedEvent(self, pressedKeys):
        # 键盘按键事件
        if not self.nowSelectButton:
            return
        if pressedKeys not in self.nowInputKeys:
            self.nowInputKeys.append(pressedKeys)
        bindings = self.nowSelectButton[1]
        nowInputKeys = tuple(self.nowInputKeys)
        bindings.keys = nowInputKeys
        self.UpdateScreen(True)
        # 保存玩家设置
        modKeyBinding = self.keyBindingData[self.selectorIndex]
        data = compFactory.CreateConfigClient(levelId).GetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), True) or {}
        key = str(bindings.default_keys) + str(bindings.description)
        data[key] = nowInputKeys
        compFactory.CreateConfigClient(levelId).SetConfigData(str(modKeyBinding.ModSpace) + str(modKeyBinding.ModName), data, True)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#arrisKeyBindingResetClick")
    def KeyBindingResetClick(self, args):
        # 重置按键映射
        index = args["#collection_index"]
        modKeyBinding = self.keyBindingData[self.selectorIndex]
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
        # 左键选择当前按键映射进行设置
        index = args["#collection_index"]
        modKeyBinding = self.keyBindingData[self.selectorIndex]
        modName = modKeyBinding.ModName
        self.nowSelectButton = (modName, modKeyBinding.Bindings[index])
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#arrisKeyBindingRightClick")
    def KeyBindingRightClick(self, _):
        # 右键退出设置当前的按键映射
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#selectorStackGrid.item_count")
    def SetSelectorStackGridCount(self):
        return len(self.keyBindingData)

    @ViewBinder.binding(ViewBinder.BF_BindInt, "#arrisKeybindingGrid.item_count")
    def SetKeybindingGridCount(self):
        modKeyBinding = self.keyBindingData[self.selectorIndex]
        return len(modKeyBinding.Bindings)

    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#arrisKeyBindingSelectorToggle")
    def SelectorToggleToggleChanged(self, args):
        self.selectorIndex = args["index"]
        self.nowSelectButton = None
        self.nowInputKeys = []
        self.UpdateScreen(True)

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "arrisKeybindingGrid", "#keybinding.description")
    def SetKeybindingItemDescription(self, index):
        modKeyBinding = self.keyBindingData[self.selectorIndex]
        if index >= len(modKeyBinding.Bindings):
            return ""
        return modKeyBinding.Bindings[index].description

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "arrisKeybindingGrid", "#keybinding.keys")
    def SetKeybindingItemKeys(self, index):
        modKeyBinding = self.keyBindingData[self.selectorIndex]
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

        # 检测按键冲突
        conflictList = []
        for modKeyBindingCls in self.keyBindingData:
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
        # 设置是否允许玩家进行修改
        modKeyBinding = self.keyBindingData[self.selectorIndex]
        if index >= len(modKeyBinding.Bindings):
            return True
        return modKeyBinding.Bindings[index].allow_modify

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "selectorStackGrid", "#selector.text")
    def SetSelectorItemName(self, index):
        return self.keyBindingData[index].ModName

    @ViewBinder.binding_collection(ViewBinder.BF_BindString, "selectorStackGrid", "#icon.texture")
    def SetSelectorItemIcon(self, index):
        return self.keyBindingData[index].ModIconPath

    @ViewBinder.binding(ViewBinder.BF_ButtonClickUp, "#CloseKeyBindingScreen")
    def CloseScreen(self, _):
        clientApi.PopScreen()
