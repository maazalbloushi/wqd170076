import json

# this imports and structures single company data from data dump

with open('20190927.json', 'r') as handle:
    dictdump = json.loads(handle.read())

for i in dictdump.keys():
    for j in dictdump[i]:
        for k in j[3]:
            if k[0] == 'TM':
                with open('20190927' + '-TM' + '.json', 'w') as outfile:
                    json.dump(json.loads(k[1]), outfile)