import data, data_pp
import sys, pprint

ppos = [(0,0), (1,0), (2,0),
        (0,1),        (2,1),
        (0,2), (1,2), (2,2)]

def create_ast(dim):
    interps = [i for i in data.interps[dim] if i.startswith('00')]

    def interps_cmp(x, y):
        nx = sum(len(permuts) for _, permuts in data_pp.combinations[dim][x].items())
        ny = sum(len(permuts) for _, permuts in data_pp.combinations[dim][y].items())
        return nx - ny

    root_cond = None

    for i, interpid in enumerate(sorted(interps, cmp=interps_cmp)):

        interp_cond_permuts = data_pp.combinations[dim][interpid].items()
        assert len(interp_cond_permuts) <= 2

        extradiff_cond = noextradiff_cond = None
        for cond, permuts in interp_cond_permuts:
            ast_cond = ['or']
            for enabled_dots, disabled_dots in permuts:
                mask_diff = mask_nodiff = 0
                for dot in enabled_dots:
                    mask_diff |= 1<<ppos[::-1].index(dot)
                for dot in disabled_dots:
                    mask_nodiff |= 1<<ppos[::-1].index(dot)
                mask_values_that_matter = mask_diff | mask_nodiff
                ast_cond.append('(k&0x%02x) == 0x%02x' % (mask_values_that_matter, mask_diff))
            if cond:
                diff_func = 'yuv_diff(w[%d], w[%d])' % (cond[0], cond[1])
                extradiff_cond = ['and', diff_func, ast_cond]
            else:
                noextradiff_cond = ast_cond

        if extradiff_cond and noextradiff_cond:
            ast_cond = ['or', extradiff_cond, noextradiff_cond]
        elif extradiff_cond:
            ast_cond = extradiff_cond
        elif noextradiff_cond:
            ast_cond = noextradiff_cond
        else:
            assert False

        if not root_cond:
            root_cond = entry_cond = ['if', ast_cond, 'PIXEL%s' % interpid, None]
        elif i == len(interp_cond_permuts) - 1:
            assert entry_cond[3] is None
            entry_cond[3] = 'PIXEL%s' % interpid
        else:
            assert entry_cond[3] is None
            entry_cond[3] = ['if', ast_cond, 'PIXEL%s' % interpid, None]
            entry_cond = entry_cond[3]

    return root_cond

def main():
    dim = int(sys.argv[1])

    root_cond = create_ast(dim)

    open('hq%dx_tpl.c' % dim, 'w').write(pprint.pformat(root_cond, width=200))

if __name__ == '__main__':
    main()
