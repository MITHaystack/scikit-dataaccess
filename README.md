<p align="left">
  <img alt="Scikit Data Access" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_logo360x100.png"/>
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
  <img alt="Scikit Data Access Overview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_overviewdiag.png" width="810"/>
</p>

Supported data sets:

<table>

 <tr>
  <td>
  <p><o:p>&nbsp;</o:p></p>
  </td>
   <!-- namespace -->
  <td width=200>
  <p>Namespace</p>
  </td>
   <!-- preview -->
  <td width=63>
    <p><span>Preview<br><sup>(link)</sup></span></p>
  </td>
   <!-- description -->
  <td width=500>
  <p><span>Description & Data Source</span></p>
  </td>
 </tr>

 <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png>  Astronomy
  </sup>  
  </td>
 </tr>

 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200>
  <sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png> 
         astro.kepler 
  </sup>
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Kepler.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.kepler.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> Light curves for stars imaged by the NASA Kepler Space Telescope <br>Source: https://keplerscience.arc.nasa.gov</sup>
  </td>
 </tr>
 

  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>

   <!-- namespace -->
  <td width=200>
  <sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png>
         astro.spectra
  </sup>
  </td>

   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_SDSS_Spectra.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.spectra.png"/></a>
  </td>

   <!-- description -->
  <td width=500>
   <sup> Spectra from the Sloan Digital Sky Survey <br>Source: https://www.sdss.org/dr14/spectro/ </sup>
  </td>
 </tr>


  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>

   <!-- namespace -->
  <td width=200>
  <sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png>
         astro.tess.data
  </sup>
  </td>

   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_TESS_Data_Alerts.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.tess.data.png"/></a>
  </td>

   <!-- description -->
  <td width=500>
   <sup> Light curves from TESS Data Alerts <br>Source: https://archive.stsci.edu/prepds/tess-data-alerts/ </sup>
  </td>
 </tr>

  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>

   <!-- namespace -->
  <td width=200>
  <sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png>
         astro.tess.simulated
  </sup>
  </td>

   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_TESS_Simulated_Data.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.tess.simulated.png"/></a>
  </td>

   <!-- description -->
  <td width=500>
   <sup> Simulated lightcurves from TESS End-to-End 6 <br>Source: https://archive.stsci.edu/prepds/tess-data-alerts/ </sup>
  </td>
 </tr>

  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_astro.png> astro.voyager 
  </sup> 
  </td>
  
   <!-- preview -->
  <td width=63><sup> 
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Voyager.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.astro.voyager.png"/></a>
  </sup> 
  </td>
   
   <!-- description -->
  <td width=500>
  <sup> 
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> Data from the Voyager mission. <br> Source: https://spdf.gsfc.nasa.gov/
  </sup> 
  </td>
 </tr>
 
  <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_engineering.png> Engineering
  </sup>
  </td>
 </tr>
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_engineering.png> engineering.la.traffic_counts 
  </sup> 
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Traffic_Counts.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.engineering.la.traffic_counts.png"/></a>  
  </td>
   
   <!-- description -->
  <td width=500><sup> 
   Traffic Count data in Los Angeles. <br> Source: https://data.lacity.org/A-Livable-and-Sustainable-City/LADOT-Traffic-Counts-Summary/94wu-3ps3
  <sup> 
  </td>
 </tr>
 
   <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>

   <!-- namespace -->
  <td width=250><sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_engineering.png> engineering.webcam.mit_sailing
  </sup>
  </td>

   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Webcam_MIT_Sailing.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.engineering.webcam.mit_sailing.png"/></a>
  </td>

   <!-- description -->
  <td width=500><sup>
   Images from webcams located at the MIT Sailing Pavilion <br> Source: http://sailing.mit.edu/webcam.php
  <sup>
  </td>
 </tr>


 <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_finance.png>  Finance
  </sup>
  </td>
 </tr>


 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>

   <!-- namespace -->
  <td width=200><sup>
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_finance.png> finance.timeseries
  </sup>
  </td>

   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Finance_Time_Series.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.finance.timeseries.png"/></a>
  </td>

   <!-- description -->
  <td width=500><sup>
   Financial time series data retrieved using Alpha Vantage API. <br> Source: https://www.alphavantage.co/
   </sup>
  </td>
 </tr>



 <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>  Geoscience
  </sup>  
  </td>
 </tr>

  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200>
  <sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.era_interim 
  </sup> 
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_ERA_Interim.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.era_interim.png"/></a>  
  </td>
   
   <!-- description -->
  <td width=500><sup> 
   Era-Interim data at different pressure values from <br/> the European Centre for Medium-Range Weather Forecasts accessed through the University Corporation for Atmospheric Research. <br> Source: https://rda.ucar.edu/datasets/ds627.0/
  </sup> 
  </td>
 </tr>
  

 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.gldas 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63><a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_GLDAS.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.gldas.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500><img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> Land hydrology model produced by NASA. This version of the data is generated to match the GRACE temporal and spatial characteristics and is available as a complementary data product. <br> Source: https://grace.jpl.nasa.gov/data/get-data/land-water-content </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.grace 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_GRACE.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.grace.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> NASA GRACE Tellus Monthly Mass Grids. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness. <br> Source: https://grace.jpl.nasa.gov/data/get-data/monthly-mass-grids-land  </sup>
  </td>
 </tr>


 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.grace.mascon
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_GRACE_Mascon.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.grace.mascon.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> NASA GRACE Tellus Monthly Mass Grids - Global Mascons. 30-day measurements of changes in Earth’s gravity field to quantify equivalent water thickness. Source: https://grace.jpl.nasa.gov/data/get-data/jpl_global_mascons </sup>
  </td>
 </tr>


 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.groundwater </sup>
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Groundwater.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.groundwater.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_usgs.png" /> <sup> United States groundwater monitoring wells measuring the depth to water level. Source: https://waterservices.usgs.gov </sup>
  </td>
 </tr>
 

 <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png> geo.magnetometer
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Magnetometer.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.magnetometer.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_usgs.png" /> <sup> Data collected at magnetic observatories operated by the U.S. Geological Survey. Source: https://geomag.usgs.gov</sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.mahali.rinex
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Mahali_Rinex.ipynb"> <img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.rinex.png"/></a> 
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_mit.png" /> <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nsf.png" /> <sup> Rinex files from the MIT led NSF project studying the Earth’s ionosphere with GPS. <br> Web: http://mahali.mit.edu  </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.mahali.tec
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Mahali_TEC.ipynb"> <img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.tec.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_mit.png" /> <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nsf.png" /> <sup> Total Electron Content from the MIT led NSF project studying the Earth’s ionosphere with GPS. <br> Web:http://mahali.mit.edu  </sup> 
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png> geo.mahali.temperature 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Mahali_Temperature.ipynb"> <img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.mahali.temperature.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_mit.png" /> <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nsf.png" /> <sup> Temperature data from the MIT led NSF project studying the Earth’s ionosphere with GPS. <br>Web: http://mahali.mit.edu </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.modis 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_MODIS.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.modis.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> Spectroradiometer aboard the NASA Terra and Aqua image satellites. Generates approximately daily images of the Earth’s surface.<br> Source:https://modis.gsfc.nasa.gov </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.pbo 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
   <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_PBO.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.pbo.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_unavco.png" /> <sup> EarthScope - Plate Boundary Observatory (PBO): Daily GPS displacement time series measurements throughout the United States.<br>Source: http://www.unavco.org/projects/major-projects/pbo/pbo.html </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.sentinel_1
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Sentinel_1.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.sentinel_1.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <sup><img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_esa.png" /> Sentinel-1 TOPSAR data from the European Space Agency retrieved from the Alaska Satellite Facility.<br>Source:https://www.asf.alaska.edu/ </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.srtm 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_SRTM.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.srtm.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_usgs.png" /> <sup> Elevation data at a one arc second resolution from the Shuttle Radar Topography Mission (SRTMGL1).<br>Source: https://lpdaac.usgs.gov/dataset_discovery/measures/measures_products_table/srtmgl1_v003  </sup>
  </td>
 </tr>
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.uavsar 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_UAVSAR.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.uavsar.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> UAVSAR SLC data from JPL.<br>Source: https://uavsar.jpl.nasa.gov/   </sup>
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_geo.png>   geo.wyoming_sounding 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_Wyoming_Sounding.ipynb"><img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.geo.wyoming_sounding.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <sup> Sounding data from the University of Wyoming.<br>Source: http://weather.uwyo.edu/upperair/sounding.html </sup>
  </td>
 </tr>
 
 
  <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_planetary.png>  Planetary Science
  </sup>  
  </td>
 </tr>
 
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_planetary.png> planetary.ode
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_ODE.ipynb"> <img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.planetary.ode.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> Mars planetary data from PDS Geosciences Node's Orbital Data Explorer.<br>Source: http://pds-geosciences.wustl.edu/default.htm</sup>
  </td>
 </tr>
 
 
   <!--- HEADER ENTRY ---------------------------------->
 <tr>
  <td colspan=4><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_solar.png> Solar Science
  </sup>  
  </td>
 </tr>
 
  <!--- ENTRY ---------------------------------->
 <tr>
  <td width=2>
  <p><o:p>&nbsp;</o:p></p>
  </td>
  
   <!-- namespace -->
  <td width=200><sup> 
  <img src=https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_solar.png> solar.sdo 
  </sup>  
  </td>
  
   <!-- preview -->
  <td width=63>
  <a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/examples/Demo_SDO.ipynb"> <img alt="Preview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_skdaccess.solar.sdo.png"/></a>
  </td>
   
   <!-- description -->
  <td width=500>
   <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/icon_datasource_logo_nasa.png" /> <sup> Images from the Solar Dynamics Observatory.<br>Source: https://sdo.gsfc.nasa.gov/</sup>
  </td>
 </tr>
