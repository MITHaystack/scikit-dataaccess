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


Supported data sets |contact|

.. |contact| raw:: html

	<sub> (For updates, follow <a href=https://twitter.com/scikit_data> https://twitter.com/scikit_data </a>
	and <a href=https://twitter.com/mithaystack> https://twitter.com/mithaystack </a>)</sub>


.. csv-table::
   :header: "Namespace", "Description", "Preview", "Data Source"

        :sup:`skdaccess.astro.kepler`          , |nasa_logo|  	       |kepler_desc|            , |kepler_preview|            , |kepler_url|
        :sup:`skdaccess.astro.voyager`         , |nasa_logo|  	       |voyager_desc|           , |voyager_preview|           , |voyager_url|
        :sup:`skdaccess.astro.sdo`             , |nasa_logo|  	       |sdo_desc|               , |sdo_preview|               , |sdo_url|
        :sup:`skdaccess.geo.groundwater`       , |usgs_logo|	       |groundwater_desc|       , |groundwater_preview|	      , |groundwater_url|
        :sup:`skdaccess.geo.pbo`               , |unavaco_logo|	       |pbo_desc|               , |pbo_preview|		      , |pbo_url|
        :sup:`skdaccess.geo.grace`             , |nasa_logo|	       |grace_desc|             , |grace_preview|	      , |grace_url|
        :sup:`skdaccess.geo.gldas`             , |nasa_logo|	       |gldas_desc|             , |gldas_preview|	      , |gldas_url|
        :sup:`skdaccess.geo.modis`             , |nasa_logo|	       |modis_desc|             , |modis_preview|	      , |modis_url|
        :sup:`skdaccess.geo.magnetometer`      , |usgs_logo|	       |magnetometer_desc|      , |magnetometer_preview|      , |magnetometer_url|
        :sup:`skdaccess.geo.mahali.rinex`      , |mit_logo| |nsf_logo| |mahali_rinex_desc|      , |mahali_rinex_preview|      , |mahali_url|
        :sup:`skdaccess.geo.mahali.tec`        , |mit_logo| |nsf_logo| |mahali_tec_desc|        , |mahali_tec_preview|	      , |mahali_url|
        :sup:`skdaccess.geo.mahali.temperature`, |mit_logo| |nsf_logo| |mahali_temperature_desc|, |mahali_temperature_preview|, |mahali_url|


.. Logos
.. |nasa_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png
.. |usgs_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_usgs.png
.. |unavaco_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_unavco.png
.. |mit_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_mit.png
.. |nsf_logo| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nsf.png

.. Preview images
.. |kepler_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.kepler.png
.. |voyager_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.voyager.png
.. |sdo_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.solar.sdo.png
.. |groundwater_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.groundwater.png
.. |pbo_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.pbo.png
.. |grace_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.grace.png
.. |gldas_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.gldas.png
.. |modis_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.modis.png
.. |magnetometer_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.magnetometer.png
.. |mahali_rinex_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.rinex.png
.. |mahali_tec_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.tec.png
.. |mahali_temperature_preview| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.temperature.png

.. URLS
.. |kepler_url| raw:: html

	<sup> <a href=https://keplerscience.arc.nasa.gov> https://keplerscience.arc.nasa.gov </a> </sup>

.. |voyager_url| raw:: html

	<sup> <a href=https://spdf.gsfc.nasa.gov/> https://spdf.gsfc.nasa.gov/ </a> </sup>

.. |sdo_url| raw:: html

	<sup> <a href=https://sdo.gsfc.nasa.gov/> https://sdo.gsfc.nasa.gov/ </a></sup>

.. |groundwater_url| raw:: html

	<sup> <a href=https://waterservices.usgs.gov> https://waterservices.usgs.gov </a> </sup>

.. |pbo_url| raw:: html

	<sup> <a href=http://www.unavco.org/projects/major-projects/pbo/pbo.html>
	http://www.unavco.org/projects/major-projects/pbo/pbo.html </a> </sup>

.. |grace_url| raw:: html

	<sup> <a href=https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land>
	https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land  </a> </sup>

.. |gldas_url| raw:: html

	<sup> <a href=https://grace.jpl.nasa.gov/data/get-data/land-water-content>
	https://grace.jpl.nasa.gov/data/get-data/land-water-content </a> </sup>

.. |modis_url| raw:: html

	<sup> <a href=https://modis.gsfc.nasa.gov> https://modis.gsfc.nasa.gov </a> </sup>

.. |magnetometer_url| raw:: html

	<sup> <a href=https://geomag.usgs.gov> https://geomag.usgs.gov </a> </sup>

.. |mahali_url| raw:: html

	<sup> <a href=http://mahali.mit.edu> http://mahali.mit.edu </a> </sup>


.. Descriptions
.. |kepler_desc| replace::

		 :sub:`Light curves for stars imaged by the NASA Kepler Space Telescope`

.. |voyager_desc| replace::

		 :sub:`Data from the Voyager mission`

.. |sdo_desc| replace::

		 :sub:`Images from the Solar Dynamics Observatory`

.. |groundwater_desc| replace::

		      :sub:`United States groundwater monitoring wells measuring the depth to water level`

.. |pbo_desc| replace::

	      :sub:`EarthScope - Plate Boundary Observatory (PBO): Daily GPS displacement time series measurements throughout the United States`

.. |grace_desc| replace::

		:sub:`NASA GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness`

.. |gldas_desc| replace::

		:sub:`Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product`

.. |modis_desc| replace::

		:sub:`Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface`

.. |magnetometer_desc| replace::

		      :sub:`Data collected at magnetic observatories operated by the U.S. Geological Survey`

.. |mahali_rinex_desc| replace::

		       :sub:`Rinex files from the MIT led NSF project studying the Earth’s ionosphere with GPS`

.. |mahali_tec_desc| replace::

		     :sub:`Total Electron Content from the MIT led NSF project studying the Earth’s ionosphere with GPS`

.. |mahali_temperature_desc| replace::

			     :sub:`Temperature data from the MIT led NSF project studying the Earth’s ionosphere with GPS`

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
| Project developers: Cody M. Rude, Justin D. Li, David M. Blair, Michael G. Gowanlock, Victor Pankratius
|
| New contributors welcome! Contact |skdaccess_contact| to contribute and add interface code for your own datasets |smiley|

.. |smiley| unicode:: 0x1F604

.. |skdaccess_contact| image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_cont.png

Acknowledgements
~~~~~~~~~~~~~~~~

We acknowledge support from NASA AISTNNX15AG84G, NSF ACI1442997, and NSF
AGS-1343967.

Examples
--------

Code examples (Jupyter notebooks) for all datasets listed above are available at:
`/skdaccess/examples <https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/examples>`__

.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess-quickexamples-combined.png
           :alt: Scikit Data Access Overview
	   :width: 810		 
