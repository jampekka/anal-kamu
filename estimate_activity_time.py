from __future__ import division

from api import kamu_api
from pprint import pprint
import itertools

import numpy as np

YEAR = "2013"
#WORKDAYS_IN_YEAR = 251 - 38
WORKDAYS_IN_YEAR = 365
WORKHOURS_IN_DAY = 10

government = ["kok", "r", "kd", "vihr", "vas", "sd"]
gov_uris = set("/api/v1/party/%s/"%p for p in government)

members = kamu_api.member(
	activity_counts="true",
	activity_counts_resolution="year",
	activity_days='term',
	current="true",
	limit="1000"
	)
members = members['objects']

activity_types = {}
activities = []
for i, member in enumerate(members):
	#pprint(member)
	mact = {}
	for act in member['activity_counts']:
		if not act['activity_date'].startswith(YEAR):
			continue
		activities.append([i, act['type'], act['count']])

activities = np.rec.fromrecords(activities, names='member,type,count')
#activities['count'] = np.log2(activities['count']+1)
activity_types = np.unique(activities['type'])
typical_counts = []
for at in activity_types:
	ta = activities[activities['type'] == at]
	#print at, len(ta)
	#print at, 1.0/np.median(ta['count']/WORKDAYS_IN_YEAR)
	#print at, np.median(ta['count']), np.mean(ta['count']), len(ta['count'])
	typical = np.mean(ta['count'])
	typical_counts.append(typical)


typical_per_year = np.array(typical_counts)
typical_per_day = typical_per_year/WORKDAYS_IN_YEAR

normer = WORKHOURS_IN_DAY/float(len(typical_per_day))

hours_per_type = normer/typical_per_day


for tp, hours in zip(activity_types, hours_per_type):
	print tp, hours

weight_dict = dict(zip(activity_types, hours_per_type))
activities.sort(order='member')

scores = []
for member_i, act in itertools.groupby(activities, lambda x: x['member']):
	total = 0.0
	for m, t, c in act:
		total += weight_dict[t]*c
	members[member_i]['activity_score'] = total/float(WORKDAYS_IN_YEAR)
	scores.append(total/float(WORKDAYS_IN_YEAR))

def kdeplot(values, *args, **kwargs):
	import scipy.stats
	kde = scipy.stats.gaussian_kde(values)
	rng = np.linspace(0, np.max(values), 100)
	plt.plot(rng, kde(rng), *args, **kwargs)

print "Mean/median of weights", np.mean(scores), np.median(scores)
import matplotlib.pyplot as plt
grouper = lambda x: ["Opp", "Gov"][x['party'] in gov_uris]
for group, members in itertools.groupby(sorted(members, key=grouper), grouper):
	scores = [m['activity_score'] for m in members if m['activity_score'] is not None]
	# :(
	if len(scores) < 2: continue
	kdeplot(scores, label=group)
	#plt.hist(scores, bins=min(len(scores), 10))
	#plt.show()
plt.legend()
#plt.hist(scores, bins=20)
#print np.percentile(scores, 95)
plt.show()
