import data
import sys, itertools, pprint

ppos = [(0,0), (1,0), (2,0),
        (0,1),        (2,1),
        (0,2), (1,2), (2,2)]

def comb2bin(comb):
    return ''.join('1' if pos in comb else '0' for pos in ppos)

def idx2pos(k):
    return ppos[k]

def factor_combs(combs):

    bins = [comb2bin(comb) for comb in combs]

    factor_bins = []

    def all_needs_met(needs):
        for _, met in needs:
            if met == False:
                return False
        return True

    for b in bins:
        current_set = []

        for b2 in bins:
            if b2 == b:
                continue

            # 'x' for common dot, '.' otherwise
            diff = ''.join('x' if x == y else '.' for x, y in zip(b, b2))
            nb_diff = diff.count('.')

            # generate all combinations (for the combinable dots) that needs to
            # be met in the subset to assume that they are optional
            products = [x for x in itertools.product('01', repeat=nb_diff)]
            need = []
            assert len(products) == 1<<nb_diff

            # generate the full combinations list in `need`
            for i in range(len(products)):
                new_need = ''
                product_pos = 0
                for pos, k in enumerate(diff):
                    if k == '.':
                        new_need += products[i][product_pos]
                        product_pos += 1
                    else:
                        new_need += b[pos]
                need.append((new_need, new_need in bins))

            # if all the needs are met and the set is not already present, we
            # add it to `factor_bins`
            if all_needs_met(need):
                merged_bins = set([x for x, _ in need])
                if merged_bins not in [x for _, x in factor_bins]:
                    factor_bins.append((diff, merged_bins))

    # keep the best factorisations
    def is_a_subset_of_another(fbins, x):
        for _, e in fbins:
            if x < e:
                return True
        return False
    best_factor_bins = [(diff, list(x)) for (diff, x) in factor_bins if not is_a_subset_of_another(factor_bins, x)]

    # construct output combs with optional support (such as "10.1..0.")
    patterns = []
    for diff, matches in best_factor_bins:
        patterns.append(''.join(matches[0][i] if k == 'x' else '.' for i, k in enumerate(diff)))

    # add the bins that match none of the patterns
    def match_a_pattern(b, combs):
        for comb in combs:
            match = True
            for i, k in enumerate(comb):
                if k != '.' and b[i] != k:
                    match = False
                    break
            if match:
                return True
        return False
    non_patterns = [b for b in bins if not match_a_pattern(b, patterns)]
    out_bins = patterns + non_patterns

    # convert bins back to positions
    out_combs = []
    for out_bin in out_bins:
        pos_enabled  = []
        pos_disabled = []
        for i, k in enumerate(out_bin):
            if k == '0':
                pos_disabled.append(idx2pos(i))
            elif k == '1':
                pos_enabled.append(idx2pos(i))
        out_combs.append((pos_enabled, pos_disabled))

    return out_combs

def main():

    pp_combs = data.combinations

    for dim in [2, 3, 4]:
        print 'postprocessing hq%dx...' % dim

        interps = [i for i in data.interps[dim]]

        # pre process combs:
        for interpid in interps:
            print '  :: %s...' % interpid
            new_cond_permuts = {}
            for cond, permuts in pp_combs[dim][interpid].items():
                new_cond_permuts[cond] = factor_combs(permuts)
            pp_combs[dim][interpid] = new_cond_permuts

    open('data_pp.py', 'w').write('''
combinations = \\
%s
''' % pprint.pformat(pp_combs, width=200))

if __name__ == '__main__':
    main()
