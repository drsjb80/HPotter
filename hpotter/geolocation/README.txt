FOR WINDOWS USERS:
Geolocation requires multiple installs outside of pip in order to work.

* Anaconda must be used rather than command prompt. Anaconda allows for the
    installation of basemap, whereas pip does not on windows.

* The C++ library for windows must also be installed via Visual Studio Build Tools.

Steps for installation:

1. Download & install VS Build Tools for windows here:
    https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15&ranMID=24542&ranEAID=
    je6NUbpObpQ&ranSiteID=je6NUbpObpQ-OaFibAbeLpjF6dQ3xTHckQ&epi=je6NUbpObpQ-OaFibAbeLpjF6dQ3xTHckQ&irgwc=1&OCID=AID681541_aff_7593_1243925&tduid=(ir__kaueklhgbnfspxctjum1djpqwf2xktp3uhzfjhxt00)(7593)(1243925)(je6NUbpObpQ-OaFibAbeLpjF6dQ3xTHckQ)()&irclickid=_kaueklhgbnfspxctjum1djpqwf2xktp3uhzfjhxt00#

2. Run the installer, choose to install C++ build tools. Choose the default options and install.
    * Restart may be required after installation

3. Download & install Anaconda for Python 3.7 here:
    https://www.anaconda.com/download/

4. Run the installer; choose the default options for everything except Advanced Options.
    * Choose whether or not to register anaconda as the default Python 3.7 (I chose not to)

5. After installation, run (in the Anaconda Prompt):
    python -m pip install --upgrade pip
    pip install PyHamcrest
    pip install -r requirements
    conda install -c conda-forge basemap=1.1
    conda install -c conda-forge basemap-data-hires

6. Change location of main.db in hpotter.geolocation.geo_ip_map.py (in def connect())
    * Must start with top level (C:/, E:/, F:/, etc.)
    * Ex: C:/Users/you/documents/hpotter/Hpotter/main.db

7. In Anaconda Prompt, navigate to hpotter.geolocation, then run:
    python geo_ip_map.py
    * Should project map after going through JSON info of IP's in main.db


Help from:
https://stackoverflow.com/questions/6600878/find-all-packages-installed-with-easy-install-pip
https://stackoverflow.com/questions/29846087/microsoft-visual-c-14-0-is-required-unable-to-find-vcvarsall-bat
https://github.com/jswhit/pyproj/issues/62
https://stackoverflow.com/questions/40374441/python-basemap-module-impossible-to-import
https://stackoverflow.com/questions/35716830/basemap-with-python-3-5-anaconda-on-windows