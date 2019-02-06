#!/usr/bin/env python
"""------------------------------------------------------------------------------------------------
Program:    exif.py
Version:    2.0.2
Py Ver:     3.5
Purpose:    This program is designed to extract the EXIF metadata from an image, convert the GPS
            information into latitude / longitude coordinates and output the results as a pandas
            Series.

Attrib:     Latitude / longitude extraction and conversion code modified from:
            Programmer: Eran Sandler
            Source:     https://gist.github.com/erans/983821

Use:
            > from exiflib import exif
            > data = exif.extract_exif_data(filename='/path/to/image.jpg')

----------------------------------------------------------------------------------------------------
UPDATE LOG:
Date        Programmer      Version     Update
16.01.18    J. Berendt      2.0.0       Near complete code re-write.  Heavily modified and
                                        simplified original code.
                                        Previous update comments removed as they are no longer
                                        applicable.
                                        Results are now returned as a pandas Series, rather than
                                        as nested dictionaries.
                                        Updated code formatting per PEP8.
                                        Updated code formatting per PEP257.
                                        pylint (10/10)
22.01.18    J. Berendt      2.0.1       Updated to return a blank pandas Series if no exif data
                                        was retrieved.
                                        If no exif data is retrieved, the filename and full path
                                        values are returned in the Series.
06.02.19    J. Berendt      2.0.2       Converted from local package lib to installed package.
------------------------------------------------------------------------------------------------"""

# TODO: Better PEP8 conformance (line lengths / docstrings).
# TODO: New Sphinx-style docstrings.
# TODO: Convert to class?

import os
import pandas as pd
import utils3.utils as u
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


# ----------------------------------------------------------------------
def extract_exif_data(filename):
    """
    Control the process flow through the extraction process.

    DESIGN:
    Using the PIL library, the image file's binary data is read and
    exif data extracted.  The exif data keys are then mapped to their
    textual counterpart and added to a pandas Series; which is returned
    to the caller.

    For additional metadata extraction design and example, refer to the
    docstring for the _extract_exif_data() function.

    USE:
    > from exiflib import exif
    > data = exif.extract_exif_data(filename='/path/to/image.jpg')
    """

    # PANDAS SERIES IS NOT REFACTORED
    # pylint: disable=redefined-variable-type

    # INITIALISE
    data     = None
    gps_data = None
    img_data = None
    results  = None

    # NOTIFICATION
    print('Extracting exif for: %s' % os.path.basename(filename))

    # TEST IF IMAGE FILE EXISTS
    if u.fileexists(filename):
        # TEST IF FILE IS MOV (NO EXIF DATA)
        img_data, gps_data = _test_for_mov(filename=filename)

        # LOAD IMAGE DATA
        if not img_data:
            img_data = _get_image_data(filename=filename)

        # EXTRACT EXIF DATA
        data, gps_data = _extract_exif_data(img_data=img_data, filename=filename)

        if all([data, gps_data]):
            # CONVERT DATA TO PANDAS SERIES
            results = _convert_to_series(data=data, gps_data=gps_data)
        else:
            results = pd.Series(data)

        return results


# ----------------------------------------------------------------------
def _convert_to_degrees(value):
    """
    Convert gps information dictionary into decimal latitude and
    longitude coordinates.

    Code attribution:
    Programmer: Eran Sandler
    Source:     https://gist.github.com/erans/983821
    """

    # DEGREES
    deg0 = value[0][0]
    deg1 = value[0][1]
    deg  = float(deg0) / float(deg1)

    # MINUTES
    mns0 = value[1][0]
    mns1 = value[1][1]
    mns  = float(mns0) / float(mns1)

    # SECONDS
    sec0 = value[2][0]
    sec1 = value[2][1]
    sec  = float(sec0) / float(sec1)

    # RETURN CALCULATION
    return deg + (mns / 60.0) + (sec / 3600.00)


# ----------------------------------------------------------------------
def _convert_to_series(data, gps_data):
    """Convert data dictionaries to pandas Series."""

    return pd.concat([pd.Series(data), pd.Series(gps_data)])