</table>



### Install
```python
pip install scikit-dataaccess
```

### Documentation

- User Manual: [/docs/skdaccess_manual.pdf](https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_manual.pdf)<br>
- Code documentation (Doxygen): [/docs/skdaccess_doxygen.pdf](https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_doxygen.pdf)
- Code visualization (treemap): [/docs/skdaccess_treemap.png](https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/skdaccess_treemap.png)
- Code class diagrams: [/docs/class_diagrams](https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/docs/class_diagrams)


### Contributors

Project lead: [Victor Pankratius (MIT)](http://www.victorpankratius.com)<br>
Contributors: Cody M. Rude, Justin D. Li, David M. Blair, Michael G. Gowanlock, Guillaume Rongier, Victor Pankratius

New contributors welcome! Contact <img src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess_cont.png" /> to contribute and add interface code for your own datasets :smile:

  
### Acknowledgements

We acknowledge support from NASA AIST14-NNX15AG84G, NASA AIST16-80NSSC17K0125, NSF ACI-1442997, and NSF AGS-1343967.

## Examples

Code examples (Jupyter notebooks) for all datasets listed above are available at: [/skdaccess/examples](https://github.com/MITHaystack/scikit-dataaccess/tree/master/skdaccess/examples)

<p align="center">
<a href="https://github.com/MITHaystack/scikit-dataaccess/blob/master/skdaccess/docs/images/skdaccess-quickexamples-combined.png">
  <img alt="Scikit Data Access Overview" src="https://github.com/MITHaystack/scikit-dataaccess/raw/master/skdaccess/docs/images/skdaccess-quickexamples-combined.png"/>
</a>
</p>
