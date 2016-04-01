import matplotlib.pyplot as plt
import csv

data = []

with open("eggs.csv","rb") as eggs:
    data_reader = csv.reader(eggs)
    for row in data_reader:
        data.append([float(i) for i in row])

x = data.pop(0)        

for i in data:
    plt.plot(x,i,'k-',alpha=0.05)

plt.tight_layout()
plt.show()