# ----------------------------------------------------------------------
def _extract_exif_data(img_data, filename):
    """
    SUMMARY:
    Extract exif data from an image.  Return results as pandas Series.

    EXAMPLE:
    ApertureValue               (7983, 3509)
    BrightnessValue             (5099, 1324)
    ColorSpace                  1
    ComponentsConfiguration
    DateTime                    2017:05:20 19:11:53
    DateTimeDigitized           2017:05:20 19:11:53
    DateTimeOriginal            2017:05:20 19:11:53
    ...
    ResolutionUnit              2
    SceneCaptureType            0
    SceneType
    SensingMethod               2
    ShutterSpeedValue           (2297, 454)
    ...
    GPSLatitude                 ((r, e), (m, o), (v, ed))
    GPSLatitudeRef              N
    GPSLongitude                ((r, e), (m, o), (v, ed))
    GPSLongitudeRef             W
    GPSSpeed                    (0, 1)
    GPSSpeedRef                 K
    Latitude                    nn.nnnnnnnn
    Longitude                   nn.nnnnnnnn
    ...

    USE:
    > from exif import extract_exif_data
    > data = extract_exif_data(filename='/path/to/image.jpg')
    """

    # INITIALISE VARIABLES
    data = dict()
    gps_data = dict()

    try:

        # DECODE TAG IDS TO TAG NAME >> BUILD NEW DATA DICT
        for k, v in img_data.items(): data[TAGS.get(k)] = v

        # REMOVE ANY NONETYPE KEYS
        if None in data.keys(): data.pop(None)

        # ADD FILE VALUES TO DICTIONARY
        data['Fullpath'] = filename
        data['Filename'] = os.path.basename(filename)

        # TEST FOR GPS DATA
        if 'GPSInfo' in data:
            # DECODE GPS TAG IDS TO TAG NAME >> BUILD NEW DATA DICT
            for k, v in data['GPSInfo'].items(): gps_data[GPSTAGS.get(k)] = v
            # GET LAT/LON FOR GPS DATA
            lat_lon = _get_lat_lon(gps_data=gps_data)
            # ADD PURE LAT/LON VALUES TO DICTIONARY
            gps_data['Latitude'] = lat_lon[0]
            gps_data['Longitude'] = lat_lon[1]

    except Exception as err:
        # PRINT ERROR
        print('ERR: %s' % (err))
        print('Process continuing for: %s' % (os.path.basename(filename)))
        # ADD FILENAME TO RESULTS
        data['Fullpath'] = filename
        data['Filename'] = os.path.basename(filename)

    return data, gps_data


# ----------------------------------------------------------------------
def _get_image_data(filename):
    """Use the PIL library to extract image and exif metadata."""

    img_data = {}

    # GET DATA FROM IMAGE
    try:
        img_data = Image.open(filename)._getexif()
    except:
        print('Cannot retrieve exif data from %s' % (filename))

    return img_data


# ----------------------------------------------------------------------
def _get_lat_lon(gps_data):
    """
    Extract latitude and longitude values from GPSInfo dictionary.

    Original code attribution:
    Programmer: Eran Sandler
    Source:     https://gist.github.com/erans/983821
    """

    # EXTRACT LAT / LON VALUES
    lat_val = gps_data.get('GPSLatitude')
    lon_val = gps_data.get('GPSLongitude')
    lat_ref = gps_data.get('GPSLatitudeRef')
    lon_ref = gps_data.get('GPSLongitudeRef')

    # TEST FOR ALL PARTS
    if all([lat_val, lon_val, lat_ref, lon_ref]):
        # CONVERT TO DECIMAL
        lat = _convert_to_degrees(value=lat_val)
        lon = _convert_to_degrees(value=lon_val)

        # DETERMINE N/S/E/W
        if lat_ref != 'N': lat = (0 - lat)
        if lon_ref != 'E': lon = (0 - lon)

    # RETURN VALUE
    return lat, lon


# ----------------------------------------------------------------------
def _test_for_mov(filename):
    """
    Test if the file is an MOV file.

    DESIGN:
    If the file is an MOV file, populate the data dictionary with
    default values - i.e.: filename and full file path.

    Otherwise, return a None type, so the data dictionary can be
    populated with exif data.
    """

    # TEST IF .MOV FILE (NO EXIF DATA)
    if os.path.splitext(filename)[1].lower() == '.mov':
        # POPULATE DEFAULT VALUES
        data = dict(Fullpath=filename,
                    Filename=os.path.basename(filename))
        gps_data = dict(default=None)

    else:
        data = None
        gps_data = None

    return data, gps_data
