# 设计稿 · 各端对应与 iOS 适配说明

> 配套设计稿：`docs/prototype/ui-v2-cold-frost.html`
> 版本：v1.0（2026-09-01）
> 适用：Flutter 三端（Android / iOS / Web）+ Windows 封装

---

## 一、设计形态总览

设计稿覆盖 **4 种形态**，对应实际落地设备的不同视口宽度：

| 形态 | 设计稿预览 | 典型视口宽度 | 导航骨架 | 答题卡 |
|---|---|---|---|---|
| 手机竖屏 | 📱 手机壳（392×820） | < 600px | 底部 Tab 单列 | 内嵌 / 浮层 |
| 平板竖屏 | 📱 iPad 竖屏（768×1024） | 600–800px | 可收起图标列侧边栏 | 右下角浮层 |
| 平板横屏 | 📟 平板横屏（920×640） | 800–1024px | 图标列侧边栏（≡ 展开） | 右下角浮层 |
| 桌面 | 🖥️ 桌面窗口（1180×760） | > 1024px | 全宽侧边栏（232px） | 右侧常驻 |

> 平板竖屏与平板横屏**共用同一套 DOM**（`wrap-desktop` + `compact` 类），仅窗口尺寸不同；响应式由 CSS 断点自动适配。

---

## 二、各端 ↔ 设计形态对应表

### 实际落地设备

| 端 | 设备 | 常用姿态 | 对应设计形态 | iOS 安全区 |
|---|---|---|---|---|
| Android 手机 | iqoo 手机 | 竖屏 | 手机竖屏 | — |
| iOS 手机 | iPhone | 竖屏 | 手机竖屏 | ✅ 刘海/灵动岛 + Home Indicator |
| Android 平板 | iqoo 平板 | 竖屏 / 横屏 | 平板竖屏 / 平板横屏 | — |
| iOS 平板 | **iPad mini 5** | 竖屏 / 横屏 | 平板竖屏 / 平板横屏 | ✅ 圆角 + Home Indicator |
| Web（手机浏览器） | 任意手机 | 竖屏 | 手机竖屏 | 浏览器地址栏占用 |
| Web（平板浏览器） | 任意平板 | 横竖 | 平板形态 | 浏览器 UI 占用 |
| Web（桌面浏览器） | 电脑 | 横屏 | 桌面形态 | — |
| Windows exe | 电脑 | 横屏 | 桌面形态 | — |

### 打包策略（以 Web 为主，再封装）

```
Flutter 源码（响应式骨架）
    ├── flutter build web --release        → Web 应用（三形态自适应）
    │     ├── 封装为 Android APK（webview / 原生）
    │     ├── 封装为 iOS IPA（webview / 原生）
    │     └── 封装为 Windows exe（桌面形态）
    └── 原生构建（可选）：flutter build apk / ios / windows
```

---

## 三、响应式断点体系

```
< 600px      手机        底部 Tab · 单列 · 答题卡内嵌
600–800px    平板竖屏    图标列侧边栏（可展开）· 1.5–2 栏 · 答题卡浮层
800–1024px   平板横屏    图标列侧边栏（≡ 展开）· 2 栏 · 答题卡浮层
> 1024px     桌面        全宽侧边栏 · 多栏 · 答题卡右侧常驻
```

**iPad 分屏（Split View）特殊处理**：
- iPad 应用可被系统分屏压缩：1/3 宽 ≈ 320pt、1/2 宽 ≈ 384–512pt、2/3 宽 ≈ 640pt
- 1/3 和 1/2 宽度会落入 `<600px` 断点，**自动回退到手机布局**（底部 Tab）——这是正确行为
- 2/3 宽度落入 `600–800px`，使用平板竖屏布局
- Flutter 侧用 `LayoutBuilder` + `MediaQuery.size.width` 判断，**不要用屏幕物理宽度**（分屏时应用宽度 ≠ 屏幕宽度）

---

## 四、iOS 适配清单

### 4.1 安全区（Safe Area）

| 区域 | iPhone（刘海/灵动岛） | iPhone（非刘海） | iPad |
|---|---|---|---|
| 顶部状态栏 | 44pt（含刘海） | 20pt | 20pt |
| 底部 Home Indicator | 34pt | 0pt（有实体 Home 键） | 20pt |
| 横屏侧边 | 左右各 0pt（内容可延伸） | — | 圆角内缩 |

**Flutter 落地**：
- 根布局包裹 `SafeArea()`，自动避开刘海、Home Indicator、圆角
- 需要延伸到安全区外的场景（如背景光斑、毛玻璃顶栏）：`SafeArea(bottom: false)` 或手动 `MediaQuery.padding`
- 设计稿手机壳已标注 iOS 状态栏（9:41 / 信号 / WiFi / 电池）和底部 Home Indicator，内容区在安全区内

### 4.2 状态栏与系统 UI

- iOS 状态栏文字颜色：深色背景用白色（`SystemUiOverlayStyle.light`），浅色背景用深色
- 我们的冷磨砂深色基调 → 状态栏用白色文字
- 进入答题/背题等沉浸页面时，可考虑隐藏状态栏（`SystemChrome.setEnabledSystemUIMode`），但返回时恢复
- Web 端无原生状态栏，由浏览器地址栏替代

