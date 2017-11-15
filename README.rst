.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_logo360x100.png
   :alt: Scikit Data Access

-  Import scientific data from various sources through one easy Python
   API.
-  Use iterator patterns for each data source (configurable data
   generators + functions to get next data chunk).
-  Skip parser programming and file format handling.
-  Enjoy a common namespace for all data and unleash the power of data
   fusion.
-  Handle data distribution in different modes: (1) local download, (2)
   caching of accessed data, or (3) online stream access
-  Easily pull data on cloud servers through Python scripts and
   facilitate large-scale parallel processing.
-  Build on an extensible plattform: Adding access to a new data source
   only requires addition of its "DataFetcher.py".
-  Open source (MIT License)

.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_overviewdiag.png
	   :alt: Scikit Data Access Overview
	   :width: 810


Supported data sets (For updates, follow https://twitter.com/scikit_data and https://twitter.com/mithaystack)


.. csv-table::
   :header: "Namespace", "Description", "Preview", "Data Source"

        |astro_icon| astro.kepler          , |nasa_logo|  	   |kepler_desc|            , |kepler_preview|            , |kepler_url|
        |astro_icon| astro.voyager         , |nasa_logo|  	   |voyager_desc|           , |voyager_preview|           , |voyager_url|
        |geo_icon|   geo.groundwater       , |usgs_logo|	   |groundwater_desc|       , |groundwater_preview|	  , |groundwater_url|
        |geo_icon|   geo.pbo               , |unavaco_logo|	   |pbo_desc|               , |pbo_preview|		  , |pbo_url|
        |geo_icon|   geo.grace             , |nasa_logo|	   |grace_desc|             , |grace_preview|	          , |grace_url|
        |geo_icon|   geo.gldas             , |nasa_logo|	   |gldas_desc|             , |gldas_preview|	          , |gldas_url|
        |geo_icon|   geo.modis             , |nasa_logo|	   |modis_desc|             , |modis_preview|	          , |modis_url|
        |geo_icon|   geo.magnetometer      , |usgs_logo|	   |magnetometer_desc|      , |magnetometer_preview|      , |magnetometer_url|
        |geo_icon|   geo.mahali.rinex      , |mit_logo| |nsf_logo| |mahali_rinex_desc|      , |mahali_rinex_preview|      , |mahali_url|
        |geo_icon|   geo.mahali.tec        , |mit_logo| |nsf_logo| |mahali_tec_desc|        , |mahali_tec_preview|        , |mahali_url|
        |geo_icon|   geo.mahali.temperature, |mit_logo| |nsf_logo| |mahali_temperature_desc|, |mahali_temperature_preview|, |mahali_url|
        |solar_icon| solar.sdo             , |nasa_logo|  	   |sdo_desc|               , |sdo_preview|               , |sdo_url|

.. Data type icons
.. |astro_icon| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png
.. |geo_icon| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png
.. |solar_icon| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_solar.png



.. Logos
.. |nasa_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png
.. |usgs_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_usgs.png
.. |unavaco_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_unavco.png
.. |mit_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_mit.png
.. |nsf_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nsf.png

.. Preview images
.. |kepler_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.kepler.png
	           :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Kepler.ipynb

.. |voyager_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.voyager.png
		    :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Voyager.ipynb

.. |sdo_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.solar.sdo.png
		:target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_SDO.ipynb

.. |groundwater_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.groundwater.png
                        :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Groundwater.ipynb

.. |pbo_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.pbo.png
                :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_PBO.ipynb

.. |grace_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.grace.png
                 :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_GRACE.ipynb

.. |gldas_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.gldas.png
                  :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_GLDAS.ipynb

.. |modis_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.modis.png
                  :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_MODIS.ipynb

.. |magnetometer_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.magnetometer.png
                         :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Magnetometer.ipynb

.. |mahali_rinex_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.rinex.png
                         :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Mahali_Rinex.ipynb

.. |mahali_tec_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.tec.png
                       :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Mahali_TEC.ipynb

.. |mahali_temperature_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.temperature.png
                               :target: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Temperature.ipynb

.. URLS
.. |kepler_url| replace::

	https://keplerscience.arc.nasa.gov

.. |voyager_url| replace::

	https://spdf.gsfc.nasa.gov

.. |sdo_url| replace::

	https://sdo.gsfc.nasa.gov

.. |groundwater_url| replace::

	https://waterservices.usgs.gov

.. |pbo_url| replace::

	http://www.unavco.org/projects/major-projects/pbo/pbo.html

.. |grace_url| replace::

	https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land

.. |gldas_url| replace::

	https://grace.jpl.nasa.gov/data/get-data/land-water-content

.. |modis_url| replace::

	https://modis.gsfc.nasa.gov

.. |magnetometer_url| replace::

	https://geomag.usgs.gov

.. |mahali_url| replace::

	http://mahali.mit.edu


.. Descriptions
.. |kepler_desc| replace::

		 Light curves for stars imaged by the NASA Kepler Space Telescope

.. |voyager_desc| replace::

		 Data from the Voyager mission

.. |sdo_desc| replace::

		 Images from the Solar Dynamics Observatory

.. |groundwater_desc| replace::

		      United States groundwater monitoring wells measuring the depth to water level

.. |pbo_desc| replace::

	      EarthScope - Plate Boundary Observatory (PBO): Daily GPS displacement time series measurements throughout the United States

.. |grace_desc| replace::

		NASA GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness

.. |gldas_desc| replace::

		Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product

.. |modis_desc| replace::

		Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface

.. |magnetometer_desc| replace::

		      Data collected at magnetic observatories operated by the U.S. Geological Survey

.. |mahali_rinex_desc| replace::

		       Rinex files from the MIT led NSF project studying the Earth’s ionosphere with GPS

.. |mahali_tec_desc| replace::

		     Total Electron Content from the MIT led NSF project studying the Earth’s ionosphere with GPS

.. |mahali_temperature_desc| replace::

			     Temperature data from the MIT led NSF project studying the Earth’s ionosphere with GPS

Install
~~~~~~~

.. code:: python

    pip install scikit-dataaccess


Documentation
~~~~~~~~~~~~~


- User Manual: `/docs/skdaccess_manual.pdf`_
- Code documentation (Doxygen): `/docs/skdaccess_doxygen.pdf`_
- Code visualization (treemap): `/docs/skdaccess_treemap.png`_
- Code class diagrams: `/docs/class_diagrams`_

.. _/docs/skdaccess_manual.pdf: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_manual.pdf
.. _/docs/skdaccess_doxygen.pdf: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_doxygen.pdf
.. _/docs/skdaccess_treemap.png: https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_treemap.png
.. _/docs/class_diagrams: https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/docs/class_diagrams


Contributors
~~~~~~~~~~~~

| Project lead: `Victor Pankratius (MIT) <http://www.victorpankratius.com>`_ 
| Contributors: Cody M. Rude, Justin D. Li, David M. Blair, Michael G. Gowanlock, Victor Pankratius
|
| New contributors welcome! Contact |skdaccess_contact| to contribute and add interface code for your own datasets |smiley|

.. |smiley| unicode:: 0x1F604

.. |skdaccess_contact| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_cont.png

Acknowledgements
~~~~~~~~~~~~~~~~

We acknowledge support from NASA AIST14-NNX15AG84G, NASA AIST16-80NSSC17K0125, NSF ACI-1442997, and NSF AGS-1343967.

Examples
--------

Code examples (Jupyter notebooks) for all datasets listed above are available at:
`/skdaccess/examples <https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/examples>`__

.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess-quickexamples-combined.png
           :alt: Scikit Data Access Overview
	   :width: 500
