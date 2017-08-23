.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/skdaccess_logo360x100.png
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

.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/skdaccess_overviewdiag.png
	   :alt: Scikit Data Access Overview
	   :width: 810


Supported data sets:

+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
| Namespace                     | Description                                                                                                                                                                                 | Data Source                                                      |
+===============================+=============================================================================================================================================================================================+==================================================================+
|                               | Light curves for stars imaged by the Kepler Space Telescope                                                                                                                                 |                                                                  |
| skdaccess.astro.kepler        |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             | https://kepler.science.arc.nasa.gov                              |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | United States groundwater monitoring wells measuring the depth to water level                                                                                                               |                                                                  |
| skdaccess.geo.groundwater     |                                                                                                                                                                                             | https://waterservices.usgs.gov                                   |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | Daily GPS displacement time series measurements throughout the United States                                                                                                                |                                                                  |
| skdaccess.geo.pbo             |                                                                                                                                                                                             | http://www.unavco.org/projects/major-projects/pbo/pbo.html       |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness                                                             |                                                                  |
| skdaccess.geo.grace           |                                                                                                                                                                                             | https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product       |                                                                  |
| skdaccess.geo.gldas           |                                                                                                                                                                                             | https://grace.jpl.nasa.gov/data/get-data/land-water-content      |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface                                                              |                                                                  |
| skdaccess.geo.modis           |                                                                                                                                                                                             |                   https://modis.gsfc.nasa.gov                    |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+
|                               | MIT led NSF project studying the Earth’s ionosphere with GPS                                                                                                                                |                                                                  |
| skdaccess.geo.mahali          |                                                                                                                                                                                             | http://mahali.mit.edu                                            |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
|                               |                                                                                                                                                                                             |                                                                  |
+-------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------------------------------------------------------------+

Install
~~~~~~~

.. code:: python

    pip install scikit-dataaccess

Documentation
~~~~~~~~~~~~~

See https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/docs

Contributors
~~~~~~~~~~~~

| Project lead: `Victor Pankratius (MIT) <http://www.victorpankratius.com>`_ 
| Project developers: Cody M. Rude, Justin D. Li, David M. Blair, Michael G. Gowanlock, Victor Pankratius

Acknowledgements
~~~~~~~~~~~~~~~~

We acknowledge support from NASA AISTNNX15AG84G, NSF ACI1442997, and NSF
AGS-1343967.

Examples
--------

Code available at
`Github <https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/examples>`__

.. image:: https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/skdaccess-quickexamples.png
           :alt: Scikit Data Access Overview
	   :width: 810		 
