# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi
from collections import Counter
# ========== 全局变量 ==========
ClientSystem = clientApi.GetClientSystemCls()
nameSpace = clientApi.GetEngineNamespace()
SystemName = clientApi.GetEngineSystemName()
compFactory = clientApi.GetEngineCompFactory()
levelId = clientApi.GetLevelId()
# ========== UI代理 ==========
NativeScreenManager = clientApi.GetNativeScreenManagerCls()
NativeScreenManager.instance().RegisterScreenProxy("settings.screen_world_controls_and_settings", "keybindingScripts.proxys.SettingScreenProxy.SettingScreenProxy")
# ===========================

def PushKeyBindingScreen():
    clientApi.PushScreen("arris", "arrisKeyBinding")

class KeyBindingData(object):
    _instance = None
    def __init__(self):
        self._bindings = []

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(KeyBindingData, cls).__new__(cls)
            cls._instance._bindings = []
        return cls._instance

    @property
    def KeyMapping(self):
        return self._bindings

    @KeyMapping.setter
    def KeyMapping(self, value):
        if not isinstance(value, CreateKeyBindingFactory):
            raise ValueError("传入的参数错误")
        if not hasattr(self, '_bindings') or not isinstance(self._bindings, list):
            self._bindings = []
        if value not in self._bindings:
            self._bindings.append(value)


keyBindingData = KeyBindingData()


class KeyBinding:
    def __init__(self, keys, callback, description, allow_modify, trigger_mode, trigger_screens, defaultKeys):
        self.__keys = tuple(keys)
        self.__callback = callback
        self.__description = description
        self.__allow_modify = allow_modify
        self.__trigger_mode = trigger_mode
        self.__trigger_screens = tuple(trigger_screens) if trigger_screens else tuple()
        # 创建默认值，用于重置
        self.__defaultKeys = defaultKeys or tuple(keys)

    @property
    def keys(self):
        return self.__keys

    @keys.setter
    def keys(self, value):
        self.__keys = tuple(value)

    @property
    def callback(self):
        return self.__callback

    @property
    def description(self):
        return self.__description

    @property
    def allow_modify(self):
        return self.__allow_modify

    @property
    def trigger_mode(self):
        return self.__trigger_mode

    @property
    def trigger_screens(self):
        return self.__trigger_screens

    @property
    def default_keys(self):
        return self.__defaultKeys

    @default_keys.setter
    def default_keys(self, value):
        self.__defaultKeys = tuple(value)

class CreateKeyBindingFactory(object):
    def __init__(self, modSpace, modName, modIconPath="textures/ui/keyboard_and_mouse_glyph_color"):
        # type: (str, str, str) -> None
        self.__modSpace = modSpace
        self.__modName = modName
        self.__modIconPath = modIconPath
        self.__bindings = []
        self.Create()

    def Create(self):
        for obj in keyBindingData.KeyMapping:
            if (obj.ModSpace, obj.ModName) == (self.__modSpace, self.__modName):
                # 防止重载时,重复添加按键映射
                return
        keyBindingData.KeyMapping = self

    def RegisterKeyBinding(self, keys, callback, description, allow_modify=True, trigger_mode=0, trigger_screens=()):
        """
        :param keys: 按下的按键，支持单个或多个组合键
        :param callback: 触发的回调函数
        :param description: 描述
        :param allow_modify: 是否允许玩家进行自定义修改 default: True
        :param trigger_mode: 触发模式: 0 为单次触发 1 为游戏Tick触发，直到松开为止 2 为渲染帧Tick触发，直到松开为止 (默认为0)
        :param trigger_screens: 允许触发的界面 (默认为空,代表全局触发)
        :return: None
        """
        configData = compFactory.CreateConfigClient(levelId).GetConfigData(str(self.ModSpace) + str(self.ModName), True) or {}
        key = str(keys) + str(description)
        if configData and key in configData:
            bindingKeys = configData.get(key)
        else:
            bindingKeys = keys
        self.__bindings.append(KeyBinding(bindingKeys, callback, description, allow_modify, trigger_mode, trigger_screens, keys))

    @property
    def ModSpace(self):
        return self.__modSpace

    @property
    def ModName(self):
        return self.__modName

    @property
    def ModIconPath(self):
        return self.__modIconPath

    @property
    def Bindings(self):
        return self.__bindings

class keybindingSystem(ClientSystem):
    def __init__(self, namespace, systemName):
        ClientSystem.__init__(self, namespace, systemName)
        self.ListenForEvent(nameSpace, SystemName, "UiInitFinished", self, self.Ui_Init)
        self.ListenForEvent(nameSpace, SystemName, "OnKeyPressInGame", self, self.ArrisKeyPressedEvent)
        self.ListenForEvent(nameSpace, SystemName, "OnScriptTickClient", self, self.ArrisGameTick)
        self.ListenForEvent(nameSpace, SystemName, "GameRenderTickEvent", self, self.ArrisRenderTick)

        self._pressed_keys = []
        self._game_tick_callbacks = []
        self._render_tick_callbacks = []

    @staticmethod
    def Ui_Init(_):
        clientApi.RegisterUI("arris", "arrisKeyBinding", "keybindingScripts.keybindingUI.keybindingUI", "arrisCustomKeyBinding.arrisKeyBindingScreen")

    def ArrisGameTick(self):
        """网易脚本刻更新处理"""
        for func in self._game_tick_callbacks:
            func()

    def ArrisRenderTick(self, _):
        """游戏渲染刻更新处理"""
        for func in self._render_tick_callbacks:
            func()

    def ArrisKeyPressedEvent(self, args):
        """处理键盘事件"""
        keyValue = int(args['key'])
        isDown = int(args["isDown"])
        screenName = args["screenName"]

        if isDown:
            if keyValue not in self._pressed_keys:
                self._pressed_keys.append(keyValue)
                if screenName == "arrisKeyBindingScreen":
                    clientApi.GetUI("arris", "arrisKeyBinding").KeyPressedEvent(keyValue)
        else:
            if keyValue in self._pressed_keys:
                self._pressed_keys.remove(keyValue)
        if screenName == "arrisKeyBindingScreen":
            # 在按键映射设置界面取消触发回调函数，防止在设置时出现意外情况
            return
        # 检查并触发键位绑定
        for cls in keyBindingData.KeyMapping:
            for mappingData in cls.Bindings:
                if Counter(mappingData.keys) == Counter(self._pressed_keys):
                    if mappingData.trigger_screens and screenName not in mappingData.trigger_screens:
                        continue

                    if mappingData.trigger_mode == 1 and mappingData.callback not in self._game_tick_callbacks:
                        self._game_tick_callbacks.append(mappingData.callback)
                    elif mappingData.trigger_mode == 2 and mappingData.callback not in self._render_tick_callbacks:
                        self._render_tick_callbacks.append(mappingData.callback)
                    else:
                        mappingData.callback()
                else:
                    if mappingData.callback in self._game_tick_callbacks:
                        self._game_tick_callbacks.remove(mappingData.callback)
                    if mappingData.callback in self._render_tick_callbacks:
                        self._render_tick_callbacks.remove(mappingData.callback)
