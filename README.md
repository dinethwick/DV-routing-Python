# Overview
This is my implementation of the Distance Vector Routing Algorithm in Python, simulating how routers exchange and update routing tables over time. 
It was built from scratch without using external libraries, for an assignment in a Computer Networks course.

Given an input file of routers and link costs, along with optional updates, it:
- creates the distance tables for each iteration (Starting from t=0), 
- applies updates, 
- and prints the routing tables for each node after convergance.

## Architecture:
![Architecture](architecture.png)

## Running the program
A sample input and output, along with its topology, is in the [sample input and topology](sample input and topology) folder.

You can run the program in the terminal by using:
```bash
python DistanceVector.py < testfilename.txt
```

You can also specify the output file name at **line 10** of `DistanceVector.py`:

```python
# change the output file name (first arg)
sys.stdout = open('sampleoutput5', 'w')
```