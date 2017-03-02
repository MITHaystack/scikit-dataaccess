# from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

package_name = 'scikit-dataaccess'

package_list = find_packages()

setup(name     = package_name,
      version  = '1.1.0',
      packages = package_list,
      zip_safe = False,
      
      install_requires = ['tqdm',
                          'numpy>=1.10',
                          'pandas>=0.17',
                          'tables',
                          'scipy',
                          'setuptools',
                          'astropy>=1.1.2'],
      
      description = 'Scikit Data Access Package for accessing scientific data sets.',
      author = 'MITHAGI',
      author_email='skdaccess@mit.edu',
      classifiers=[
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
          ],

      package_data={'skdaccess': ['examples/groundwater_example.py', 'examples/Demo_Grace.ipynb',
                                  'examples/Demo_Groundwater.ipynb', 'examples/Demo_Kepler.ipynb',
                                  'examples/Demo_PBO.ipynb','docs/skdaccess_doxygen.pdf',
                                  'docs/skdaccess_manual.pdf']},

      entry_points = {'console_scripts': [
          'skdaccess = skdaccess.commands:skdaccess_script'
          ]}
      )
