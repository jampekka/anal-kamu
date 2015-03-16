#!/usr/bin/python2
from __future__ import division

from api import kamu_api
from pprint import pprint
import itertools
from collections import defaultdict

import numpy as np

from api import kamu_api

def estimate(activity_days=365, normer_act='ST'):
	members = kamu_api.member(
		activity_counts="true",
		activity_counts_resolution="day",
		activity_days=activity_days,
		current="true",
		limit="1000"
		)['objects']
	
	activity_types = {}
	activities = []
	for i, member in enumerate(members):
                mact = defaultdict(lambda: 0)
		for act in member['activity_counts']:
                        mact[act['type']] += act['count']
		activities.extend([i, t, v] for t, v in mact.items())
	
	activities = np.rec.fromrecords(activities, names='member,type,count')
	activity_types = np.unique(activities['type'])
	typical_counts = []
	for at in activity_types:
		ta = activities[activities['type'] == at]
		typical = np.mean(ta['count'])
		typical_counts.append(typical)
        weights = dict(zip(activity_types, typical_counts))
        normer = weights[normer_act]
        for k,v in weights.items():
            weights[k] = normer/v
        return weights

def dump(*args, **kwargs):
    for k, v in estimate(*args, **kwargs).items():
        print "%s\t%f"%(k, v)
        

if __name__ == '__main__':
    import argh
    argh.dispatch_command(dump)
