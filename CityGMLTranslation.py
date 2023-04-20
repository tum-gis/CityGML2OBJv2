##!/usr/bin/python
# -*- coding: utf-8 -*-

# The MIT License (MIT)

# This code is part of the CityGML2OBJs package

# Copyright (c) 2023
# Thomas Fröch
# Technische Universität München (TUM)
# thomas.froech@tum.de

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import markup3dmodule as m3dm
from decimal import Decimal, getcontext
import numpy as np

# Setting the precision of Decimal
getcontext().prec = 28


# Todo: This function works, but it does not deliver the desired results.
def performStableAddition(number1, number2):
    # Input: string number1, string number 2, output: string sum
    # Determine the number of positions after the comma.
    # print("Number 1 totally before: ", number1)
    # print("Number 2 totally before: ", number2)

    try:
        n_after_comma_number1 = len(number1.split(".")[1])
    except:
        n_after_comma_number1 = 0
    try:
        n_after_comma_number2 = len(number2.split(".")[1])
    except:
        n_after_comma_number2 = 0
    lengths = [n_after_comma_number1, n_after_comma_number2]

    # convert float numbers into integers by removing the comma
    # print("Number 1 before all: ", number1)
    # print("Number 2 before all: ", number2)
    number1 = number1.replace(".", "")
    number2 = number2.replace(".", "")

    # print("Number 1 after: ", number1)
    # print("Number 2 after: ", number2)

    # find the number with more positions after the comma
    abs_lengths = np.abs(lengths)  # Erstellen eines Arrays mit den Beträgen
    max_index = np.argmax(abs_lengths)

    # Distinguish the two different cases
    # Case 1: number one has more positions after the comma than number two
    if max_index == 0:
        # Find the difference of positions after the comma
        n_positions_difference = (lengths[0] - lengths[1])
        # print("n_positions_difference: ", n_positions_difference)
        # Fill up the missing digits of number 2 with zeros
        # print("number2 before: ", number2)
        for i in range(n_positions_difference):
            number2 = number2 + "0"
        # print("number2_after", number2)
        # print("Number1: ", number1)
        # convert both stings into integers
        number1_int = np.double(number1)
        number2_int = np.double(number2)

        # Add both numbers
        number_sum = number1_int + number2_int

        # convert back into string
        format_string = "{:.0f}"
        number_sum_string = format_string.format(number_sum)

        # Insert the comma at the correct position
        length_of_number = len(number_sum_string.replace("-",
                                                         ""))
        if length_of_number >= lengths[max_index]:
            if n_after_comma_number1 != 0:
                number_sum_string = number_sum_string[:-(lengths[0])] + "." + number_sum_string[-(lengths[0]):]
                print("Number sum string 1: ", number_sum_string)
                return number_sum_string
            else:
                number_sum_string = number_sum_string
                print("Number sum string 3: ", number_sum_string)
                return number_sum_string
        elif length_of_number < n_after_comma_number1:
            new_string = ""
            for i in range(len(number_sum_string)):
                if number_sum_string[i] == "-":
                    new_string += "0."
                else:
                    new_string += number_sum_string[i]
            number_sum_string = new_string
            print("Number sum string 4: ", number_sum_string)
            return number_sum_string
        else:
            number_sum_string = number_sum_string
            print("Number sum string 5: ", number_sum_string)
            return number_sum_string

    # Case 2: number two has more positions after the comma than number one
    else:
        # find the difference of positions after the comma
        n_positions_difference = lengths[1] - lengths[0]

        # Fill up the missing digits of number 2 with zeros
        for i in range(n_positions_difference):
            number1 = number1 + "0"

        # convert both stings into integers
        number1_int = Decimal(number1)
        number2_int = Decimal(number2)

        # Add both numbers
        number_sum = number1_int + number2_int

        # convert back into string
        format_string = "{:.0f}"
        number_sum_string = format_string.format(number_sum)

        # Insert the comma at the correct position
        length_of_number = len(number_sum_string.replace("-",
                                                         ""))  # Todo: diese funcktion muss auch noch bei der anderen Falluntrscheidun einf´gefügt werden!
        if length_of_number > n_after_comma_number2:
            if n_after_comma_number2 != 0:

                number_sum_string = number_sum_string[:-(lengths[1])] + "." + number_sum_string[-(lengths[1]):]
                print("Number sum string 6: ", number_sum_string)
                return number_sum_string

            else:
                number_sum_string = number_sum_string
                print("Number sum string 8: ", number_sum_string)
                return number_sum_string

        elif length_of_number < n_after_comma_number2:
            new_string = ""
            for i in range(len(number_sum_string)):
                if number_sum_string[i] == "-":
                    new_string += "0."
                else:
                    new_string += number_sum_string[i]
            number_sum_string = new_string
            print("Number sum string 9: ", number_sum_string)
            return number_sum_string
        else:
            number_sum_string = number_sum_string
            print("Number sum string 10: ", number_sum_string)
            return number_sum_string


