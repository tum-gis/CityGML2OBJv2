# CityGML2OBJ 2.0
Command line converter of CityGML (.gml) to OBJ (.obj) files, while maintaining the semantics 

## Features
...

## Requirements
...

## How to run?
In order to run the converter, the following run/debug configurations are required to run the program code:
<br></br>
<ul>
  <li>Specification of the input path:    `-i "your input-path here"`</li>
  <li>Specification of the output path:   `-o "your output-path here"`</li>
</ul>
<br></br>
Additional configurations ave to be mde in order to make use of the optional features:
<br></br>
| Optional feature | specification |
| -------- | -------- |
| Semanitcs Option|`-s 1`|
| Geometry Validation | `-v 1`|
| Object Preservation | `-g 1`|
| Skip the triangulation | `-p 1`|
| Conversion of the resulting dataset into a local coordinate system | `-t 1`|
| Translation of the CityGML dataset into a local coordinate system pefore further processing, without saving the translation parameters|`-tC 1`|
| Translation of the CityGML dataset into a local coordinate system pefore further processing, with saving the translation parameters to a designated .txt file|`-tCw1`|

## Credits
We are indebted to [Filip Biljecki](https://github.com/fbiljecki), [Hugo Ledoux](https://github.com/hugoledoux) and [Ravi Peters](https://github.com/Ylannl) from [TU Delft](https://github.com/tudelft3d) for their initial version of the CityGML2OBJs converter. The archived version of the repo can still be found here: https://github.com/tudelft3d/CityGML2OBJs
