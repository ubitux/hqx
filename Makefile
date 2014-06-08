all: show
hqx-read-only:
	# tested with revision 14
	svn checkout http://hqx.googlecode.com/svn/trunk/ hqx-read-only
extract.py: hqx-read-only
data.py: extract.py
	python2 ./extract.py
picgen.py: data.py data_pp.py
data_pp.py: data.py factor.py
	python2 ./factor.py
codegen.py: data.py data_pp.py
hq%x_tpl.c: codegen.py
	python2 ./codegen.py $*
hq%x.png: picgen.py
	python2 ./picgen.py $*
show: hq2x.png
	feh hq2x.png
code: hq2x_tpl.c
	cat hq2x_tpl.c
code4: hq4x_tpl.c
	cat hq4x_tpl.c
clean:
	$(RM) *.pyc hq*x.png data.py pp_data.py hq*x_tpl.c
re: clean all
distclean: clean
	$(RM) -r hqx-read-only
.PHONY: all show code clean re distclean