# This function is used in order to extract all the envelopes from the CityGML-File
# These envelopes are going to be used in order to determine the translation parameters later
def getEnvelopes(root, ns_bldg, ns_gml, ns_citygml):
    envelopes = []
    for envelope in root.getiterator('{%s}Envelope' % ns_gml):
        envelopes.append(envelope)
    return envelopes


# This function is used in order to calculate the translation parameters from the
# envelopes that were previously extracted from the envelopes
def getTranslationParameters(envelopes, ns_gml):
    # Setting up some initial values
    dx = Decimal("0")
    dy = Decimal("0")
    lowerCorner = []
    upperCorner = []

    # Iterating through all the envelopes in the CityGML-File
    for envelope in envelopes:
        # print(" Envelope: ", envelope)
        # Finding the upper and the lower corner
        for child in envelope.getchildren():
            if child.tag == '{%s}lowerCorner' % ns_gml:
                lowerCorner.append(child.text)
            elif child.tag == '{%s}upperCorner' % ns_gml:
                upperCorner.append(child.text)
    # Converting into Decimal
    pointCounter = 0
    for point in lowerCorner:
        dy = dy + (Decimal(point.split(" ")[0]))
        dx = dx + (Decimal(point.split(" ")[1]))
        pointCounter = pointCounter + 1

    dyret = -dy / pointCounter
    dxret = -dx / pointCounter

    return [Decimal(str(int(dxret))), Decimal(str(int(dyret)))]


# This function is used to Parse the text from the CityGML file to Decimal numbers and
# to aplly the previously calculated translation parameters
# Notice: this code only allows ONE "gml:PosList-Element" for each Interior and exterior of a Polygon
# If there are more than just one,just the first one is going to be transformed
def splitAndApplyTrafo(coordString, transParam):
    # Splitting the coordinate string by empty spaces
    split = coordString.split(" ")
    # Apply the Trafo # Todo: Check for redundant code!
    counter = 0
    length = int(len(split))
    length_new = int(length / 3)
    for i in range(length_new):
        # split[counter] = (Decimal(split[counter])) + transParam[1]
        # split[counter + 1] = (Decimal(split[counter + 1])) + transParam[0]
        # split[counter + 2] = (Decimal(split[counter + 2])) - transParam[2]
        #
        # Todo: Dies ist nur ein test der neuen eventuell besser funtionierenden addition
        print("y")
        split[counter] = performStableAddition(split[counter], str(transParam[1]))
        print("x")
        split[counter + 1] = performStableAddition(split[counter + 1], str(transParam[0]))
        print("z")
        split[counter + 2] = performStableAddition(split[counter + 2], str(transParam[2]))

        counter += 3
    # converting back to a string
    translated = ""
    for i in split:
        if len(translated) == 0:
            translated = str(i)
        else:
            translated = translated + " " + str(i)
    return translated


