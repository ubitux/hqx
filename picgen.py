import data, data_pp
import cairo, sys

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
            if (i, j) == (1, 1):
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
        cr.stroke()

def main():

    dim = int(sys.argv[1])
    SZ = 3
    STEP = SZ*DOTSIZE + (SZ-1)*DOTSPACE + TBLSPACE

    mandatory_prefixes = {
        2: ['00'],
        3: None, # TODO
        4: ['00', '01', '10', '11']
    }

    interps = []
    for prefix in mandatory_prefixes[dim]:
        interps += [i for i in data.interps[dim] if i.startswith(prefix)]

    # estimate size
    nb_w, nb_h = 0, 0
    for interpid in interps:
        total_permuts = 0
        for cond, permuts in data_pp.combinations[dim][interpid].items():
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
    prefix = None
    for interpid in interps:
        x = MARGINX

        # add a separation line between interpolation group (different
        # destinations)
        new_prefix = interpid[:2]
        if prefix and prefix != new_prefix:
            cr.set_line_width(2)
            cr.set_source_rgb(1, 1, 0)
            cr.move_to(x, y - TBLSPACE/2)
            cr.line_to(x + w - 2*MARGINX, y - TBLSPACE/2)
            cr.stroke()
        prefix = new_prefix

        # draw interpolation
        pos, interp_values_id = data.interp_def[dim][interpid]
        interp = [WPOS[p] for p in pos]
        draw_interp(cr, x, y, SZ, interp, data.interp_values[interp_values_id])

        # draw combinations
        n = 0
        x = MARGINX + STEP
        for cond, permuts in data_pp.combinations[dim][interpid].items():
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
