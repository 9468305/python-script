### 背景  
[携程旅行网 云海竞赛平台](https://yunhai.ctrip.com)举办算法竞赛，携程机票BU与飞常准合作命题[携程机票航班延误预测算法大赛](https://yunhai.ctrip.com/Games/11)，希望以此提升航班延误的预测准确性。  
由于云海平台仅支持Python语言，原算法使用R语言实现，因此实现一份Python版，用于竞赛算法的结果核算。  
源数据样本csv格式说明：[航班动态起降数据集](https://www.kesci.com/apps/home/dataset/59793a5a0d84640e9b2fedd3)。  
提交预测样本csv格式说明：[submission_sample.csv](http://ofy9izzlw.bkt.clouddn.com/ctrip_fligtht/submission_sample.csv)。  
示例：  
```
Flightno	FlightDepcode	FlightArrcode	PlannedDeptime	PlannedArrtime	prob
CA1351	PEK	CAN	1496273700	1496285700	0.041386555
8L9647	KMG	HIA	1496272200	1496282400	0.022590361
CZ6299	DLC	SZX	1496274000	1496286900	0.025210084
HU7377	URC	CKG	1496273700	1496287500	0.106757728
```
本次比赛采用PR曲线的AUC（baseline：auc=0.45）。  
评估指标参考文献：http://mark.goadrich.com/articles/davisgoadrichcamera2.pdf  
  
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
Windows的scikit-learn库环境搭建略繁琐，对NumPy和SciPy版本有要求。  
因此直接使用 http://www.lfd.uci.edu/~gohlke/pythonlibs/ 的第三方预编译库。  
```
pip install http://www.lfd.uci.edu/~gohlke/pythonlibs/ru4fxw3r/numpy-1.13.1+mkl-cp36-cp36m-win32.whl
pip install http://www.lfd.uci.edu/~gohlke/pythonlibs/ru4fxw3r/scipy-0.19.1-cp36-cp36m-win32.whl
pip install pandas
pip install scikit-learn
```

### 源码见GitHub
https://github.com/9468305/script/blob/master/auc_pr_roc/
