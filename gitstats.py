# -*- coding: utf-8 -*-
'''Analyse git branch commit log, for every version, every person.'''
import os
import re
import csv

GIT_LOG = r'git -C {} log --since={} --until={} --pretty=tformat:%ae --shortstat --no-merges -- {} > {}'

GIT_LOG_TXT = 'gitstats.txt'

REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"
CSV_FILE_HEADER = ["Author", "Commit", "Insert", "Delete", "Loc"]


def gitstats(repo, since, until, subdir, csvfile):
    '''Analyse git log and sort to csv file.'''
    logfile = os.path.join(os.getcwd(), GIT_LOG_TXT)
    git_log_command = GIT_LOG.format(repo, since, until, subdir, logfile)
    os.system(git_log_command)
    lines = None
    with open(logfile, 'r') as logfilehandler:
        lines = logfilehandler.readlines()
    assert lines is not None

    prog_full = re.compile(REPATTERN_FULL)
    prog_insert_only = re.compile(REPATTERN_INSERT_ONLY)
    prog_delete_only = re.compile(REPATTERN_DELETE_ONLY)

    stats = {}
    for i in range(0, len(lines), 3):
        author = lines[i]
        #empty = lines[i+1]
        info = lines[i+2]

        #change = 0
        insert = int(0)
        delete = int(0)
        result = prog_full.search(info)
        if result:
            #change = result[0]
            insert = int(result.group(2))
            delete = int(result.group(3))
        else:
            result = prog_insert_only.search(info)
            if result:
                #change = result[0]
                insert = int(result.group(2))
                delete = int(0)
            else:
                result = prog_delete_only.search(info)
                if result:
                    #change = result[0]
                    insert = int(0)
                    delete = int(result.group(2))
                else:
                    print 'Regular expression failed!'
                    return

        loc = insert - delete
        stat = stats.get(author)
        if stat is None:
            stats[author] = [1, insert, delete, loc]
        else:
            stat[0] += 1
            stat[1] += insert
            stat[2] += delete
            stat[3] += loc

        with open(csvfile, 'w') as csvfilehandler:
            writer = csv.writer(csvfilehandler)
            writer.writerow(CSV_FILE_HEADER)
            for author, stat in stats.items():
                writer.writerow([author, stat[0], stat[1], stat[2], stat[3]])


if __name__ == "__main__":
    REPO = '../ctrip/IOS_2/'
    SINCE = '2017-04-01'
    UNTIL = '2017-05-01'
    SUB_DIR = 'CTFlight'
    CSV_FILE = os.path.join(os.getcwd(), 'gitstats_iOS_v7_4.csv')
    gitstats(REPO, SINCE, UNTIL, SUB_DIR, CSV_FILE)

    REPO = '../ctrip/android_2/'
    SINCE = '2017-04-01'
    UNTIL = '2017-05-01'
    SUB_DIR = 'CTFlight'
    CSV_FILE = os.path.join(os.getcwd(), 'gitstats_Android_v7_4.csv')
    gitstats(REPO, SINCE, UNTIL, SUB_DIR, CSV_FILE)