# This code is used in order to find all the coordinates that are defined in the CityGML-File
# Please Notice: the search for coordinates here has the same limitations as the search for coordinates that
# is used in the "CityGML2OBJ" functionality!
def appyTranslationToCityGML(CITYGML, root, transParam, ns_citygml, ns_gml, ns_frn, ns_veg, filename):
    # Iterate over all the cityObjectMembers
    for obj in root.getiterator('{%s}cityObjectMember' % ns_citygml):
        # Iterate over all the children of cityObject Member
        for child in obj.getchildren():
            # Exclude all the implicitly referenced objects from the transformation
            if child.findall(
                    './/{%s}ImplicitGeometry' % ns_citygml) == []:
                polys = m3dm.polygonFinder(child)
                # Iterate over all the polygons of the children of cityObjectMember
                for poly in polys:
                    # decompose all the polygons in the interior and exterior rings
                    exter, inter = m3dm.polydecomposer(poly)
                    # iterate over all the exterior rings
                    for e in exter:
                        # find all the coordinates that are stored as a "posList"
                        if len(e.findall('.//{%s}posList' % ns_gml)) > 0:
                            points = e.findall('.//{%s}posList' % ns_gml)[0].text
                            translated = splitAndApplyTrafo(points, transParam)
                            # print("Before: ", e.findall('.//{%s}posList' % ns_gml)[0].text)
                            e.findall('.//{%s}posList' % ns_gml)[0].text = translated
                            # print("Result: ", e.findall('.//{%s}posList' % ns_gml)[0].text)
                        # find all the coordinates that are stored as "pos"
                        elif len(e.findall('.//{%s}pos' % ns_gml)) > 0:
                            points = e.findall('.//{%s}pos' % ns_gml)
                            counter = 0
                            for k in points:
                                translated = splitAndApplyTrafo(k.text, transParam)
                                e.findall('.//{%s}pos' % ns_gml)[counter].text = translated
                                counter = counter + 1
                    # iterate over all the interior rings
                    for i in inter:
                        # find all the coordinates that are stored as a "posList"
                        if len(i.findall('.//{%s}posList' % ns_gml)) > 0:
                            points = i.findall('.//{%s}posList' % ns_gml)[0].text
                            translated = splitAndApplyTrafo(points, transParam)
                            i.findall('.//{%s}posList' % ns_gml)[0].text = translated
                        # find all the coordinates that are stored as "pos"
                        elif len(i.findall('.//{%s}pos' % ns_gml)) > 0:
                            points = i.findall('.//{%s}pos' % ns_gml)
                            counter = 0
                            for k in points:
                                translated = splitAndApplyTrafo(k.text, transParam)
                                i.findall('.//{%s}pos' % ns_gml)[counter].text = translated
                                counter = counter + 1

            else:  # This condition is used in order to transform the reference points of the implicitly defined geometries
                # Step 1: find all the reference points:
                referencePoints = child.findall('.//{%s}referencePoint' % ns_citygml)
                for referencePoint in referencePoints:
                    points = referencePoint.findall('.//{%s}pos' % ns_gml)
                    counter = 0
                    for l in points:
                        translated = splitAndApplyTrafo(l.text, transParam)
                        referencePoint.findall('.//{%s}pos' % ns_gml)[counter].text = translated
                        counter = counter + 1

    # Iterate over all the envelopes
    for envelope in root.getiterator('{%s}Envelope' % ns_gml):
        lowerCorner = envelope.findall('.//{%s}lowerCorner' % ns_gml)[0].text
        upperCorner = envelope.findall('.//{%s}upperCorner' % ns_gml)[0].text
        translatedLowerCorner = splitAndApplyTrafo(lowerCorner, transParam)
        translatedUpperCorner = splitAndApplyTrafo(upperCorner, transParam)
        envelope.findall('.//{%s}lowerCorner' % ns_gml)[0].text = translatedLowerCorner
        envelope.findall('.//{%s}upperCorner' % ns_gml)[0].text = translatedUpperCorner

    CITYGML.write(filename + "_local_" + ".gml")
    return root


# This function is used in order to write the previously calculated translation parameters to a
# designated .txt file. The use of this functionality is optional and can be activated by setting the
# optional "write2file" parameter to "True" when calling the "translateToLocalCRS" - function.
def writeTransparam2File(filename, directory, transParam):
    textfileName = directory + filename + "_Translation_Parameters.txt"
    f = open(textfileName, "w")
    f.write("This file contains the translation parameters that were applied to the original CityGML file." + "\n" +
            "Conversion tool developed by Filip Biljecki, TU Delft <fbiljecki@gmail.com>" + "\n" +
            "Conversion tool extended by Thomas Fröch, TUM <thomas.froech@tum.de>" + "\n" +
            "see more at Github:" + "\n" +
            "https://github.com/tudelft3d/CityGML2OBJs" + "\n" + "\n")
    key = ['y', 'x', 'z']
    for i in range(len(transParam)):
        f.write(key[i] + ': ' + str(transParam[i]) + '  ')
    f.close()
    print("Translation parameters written to: " + textfileName)
    return 0

def translateToLocalCRS(CITYGML, file, root, ns_bldg, ns_gml, ns_citygml, ns_frn, ns_veg, directory, write2file=False,
                        applyHeight=Decimal("0")):
    envelopes = getEnvelopes(root, ns_bldg, ns_gml, ns_citygml)
    transParam = getTranslationParameters(envelopes, ns_gml)
    transParam.append(applyHeight)
    if write2file == True:
        writeTransparam2File(file, directory, transParam)
    appyTranslationToCityGML(CITYGML, root, transParam, ns_citygml, ns_gml, ns_frn, ns_veg, file)
    return 0
