<p align="left">
  <img src="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_logo.png" width="350"/>
</p>

# Scikit Data Access

- Import scientific data from various sources in Python through one easy API.
- Use iterator patterns for each data source (configurable data generators + functions to get next data chunk).
- Skip parser programming and time understanding file formats.
- Enjoy a common namespace for all data and unleash the power of data fusion across a variety of data sets.
- Handle data distribution in different modes: (1) local download, (2) caching of accessed data, or (3) online stream access
- Distribute data chunks easily on cloud servers for parallel processing
- Build on an extensible plattform. Accessing a new data source only requires addition of its "DataFetcher.py".   
- Open source (MIT License)

Supported data sets:

| Namespace  | Description | Data Source |
| ------------- | ------------- |------------- |
| skdaccess.astro.kepler  | Light curves for stars imaged by the Kepler Space Telescope  | https://keplerscience.arc.nasa.gov |
|skdaccess.geo.groundwater | United States groundwater monitoring wells measuring the depth to water level | https://waterservices.usgs.gov |
| skdaccess.geo.pbo | Daily GPS displacement time series measurements throughout the United States | http://www.unavco.org/ projects/major-projects/pbo/pbo.html|
|skdaccess.geo.grace | GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness | https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land |
| skdaccess.geo.gldas  | Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product | https://grace.jpl.nasa.gov/data/get-data/land-water-content |
| skdaccess.geo.modis | Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface | https://modis.gsfc.nasa.gov |
| skdaccess.geo.mahali | MIT led NSF project studying the Earth’s ionosphere with GPS | http://mahali.mit.edu |

### Install
```
pip install scikit-dataaccess
```

### Documentation

See <https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/docs>
