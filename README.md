# 棱花Arris - 自定义按键映射设置模块

**作者: lovely_小柒丫**

## 简介

这是一个为MC基岩版开发的自定义按键绑定模块，允许玩家在游戏内自定义键盘按键映射，并提供了可视化的设置界面。
模块支持单键、组合键绑定，支持按键冲突检测，并能将玩家的设置持久化保存，开发者还可以设置触发模式及其可触发界面等等设置。
非常简单便捷，几行代码即可搞定！

## 📖 效果展示

![示例图片1](img/demo1.png)
![示例图片2](img/demo2.png)

## 🚀 安装说明

### 1. 文件部署

##### *注意：请不要随意修改 keybindingScripts 和 ui 内的文件,同时也包含文件名*
##### *避免和其他模组之间,出现意料之外的冲突*

#### 行为包

将 `keybindingScripts/` 文件夹复制到您的模组 `行为包` 目录下：
```
behavior_pack/
└── keybindingScripts/
    ├── __init__.py
    ├── modMain.py
    ├── keybindingSystem.py
    ├── keybindingUI.py
    ├── KeyBoardFormat.py
    └── proxys/
        ├── __init__.py
        └── SettingScreenProxy.py
```

#### 资源包
将 `ui/` 文件夹中的内容复制到您的模组 `资源包` 目录下：

```
resource_pack/
└── ui/
    ├── _ui_defs.json
    └── arrisCustomKeyBinding.json
```

请注意将arrisCustomKeyBinding.json写入你的_ui_defs.json内

## 💻 使用方法

### 开发者使用

#### 1. 参数说明

**CreateKeyBindingFactory 方法参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `modSpace` | str | 是 | 模组命名空间,请务必确保唯一性 |
| `modName` | str | 是 | 模组显示名称 (UI界面内显示) |
| `modIconPath` | str | 否 | 模组图标路径 (可选，默认为键盘图标) |

**RegisterKeyBinding 方法参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `keys` | tuple | 是 | 按键代码元组，支持单键或组合键 |
| `callback` | function | 是 | 按键触发时调用的回调函数 |
| `description` | str | 是 | 按键功能描述（显示在UI中） |
| `allow_modify` | bool | 否 | 是否允许玩家自定义修改（默认True） |
| `trigger_mode` | int | 否 | 触发模式（默认0）详细见下方说明 |
| `trigger_screens` | tuple | 否 | 允许触发的界面列表（默认空元组表示全局） |

**trigger_mode 触发模式：**

- `0`：单次触发 - 按键按下时触发一次
- `1`：游戏Tick触发 - 按键按住期间每个游戏刻都触发（20次/秒）
- `2`：渲染帧Tick触发 - 按键按住期间每个渲染帧都触发（取决于帧率）

#### 2. 创建按键绑定工厂

在您的模组代码中导入并创建按键绑定工厂：

```python
keybindingSystem = clientApi.ImportModule("keybindingScripts.keybindingSystem")
if keybindingSystem:
    # 创建按键绑定工厂实例
    keyFactory = keybindingSystem.CreateKeyBindingFactory(
        modSpace="myMod", # 模组命名空间（字符串）
        modName="我的模组", # 模组显示名称（字符串）
        modIconPath="textures/ui/my_mod_icon" # 模组图标路径(可选，默认为键盘图标)
    )
else:
    print("未加载keybindingSystem")
```

#### 3. 注册按键绑定

使用工厂实例注册按键绑定：

```python
# 示例1：单键绑定
def callback():
    print("按键被触发了！")

keyFactory.RegisterKeyBinding(
    keys=(69,),  # E键
    callback=callback,
    description="打开菜单",
    allow_modify=True,  # 允许玩家自定义修改
    trigger_mode=0,  # 单次触发模式
    trigger_screens=()  # 全局触发（空元组表示所有界面）
)

# 示例2：组合键绑定
def open_inventory():
    print("打开背包")

keyFactory.RegisterKeyBinding(
    keys=(17, 73),  # Ctrl + I
    callback=open_inventory,
    description="打开背包",
    allow_modify=True,
    trigger_mode=0,
    trigger_screens=("hud_screen",)  # 仅在HUD界面触发
)

# 示例3：持续触发（游戏刻）
def game_tick():
    print("游戏Tick触发")

keyFactory.RegisterKeyBinding(
    keys=(32,),  # 空格键
    callback=game_tick,
    description="Test",
    allow_modify=True,
    trigger_mode=1,  # 游戏Tick触发模式
    trigger_screens=()
)

# 示例4：渲染刻触发
def render_tick():
    print("渲染Tick触发")

keyFactory.RegisterKeyBinding(
    keys=(70,),  # F键
    callback=render_tick,
    description="Test",
    allow_modify=False,  # 不允许玩家修改
    trigger_mode=2,  # 渲染帧Tick触发模式
    trigger_screens=()
)
```

