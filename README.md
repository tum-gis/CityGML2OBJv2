# :cityscape: CityGML2OBJ 2.0 :cityscape:
Command line converter of **CityGML (.gml)** to **OBJ (.obj)** files, while maintaining the semantics 

![](https://github.com/tum-gis/CityGML2OBJv2/blob/main/citygmltoobj2small.gif)

## :arrow_forward: How to run?
The `CityGML2OBJs.py` represents the starting point of the code, choose this file when configuring the runtime and pass the following parameters:

  `-i  your-input-citygml-path-here` 
  
  `-o  your-output-obj-path-here` 

Please make sure to use the absolute paths to the respective directories.

and Bob's your uncle! :construction_worker:

### :wrench: Optional features

| Optional feature | specification |
| -------- | -------- |
| Semanitcs Option|`-s 1`|
| Geometry Validation | `-v 1`|
| Object Preservation | `-g 1`|
| Skip the triangulation | `-p 1`|
| Conversion of the resulting dataset into a local coordinate system | `-t 1`|
| Translation of the CityGML dataset into a local coordinate system before further processing, without saving the translation parameters|`-tC 1`|
| Translation of the CityGML dataset into a local coordinate system before further processing, with saving the translation parameters to a designated .txt file|`-tCw 1`|


## :page_with_curl: Requirements

### Python packages:

+ [Numpy](http://docs.scipy.org/doc/numpy/user/install.html) 
+ [Triangle](http://dzhelil.info/triangle/)
+ [lxml](http://lxml.de)
+ [Shapely](https://github.com/Toblerity/Shapely)
+ [Decimal](https://docs.python.org/3/library/decimal.html)
  
#### Optional:

+ [Matplotlib](http://matplotlib.org/users/installing.html)

### Tested:

Using Python 3.10 and Windows 10 OS

### CityGML Requirements:

#### Mandatory:

+ CityGML 1.0 or 2.0
+ Files must end with `.gml`, `.GML`, `.xml`, or `.XML`
+ Vertices in either `<gml:posList>` or `<gml:pos>`
+ Your files must be valid (e.g., free check with [CityDoctor](https://www.citydoctor.eu/de/startseite.html))

#### Optional, but recommended:

+ `<gml:id>` for each `<bldg:Building>` and other types of city objects
+ `<gml:id>` for each `<gml:Polygon>`

 
## Limitations

Information on the limitations can be found in this [Wiki Page](https://github.com/tum-gis/citygml2obj-2.0/wiki/Limitations) 

## :handshake: Credits
We are indebted to [Filip Biljecki](https://github.com/fbiljecki), [Hugo Ledoux](https://github.com/hugoledoux) and [Ravi Peters](https://github.com/Ylannl) from [TU Delft](https://github.com/tudelft3d) for their initial version of the CityGML2OBJs converter. The archived version of the repo can still be found here: https://github.com/tudelft3d/CityGML2OBJs; the paper: 

Biljecki, F., & Arroyo Ohori, K. (2015). Automatic semantic-preserving conversion between OBJ and CityGML. Eurographics Workshop on Urban Data Modelling and Visualisation 2015, pp. 25-30.

[[PDF]](http://filipbiljecki.com/publications/Biljecki2015vk.pdf) [[DOI]](http://doi.org/10.2312/udmv.20151345)

## :mailbox: Contact & Feedback

Feel free to open a discussion under Issues or write us an email

- [Thomas Froech](thomas.froech@tum.de)
- [Benedikt Schwab](benedikt.schwab@tum.de) 
- [Olaf Wysocki](olaf.wysocki@tum.de)
