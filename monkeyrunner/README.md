# MonkeyRunner is DEAD

## UI Automator

https://developer.android.com/training/testing/ui-automator

Android 平台所有自动化测试框架的底层实现都依赖官方提供的 UI Automator 测试框架，适用于跨系统和已安装应用程序的跨应用程序功能UI测试。主要功能包括三部分：

+ UI Automator Viewer 检查布局层次结构的查看器。
+ UiDevice 设备状态信息并在目标设备上执行操作的API。
+ UI Automator API 支持跨应用程序UI测试的API。

## UI Automator Viewer

PC 端 GUI 工具，扫描和分析 Android 设备上当前显示的 UI 组件。展示 UI 布局层次结构，查看设备上当前对用户可见的 UI 组件的属性。从名称可以看出，它是 UI Automator 的只读功能部分，即只能查看 UI 组件的树形结构和属性，不能操作控制 UI 组件。

`uiautomatorviewer` 位于 `<android-sdk>/tools/bin` 目录。启动入口是一个bash文件，实际调用 `<android-sdk>/tools/lib` 目录的 `uiautomatorviewer-26.0.0-dev.jar` 。 GUI 基于 Eclipse + SWT 实现，使用 Gradle 构建。系列工具源码在 `https://android.googlesource.com/platform/tools/swt/` ，依赖 `https://android.googlesource.com/platform/tools/base/` 。活跃分支： `mirror-goog-studio-master-dev` 。该仓库还包含 `chimpchat, ddms, hierarchyviewer2, monkeyrunner, swtmenubar, traceview` 这些工具。

其内部实现基于 `adb shell uiautomator dump` 。从源码仓库提交记录看，主要功能开发的活跃时间是 2014-2015，2016之后已经很少更新维护。那个年代的 Android 开发主要使用 Eclipse ， 所以基于 SWT 实现多平台 PC GUI ，在当时合理。

该工具实际使用运行不稳定，极易报错：`Error while obtaining UI hierarchy XML file: com.android.ddmlib.SyncException: Remote object doesn't exist!`  

错误原因通常是：

+ adb 连接通道不稳定。
+ 机型兼容性问题，权限问题。
+ 当前手机应用程序界面处于动态，例如播放视频，动画。并且10秒超时时间仍未进入静态。

分析源码可知，错误都源于 `Android Framework uiautomator` 。

## MonkeyRunner

https://developer.android.com/studio/test/monkeyrunner

官方提供的另外一个工具，封装 uiautomator API，供 Python 脚本调用，也可注入 java 扩展插件。相比 `uiautomatorviewer` 和 `uiautomator` 命令行工具，可编程扩展性更佳。

MonkeyRunner 使用了比较冷门的 Jython 实现。

### 1. 启动运行入口

> monkeyrunner -plugin <plugin_jar> <program_filename> <program_options>

monkeyrunner 是一个bash文件，位于 `<android-sdk>/tools/bin` ，启动调用 `<android-sdk>/tools/lib/monkeyrunner-26.0.0-dev.jar` 。

```bash
export ANDROID_HOME="~/Library/Android/sdk"
$ANDROID_HOME/tools/bin/monkeyrunner uiparser.py
```

### 2. 主要方法

#### MonkeyDevice.getProperty()

等同于调用 `adb shell getprop <keyword>` 。获取设备系统环境变量。  
不同厂商的设备，key可能不同。针对具体测试机型，可使用 `adb shell getprop` ，显示所有系统环境变量的key字符串。

#### MonkeyDevce.shell()

等同于调用`adb shell`命令。

### 3. 缺陷

MonkeyRunner 基于 Jython 2.5.3 。看上去结合了Java和Python的优势，实际对于Java和Python编程都不友好。  

