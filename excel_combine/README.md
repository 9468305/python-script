工作中经常遇到一种繁琐的事情。例如绩效考核，晋升调薪，固定资产盘点，团建出游时，部门秘书发来一个全部门的Excel文件，各小组Leader拆分出自己团队的Excel文件。下发给每个成员。成员填写完毕后发回给小组Leader，小组Leader汇总后发给部门秘书。部门秘书再汇总各小组Excel到一个完整的大Excel文件。  
**吐槽：由于种种原因，我司内网Web OA系统建设不足，很多事情都以Excel分发和汇总。**  
一直没有找到方便好用的Excel多文件合并工具。于是自己动手撸一个Python脚本，一键自动合并。  

### 一键执行
为了方便非技术人员使用，不添加任何启动参数，直接将脚本放在Excel文件夹根目录，双击执行。  
也不需要指定合并汇总文件名，`combine.xlsx`这个名字的重复率很低，使用者留意即可。  
```Python
if __name__ == "__main__":
    FROM_DIR = os.getcwd()
    TO_FILE = os.path.join(FROM_DIR, 'combine.xlsx')
    combine(FROM_DIR, TO_FILE)
```

### openpyxl
目前主流Office版本支持Excel 2010格式，即xlsx后缀名。如果源文件是xls后缀名，直接另存为xlsx即可。因此使用openpyxl库读写Excel文件，忽略xls后缀名文件。  
[openpyxl - A Python library to read/write Excel 2010 xlsx/xlsm files](https://openpyxl.readthedocs.io/en/default/)  

### 遍历文件夹，查找Excel文件
使用os.walk()  
```Python
_results = []
    for _root, _dirs, _files in os.walk(from_dir):
        for _file in _files:
            if _file.endswith('.xlsx'):
                _results.append(os.path.join(_root, _file))
    return _results
```

### 注意：删除合并汇总文件，即combine.xlsx。
合并之前，删除结果文件，以防数据错误。  
```Python
_result = search_file(from_dir)
try:
    _result.remove(to_file)
except ValueError:
    print('Result file not exist.')
return _result
```

### 多文件重复数据清理
+ 如何确定Excel中每行数据是唯一的？  
+ 如何检测重复的Excel文件（例如文件名不同，内容相同）？
+ 如何合并不同格式（行，列）的Excel文件？
  
这里设定一些潜规则：
+ Excel第一行必须是Title标题。
+ Excel第一列必须是唯一Key。例如工号，邮箱等全局唯一值。

因此使用 Python 内建的 collections 集合模块的 OrderedDict 有序字典，以第一列为Key。  
完整的读取Excel文件并建立内存字典如下：  
```Python
_wb = load_workbook(excel_file, read_only=True)
_ws = _wb.active
_title = []
_items = collections.OrderedDict()
for _r in _ws.rows:
    if not _title:
        for _i in _r:
            _title.append(_i.value)
    else:
        _item = []
        for _i in _r:
            _item.append(_i.value)
        _items[_item[0]] = _item
_wb.close()
return _title, _items
```

### 如何判断2个字典的元素一致？
Python內建了强大的[operator](https://docs.python.org/3/library/operator.html)。
```Python
if not operator.eq(dict_src, dict_dst):
    print('Warning: dict elements are different!')
```

### 最后把数据写入Excel文件
```Python
_wb = Workbook()
_ws = _wb.active
_ws.append(excel_title)
for _k, _v in excel_items.items():
    _ws.append(_v)
_wb.save(excel_file)
```

### 遗留的坑
+ 没有处理多个Sheet的Case。
+ 没有处理Excel公式计算。

### 源码见GitHub
https://github.com/9468305/python-script/tree/master/excel_combine  
