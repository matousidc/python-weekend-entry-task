# Python weekend entry task by Matouš Slonek

### Description
Python script, that for given flight data prints out a structured list of all flight combinations for a selected route between airports A -> B, sorted by the final price for the trip.

### Input arguments

| Argument name | type    | Description              | Notes                        |
|---------------|---------|--------------------------|------------------------------|
| `file`        | string  | Dataset file             | .csv file                    |
| `origin`      | string  | Origin airport code      |                              |
| `destination` | string  | Destination airport code |                              |

### Optional arguments

| Argument name | type    | Description                                                                       | Notes                        |
|---------------|---------|-----------------------------------------------------------------------------------|------------------------------|
| `bags`        | integer | Number of requested bags.                                                         | Optional (defaults to 0)     |
| `returns`     | integer | Finds first available flight combination back after specified number of days.     | Optional (defaults to False) |

### Output
The output is a json-compatible structured list of trips sorted by price. The trip has the following schema:
| Field          | Description                                                   |
|----------------|---------------------------------------------------------------|
| `flights`      | A list of flights in the trip according to the input dataset. |
| `origin`       | Origin airport of the trip.                                   |
| `destination`  | The final destination of the trip.                            |
| `bags_allowed` | The number of allowed bags for the trip.                      |
| `bags_count`   | The searched number of bags.                                  |
| `total_price`  | The total price for the trip.                                 |
| `travel_time`  | The total travel time.                                        |

### How to run

Example with mandatory arguments:
```
python -m solution example1.csv DHE SML 
```
Example with added optional arguments:
```
python -m solution example1.csv DHE SML --bags=1 --returns=2
```