+ Jython 2.5.3 过时，主流的Python 3.x和2.7的很多语法和库无法使用。
+ 使用vscode等编辑器编码时，缺少智能提示和自动补全。编辑器和pylint无法识别导入的库， 例如 `from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice, MonkeyImage` 。
+ Jython 似乎不能像常规的python程序一样引用外部库。实测只能使用 MonkeyRunner 内置的 `os, sys, subprocess` 等库。
+ Java extend plugin 能做的事情较少。

MonkeyRunner 实际仍然是使用 `adb shell` 和其中的 `uiautomator` 命令获取UI组件状态和属性。所以它跟 `UI Automator Viewer` 一样受限于 `uiautomator` 本身的缺陷，导致运行不稳定。

## adb shell uiautomator

**adb**  
https://developer.android.google.cn/studio/command-line/adb

**adb shell am**  
https://developer.android.google.cn/studio/command-line/adb#am  
使用 Activity Manager (am) 工具发出命令以执行各种系统操作，如启动 Activity、强行停止进程、广播 intent、修改设备屏幕属性及其他操作。  

**adb shell pm**  
https://developer.android.google.cn/studio/command-line/adb#pm  
使用软件包管理器 Package Manager (pm) 工具发出命令，安装，卸载，查询安装包。  

**adb shell uiatomator**  
官网相关页面已被删除，仅能从搜索引擎历史快照中找到。猜测可能近期会有变更，或者官方建议不再使用。  
通过执行命令可以查看使用方法和参数。  

```bash
Usage: uiautomator <subcommand> [options]

Available subcommands:

help: displays help message

runtest: executes UI automation tests
    runtest <class spec> [options]
    <class spec>: <JARS> < -c <CLASSES> | -e class <CLASSES> >
      <JARS>: a list of jar files containing test classes and dependencies. If
        the path is relative, it's assumed to be under /data/local/tmp. Use
        absolute path if the file is elsewhere. Multiple files can be
        specified, separated by space.
      <CLASSES>: a list of test class names to run, separated by comma. To
        a single method, use TestClass#testMethod format. The -e or -c option
        may be repeated. This option is not required and if not provided then
        all the tests in provided jars will be run automatically.
    options:
      --nohup: trap SIG_HUP, so test won't terminate even if parent process
               is terminated, e.g. USB is disconnected.
      -e debug [true|false]: wait for debugger to connect before starting.
      -e runner [CLASS]: use specified test runner class instead. If
        unspecified, framework default runner will be used.
      -e <NAME> <VALUE>: other name-value pairs to be passed to test classes.
        May be repeated.
      -e outputFormat simple | -s: enabled less verbose JUnit style output.

dump: creates an XML dump of current UI hierarchy
    dump [--verbose][file]
      [--compressed]: dumps compressed layout information.
      [file]: the location where the dumped XML should be stored, default is
      /sdcard/window_dump.xml

events: prints out accessibility events until terminated
```

### uiautomator 缺陷

运行耗时长，失败率高，频繁报错。  
`ERROR: could not get idle state.` 通常表示当前UI处于动态渲染刷新期间，例如正在播放视频，动画。在10秒超时时间内仍未进入静态。因为此时 UI 树的节点对象快速变化中，不能稳定获取。  

### uiautomator 源码

PC端工具源码位于仓库 https://android.googlesource.com/platform/frameworks/testing/ 的 `master` 分支，最新更新于 2014.11.14。之后活跃分支变更为 `android-support-test` 分支。`uiautomator` 源码被移除，改成 `android.support.test library, expresso` 等工具的源码工程。  
手机端框架源码位于仓库 https://android.googlesource.com/platform/frameworks/base/ 的 `master` 分支。  
关键代码 `uiAutomation.waitForIdle(1000, 1000 * 10);` 即单次超时等待1秒，最长超时等待10秒。超时抛出异常。

`DumpCommand.java`  
> https://android.googlesource.com/platform/frameworks/testing/+/master/uiautomator/cmds/uiautomator/src/com/android/commands/uiautomator/DumpCommand.java  

