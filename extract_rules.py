import pprint, re

hqx_path = '/home/ubitux/src/hqx-read-only/src'

k_to_pos = [(0,0), (1,0), (2,0),
            (0,1),        (2,1),
            (0,2), (1,2), (2,2)]

def get_cases(mask):
    cases = []
    for k in range(9):
        if mask & 1<<k:
            cases.append(k_to_pos[k])
    return cases

interp_def = []
for i in [2, 3, 4]:
    hqx_c = hqx_path + '/hq%dx.c' % i

    reset_cases = True
    rules = {}

    for line in open(hqx_c).readlines():
        line = line.strip()
        if line.startswith('case '):
            if reset_cases:
                cases = []
            cases.append(get_cases(int(line[5:-1])))
            reset_cases = False
            current_condition = None
        else:
            if not reset_cases: # first non "case xx:" line
                #print '<<<', cases
                common_cases = reduce(lambda a,b: set(a)&set(b), cases)
                cases = tuple(common_cases), [tuple(set(x)-set(common_cases)) for x in cases]
                #print '>>>', cases

            '''
            >>> t = ([1,2,3], [1,3,5,9], [1,3,7,9], [1,3])
            >>> common = reduce(lambda a,b: set(a)&set(b), t)
            >>> tuple(common), [tuple(set(x)-common) for x in t]
            ((1, 3), [(2,), (9, 5), (9, 7), ()])
            '''

            reset_cases = True
            if 'Diff(' in line:
                current_condition = tuple(int(x) - 1 for x in re.findall('\[(\d+)\]', line))
            elif 'else' in line:
                current_condition = None
            elif line.startswith('PIXEL'):
                pxid = line[5:] #.split('_', 1)
                pxrules = rules.get(pxid, {})
                condrules = pxrules.get(current_condition, [])
                #print 'COND<<<',condrules
                condrules.append(cases)
                #print 'COND>>>',condrules
                pxrules[current_condition] = condrules
                rules[pxid] = pxrules

open('rules.py', 'w').write('''
data = \\
%s
''' % pprint.pformat(rules))
