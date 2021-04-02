Python实现的一个小工具，用于分析Git commit log，获得Git Project每个成员的简单行为数据。

**Warning：代码量不能代表程序员能力水平！**  

### 启动参数

共5个。  

+ Repo地址
+ Commit 起始日期
+ Commit 结束日期
+ Git仓库子目录
+ 统计分析结果CSV文件目标路径

### exec_git

Git Log命令：

> git -C {} log --since={} --until={} --pretty=tformat:%ae --shortstat --no-merges -- {} > {}

填入参数，调用系统命令 `os.system()`，输出结果至本地临时文件。读取至内存，简单的String Array。

### parse

Git Log输出有3种格式，对应3种正则表达式。  

```Python
REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"
```

遍历得到的数据，首先构造一个以Author为Key，分析结果为Value的字典。分析结果构造一个元祖，包括：

+ Commit 次数
+ 增加代码行数
+ 删除代码行数
+ 变更代码行数

### save_csv

简单省略。
