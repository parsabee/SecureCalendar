# To run from source: 
#    make install
#    make run
#
# Many recipes need to be run in a virtual environment,
# so run them using $(PVENV) command
PVENV = . env/bin/activate ;

#  Virtual environment
MAKEPYVENV = python3 -m venv

env:
	$(MAKEPYVENV)  env
	($(PVENV) pip3 install -r requirements.txt)

install:  env

run:	env
	$(PVENV) python3 calgui.py

test:	env
	$(PVENV) nosetests

# Preserve virtual environment for git repository
dist:	env
	$(PVENV) pip freeze >requirements.txt

# clean leaves project ready to run.
clean:
	cd source; rm -f *.pyc
	cd source; rm -rf __pycache__

# veryclean removes all files except source files.
veryclean:
	make clean
	rm -rf env
