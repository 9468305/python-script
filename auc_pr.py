#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''使用real.csv和result.csv表格数据，计算PR曲线的AUC值'''
import sys
import pandas
from pandas import DataFrame
from sklearn.metrics import auc, precision_recall_curve #average_precision_score

REAL_HEADERS = ['Flightno',
                'FlightDepcode',
                'FlightArrcode',
                'PlannedDeptime',
                'PlannedArrtime',
                'label']

RESULT_HEADERS = ['Flightno',
                  'FlightDepcode',
                  'FlightArrcode',
                  'PlannedDeptime',
                  'PlannedArrtime',
                  'prob']


def check_format(real_df, result_df):
    '''检查real.csv和result.csv的头格式'''
    real_headers = real_df.columns.values.tolist()
    if REAL_HEADERS != real_headers:
        print('Error: real.csv has wrong headers!')
        print(real_headers)
        exit(1)
    result_headers = result_df.columns.values.tolist()
    if RESULT_HEADERS != result_headers:
        print('Error: result.csv has wrong headers!')
        print(result_headers)
        exit(1)


def auc_pr(real_csv, result_csv):
    '''使用real.csv和result.csv表格数据，计算PR曲线的AUC值'''
    real_df, result_df = pandas.read_csv(real_csv), pandas.read_csv(result_csv)
    check_format(real_df, result_df)
    label, prob = real_df['label'].values, result_df['prob'].values
    for i in range(len(prob)):
        prob[i] = round(prob[i], 4)
    precision, recall, thresholds = precision_recall_curve(label, prob)
    area = auc(recall, precision)
    print(area)


if __name__ == "__main__":
    #auc_pr(sys.argv[1], sys.argv[2])
    auc_pr('real.csv', 'result.csv')
