# Summary

This data collects the science, flat and bias frames for the i filter 
only. Observations were made on the night of 19. 03. 2021. by the DEEP
survey using DECam.

The same data can be identified and independently downloaded by invoking
the `scripts/download_data.py` script while specifying the `i` filter,
from the home directory of this repository:

```bash
scripts/download_data.py --filters i --download-science trimmedRawData/210318/science/

scripts/trim_ccds.py trimmedRawData/210318/science 35 --verbose --overwrite
```

# Contents

####                          BIAS RAW

idx | md5sum                           | ifilter             | proposal   | caldat     | archive_filename                                                                                     
----|----------------------------------|---------------------|------------|------------|------------------------------------------------------------------------                              
 0  | 1ea5780799f7b46799c8a972da32b931 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191405_zri.fits.fz
 1  | 2b5eafce9f32dad9a8ad2a96fb424cb0 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191318_zri.fits.fz
 2  | 7a08ca7430f60bcff5d4664185f4453c | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191255_zri.fits.fz
 3  | 96502171abc97b49374c2be10509eebe | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191208_zri.fits.fz
 4  | a0c59e2e433e860f9104b0af5b79ed95 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191144_zri.fits.fz
 5  | d7ccb573ebe8868072167b4640caa6ba | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191342_zri.fits.fz
 6  | e44561298fe9538385dfdf37173e0d1f | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191232_zri.fits.fz
 7  | 389616a979d9f1fc22604f549d55f002 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191121_zri.fits.fz
 8  | 526352744666ce5bb5d18540dbbf2c98 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191058_zri.fits.fz
 9  | 8c1917bbb2824f7493157a8182178404 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191011_zri.fits.fz
10  | f977b38c6b707162752a91bfcef9b90b | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_191034_zri.fits.fz
11  | 0070316e8fccc3d0d7a8840dfd98fe20 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204941_zri.fits.fz
12  | 0c3e9919bbaf0f46e45a9c4e6b2c384e | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_205051_zri.fits.fz
13  | 8fa9a8cbd460f46ee0941d185cf5a579 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_205004_zri.fits.fz
14  | 9a6a401b644e516b437839267f4274d3 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_205028_zri.fits.fz
15  | 0d2c5849d52854721136f5cd9284e6a5 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204917_zri.fits.fz
16  | 3e323a820beff11c7c8dff7fb0c0cfaa | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204854_zri.fits.fz
17  | 62121a343a8188fb188f256b965dd965 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204720_zri.fits.fz
18  | 95b8b7beaa56d376df12793a1b89ab4a | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204657_zri.fits.fz
19  | a5fd5afb8ad84d8571749f09ce1af3a1 | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204807_zri.fits.fz
20  | b77f01e765e2961413c1074a1a684a9a | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204744_zri.fits.fz
21  | c53f9986f47cd1a0f4afb26cd619609f | solid plate 0.0 0.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_204830_zri.fits.fz

####                          FLAT RAW

idx | md5sum                           | ifilter                          | proposal   | caldat     | archive_filename                                                                        
----|----------------------------------|----------------------------------|------------|------------|------------------------------------------------------------------------                 
 0  | 04bdc4bb9f46684393b5d3e0dcb6e7fa | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195459_fri.fits.fz
 1  | 536393d934e6ee0157f6a4bfb1145bc4 | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195404_fri.fits.fz
 2  | 808ace9f155e54aa5a2576b88056e3af | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195553_fri.fits.fz
 3  | e6f15444f38024a37dc77074066a42a3 | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195310_fri.fits.fz
 4  | 2aaa78091c2d5aa1d89e39e342b663ae | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195028_fri.fits.fz
 5  | 65f7e60f007de34409c62c7d05ec3379 | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195122_fri.fits.fz
 6  | 6a39262550e048e7c9847ee9daa81a03 | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_194745_fri.fits.fz
 7  | 760067bea7c79173a9b78550e4ff206b | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_194651_fri.fits.fz
 8  | 8c027c6726dc9e2094721dd6a647b8aa | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_194840_fri.fits.fz
 9  | a1d90ec8dea4009e70d25e89ecad331b | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_194934_fri.fits.fz
10  | f080a68a473809d0f87ceb2bbaff7b89 | i DECam SDSS c0003 7835.0 1470.0 | 2020A-0906 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2020A-0906/c4d_210318_195216_fri.fits.fz

####                         SCIENCE RAW

idx | md5sum                           | ifilter                          | proposal   | caldat     | archive_filename                                                                        
----|----------------------------------|----------------------------------|------------|------------|------------------------------------------------------------------------                 
 0  | 020c85f7e80ca26821aed1f6c0902127 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_024912_ori.fits.fz                 
 1  | 35330f682b64d4b6ccd8bc402b408888 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_024310_ori.fits.fz                 
 2  | e126aab419d1b5a7503b36d0b31d3e05 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_023704_ori.fits.fz                 
 3  | f8290547a6124d65a63f75897087af04 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_023059_ori.fits.fz                 
 4  | e33ae2af4f5f52d147dfd878dd958b2e | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_022455_ori.fits.fz                 
 5  | fa80fd7530560622e450a30174d9a2b7 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_005134_ori.fits.fz                 
 6  | 56d81414ab12a448b8ac5fce2181b339 | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_004532_ori.fits.fz                 
 7  | fea13cc71be5302de7e9f63e4109f26f | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_003928_ori.fits.fz                 
 8  | c74f675c59185dfee2cd8fd661806e7f | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_003322_ori.fits.fz                 
 9  | 202f4137d1f7571054e9f0539ff9bc3d | i DECam SDSS c0003 7835.0 1470.0 | 2021A-0113 | 2021-03-18 | /net/archive/mtn/20210318/ct4m/2021A-0113/c4d_210319_002721_ori.fits.fz

Of the science exposures:

 Filename                     | Target                                                                                                                                                        
------------------------------|---------                                                                                                                                                      
c4d_210319_003928_ori.fits.fz | cosmos_1                                                                                                                                                      
c4d_210319_024310_ori.fits.fz | cosmos_1                                                                                                                                                      
c4d_210319_022455_ori.fits.fz | cosmos_1                                                                                                                                                      
c4d_210319_024912_ori.fits.fz | cosmos_2                                                                                                                                                      
c4d_210319_023059_ori.fits.fz | cosmos_2                                                                                                                                                      
c4d_210319_004532_ori.fits.fz | cosmos_2                                                                                                                                                      
c4d_210319_002721_ori.fits.fz | cosmos_2                                                                                                                                                      
c4d_210319_023704_ori.fits.fz | cosmos_3                                                                                                                                                      
c4d_210319_005134_ori.fits.fz | cosmos_3                                                                                                                                                      
c4d_210319_003322_ori.fits.fz | cosmos_3 
