import itertools

import numpy as np
import matplotlib.pyplot as plt

from api import kamu_api

def get_activities(members):
	for member in members:
		yield member['activity_score']


members = kamu_api.member(since='month', include="stats",
	current='true', activity_counts=True, limit='1000')

members = members['objects']

sorting = lambda m: m['party']
members.sort(key=sorting)
partyacts = []
for party, members in itertools.groupby(members, sorting):
	act = np.array(list(get_activities(members)))
	partyacts.append((party, act ))
	

labels, acts = zip(*partyacts)
plt.hist(acts, stacked=True, label=labels, histtype='stepfilled')
plt.legend()

#plt.show()
#plt.hist(activities, bins=30)
plt.show()
