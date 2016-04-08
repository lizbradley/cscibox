import matplotlib.pyplot as plt
import csv

data = []

with open("eggs.csv","rb") as eggs:
    data_reader = csv.reader(eggs)
    for row in data_reader:
        data.append([float(i) for i in row])

depths = data.pop(0)        

for ages in data:
    plt.plot(depths,ages,'k-',alpha=0.05)

plt.tight_layout()
plt.show()