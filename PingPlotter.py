import matplotlib.pyplot as plt
import sys
import json
import csv

results = []

with open(str(sys.argv[1]),'r') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		results.append(row)
		
with open('config.json','r') as f:
	config = json.load(f)

#dump = [item.rstrip() for item in dump]

#ping_start = dump.index('-RUN LIST-') + 1

# ping_list = []
# lost_list = []
# for i,item in enumerate(dump[ping_start:]):
# 	try:
# 		temp = item.split()
# 		temp2 = temp[9]
# 		temp3 = temp[3]
# 		print(temp)
# 		#if item == 'NaN':
# 		#	ping_list.append(0.)
# 		#	lost_list.append(i)
# 		#else:
# 		#	ping_list.append(float(item))
# 		ping_list.append(int(temp2))
# 		if len(ping_list) % 30 == 0:
# 			lost_list.append(temp3)
# 	except:
# 		break

packetLossRate = [float(result['packet_loss_rate']) for result in results]
time = [result['time'] for result in results]

plt.plot(packetLossRate)
#for item in lost_list:
#	plt.axvline(item, 0, 1, color = 'red')
plt.ylabel('Packet Loss [%]')
plt.xlabel('Time')
plt.xticks(range(0,len(packetLossRate), int(config['tickFrequency'])), [x for n, x in enumerate(time) if n%int(config['tickFrequency'])==0 ], rotation=45)
plt.ylim(0, max(packetLossRate))
plt.title(f'Ping report for target {results[0]["destination"]} on {results[0]["time"]}')
plt.show()
