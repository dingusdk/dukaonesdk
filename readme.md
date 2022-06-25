# Introduction

This is a Python module for making a connection to a Duka One S6W.
The Duka One is a one room ventilationsystem with a heat exchanger. It is a Danish product and youi can read more about it [here](
https://dukaventilation.dk/produkter/1-rums-ventilationsloesninger/duka-one-s6w). It may be sold in other countries too. 
I did contact the manufacture to get more information in case they aready have a public API for connection to the device, but I did not get any reply at all.
All the information about how to communicate with the device has been extracted by looking at the packages send to/from the device, so there are still some unknon data in the packets.I have it working on 2 devices so I assume it is ok.

The primary goal for this module is to make an interface from Home Assistant to Duka One

The module implements:

* On/Off 
* Set/Get speed
* Set/Get Mode
* Notification when a state changes. 
 
## Example

See the examples.py file

When I have been using it for a while I will make a post about it on my blog http://www.dingus.dk/

## Other compatible devices

There are several one "bands" of the duka one ventilator.
* Blauberg Vento
* Siku With several models.

These should also work - I don't know which one is the orginal manufacture. Both Blauberg and Siku has documentation for the interface.

[You can see the documentation from Blauberg here](https://blaubergventilatoren.de/uploads/download/b133_4_1en_01preview.pdf)

# License

Dukaonesdk is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dukaonesdk is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this library.  If not, see <http://www.gnu.org/licenses/>.

