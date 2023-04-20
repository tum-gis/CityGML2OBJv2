# CityGML2OBJ 2.0
Command line converter of CityGML (.gml) to OBJ (.obj) files, while maintaining the semantics 

## Features
This conversion tool provides several additional optional functionalities:

| Optional feature | Explanation |
| -------- | -------- |
| Semanitcs Option| This option will create an individual OBJ file for each of the boundary surfaces. (e.g. `RoofSurface`, `WallSurface` and `GroundSurface`) |
| Geometry Validation | This option can be used in order to validate the geometries and skip invalid ones. Invalid geometries will be reported with their respective `<gml:id>`.|
| Object Preservation | For the object option the name of the object will be derived from the `<gml:id>`, if not, an ordered list will be made starting from 1, and each object will be named as an integer from 1 to *n*, where *n* is the number of objects. |
| Skip the triangulation | OBJ supports polygons, but most software packages prefer triangles. Hence the polygons are triangulated by default (another reason is that OBJ doesn't support polys with holes). However, this may cause problems in some instances, or you might prefer to preserve polygons. Sometimes it also helps to bypass invalid geometries in CityGML data sets. |
| Conversion of the resulting dataset into a local coordinate system | Normally CityGML data sets are geo-referenced. This may be a problem for some software packages. This option can be used in order to convert the data set to a local system. The origin of the local system correspond to the point with the smallest coordinates (usually the one closest to south-west). this conversion takes place after theprocessing and only affects the vertices in the OBJ file. |
| Translation of the CityGML dataset into a local coordinate system pefore further processing |Invoke this option in order to translate the CityGML File into a local coordinate system before performing the conversion to OBJ. The translated dataset is saved as a new GML file in the output directory as well. Optionally, the translation parameters can be saved into a designated .txt file. The translation parameters are determined from the envelopes specified in the GML document. Therefore, the translation only takes place in the horizontal directions, a height translation is not applied automatically. It is possible to apply a height translation manually by inserting the height correction in the `CityGML2OBJs` file in line 420 or 424. This functionality is also able to perform the translation of objets that are defined using implicite geometry (e.g vegetation objeczs)|

Without any of these options invoked, a simple straightforward conversion from CityGML to OBJ will be performed.

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

*<span style="color:red">The conversion tool does not work for CityGML 3.0 !</span>*

You can check your CityGML files for validity for example with the [CityDoctor](https://www.citydoctor.eu/de/startseite.html) software.

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

## Known Limitations

* Some polygon normals sometimes get inverted. Usually a (wrong) normal is preserved from the data set, but in rare instances a bug may cause a correct normal to be inverted (and the other way around--in that case it's a feature!).
* Non-building thematic classes are not supported in the semantic sense (they will be converted together as `Other` class). However, all geometry will be converted to the plain OBJ regardless of the theme, when the corresponding option is invoked).
* The texture from the CityGML is not converted to OBJ (future work).
* The tool supports only single-LOD files. If you load a multi-LOD file, you'll get their union.
* If the converter crashes, it's probably because your CityGML files contain invalid geometries. Run the code with the `-v 1` flag to validate and skip the invalid geometries. If that doesn't work, try to invoke the option `-p 1`. If that fails too, please report the error.
* `XLink` is not supported, nor will be because for most files it will result in duplicate geometry. 
* The tool does not support non-convex polygons in the interior, for which might happen that the centroid of a hole is outside the hole, messing up the triangulation.
* Skipping triangulation does not work with polygons with holes.
* Skipping the triangulation will cause incorrect representation of non-convex polygons
* For some datasets, there will be geometric distortions (image below) These geometric distortions usually disappear when the dataset is translated into a local   coordinate systemwith FME. This problem was the main motivation to extend the existing code by the translation functionality. Unfortunately, this translation does not solve the issue. Apparently, the error mainly appears for CityGML Datasets that are published by the LDBV.




## Credits
We are indebted to [Filip Biljecki](https://github.com/fbiljecki), [Hugo Ledoux](https://github.com/hugoledoux) and [Ravi Peters](https://github.com/Ylannl) from [TU Delft](https://github.com/tudelft3d) for their initial version of the CityGML2OBJs converter. The archived version of the repo can still be found here: https://github.com/tudelft3d/CityGML2OBJs
