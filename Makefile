all: show
hqx-read-only:
	# tested with revision 14
	svn checkout http://hqx.googlecode.com/svn/trunk/ hqx-read-only
extract.py: hqx-read-only
data.py: extract.py
	python2 ./extract.py
hqx.py: data.py
hq%x.png: hqx.py
	python2 ./hqx.py $*
show: hq2x.png
	feh hq2x.png
clean:
	$(RM) *.pyc hq*x.png data.py
re: clean all
distclean: clean
	$(RM) -r hqx-read-only
.PHONY: all show clean re
