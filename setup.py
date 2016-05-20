# from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

package_name = 'skdaccess'

package_list = find_packages()

setup(name     = package_name,
      version  = '0.9.3',
      packages = package_list,
      zip_safe = False,
      scripts=['bin/skdaccess'],      
      install_requires = ['tqdm',
                          'numpy>=1.10',
                          'pandas>=0.17',
                          'tables',
                          'scipy',
                          'setuptools',
                          'astropy>=1.1.2'],
      description = 'Sci-kit Data Access Package for accessing scientific data sets.',
      author = 'MITHAGI',
      author_email='skdaccess@mit.edu',
      classifiers=[
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
          ],

      package_data={'skdaccess': ['examples/groundwater_example.py','docs/skdaccess_doxygen.pdf','docs/skdaccess_manual.pdf']}
      )
