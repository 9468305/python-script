### 背景

2017年某算法竞赛平台出题，飞机航班延误预测算法，需要验收提交答案的准确性。

源数据样本csv格式：失效，省略。  
提交预测样本csv格式说明：失效，省略。  
示例：

Flightno | FlightDepcode | FlightArrcode | PlannedDeptime | PlannedArrtime | prob
-- | -- | -- | -- | -- | --
CA1351 | PEK | CAN | 1496273700 | 1496285700 | 0.041386555
8L9647 | KMG | HIA | 1496272200 | 1496282400 | 0.022590361
CZ6299 | DLC | SZX | 1496274000 | 1496286900 | 0.025210084
HU7377 | URC | CKG | 1496273700 | 1496287500 | 0.106757728

本次比赛采用PR曲线的AUC（baseline：auc=0.45）。评估指标参考：[The Relationship Between Precision-Recall and ROC Curves](http://mark.goadrich.com/articles/davisgoadrichcamera2.pdf)

### 实现

csv文件读取使用pandas库。

```Python
def load_label_prob(real_csv, result_csv):
    '''读取real.csv和result.csv表格数据的label数组和prob数组'''
    real_df, result_df = pandas.read_csv(real_csv), pandas.read_csv(result_csv)
    # 检查real.csv和result.csv的数据是否合规
    check_format(real_df, result_df)
    label, prob = real_df['label'].values, result_df['prob'].values
    # 四舍五入, 小数点后保留4位
    for _i, _e in enumerate(prob):
        prob[_i] = round(_e, 4)
    return label, prob
```

PR曲线AUC值计算使用sklearn库。  

```Python
'''使用real.csv和result.csv列数据，计算PR曲线的AUC值'''
precision, recall, _thresholds = metrics.precision_recall_curve(label, prob)
area = metrics.auc(recall, precision)
return area
```

附：ROC曲线的AUC值计算。

```Python
'''使用real.csv和result.csv列数据，计算ROC曲线的AUC值'''
area = metrics.roc_auc_score(label, prob)
return area
```

### 环境搭建

scikit-learn Windows 环境搭建略繁琐，对 NumPy 和 SciPy 版本有要求。  
因此直接使用[第三方预编译库](http://www.lfd.uci.edu/~gohlke/pythonlibs/)。

```bash
pip install http://www.lfd.uci.edu/~gohlke/pythonlibs/ru4fxw3r/numpy-1.13.1+mkl-cp36-cp36m-win32.whl
pip install http://www.lfd.uci.edu/~gohlke/pythonlibs/ru4fxw3r/scipy-0.19.1-cp36-cp36m-win32.whl
pip install pandas
pip install scikit-learn
```

### [GitHub源码](https://github.com/9468305/python-script/blob/master/auc_pr_roc/)
