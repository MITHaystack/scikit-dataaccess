# from distutils.core import setup
from setuptools import setup
from setuptools import find_packages

package_name = 'scikit-dataaccess'

package_list = find_packages()

with open("README.md", encoding='utf-8') as rfile:
    readme = rfile.read()


setup(name     = package_name,
      version  = '1.9.16',
      packages = package_list,
      zip_safe = False,

      install_requires = [
          'astropy>=1.1.0',
          'atomicwrites',
          'geomag-algorithms',
          'ipython',
          'ipywidgets',
          'matplotlib',
          'netCDF4',
          'GDAL',
          'numpy>=1.10',
          'obspy',
          'pandas>=0.17',
          'pyproj',
          'requests',
          'scikit-image',
          'scipy',
          'setuptools',
          'six',
          'tables',
          'tqdm',
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

      package_data={'skdaccess': [
          'examples/Demo_ERA_Interim.ipynb',
          'examples/Demo_Finance_Time_Series.ipynb',
          'examples/Demo_GLDAS.ipynb',
          'examples/Demo_GRACE.ipynb',
          'examples/Demo_GRACE_Mascon.ipynb',
          'examples/Demo_Groundwater.ipynb',
          'examples/Demo_Kepler.ipynb',
          'examples/Demo_MODIS.ipynb',
          'examples/Demo_Magnetometer.ipynb',
          'examples/Demo_Mahali_Rinex.ipynb',
          'examples/Demo_Mahali_Rinex_Links.ipynb',
          'examples/Demo_Mahali_TEC.ipynb',
          'examples/Demo_Mahali_Temperature.ipynb',
          'examples/Demo_ODE.ipynb',
          'examples/Demo_PBO.ipynb',
          'examples/Demo_SDO.ipynb',
          'examples/Demo_SDSS_Spectra.ipynb',
          'examples/Demo_SRTM.ipynb',
          'examples/Demo_Sentinel_1.ipynb',
          'examples/Demo_Traffic_Counts.ipynb',
          'examples/Demo_UAVSAR.ipynb',
          'examples/Demo_Voyager.ipynb',
          'examples/Demo_Webcam_MIT_Sailing.ipynb',
          'examples/Demo_Wyoming_Sounding.ipynb',
          'examples/terminal_groundwater_example.py',
          'docs/skdaccess_doxygen.pdf',
          'docs/skdaccess_manual.pdf',
          'license/LICENSE',
          'support/mahali_data_info.hdf',
          'support/mahali_tec_info.hdf',
          'support/mahali_temperature_info.txt',
          'support/usgs_geomagnetism_observatories.txt',
          'support/srtm_gl1.txt',
          'support/srtm_gl3.txt']},

      entry_points = {'console_scripts': [
          'skdaccess = skdaccess.bin.skdaccess:skdaccess_script'
      ]},
      url = 'https://github.com/MITHaystack/scikit-dataaccess',
      python_requires='>=3.4',
      long_description = readme,
      long_description_content_type='text/markdown'
      )
