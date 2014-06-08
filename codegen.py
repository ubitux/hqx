import data, data_pp
import sys, pprint

ppos = [(0,0), (1,0), (2,0),
        (0,1),        (2,1),
        (0,2), (1,2), (2,2)][::-1]

def create_ast(dim, dstpos):
    interps = [i for i in data.interps[dim] if i.startswith(dstpos)]

    # combinations with a condition must be dealt with first, because those
    # without mean they must not be met (as long as a same combination with a
    # condition exists)
    def combs_cmp(x, y):
        ix, cx, px = x
        iy, cy, py = y
        if cx and not cy:
            return -1
        if cy and not cx:
            return 1
        return len(px) - len(py)
    combs = []
    for interpid in interps:
        for cond, permuts in data_pp.combinations[dim][interpid].items():
            combs.append((interpid, cond, permuts))
    combs.sort(cmp=combs_cmp)

    root_cond = None

    for i, comb in enumerate(combs):

        interpid, cond, permuts = comb

        ast_cond = ['||']
        for enabled_dots, disabled_dots in permuts:
            mask_diff = mask_nodiff = 0
            for dot in enabled_dots:
                mask_diff |= 1<<ppos.index(dot)
            for dot in disabled_dots:
                mask_nodiff |= 1<<ppos.index(dot)
            mask_values_that_matter = mask_diff | mask_nodiff
            ast_cond.append('(k&0x%02x) == 0x%02x' % (mask_values_that_matter, mask_diff))

        if len(ast_cond) == 2:
            ast_cond = ast_cond[1]

        if cond:
            diff_func = 'Diff(hqx, w[%d], w[%d])' % (cond[0]+1, cond[1]+1)
            ast_cond = ['&&', ast_cond, diff_func]

        if not root_cond:
            root_cond = entry_cond = ['if', ast_cond, 'PIXEL%s' % interpid, None]
        elif i == len(combs) - 1:
            assert entry_cond[3] is None
            entry_cond[3] = 'PIXEL%s' % interpid
        else:
            assert entry_cond[3] is None
            entry_cond[3] = ['if', ast_cond, 'PIXEL%s' % interpid, None]
            entry_cond = entry_cond[3]

    return root_cond

def get_c_code(node, need_protective_parenthesis=True):

    code = []

    if not isinstance(node, list):
        return node

    if node[0] == 'if':
        code.append('if (%s)' % get_c_code(node[1], need_protective_parenthesis=False))
        code.append(' ' * 4 + get_c_code(node[2]))
        code.append('else')
        c_code = get_c_code(node[3])
        if c_code.startswith('if'):
            code[-1] += ' ' + c_code
        else:
            code.append(' ' * 4 + c_code)
        return '\n'.join(code)

    assert node[0] in ('||', '&&')
    c_code = (' %s ' % node[0]).join(get_c_code(x) for x in node[1:])
    return '(%s)' % c_code if need_protective_parenthesis else c_code

def main():
    dim = int(sys.argv[1])

    code = ''

    code += get_c_code(create_ast(dim, '00')) + '\n\n'
    code += get_c_code(create_ast(dim, '01')) + '\n\n'
    code += get_c_code(create_ast(dim, '10')) + '\n\n'
    code += get_c_code(create_ast(dim, '11')) + '\n\n'

    open('hq%dx_tpl.c' % dim, 'w').write(code)

if __name__ == '__main__':
    main()
