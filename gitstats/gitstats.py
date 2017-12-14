#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''Analyse git branch commit log, for every version, every person.'''
import os
import sys
import re
import csv

GIT_LOG = r'git -C {} log --since={} --until={} --pretty=tformat:%ae --shortstat --no-merges -- {} > {}'

REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"

CSV_FILE_HEADER = ["Author", "Commit", "Insert", "Delete", "Loc"]


def exec_git(repo, since, until, subdir):
    '''Execute git log commant, return string array.'''
    logfile = os.path.join(os.getcwd(), 'gitstats.txt')
    git_log_command = GIT_LOG.format(repo, since, until, subdir, logfile)
    os.system(git_log_command)
    lines = None
    with open(logfile, 'r', encoding='utf-8') as logfilehandler:
        lines = logfilehandler.readlines()
    return lines


def save_csv(stats, csvfile):
    '''save stats data to csv file.'''
    with open(csvfile, 'w', encoding='utf-8') as csvfilehandler:
        writer = csv.writer(csvfilehandler)
        writer.writerow(CSV_FILE_HEADER)
        for author, stat in stats.items():
            writer.writerow([author, stat[0], stat[1], stat[2], stat[3]])


def parse(lines):
    '''Analyse git log and sort to csv file.'''
    prog_full = re.compile(REPATTERN_FULL)
    prog_insert_only = re.compile(REPATTERN_INSERT_ONLY)
    prog_delete_only = re.compile(REPATTERN_DELETE_ONLY)

    stats = {}
    for i in range(0, len(lines), 3):
        author = lines[i]
        #empty = lines[i+1]
        info = lines[i+2]
        #change = 0
        insert, delete = int(0), int(0)
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
                    print('Regular expression fail!')
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

    return stats


if __name__ == "__main__":
    print('gitstats begin')
    if len(sys.argv) != 6:
        print('Invalid argv parameters.')
        exit(0)

    REPO = os.path.join(os.getcwd(), sys.argv[1])
    SINCE = sys.argv[2]
    UNTIL = sys.argv[3]
    SUB_DIR = sys.argv[4]
    CSV_FILE = os.path.join(os.getcwd(), sys.argv[5])
    LINES = exec_git(REPO, SINCE, UNTIL, SUB_DIR)
    assert LINES is not None
    STATS = parse(LINES)
    save_csv(STATS, CSV_FILE)
    print('gitstats done')
