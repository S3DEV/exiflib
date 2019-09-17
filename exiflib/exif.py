#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:App:       exiflib
:Purpose:   This installed library is designed to be a light-weight and
            easy to use wrapper for extracting meta data from an image.

            The GPS information is converted into latitude /longitude
            coordinates and the full extracted dataset is returned as a
            pandas Series.

:Version:   3.0.0
:Platform:  Linux/Windows | Python 3.5
:Developer: J Berendt
:Email:     support@s3dev.uk

:Attrib:    The latitude / longitude extraction and conversion code is
            a modified version of:

                * Programmer: Eran Sandler
                * Source:     https://gist.github.com/erans/983821

:Example:
    Example code use::

        from exiflib.exif import Exif
        data = Exif(image_path='/path/to/image.jpg').extract()

"""

import os
import pandas as pd
import utils3.utils as u
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class Exif():
    """Wrapper for extracting exif data from images.

    Args:
        image_path (str): Full file path to the image to be read.

    """

    def __init__(self, image_path):
        """Class initialiser."""
        self._img = image_path
        self._s_data = pd.Series()
        self._img_data = {}
        self._gps_data = {}
        self._exif_data = {}
        self._data = {}

    def extract(self) -> pd.Series:
        """Extract meta data from an image file.

        :Design:
            Using the ``PIL`` library, the image file's binary data is
            read and exif meta data extracted.  The exif data keys are
            mapped to their textual counterpart and added to a pandas
            Series; which is returned to the caller.

            For additional metadata extraction design and example,
            refer to the docstring for the
            :func:`~exif._extract_exif_data` function.

        Returns:
            If meta data was found, a pandas Series containing the
            extracted meta data is returned.  Otherwise, an empty
            Series is returned.

        """
        print('Extracting exif for: {}'.format(os.path.basename(self._img)))
        if u.fileexists(self._img):
            # Test if file is MOV (no exif data).
            self._test_for_mov()
            # Load image data.
            if not self._img_data:
                self._get_image_data()
            # Extract exif data.
            self._extract_exif_data()
            # Convert data to pandas Series.
            self._convert_to_series()
        return self._s_data

    @staticmethod
    def _convert_to_degrees(value):
        """Convert GPS values into decimal lat/lon coordinates.

        Args:
            value (tuple): A tuple containing data extracted from the
                'GPSLatitude' or 'GPSLongitude' GPS tags.

        The code in this method is modified from:

            * Programmer: Eran Sandler
            * Source:     https://gist.github.com/erans/983821

        """
        # Degrees
        deg0 = value[0][0]
        deg1 = value[0][1]
        deg  = float(deg0) / float(deg1)
        # Minutes
        mns0 = value[1][0]
        mns1 = value[1][1]
        mns  = float(mns0) / float(mns1)
        # Seconds
        sec0 = value[2][0]
        sec1 = value[2][1]
        sec  = float(sec0) / float(sec1)
        # Return calculation
        return deg + (mns / 60.0) + (sec / 3600.00)

    def _convert_to_series(self):
        """Convert data dictionaries to pandas Series."""
        # Test both datasets exist.
        if all([self._data, self._gps_data]):
            self._s_data = pd.concat([pd.Series(self._data),
                                      pd.Series(self._gps_data)])
        else:
            # Convert simple data to Series, without GPS data.
            self._s_data = pd.Series(self._data)

    def _extract_exif_data(self):
        """Extract exif data from an image.

        :Example Data:
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

        """
        try:
            # Decode tag ids to tag name.  Build a new data dict.
            for k, v in self._img_data.items():
                self._data[TAGS.get(k)] = v
            # Remove any `None` keys.
            if None in self._data.keys():
                self._data.pop(None)
            self._data['Fullpath'] = self._img
            self._data['Filename'] = os.path.basename(self._img)
            # Test for GPS data.
            if 'GPSInfo' in self._data:
                # Decode GPS tag ids to tag name.  Build new data dict.
                for k, v in self._data['GPSInfo'].items():
                    self._gps_data[GPSTAGS.get(k)] = v
                # Convert latitude / longitude data.
                self._get_lat_lon()
        except Exception as err:
            # Print error.
            print('ERR: {}'.format(err))
            print('Process continuing for: {}'.format(os.path.basename(self._img)))
            # Add filename to results.
            self._data['Fullpath'] = self._img
            self._data['Filename'] = os.path.basename(self._img)

    def _get_image_data(self):
        """Use the ``PIL.Image`` library to extract exif metadata."""
        try:
            self._img_data = Image.open(self._img)._getexif()
        except Exception:
            print('Cannot retrieve exif data from {}'.format(self._img))

    def _get_lat_lon(self):
        """Extract lat/lon values from GPSInfo dictionary.

        The code in this method is modified from:

            * Programmer: Eran Sandler
            * Source:     https://gist.github.com/erans/983821

        """
        lat = 0
        lon = 0
        lat_val = self._gps_data.get('GPSLatitude')
        lon_val = self._gps_data.get('GPSLongitude')
        lat_ref = self._gps_data.get('GPSLatitudeRef')
        lon_ref = self._gps_data.get('GPSLongitudeRef')
        # Test for all parts.
        if all([lat_val, lon_val, lat_ref, lon_ref]):
            # Convert to decimal.
            lat = self._convert_to_degrees(value=lat_val)
            lon = self._convert_to_degrees(value=lon_val)
            # Determine N/S/E/W
            if lat_ref != 'N': lat = (-1 * lat)
            if lon_ref != 'E': lon = (-1 * lon)
        self._gps_data['Latitude'] = lat
        self._gps_data['Longitude'] = lon

    def _test_for_mov(self):
        """Test if the file is an MOV file.

        :Design:
            If the file is an MOV file, populate the data dictionary
            with default values.  (i.e.: Filename and full file path)

        """
        if os.path.splitext(self._img)[1].lower() == '.mov':
            # Populate default values.
            self._img_data = {'Fullpath': self._img,
                              'Filename': os.path.basename(self._img)}
            self._gps_data = {'default': None}
