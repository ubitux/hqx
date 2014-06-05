import data
import cairo, sys, itertools

DOTSIZE  = 10
DOTSPACE = 5
TBLSPACE = 15
MARGINX = MARGINY = 10
MAX_NB_W = 15
WPOS = [(0,0), (1,0), (2,0),
        (0,1), (1,1), (2,1),
        (0,2), (1,2), (2,2)]

tbl_x = lambda i: i*(DOTSIZE + DOTSPACE)
tbl_y = lambda j: j*(DOTSIZE + DOTSPACE)

def draw_interp(cr, x, y, sz, interp, values):
    coeffs, nbits = values
    for j in range(sz):
        for i in range(sz):
            if (i, j) in interp:
                coeff = coeffs[interp.index((i, j))]
                power = 1. - float(coeff) / (1<<nbits)
                cr.set_source_rgb(power, 1, 1)
            else:
                cr.set_source_rgb(0.4, 0.4, 0.4)
            cr.rectangle(x + tbl_x(i), y + tbl_y(j), DOTSIZE, DOTSIZE)
            cr.fill()

def draw_combi(cr, x, y, sz, dots, conditionnal_diff):
    enabled_dots, disabled_dots = dots
    for j in range(sz):
        for i in range(sz):
            if (j, i) == (1, 1):
                continue
            if (i, j) in enabled_dots:
                cr.set_source_rgb(1, 0, 0)
            elif (i, j) in disabled_dots:
                cr.set_source_rgb(0.4, 0.4, 0.4)
            else:
                cr.set_source_rgb(0, 0, 0) # optionals (value doesn't matter)
            cr.rectangle(x + tbl_x(i), y + tbl_y(j), DOTSIZE, DOTSIZE)
            cr.fill()

    if conditionnal_diff:
        cr.set_line_width(2)
        cr.set_source_rgb(0, 1, 0)

        pt0, pt1 = conditionnal_diff
        cr.move_to(x + tbl_x(pt0 % 3) + DOTSIZE/2,
                   y + tbl_y(pt0 / 3) + DOTSIZE/2)
        cr.line_to(x + tbl_x(pt1 % 3) + DOTSIZE/2,
                   y + tbl_y(pt1 / 3) + DOTSIZE/2)
        cr.close_path()
        cr.stroke()

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

    dim = int(sys.argv[1])
    SZ = 3
    STEP = SZ*DOTSIZE + (SZ-1)*DOTSPACE + TBLSPACE

    interps = [i for i in data.interps[dim] if i.startswith('00')]

    # pre process combs:
    for interpid in interps:
        new_cond_permuts = {}
        for cond, permuts in data.combinations[dim][interpid].items():
            new_cond_permuts[cond] = factor_combs(permuts)
        data.combinations[dim][interpid] = new_cond_permuts

    # estimate size
    nb_w, nb_h = 0, 0
    for interpid in interps:
        total_permuts = 0
        for cond, permuts in data.combinations[dim][interpid].items():
            nb_permuts = len(permuts)
            total_permuts += nb_permuts
        nb_w = min(max(total_permuts, nb_w), MAX_NB_W)
        nb_h += total_permuts / nb_w + (1 if total_permuts % nb_w else 0)
    nb_w += 1

    w = 2*MARGINX + nb_w*SZ*DOTSIZE + nb_w*(SZ-1)*DOTSPACE + (nb_w-1)*TBLSPACE
    h = 2*MARGINY + nb_h*SZ*DOTSIZE + nb_h*(SZ-1)*DOTSPACE + (nb_h-1)*TBLSPACE

    # draw surface
    s = cairo.SVGSurface(None, w, h)
    cr = cairo.Context(s)
    cr.set_source_rgb(0.3, 0.3, 0.3)
    cr.rectangle(0, 0, w, h)
    cr.fill()

    y = MARGINY
    for interpid in interps:
        x = MARGINX

        # draw interpolation
        pos, interp_values_id = data.interp_def[dim][interpid]
        interp = [WPOS[p] for p in pos]
        draw_interp(cr, x, y, SZ, interp, data.interp_values[interp_values_id])

        # draw combinations
        n = 0
        x = MARGINX + STEP
        for cond, permuts in data.combinations[dim][interpid].items():
            for dots in permuts:
                if n and n % MAX_NB_W == 0:
                    x = MARGINX + STEP
                    y += STEP
                draw_combi(cr, x, y, SZ, dots, cond)
                x += STEP
                n += 1
        y += STEP

    s.write_to_png('hq%dx.png' % dim)

if __name__ == '__main__':
    main()
