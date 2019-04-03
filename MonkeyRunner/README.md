### uiparser (MonkeyRunner is DEAD!)

Setup
> export ANDROID_HOME="/Users/chenqi/Library/Android/sdk"

Run
> $ANDROID_HOME/tools/bin/monkeyrunner uiparser.py

### MonkeyRunner
https://developer.android.google.cn/studio/test/monkeyrunner

#### MonkeyDevce.shell()
>object	shell (string cmd)  
Executes an `adb` shell command and returns the result, if any.

等同于调用`adb shell`命令。  
https://developer.android.google.cn/studio/command-line/adb#shellcommands  

#### MonkeyDevice.getProperty()
> object getProperty (string key)  
Given the name of a system environment variable, returns its value for this device.

获取设备系统环境变量。  
等同于调用`adb shell getprop <keyword>`。  
不同厂商的设备，key可能不同。  
使用`adb shell getprop`，显示所有系统环境变量的key字符串  

### adb
https://developer.android.google.cn/studio/command-line/adb

#### adb shell am
https://developer.android.google.cn/studio/command-line/adb#am  
使用 Activity Manager (am) 工具发出命令以执行各种系统操作，如启动 Activity、强行停止进程、广播 intent、修改设备屏幕属性及其他操作。  

#### adb shell pm
https://developer.android.google.cn/studio/command-line/adb#pm  
使用软件包管理器 Package Manager (pm) 工具发出命令，安装，卸载，查询安装包。  

#### adb shell uiautomator
获取当前界面的层级结构XML信息。  
```
adb shell uiautomator dump /sdcard/uiparser/ui.xml  
adb pull /sdcard/uiparser/ui.xml ./ui.xml
```
Usage:  
```
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

### Bug
[DumpCommand.java](https://android.googlesource.com/platform/frameworks/testing/+/master/uiautomator/cmds/uiautomator/src/com/android/commands/uiautomator/DumpCommand.java)  

`uiAutomation.waitForIdle(1000, 1000 * 10);`  

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

[UiAutomation.java](https://android.googlesource.com/platform/frameworks/base.git/+/master/core/java/android/app/UiAutomation.java)  

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