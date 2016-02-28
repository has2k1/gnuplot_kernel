import sys
import os
import json
import pkgutil

from distutils import log
from distutils.command.install import install
from setuptools import setup
try:
    from jupyter_client.kernelspec import install_kernel_spec
except ImportError:
    from IPython.kernel.kernelspec import install_kernel_spec
from IPython.utils.tempdir import TemporaryDirectory


kernel_json = {
    'argv': [sys.executable,
             '-m', 'gnuplot_kernel',
             '-f', '{connection_file}'],
    'display_name': 'gnuplot',
    'language': 'gnuplot',
    'name': 'gnuplot',
}


def install_kernel_resources(destination,
                             resource='gnuplot_kernel',
                             files=None):
    """
    Copy the resource files to the kernelspec folder.
    """
    if files is None:
        files = ['logo-64x64.png', 'logo-32x32.png']

    for filename in files:
        try:
            data = pkgutil.get_data(resource,
                                    os.path.join('images', filename))
            with open(os.path.join(destination, filename), 'wb') as fp:
                fp.write(data)
        except Exception as e:
            sys.stderr.write(str(e))


class install_with_kernelspec(install):
    def run(self):
        install.run(self)
        with TemporaryDirectory() as td:
            os.chmod(td, 0o755)  # Starts off as 700, not user readable
            with open(os.path.join(td, 'kernel.json'), 'w') as f:
                json.dump(kernel_json, f, sort_keys=True)
            log.info('Installing kernel spec')
            install_kernel_resources(td, files=['logo-64x64.png'])
            kernel_name = kernel_json['name']
            try:
                install_kernel_spec(td, kernel_name, user=self.user,
                                    replace=True)
            except:
                install_kernel_spec(td, kernel_name, user=not self.user,
                                    replace=True)


svem_flag = '--single-version-externally-managed'
if svem_flag in sys.argv:
    # Die, setuptools, die.
    sys.argv.remove(svem_flag)


with open('gnuplot_kernel/kernel.py', 'rb') as fid:
    for line in fid:
        line = line.decode('utf-8')
        if line.startswith('__version__'):
            version = line.strip().split()[-1][1:-1]
            break


setup(name='gnuplot_kernel',
      version=version,
      description='A gnuplot kernel for Jupyter',
      long_description=open('README.rst', 'r').read(),
      author='Hassan Kibirige',
      author_email='has2k1@gmail.com',
      license='BSD',
      url="https://github.com/has2k1/gnuplot_kernel",
      cmdclass={'install': install_with_kernelspec},
      install_requires=[
          'metakernel >= 0.10.5',
          'notebook>=4.0'],
      packages=['gnuplot_kernel',
                'gnuplot_kernel.magics',
                'gnuplot_kernel.tests'],
      package_data={
          'gnuplot_kernel': [
              'images/logo-64x64.png']},
      classifiers=[
          'Framework :: IPython',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: System :: Shells',
      ]
      )
