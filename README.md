# dolueg2overview

How to make an overview, i.e. landing page with measurement values for [the dolueg2 page](https://github.com/spirrobe/dolueg2page).
The overview is based on a HTML template files. these files contain the table structure and the designated database codes that should be included.
A Python program (htmlfileprocessor.py) fills in the correct values (by using a getdata function that is also required for [dolueg2](https://mcr.unibas.ch/dolueg2figures)).

[The example file ](https://mcr.unibas.ch/dolueg2overview/template.txt/) is the same that is used for [the live landing page ](https://mcr.unibas.ch/dolueg).


## Requirements

numpy and pandas are required

Two functions need to be written as they are particular to the organisation of our database
The first one is a getdata functiion that is already needed for the [dolueg2figures](https:/github.com/spirrobe/dolueg2figures)
The second one is "gettimezones", a function that returns the timezone the codes are saved in. If all your codes are in UTC then you can remove this part. 
All other functions are provided in the top directory. 
*It is prudent to move these to subdirectories and adjust the imports to your setup.*

## Examples

*In general, codes that should be replaced are in square brackets.*
htmlfileprocessor has a "pattern" keyword to change these in case another set is prefered.

#### Creating file from template
No explcit return value is defined (detaults to True by Python)
```
htmlfileprocessor('template.txt', 'current.html')
```

#### Current values of a time seriees (BKLIDTA9)
```
[BKLIDTA9,ACT]
```
which is interpreted as getting data from the current computer time of BKLIDTA9 (a temperature time series in this case)


#### Make units
```
[UNITh<sup>-1</sup>]
```
Special case of just keeping what is in the square bracket (basically keep square brackets), in this case h<sup>-1</sup>

#### Get the trend of the time series of the last hour
```
[BKLIDTA9,TEN,0.041666]
```
#### Get the maximum/minimum over the last day of a time seriees (BKLIDTA9)
```
[BKLIDTA9,MAX,1]
[BKLIDTA9,MIN,1]
```
#### Get the sum (of rain for example) 
```
[BKLIPCT2,SUM,1] 
```

#### Restrict values
For example to ensure a solar irradiance of 0 during night, clip it to a range of 0 to 1200 with the following
```
[BKLISDA1,MAX,1,CLIP:0:1200]
```

#### Exchange wind direction (0-360) with a string denoting the geographical orientation
Given a windcode (or any code for that matter), report a string (e.g. NW) 
```
[BLEOWDA1,ACT,1,HR]
[BLEOWDA1,ACT,1,HRA]
```
A number for the time frame has to be given (and be non-zero), even is ACT takes in the end the last value for HRA/HR to work.
The second call with the A at the end introduces an unicode arrow in addition, making it obvious it is where wind is coming from
Since the available unicode arrows are limited to the 4 main directions (N/E/S/W) and the 4 subdirection (NE/SE/SW/NW) only those are reported as well

#### Value from a specific point or range in time 
The first two give the last value of the last 6h or 12h interval of the current day (e.g. 6, 12, 18, 24; resp. 12, 24)
The thid one gives the sum of the last six hours, in this case the sum of rain (BKLIPCT2 is a rain measurement) of the last six hours
```
[BKLIWDA1,V06,1,HRA]
[BKLIWDA1,V06,1,HRA]
[BKLIPCT2,S06]
```

#### Choosing a data interval
The first one below gets the rain sum of the last seven days 
The second one below gets the radiation (BKLISDA1) for the last 3 days and checks where values above 0 were measured and calculations the *sun* hours
The datainterval is given in days back from now (when the computer runs the code)
```
[BKLIPCT2,SUM,7]
[BKLIPCT2,SUN,3]
```

#### Getting a time interval/month relative to now
Both codes below go one month back (M1) and get either the name (FULLMONTH) or the year of that month
```
[FULLMONTH,AVG,M1]
[YEAR,AVG,M1]
```

#### Getting the climate from a time series
Sometimes it is interesting to be able to compare the current values with the long-term variation. For shortness these are called climate codes and calculate for example the average
of the whole time series for the current month.
It is important to note that the first aggregation, i.e. the one for the month is given by the database (for PCT (=precipitaton) this is the sum).
The second aggregation is chosen as average here, indicating that grouping occurs to month (M1) with the sum (given by database variable) and then the average of all months.
Check the function getclimatedata.py for details

```
[BLER#DTA1,AVG,M1]
[BLER#PCT1,AVG,M1]
[BLER#SDA1,SUN,M1]
```

#### UVBINDEX
For completeness: uvbindex is provided as htmlfileprocessor can get uvbindex values according to [meteoschweiz](http://www.meteoschweiz.ch/de/Freizeit/Gesundheit/UV_Index/uv_protec.shtml)
Currently, no UV measurements are conducted by us, therefore no example is contained in the template

```
[BKLIUVB1,ACT, UV]
```
