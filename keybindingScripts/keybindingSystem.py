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

PushKeyBindingScreen = lambda: clientApi.PushScreen("arris", "arrisKeyBinding")

class KeyBindingData(object):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KeyBindingData, cls).__new__(cls)
            cls._instance._bindings = []
        return cls._instance
    
    def __init__(self):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self._bindings = []
        self._initialized = True

    @property
    def KeyMapping(self):
        # type: () -> list
        return self._bindings

    @KeyMapping.setter
    def KeyMapping(self, value):
        # type: (CreateKeyBindingFactory) -> None
        if not isinstance(value, CreateKeyBindingFactory):
            raise ValueError("传入的参数错误")
        if not hasattr(self, '_bindings') or not isinstance(self._bindings, list):
            self._bindings = []
        if value not in self._bindings:
            self._bindings.append(value)


keyBindingData = KeyBindingData()


class KeyBinding(object):
    """
    按键绑定数据类
    存储单个按键绑定的所有相关信息
    """
    def __init__(self, keys, callback, description, allow_modify, trigger_mode, trigger_screens, defaultKeys):
        # type: (tuple, callable, str, bool, int, tuple, tuple) -> None
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
        # type: () -> tuple
        return self.__keys

    @keys.setter
    def keys(self, value):
        # type: (tuple) -> None
        self.__keys = tuple(value)

    @property
    def callback(self):
        # type: () -> callable
        return self.__callback

    @property
    def description(self):
        # type: () -> str
        return self.__description

    @property
    def allow_modify(self):
        # type: () -> bool
        return self.__allow_modify

    @property
    def trigger_mode(self):
        # type: () -> int
        return self.__trigger_mode

    @property
    def trigger_screens(self):
        # type: () -> tuple
        return self.__trigger_screens

    @property
    def default_keys(self):
        # type: () -> tuple
        return self.__defaultKeys

    @default_keys.setter
    def default_keys(self, value):
        # type: (tuple) -> None
        self.__defaultKeys = tuple(value)

class CreateKeyBindingFactory(object):
    """
    按键绑定工厂类
    用于创建和管理特定模组的按键绑定
    """
    def __init__(self, modSpace, modName, modIconPath="textures/ui/keyboard_and_mouse_glyph_color"):
        # type: (str, str, str) -> None
        self.__modSpace = modSpace
        self.__modName = modName
        self.__modIconPath = modIconPath
        self.__bindings = []
        self.Create()

    def Create(self):
        # type: () -> None
        for obj in keyBindingData.KeyMapping:
            if (obj.ModSpace, obj.ModName) == (self.__modSpace, self.__modName):
                # 防止重载时,重复添加按键映射
                return
        keyBindingData.KeyMapping = self

    def RegisterKeyBinding(self, keys, callback, description, allow_modify=True, trigger_mode=0, trigger_screens=()):
        # type: (tuple, callable, str, bool, int, tuple) -> None
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
        # type: () -> str
        return self.__modSpace

    @property
    def ModName(self):
        # type: () -> str
        return self.__modName

    @property
    def ModIconPath(self):
        # type: () -> str
        return self.__modIconPath

    @property
    def Bindings(self):
        # type: () -> list
        return self.__bindings

class keybindingSystem(ClientSystem):
    """
    按键绑定系统主类
    处理按键事件、游戏刻更新和渲染刻更新
    """
    def __init__(self, namespace, systemName):
        # type: (str, str) -> None
        ClientSystem.__init__(self, namespace, systemName)
        self.ListenForEvent(nameSpace, SystemName, "UiInitFinished", self, self.Ui_Init)
        self.ListenForEvent(nameSpace, SystemName, "OnKeyPressInGame", self, self.ArrisKeyPressedEvent)
        self.ListenForEvent(nameSpace, SystemName, "OnScriptTickClient", self, self.ArrisGameTick)
        self.ListenForEvent(nameSpace, SystemName, "GameRenderTickEvent", self, self.ArrisRenderTick)

        self._pressed_keys = set()  # type: set
        self._game_tick_callbacks = set()  # type: set
        self._render_tick_callbacks = set()  # type: set

    @staticmethod
    def Ui_Init(_):
        # type: (any) -> None
        clientApi.RegisterUI("arris", "arrisKeyBinding", "keybindingScripts.keybindingUI.keybindingUI", "arrisCustomKeyBinding.arrisKeyBindingScreen")

    def ArrisGameTick(self):
        # type: () -> None
        """网易脚本刻更新处理"""
        for func in self._game_tick_callbacks:
            func()

    def ArrisRenderTick(self, _):
        # type: (any) -> None
        """游戏渲染刻更新处理"""
        for func in self._render_tick_callbacks:
            func()

    def ArrisKeyPressedEvent(self, args):
        # type: (dict) -> None
        """处理键盘事件"""
        keyValue = int(args['key'])
        isDown = int(args["isDown"])
        screenName = args["screenName"]

        if isDown:
            if keyValue not in self._pressed_keys:
                self._pressed_keys.add(keyValue)
                if screenName == "arrisKeyBindingScreen":
                    clientApi.GetUI("arris", "arrisKeyBinding").KeyPressedEvent(keyValue)
        else:
            self._pressed_keys.discard(keyValue)
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
                        self._game_tick_callbacks.add(mappingData.callback)
                    elif mappingData.trigger_mode == 2 and mappingData.callback not in self._render_tick_callbacks:
                        self._render_tick_callbacks.add(mappingData.callback)
                    else:
                        mappingData.callback()
                else:
                    self._game_tick_callbacks.discard(mappingData.callback)
                    self._render_tick_callbacks.discard(mappingData.callback)
