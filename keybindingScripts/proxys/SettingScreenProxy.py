# -*- coding: utf-8 -*-
import mod.client.extraClientApi as clientApi

CustomUIScreenProxy = clientApi.GetUIScreenProxyCls()
ViewBinder = clientApi.GetViewBinderCls()
compFactory = clientApi.GetEngineCompFactory()

ROOT_PANEL = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix/safezone_screen_panel/root_screen_panel"

class SettingScreenProxy(CustomUIScreenProxy):
    def __init__(self, screenName, screenNode):
        CustomUIScreenProxy.__init__(self, screenName, screenNode)
        self.inputModeId = compFactory.CreatePlayerView(clientApi.GetLevelId()).GetToggleOption(clientApi.GetMinecraftEnum().OptionId.INPUT_MODE)  # 操作模式 0 键鼠 1 触摸屏 2 手柄
        self.screenNode = screenNode
        self.contentControl = None
        if self.inputModeId == 1:
            self.contentControl = ROOT_PANEL + "/stack_panel/content_panel/container/settings_common.dialog_content/selector_area/scrolling_panel/scroll_touch/scroll_view/panel/background_and_viewport/scrolling_view_port/scrolling_content/settings.selector_stack_panel/world_selector_pane"
        else:
            self.contentControl = ROOT_PANEL + "/stack_panel/content_panel/container/settings_common.dialog_content/selector_area/scrolling_panel/scroll_mouse/scroll_view/stack_panel/background_and_viewport/scrolling_view_port/scrolling_content/settings.selector_stack_panel/world_selector_pane"

    def OnCreate(self):
        parentControl = self.screenNode.GetBaseUIControl(self.contentControl)
        self.screenNode.CreateChildControl("arrisCustomKeyBinding.arris_addon_keyboard_bindings", "arrisAddonKeyboardBindings", parentControl, True)

    @ViewBinder.binding(ViewBinder.BF_ToggleChanged, "#arrisAddonKeyboardBindings")
    def OpenScreen(self, args):
        clientApi.PopTopUI()
        clientApi.PushScreen("arris", "arrisKeyBinding")
