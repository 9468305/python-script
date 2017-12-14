### Python leveldb Utils 常用方法封装。  
[leveldb](http://leveldb.org/)是Google开源的一个轻量级，高性能，KeyValue 存储数据库。作者是Google战神Jeff Dean，基于他自己的BigTable论文，使用C++ POSIX实现。  
> LevelDB is a light-weight, single-purpose library for persistence with bindings to many platforms.

官网 http://leveldb.org/  
GitHub https://github.com/google/leveldb  
官方 Javascript Binding https://github.com/Level/levelup  
### Python Binding
早期官方仅提供C++和Javascript。Python实现均是第三方开发。其中使用较广泛和稳定的是 https://github.com/rjpower/py-leveldb 。目前处于稳定运行，维护停滞状态。  
在Python爬虫实现过程中，常常需要快速简单处理存储大量数据至本地文件，构建SQL数据库表过于复杂，变更不灵活。使用JSON文本格式，缺乏索引，过滤，随机增删数据。因此leveldb是一种轻便快捷的最佳解决方案。  

这里封装了一些常用方法，均是日常爬虫数据采集存储的常用方法。  
### exist()
判断key是否存在于database中。返回Boolean值。  
```Python
def exist(db_src, key):
    try:
        db_src.Get(_key_obj)
        return True
    except KeyError:
        return False
```

### count()
统计database中数据总量计数，支持key过滤子字符串，value过滤子字符串，返回总数和过滤后有效总数。
```Python
def count(db_src, k_filter, v_filter):
    total, valid = 0, 0
    for _k, _v in db_src.RangeIter():
        total += 1
        if k_filter:
            if _k.find(k_filter) == -1:
                continue
        if v_filter:
            if _v.find(v_filter) == -1:
                continue
        valid += 1
    return total, valid
```

### copy()
从源库到目标库，拷贝database，支持key过滤子字符串。返回源库总数和过滤后有效拷贝总数。  
```Python
def copy(db_src, db_dst, k_filter):
    total, valid = 0, 0
    for _k, _v in db_src.RangeIter():
        total += 1
        if k_filter:
            if _k.find(k_filter) != -1:
                valid += 1
                db_dst.Put(_k, _v, sync=True)
        else:
            valid += 1
            db_dst.Put(_k, _v, sync=True)
    return total, valid
```

### delete()
删除目标库中与源库相同key的数据项。  
```Python
def delete(db_src, db_dst):
    for _k, _v in db_src.RangeIter():
        db_dst.Delete(_k)
```

### diff()
查找源库与目标库的key值差异数据项，存储至差异库。返回差异项总数。  
```Python
def diff(db_src, db_dst, db_diff):
    diff_count = 0
    for _k, _v in db_src.RangeIter():
        if not exist(db_dst, _k):
            diff_count += 1
            db_diff.Put(_k, _v)
    return diff_count
```

### clean_copy()
拷贝源库至目标库，并删除value值为空的数据项。返回拷贝总数。  
```Python
def clean_copy(db_src, db_dst):
    total = 0
    for _k, _v in db_src.RangeIter():
        if _v:
            db_dst.Put(_k, _v)
            total += 1
    return total

```

### dump()
打印输出当前数据库中所有key value数据。  
安全兼容：当参数是字符串时，当作本地路径文件名处理，临时打开数据库。  
```Python
def dump(db_src):
    _db = leveldb.LevelDB(db_src, create_if_missing=False) if isinstance(db_src, str) else db_src
    for _k, _v in _db.RangeIter():
        print(_k.decode(), _v.decode())
```

### db_to_text()
导出leveldb数据库至文本文件，以','分隔。  
安全兼容：当参数是字符串时，当作本地路径文件名处理，临时打开数据库。  
```Python
def db_to_text(from_db, to_text):
    _db = leveldb.LevelDB(from_db, create_if_missing=False) if isinstance(from_db, str) else from_db
    with open(to_text, 'w', encoding='utf-8') as _f:
        for _k, _v in _db.RangeIter():
            _f.write(_k.decode() + ',' + _v.decode() + '\n')
```

### text_to_db()
从文本文件导入至leveldb数据库。参数支持自定义分隔符。  
安全兼容：当参数是字符串时，当作本地路径文件名处理，临时打开数据库。  
```Python
def text_to_db(from_text, to_db, split_char):
    total, invalid = 0, 0
    _split = split_char if split_char else ','
    _db = leveldb.LevelDB(to_db, create_if_missing=True) if isinstance(to_db, str) else to_db
    with open(from_text, 'r', encoding='utf-8') as _f:
        lines = _f.readlines()
        total = len(lines)
        for line in lines:
            if not line:
                invalid += 1
                continue
            # line = line.strip()
            if _split in line:
                _sub = line.split(_split, 1)
                _db.Put(_sub[0].encode('utf-8'), _sub[1].encode('utf-8'))
            else:
                _db.Put(line, '')
        return total, invalid
```

### db_to_excel()
导出leveldb数据库至Excel文件，返回总数。  
Excel文件共2列，分别对应leveldb的Key，Value。  
安全兼容：当参数是字符串时，当作本地路径文件名处理，临时打开数据库。  
```Python
def db_to_excel(from_db, to_excel):
    _db = leveldb.LevelDB(from_db, create_if_missing=False) if isinstance(from_db, str) else from_db
    _wb = Workbook()
    _ws = _wb.active
    total = 0
    for _k, _v in _db.RangeIter():
        _ws.append([_k.decode(), _v.decode()])
        total += 1
    _wb.save(to_excel)
    return total
```

### excel_to_db()
从Excel文件导入至leveldb数据库。  
仅读取Excel文件中的前2列数据，对应leveldb的Key，Value。  
安全兼容：当参数是字符串时，当作本地路径文件名处理，临时打开数据库。  
```Python
def excel_to_db(from_excel, to_db):
    _wb = load_workbook(from_excel, read_only=True)
    _ws = _wb.active
    _db = leveldb.LevelDB(to_db, create_if_missing=True) if isinstance(to_db, str) else to_db
    total = 0
    for _row in _ws.iter_rows(min_row=2, min_col=1, max_col=1):
        if _row and _row[0] and _row[1]:
            _key, _value = '', ''
            if _row[0].data_type == cell.Cell.TYPE_STRING:
                _key = _row[0].value.encode('utf-8')
                _key = ''.join(_key.split())
            if _row[1].data_type == cell.Cell.TYPE_STRING:
                _value = _row[0].value.encode('utf-8')
                _value = ''.join(_value.split())
            _db.Put(_key, _value)
            total += 1

    _wb.close()
    return total
```
### 源码见GitHub
https://github.com/9468305/script/tree/master/level  

### 后记
这篇文档整理完成时，leveldb官网已经推出官方Python版本。  
详见 https://plyvel.readthedocs.io/en/latest/  
