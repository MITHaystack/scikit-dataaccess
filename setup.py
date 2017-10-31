# from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

package_name = 'scikit-dataaccess'

package_list = find_packages()

with open("README.rst") as rfile:
    readme = rfile.read()


setup(name     = package_name,
      version  = '1.9.4.post1',
      packages = package_list,
      zip_safe = False,
      
      install_requires = ['tqdm',
                          'numpy>=1.10',
                          'pandas>=0.17',
                          'tables',
                          'scipy',
                          'setuptools',
                          'astropy>=1.1.0',
                          'netCDF4',
      ],
      
      description = 'Scikit Data Access Package for accessing scientific data sets.',
      author = 'MITHAGI',
      author_email='skdaccess@mit.edu',
      classifiers=[
          'Topic :: Scientific/Engineering',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only'
          ],

      package_data={'skdaccess': ['examples/terminal_groundwater_example.py', 'examples/Demo_Grace.ipynb',
                                  'examples/Demo_Groundwater.ipynb', 'examples/Demo_Kepler.ipynb',
                                  'examples/Demo_PBO.ipynb','docs/skdaccess_doxygen.pdf',
                                  'docs/skdaccess_manual.pdf','support/mahali_data_info.hdf',
                                  'support/mahali_temperature_info.txt', 'support/mahali_tec_info.hdf',
                                  'support/usgs_geomagnetism_observatories.txt']},

      entry_points = {'console_scripts': [
          'skdaccess = skdaccess.bin.skdaccess:skdaccess_script'
          ]},
      url = 'https://github.com/MITHaystack/scikit-dataaccess',
      python_requires='>=3.4',
      long_description = readme
      )
