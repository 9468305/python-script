#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''使用real.csv和result.csv表格数据，计算PR ROC曲线的AUC值'''
import sys
import pandas
#from pandas import DataFrame
from sklearn import metrics

REAL_HEADER = ['Flightno',
               'FlightDepcode',
               'FlightArrcode',
               'PlannedDeptime',
               'PlannedArrtime',
               'label']

RESULT_HEADER = ['Flightno',
                 'FlightDepcode',
                 'FlightArrcode',
                 'PlannedDeptime',
                 'PlannedArrtime',
                 'prob']


def check_column(column1, column2):
    '''检查列数据是否一致'''
    if not column1.equals(column2):
        print('Error: csv column has different data!')
        exit(1)


def check_format(real_df, result_df):
    '''检查real.csv和result.csv的数据是否合规'''
    real_header, result_header = real_df.columns.values.tolist(), result_df.columns.values.tolist()
    if REAL_HEADER != real_header or RESULT_HEADER != result_header:
        print('Error: csv has different headers!')
        print(real_header)
        print(result_header)
        exit(1)
    check_column(real_df['Flightno'], result_df['Flightno'])
    check_column(real_df['FlightDepcode'], result_df['FlightDepcode'])
    check_column(real_df['FlightArrcode'], result_df['FlightArrcode'])
    check_column(real_df['PlannedDeptime'], result_df['PlannedDeptime'])
    check_column(real_df['PlannedArrtime'], result_df['PlannedArrtime'])


def load_label_prob(real_csv, result_csv):
    '''读取real.csv和result.csv表格数据的label数组和prob数组'''
    real_df, result_df = pandas.read_csv(real_csv), pandas.read_csv(result_csv)
    check_format(real_df, result_df)
    label, prob = real_df['label'].values, result_df['prob'].values
    # 四舍五入, 小数点后保留4位
    for _i, _e in enumerate(prob):
        prob[_i] = round(_e, 4)
    return label, prob


def auc_roc(real_csv, result_csv):
    '''使用real.csv和result.csv表格数据，计算ROC曲线的AUC值'''
    label, prob = load_label_prob(real_csv, result_csv)
    area = metrics.roc_auc_score(label, prob)
    #print(area)
    return area


def auc_pr(real_csv, result_csv):
    '''使用real.csv和result.csv表格数据，计算PR曲线的AUC值'''
    label, prob = load_label_prob(real_csv, result_csv)
    precision, recall, _thresholds = metrics.precision_recall_curve(label, prob)
    area = metrics.auc(recall, precision)
    #print(area)
    return area


if __name__ == "__main__":
    auc_pr(sys.argv[1], sys.argv[2])
    #auc_roc(sys.argv[1], sys.argv[2])
    #hard code parameters for test
    #print(auc_pr('real.csv', 'result.csv'))
    #print(auc_roc('real.csv', 'result.csv'))
