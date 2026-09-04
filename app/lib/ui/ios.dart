/// V3 iOS 风格 UI 统一导出（Barrel File）
///
/// 后续 agent 只需 `import 'package:quiz_app/ui/ios.dart';`
/// 即可使用全部 V3 设计系统：令牌、主题、动效、组件、路由。
///
/// 包含：
/// - 设计令牌：IOSColors / IOSFontSize / IOSSpacing / IOSRadius / IOSShadow / IOSGlass / IOSBreakpoint / IOSFloatingBar / IOSTypography / IOSSystemColors / IOSSubjectColors
/// - 动效系统：IOSDuration / IOSCurve / IOSSpring / IOSAnimations / IOSAnimationPresets
/// - 主题：buildIOSLightTheme / buildIOSDarkTheme
/// - 全屏返回路由：IOSPageRoute / iosPageRoute
/// - 组件：LiquidGlass / FloatingTabBar / FloatingActionBar / IOSButton / IOSCard / IOSListGroup / IOSListItem
library;

// 主题层
export 'theme/ios_tokens.dart';
export 'theme/ios_animations.dart';
export 'theme/ios_theme.dart';
export 'theme/ios_page_route.dart';

// 组件层
export 'widgets/liquid_glass.dart';
export 'widgets/floating_tab_bar.dart';
export 'widgets/floating_action_bar.dart';
export 'widgets/ios_button.dart';
export 'widgets/ios_card.dart';
export 'widgets/ios_list_group.dart';
export 'widgets/ios_action_sheet.dart';
