from __future__ import division

from api import kamu_api
from pprint import pprint
import itertools

import numpy as np
import scipy.stats

YEAR = "2013"

members = kamu_api.member(
	activity_counts="true",
	activity_counts_resolution="year",
	activity_days='term',
	limit="1000"
	)
members = members['objects']

activity_types = set()

for member in members:
	mact = {}
	for act in member['activity_counts']:
		if not act['activity_date'].startswith(YEAR):
			continue
		activity_types.add(act['type'])
print activity_types
activity_types = list(activity_types)
activity_types = [t for t in activity_types if t not in ['IN']]
activities = []
for member in members:
	acts = [0]*len(activity_types)
	for act in member['activity_counts']:
		if not act['activity_date'].startswith(YEAR):
			continue
		if act['type'] not in activity_types: continue
		acts[activity_types.index(act['type'])] = act['count']

	activities.append([member['id']] + acts)
names = ['member_id']+activity_types
act_arr = np.array(activities)
act_arr = act_arr[:,1:]

nonzeros = np.prod(act_arr > 0, axis=1).astype(bool)
act_arr = act_arr[nonzeros]
act_arr = np.log(act_arr)

import matplotlib.pyplot as plt
import mdp
pcan = mdp.nodes.PCANode()
pcan.execute(act_arr)
pca = mdp.pca(act_arr)
print activity_types
print pcan.v.T
plt.hist(pca[:,0])
plt.show()
print pca.shape
plt.scatter(pca[:,0], pca[:,1])
plt.show()
print pca

activities = np.rec.fromrecords(activities, names=names)

handled = []
for x in activity_types:
	for y in activity_types:
		if set((x, y)) in handled:
			continue
		handled.append(set((x, y)))
		acts = activities[activities[x] > 0]
		acts = acts[acts[y] > 0]
		if x == y:
			continue
		xd, yd = map(np.log, (acts[x], acts[y]))
		r, p = scipy.stats.spearmanr(xd, yd)

		if p > 0.05:
			continue
		import matplotlib.pyplot as plt
		plt.title("%.5f %.5f %i"%(r, p, len(xd)))
		fit = np.poly1d(np.polyfit(xd, yd, 1))
		rng = np.min(xd), np.max(xd)
		
		print x, y, "%.5f %.5f %i"%(r, p, len(xd))
		continue
		plt.xlabel(x)
		plt.ylabel(y)
		plt.scatter(xd, yd)
		plt.plot(rng, fit(rng))
		plt.show()
