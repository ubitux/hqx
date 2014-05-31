import pprint, re

hqx_path = '/home/ubitux/src/hqx-read-only/src'

common_h = hqx_path + '/common.h'
interps_values = []
for line in open(common_h).readlines():
    if 'pc = Interp' in line:
        nums = [int(x) for x in re.findall('[^c_](\d+)', line)]
        coeffs, nbits = nums[:-1], nums[-1]
        interps_values.append((coeffs, nbits))

interp_def = {}
for i in [2, 3, 4]:
    hqx_c = hqx_path + '/hq%dx.c' % i
    interp_defx = {}
    for line in open(hqx_c).readlines():
        if line.startswith('#define PIXEL') and 'Interp' in line:
            m = re.match(r'.*PIXEL(\d+)_([^ ]+) +Interp(\d+)', line)
            dim, idx, interp = m.group(1, 2, 3)
            pos = [int(x) - 1 for x in re.findall('\[(\d+)\]', line)]
            interp_defx['%s_%s' % (dim, idx)] = (pos, int(interp) - 1)
    interp_def[i] = interp_defx

open('data.py', 'w').write('''
interp_values = \\
%s

interp_def = \\
%s
''' % (pprint.pformat(interps_values), pprint.pformat(interp_def)))