### 4.3 手势与导航

- **边缘左滑返回**：iOS 用户习惯从屏幕左边缘滑动返回上一页。Flutter `CupertinoPageRoute` 默认支持；用 `MaterialPageRoute` 时 iOS 也有边缘滑动返回
- **底部 Home Indicator 上滑**：回到主屏幕 / 切换 App，内容底部需留出 34pt 避免误触
- **答题页选项点击**：触控目标 ≥ 44×44pt（HIG 规范），当前设计稿选项高度已满足
- **长按存疑标记**：iOS 长按手势可用 `GestureDetector(onLongPress:)`

### 4.4 HIG（Human Interface Guidelines）契合点

我们的冷磨砂设计与 iOS HIG 高度契合：

| HIG 规范 | 我们的设计 |
|---|---|
| 毛玻璃材质（Frosted Glass） | ✅ 冷磨砂深色 + `backdrop-filter: blur` |
| 圆角层级（8/12/16/22pt） | ✅ 卡片 16–22px、按钮 12–14px |
| 间距栅格（8/12/16/20/24pt） | ✅ 统一 8pt 栅格 |
| 层级与阴影 | ✅ 光斑 + 柔和阴影 + 级联浮现 |
| 系统字体（SF Pro） | Flutter 默认 `CupertinoIcons` / 系统字体 |
| 减少装饰、突出内容 | ✅ 极简信息架构 |

### 4.5 iPad 专属

- **分屏（Split View）**：见第三节，断点自动回退
- **Slide Over**：侧边悬浮小窗，宽度约 320pt，同样回退手机布局
- **横竖屏切换**：`OrientationBuilder` 监听，布局平滑过渡（当前设计稿横屏/竖屏共用 compact DOM）
- **鼠标/触控板支持**：iPad 支持鼠标，hover 状态可用（设计稿侧边栏 hover 展开在 iPad 鼠标下有效）
- **Apple Pencil**：暂不需要（刷题 App 无手写需求）

### 4.6 横竖屏策略

| 设备 | 允许方向 | 说明 |
|---|---|---|
| iPhone | 仅竖屏 | 刷题 App 竖屏体验最佳，横屏信息密度低 |
| iPad | 竖屏 + 横屏 | 两种姿态都支持，布局自动切换 |
| Android 手机 | 仅竖屏 | 同 iPhone |
| Android 平板 | 竖屏 + 横屏 | 同 iPad |
| Web / Windows | 任意 | 响应式自适应 |

Flutter 配置：`SystemChrome.setPreferredOrientations([DeviceOrientation.portraitUp])`（手机端），iPad/平板不限制。

---

## 五、Flutter 落地建议

### 5.1 响应式骨架

```dart
LayoutBuilder(
  builder: (context, constraints) {
    final w = constraints.maxWidth;
    if (w < 600) return PhoneLayout();        // 底部 Tab
    if (w < 1024) return TabletLayout();       // 侧边栏 + 浮层
    return DesktopLayout();                     // 全宽侧边栏 + 常驻答题卡
  },
)
```

### 5.2 安全区

```dart
SafeArea(
  top: true,    // 避开刘海/状态栏
  bottom: true, // 避开 Home Indicator
  child: Scaffold(...),
)
```

背景光斑/毛玻璃需要延伸到安全区外时，用 `Stack` 把背景放在 `SafeArea` 外层。

### 5.3 横竖屏

```dart
OrientationBuilder(
  builder: (context, orientation) {
    return orientation == Orientation.portrait
        ? PortraitLayout()
        : LandscapeLayout();
  },
)
```

### 5.4 iOS 状态栏样式

```dart
SystemChrome.setSystemUIOverlayStyle(
  SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light, // 深色背景用白色图标
  ),
)
```

### 5.5 触控目标

所有可点击元素（选项、按钮、导航项）最小尺寸 **44×44pt**，用 `Padding` 或 `SizedBox` 保证。

---

## 六、设计稿使用说明

设计稿 `ui-v2-cold-frost.html` 顶部有形态切换器：

| 按钮 | 形态 | 用途 |
|---|---|---|
| 📱 手机竖屏 | 手机壳 | iPhone / Android 手机开发参考 |
| 📱 iPad 竖屏 | 紧凑窗口（768×1024） | iPad / Android 平板竖屏参考 |
| 📟 平板横屏 | 紧凑窗口（920×640） | iPad / Android 平板横屏参考 |
| 🖥️ 桌面 | 桌面窗口（1180×760） | Web / Windows 开发参考 |

每个形态下可点击导航切换页面（今日/题库/背题/统计/我的），进入答题页可测试答题卡浮层（平板）或常驻栏（桌面）。

---

## 七、待办与后续

- [ ] Flutter 侧实现 `LayoutBuilder` 响应式骨架（当前 App 仅手机布局）
- [ ] iOS 端配置 `SafeArea` + 状态栏样式 + 方向限制
- [ ] iPad 端验证分屏（1/3 / 1/2 / 2/3）下回退手机布局
- [ ] Windows 平台目录初始化（当前仅 android/ + web/）
- [ ] 触控目标全量检查（≥44pt）