#### 4. 打开按键设置界面

除了使用我们在setting页面注册的按钮打开以外，还可以在您的代码中调用以下方法打开按键设置界面
或者直接使用PushScreen接口

```python
keybindingSystem = clientApi.ImportModule("keybindingScripts.keybindingSystem")
if keybindingSystem:
    keybindingSystem.PushKeyBindingScreen()
```

### 玩家使用

1. **进入设置界面**
   - 在游戏设置中找到"自定义按键绑定"选项
   - 点击"自定义按键绑定"选项

2. **修改按键**
   - 左侧列表显示所有已注册的模组
   - 右侧显示该模组的所有按键绑定
   - 点击要修改的按键绑定
   - 按下新的按键或组合键
   - 系统会自动保存设置

3. **重置按键**
   - 点击按键绑定旁边的"重置"按钮
   - 按键将恢复为默认值

4. **冲突检测**
   - 如果多个功能绑定了相同的按键，冲突的按键会以红色显示
   - 建议修改冲突的按键以避免功能冲突

## 🎹 按键代码参考

常用按键代码：

| 按键 | 代码 | 按键 | 代码 |
|------|------|------|------|
| 鼠标左键 | -99 | A-Z | 65-90 |
| 鼠标右键 | -98 | 0-9 | 48-57 |
| 鼠标中键 | -97 | F1-F12 | 112-123 |
| 空格 | 32 | Shift | 16 |
| Enter | 13 | Ctrl | 17 |
| Esc | 27 | Alt | 18 |
| Tab | 9 | 方向键↑↓←→ | 38,40,37,39 |

完整按键代码请参考 `KeyBoardFormat.py` 文件中的 `KeyBoardType` 字典或者网易开发者文档。

## 🔧 核心功能

### 1. 按键绑定管理
- 支持单键和组合键绑定
- 自动处理按键状态

### 2. 触发模式
- **单次触发**：适合开关类操作（如打开菜单）
- **游戏刻触发**：适合持续逻辑操作（如技能持续释放）
- **渲染刻触发**：适合渲染相关的平滑操作（如视角调整）

### 3. 界面限制
- 可指定按键仅在特定界面触发
- 支持全局触发（所有界面）
- 在按键设置界面自动禁用回调防止误触

### 4. 玩家设置持久化
- 玩家的按键设置自动保存
- 重新进入游戏后设置保持不变
- 支持重置到默认值

### 5. 冲突检测
- 自动检测按键绑定冲突
- 冲突按键在UI中标红显示
- 帮助玩家识别并解决冲突

## ⚠️ 注意事项

1. **按键代码**：使用正确的按键代码，参考 `KeyBoardFormat.py`
2. **组合键顺序**：组合键的顺序不影响触发（使用Counter比较）
3. **回调函数**：确保回调函数不会抛出异常，建议添加异常处理
4. **性能考虑**：
   - 慎用 `trigger_mode=1` 和 `trigger_mode=2`
   - 持续触发模式会频繁调用回调函数
   - 确保回调函数执行效率高
5. **界面限制**：在按键设置界面（`arrisKeyBindingScreen`）按键不会触发回调
6. **命名空间**：确保 `modSpace` 和 `modName` 的组合在所有模组中唯一

## 📄 MIT许可

请参阅 [LICENSE](LICENSE) 文件了解详细信息。

## 🤝 贡献

欢迎提交问题和拉取请求来改进这个模块！

## 📧 联系方式

如有问题或建议，请通过以下方式联系：
- 创建 Issue
- 提交 Pull Request
- QQ 1493623908

---
