# CityGML2OBJ 2.0
Command line converter of CityGML (.gml) to OBJ (.obj) files, while maintaining the semantics 

![Before-After](https://user-images.githubusercontent.com/44395224/235768949-747bd3c7-e347-45ab-9ae0-713065da90f3.png)


## Requirements
### Python packages:

+ [Numpy](http://docs.scipy.org/doc/numpy/user/install.html) 
+ [Triangle](http://dzhelil.info/triangle/)
+ [lxml](http://lxml.de)
+ [Shapely](https://github.com/Toblerity/Shapely)
+ [Decimal](https://docs.python.org/3/library/decimal.html)
  
Optional:

+ [Matplotlib](http://matplotlib.org/users/installing.html)

### Operating System:

The original project code has been developed on Mac OSX in Python 2.7. It has been adapted to python 3.10 and was successfully tested on a Windows 10 OS.

### CityGML Requirements:

#### Mandatory:

+ CityGML 1.0 or 2.0
+ Files must end with `.gml`, `.GML`, `.xml`, or `.XML`
+ Vertices in either `<gml:posList>` or `<gml:pos>`
+ Your files must be valid (see the next section)

<span style="color:red">The conversion tool does not work for CityGML 3.0 !</span>

You can check your CityGML files for validity for example with the [CityDoctor](https://www.citydoctor.eu/de/startseite.html) software.

#### Optional, but recommended:

+ `<gml:id>` for each `<bldg:Building>` and other types of city objects
+ `<gml:id>` for each `<gml:Polygon>`

## How to run?
In order to run the converter, the following run/debug configurations are required to run the program code:
<br></br>



  
  `-i  your-input-path-here` 
  
  `-o  your-output-path-here` 
  


Additional configurations have to be made in order to make use of the different optional features:
<br></br>

| Optional feature | specification | short explanation |
| -------- | -------- | -------- |
| Semanitcs Option|`-s 1`| create an individual OBJ file for each of the boundary surfaces |
| Geometry Validation | `-v 1`| validate the geometries and skip invalid ones |
| Object Preservation | `-g 1`| keep the names of the objects |
| Skip the triangulation | `-p 1`| preserve polygons in the OBJ file |
| Conversion of the resulting dataset into a local coordinate system | `-t 1`| convert the resulting dataset to a local system |
| Translation of the CityGML dataset into a local coordinate system pefore further processing, without saving the translation parameters|`-tC 1` `-tCw 1`| translate the CityGML dataset into a local CRS before processing | 

More detailed information on the optional features can be found in this [Wiki Page](https://github.com/tum-gis/citygml2obj-2.0/wiki/Optional-Functionalities)

## Limitations

Information on the limitations can be found in this [Wiki Page](https://github.com/tum-gis/citygml2obj-2.0/wiki/Limitations) 

## Credits
We are indebted to [Filip Biljecki](https://github.com/fbiljecki), [Hugo Ledoux](https://github.com/hugoledoux) and [Ravi Peters](https://github.com/Ylannl) from [TU Delft](https://github.com/tudelft3d) for their initial version of the CityGML2OBJs converter. The archived version of the repo can still be found here: https://github.com/tudelft3d/CityGML2OBJs
