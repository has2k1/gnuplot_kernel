##############
How to release
##############

Testing
=======

* `cd` to the root of project and run
  ::

    make test

* Once all the tests pass move on


Tagging
=======

* Check out the master branch, open `gnuplot_kernel/kernel.py`
  increment the `__version__` string and make a commit.

* Tag with the version number e.g
  ::

    git tag -a v0.1.0 -m 'Version 0.1.0'

  Note the `v` before the version number.

* Push tag upstream
  ::

    git push upstream v0.1.0


Packaging
=========

* Make sure your `.pypirc` file is setup
  `correctly <http://docs.python.org/2/distutils/packageindex.html>`_.
  ::

    cat ~/.pypirc


* Build distribution
  ::

    make dist

* (optional) Upload to PyPi test repository
  and then try install and test
  ::

     make release-test

     mkvirtualenv test-gnuplot-kernel

     pip install -r pypyitest gnuplot_kernel

     cd cdsitepackages

     cd gnuplot_kernel

     nosetests

     cd ..

     deactivate

     rmvirtualenv test-gnuplot-kernel


* Upload to PyPi
  ::

    make release

* Done.
