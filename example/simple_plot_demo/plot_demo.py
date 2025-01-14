import matplotlib.pyplot as plt
import csv

# Installation instructions for matplotlib
# https://matplotlib.org/stable/users/installing.html

# Longer tutorial here
# https://docs.python.org/3/library/csv.html

data="run.csv"
generations=[]
best=[]
average=[]
mins=[]

with open(data, newline='') as csvfile:
    # Using the csv reader automatically places all values 
    # in columns within a row in a dictionary with a 
    # key based on the header (top line of the file)
    reader = csv.DictReader(csvfile)
    for row in reader:
        generations.append( row["generation"] )
        best.append( int(row["max"] ) )
        average.append( int(row["average"] ))
        mins.append( int(row["min"] ))
        

plt.plot(generations,best,label="best")
plt.plot(generations,average,label="average")
plt.plot(generations,mins,label="min")

plt.legend()
plt.xlabel('generations')
plt.ylabel('fitness')


plt.savefig('demo_plot.png')
plt.show()
