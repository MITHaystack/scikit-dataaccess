# Scikit Data Access

Advantages of skdacces
- API to import a data generator + function to get next data chunk (configurable)
- Eliminates the need to create parsers for each data set and simplifies the construction of scientific data processing pipelines.
- Enables studies involving data fusion and cross-comparisons from several sources.
- Skip parser development, dealing with physical file formats, etc.
- Can be used to download data locally or to a cloud node (e.g., Amazon Cloud). This feature simplifies distributing entire data sets or partitions of data to the cloud, and enables parallel processing in cloud computing environments.
- Easy expansion for more data sets in the future
- Skdaccess code is open source (MIT License)

The package introduces a common namespace and currently supports the following data sets:
- Light curves from *Kepler*
- Water depth from wells in California obtained from the USGS
- GPS time series data from the UNAVACO Plate Boundary
- Grace Tellus Monthly Mass Grids from JPL

### Install

pip install scikit-dataaccess


### Documentation

See <https://github.com/skdaccess/skdaccess/tree/master/skdaccess/docs>
