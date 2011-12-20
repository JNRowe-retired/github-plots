import logging
import os
import argparse
from collections import defaultdict
from datetime import datetime, time, timedelta
from operator import itemgetter
from configobj import ConfigObj
from github2.client import Github

logging.basicConfig(level=logging.ERROR)


def github_client(cache):
    config = ConfigObj(os.path.join(os.getenv('HOME'), '.gitconfig'))
    return Github(username=config['github']['user'],
                  api_token=config['github']['token'],
                  requests_per_second=1,
                  cache=os.path.expanduser(cache) if cache else None)


class IssueTimeline(object):

    def __init__(self, github, repo_name):
        self.github = github
        self.repo_name = repo_name
        self.changes = []

    def load(self):
        changes = []
        for state in ('open', 'closed'):
            for issue in self.github.issues.list(self.repo_name, state=state):
                changes.append((issue.created_at, 1))
                if issue.closed_at:
                    changes.append((issue.closed_at, -1))
        changes.sort(key=itemgetter(0))
        self.changes = changes

    def range(self):
        if not self.changes:
            self.load()
        start_date = self.changes[0][0].date()
        end_date = self.changes[-1][0].date()
        num_days = int((end_date - start_date).total_seconds() / 86400)
        return (start_date + timedelta(days=ii) for ii in xrange(num_days + 1))

    def issues_on(self, d):
        if not self.changes:
            self.load()
        d = datetime.combine(d, time())
        num = 0
        for change_date, change_diff in self.changes:
            if change_date < d:
                num += change_diff
            else:
                break
        return num

    def open_issues_by_date(self):
        data = []
        for day in self.range():
            data.append((day.strftime('%m/%d/%Y'), self.issues_on(day)))
        tomorrow = self.changes[-1][0].date() + timedelta(days=1)
        data.append(("NOW", self.issues_on(tomorrow)))
        return data

    def handled_issues_by_date(self):
        if not self.changes:
            self.load()
        handled_by_date = defaultdict(int)
        for change_date, change_diff in self.changes:
            day = change_date.date()
            if change_diff < 0:
                handled_by_date[day] += 1
        
        data = []
        for day in self.range():
            data.append((day.strftime('%m/%d/%Y'), handled_by_date[day]))
        return data


def horizontal_bar(data, plot_width=80, bar_char='#', values=True):
    label_width = max(len(row[0]) for row in data)
    data_range = max(row[1] for row in data)
    scale = (plot_width - label_width - 1) / data_range
    for label, value in data:
        label = label.rjust(label_width)
        bar_width = value * scale
        bars = bar_char * bar_width
        s = "%s %s" % (label, bars)
        if values and value > 0:
            s += " %s" % value
        print s


def main():
    p = argparse.ArgumentParser(description='plots from github.')
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                   help='print detailed output')
    p.add_argument('-c', '--cache', default=None, metavar='directory',
                   help='location for network cache')
    p.add_argument('--out', metavar='filename', dest='out_file', type=str,
                   help='file to save output to')
    p.add_argument('mode', type=str,
                   help='plot to generate',
                   choices=('open-issues', 'handled-issues'))
    p.add_argument('repos', metavar='repos', type=str, nargs='+',
                   help='repos to plot data for')
    args = p.parse_args()
    if args.verbose:
        print "Running %s for %s" % (args.mode, ', '.join(args.repos))

    github = github_client(args.cache)
    for repo in args.repos:
        if args.mode == 'open-issues':
            print "Open issue timeline for %s" % repo
            data = IssueTimeline(github, repo).open_issues_by_date()
            horizontal_bar(data)
        elif args.mode == 'handled-issues':
            print "Handled issue timeline for %s" % repo
            data = IssueTimeline(github, repo).handled_issues_by_date()
            horizontal_bar(data)


if __name__ == '__main__':
    main()