```Java
// It appears that the bridge needs time to be ready. Making calls to the
// bridge immediately after connecting seems to cause exceptions. So let's also
// do a wait for idle in case the app is busy.
try {
    UiAutomation uiAutomation = automationWrapper.getUiAutomation();
    uiAutomation.waitForIdle(1000, 1000 * 10);
    AccessibilityNodeInfo info = uiAutomation.getRootInActiveWindow();
    if (info == null) {
        System.err.println("ERROR: null root node returned by UiTestAutomationBridge.");
        return;
    }
    Display display =
            DisplayManagerGlobal.getInstance().getRealDisplay(Display.DEFAULT_DISPLAY);
    int rotation = display.getRotation();
    Point size = new Point();
    display.getSize(size);
    AccessibilityNodeInfoDumper.dumpWindowToFile(info, dumpFile, rotation, size.x, size.y);
} catch (TimeoutException re) {
    System.err.println("ERROR: could not get idle state.");
    return;
} finally {
    automationWrapper.disconnect();
}
System.out.println(
        String.format("UI hierchary dumped to: %s", dumpFile.getAbsolutePath()));
```

`UiAutomation.java`  
> https://android.googlesource.com/platform/frameworks/base/+/master/core/java/android/app/UiAutomation.java

```Java
/**
  * Waits for the accessibility event stream to become idle, which is not to
  * have received an accessibility event within <code>idleTimeoutMillis</code>.
  * The total time spent to wait for an idle accessibility event stream is bounded
  * by the <code>globalTimeoutMillis</code>.
  *
  * @param idleTimeoutMillis The timeout in milliseconds between two events
  *            to consider the device idle.
  * @param globalTimeoutMillis The maximal global timeout in milliseconds in
  *            which to wait for an idle state.
  *
  * @throws TimeoutException If no idle state was detected within
  *            <code>globalTimeoutMillis.</code>
  */
public void waitForIdle(long idleTimeoutMillis, long globalTimeoutMillis)
        throws TimeoutException {
    synchronized (mLock) {
        throwIfNotConnectedLocked();
        final long startTimeMillis = SystemClock.uptimeMillis();
        if (mLastEventTimeMillis <= 0) {
            mLastEventTimeMillis = startTimeMillis;
        }
        while (true) {
            final long currentTimeMillis = SystemClock.uptimeMillis();
            // Did we get idle state within the global timeout?
            final long elapsedGlobalTimeMillis = currentTimeMillis - startTimeMillis;
            final long remainingGlobalTimeMillis =
                    globalTimeoutMillis - elapsedGlobalTimeMillis;
            if (remainingGlobalTimeMillis <= 0) {
                throw new TimeoutException("No idle state with idle timeout: "
                        + idleTimeoutMillis + " within global timeout: "
                        + globalTimeoutMillis);
            }
            // Did we get an idle state within the idle timeout?
            final long elapsedIdleTimeMillis = currentTimeMillis - mLastEventTimeMillis;
            final long remainingIdleTimeMillis = idleTimeoutMillis - elapsedIdleTimeMillis;
            if (remainingIdleTimeMillis <= 0) {
                return;
            }
            try {
                  mLock.wait(remainingIdleTimeMillis);
            } catch (InterruptedException ie) {
                  /* ignore */
            }
        }
    }
}
```

## Android Device Monitor

https://developer.android.com/studio/profile/monitor

Android SDK 工具集的 `Android Device Monitor` 已废弃。

>Android Device Monitor was deprecated in Android Studio 3.1 and removed from Android Studio 3.2. The features that you could use through the Android Device Monitor have been replaced by new features. The table below helps you decide which features you should use instead of these deprecated and removed features.

官方给出的替代品 `Layout Inspector` 功能更强大，界面也更美观，但目前还不成熟，相比 iOS 神器 [Reveal](https://revealapp.com/) ， 仍需努力。  
https://developer.android.com/studio/debug/layout-inspector

## uiparser

参照 MonkeyRunner 官方文档实现的 Python Demo。

https://github.com/9468305/python-script/blob/master/monkeyrunner/uiparser.py
