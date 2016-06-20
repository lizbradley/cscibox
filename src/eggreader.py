import matplotlib.pyplot as plt
import csv

data = []

with open("eggs.csv","rb") as eggs:
    data_reader = csv.reader(eggs)
    for row in data_reader:
        data.append([float(i) for i in row])

# the first list in data is a list of depths
depths = data.pop(0)        

# every other list is a list of ages to be plotted against the depths
for ages in data:
    plt.plot(depths,ages,'k-',alpha=0.01)

plt.tight_layout()
plt.show()