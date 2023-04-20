# CityGML2OBJ 2.0
Command line converter of CityGML (.gml) to OBJ (.obj) files, while maintaining the semantics 

## Features
...

## Requirements
### Python packages:

+ [Numpy](http://docs.scipy.org/doc/numpy/user/install.html) 
+ [Triangle](http://dzhelil.info/triangle/). 
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

*<span style="color:red">The conversion tool does not work for CityGML 3.0 !</span>*

#### Optional, but recommended:

+ `<gml:id>` for each `<bldg:Building>` and other types of city objects
+ `<gml:id>` for each `<gml:Polygon>`

## How to run?
In order to run the converter, the following run/debug configurations are required to run the program code:
<br></br>
<ul>
  <li>Specification of the input path:    `-i "your input-path here"` </li>
  <li>Specification of the output path:   `-o "your output-path here"` </li>
</ul>
<br></br>
Additional configurations have to be made in order to make use of the different optional features:
<br></br>

| Optional feature | specification |
| -------- | -------- |
| Semanitcs Option|`-s 1`|
| Geometry Validation | `-v 1`|
| Object Preservation | `-g 1`|
| Skip the triangulation | `-p 1`|
| Conversion of the resulting dataset into a local coordinate system | `-t 1`|
| Translation of the CityGML dataset into a local coordinate system pefore further processing, without saving the translation parameters|`-tC 1`|
| Translation of the CityGML dataset into a local coordinate system pefore further processing, with saving the translation parameters to a designated .txt file|`-tCw 1`|

## Credits
We are indebted to [Filip Biljecki](https://github.com/fbiljecki), [Hugo Ledoux](https://github.com/hugoledoux) and [Ravi Peters](https://github.com/Ylannl) from [TU Delft](https://github.com/tudelft3d) for their initial version of the CityGML2OBJs converter. The archived version of the repo can still be found here: https://github.com/tudelft3d/CityGML2OBJs
