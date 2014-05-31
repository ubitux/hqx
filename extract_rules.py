import pprint, re

hqx_path = '/home/ubitux/src/hqx-read-only/src'

k_to_pos = [(0,0), (1,0), (2,0),
            (0,1),        (2,1),
            (0,2), (1,2), (2,2)]

data = {}

for i in [2, 3, 4]:
    hqx_c = hqx_path + '/hq%dx.c' % i

    reset_cases = True
    rules = {}

    for line in open(hqx_c).readlines():
        line = line.strip()
        if line.startswith('case '):
            if reset_cases:
                cases = []
            mask = int(line[5:-1])
            cases.append(sorted([pos for k, pos in enumerate(k_to_pos) if mask & 1<<k]))
            reset_cases = False
            current_condition = None
        else:
            reset_cases = True
            if 'Diff(' in line:
                current_condition = tuple(int(x) - 1 for x in re.findall('\[(\d+)\]', line))
            elif 'else' in line:
                current_condition = None
            elif line.startswith('PIXEL'):
                pxid = line[5:] #.split('_', 1)
                pxrules = rules.get(pxid, {})
                condrules = pxrules.get(current_condition, [])
                condrules += cases
                pxrules[current_condition] = sorted(condrules)
                rules[pxid] = pxrules

    data[i] = rules

open('rules.py', 'w').write('data = \\\n%s' % pprint.pformat(data, width=200))
