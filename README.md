<p align="left">
  <img alt="Scikit Data Access" src="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_logo360x100.png"/>
</p>

- Import scientific data from various sources through one easy Python API.
- Use iterator patterns for each data source (configurable data generators + functions to get next data chunk).
- Skip parser programming and file format handling.
- Enjoy a common namespace for all data and unleash the power of data fusion.
- Handle data distribution in different modes: (1) local download, (2) caching of accessed data, or (3) online stream access
- Easily pull data on cloud servers through Python scripts and facilitate large-scale parallel processing.
- Build on an extensible plattform: Adding access to a new data source only requires addition of its "DataFetcher.py".   
- Open source (MIT License)

<p align="center">
  <img alt="Scikit Data Access" src="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_overviewdiag.png"/>
</p>

Supported data sets:

| Namespace  | Description | Data Source |
| ------------- | ------------- |------------- |
| <sup> skdaccess.astro.kepler</sup>   | <sup> Light curves for stars imaged by the Kepler Space Telescope</sup>   | <sup> https://keplerscience.arc.nasa.gov </sup> |
|<sup> skdaccess.geo.groundwater </sup> | <sup> United States groundwater monitoring wells measuring the depth to water level </sup> | <sup> https://waterservices.usgs.gov </sup> |
| <sup> skdaccess.geo.pbo </sup> | <sup> Daily GPS displacement time series measurements throughout the United States </sup> | <sup> http://www.unavco.org/projects/major-projects/pbo/pbo.html</sup> |
|<sup> skdaccess.geo.grace </sup> | <sup> GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness </sup> | <sup> https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land </sup> |
| <sup> skdaccess.geo.gldas </sup>  | <sup> Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product </sup> | <sup> https://grace.jpl.nasa.gov/data/get-data/land-water-content </sup> |
| <sup> skdaccess.geo.modis </sup> | <sup> Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface </sup> | <sup> https://modis.gsfc.nasa.gov </sup> |
| <sup> skdaccess.geo.mahali </sup> | <sup> MIT led NSF project studying the Earth’s ionosphere with GPS </sup> | <sup> http://mahali.mit.edu </sup> |



### Install
```python
pip install scikit-dataaccess
```

### Documentation

See <https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/docs>


### Contributors

Project lead: [Victor Pankratius (MIT)](http://www.victorpankratius.com)<br>
Project developers: Cody M. Rude, Justin D. Li, David M. Blair, Michael G. Gowanlock, Victor Pankratius

### Acknowledgements

We acknowledge support from NASA AISTNNX15AG84G, NSF ACI1442997, and NSF AGS-1343967.
