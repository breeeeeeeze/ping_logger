import time
import datetime
import csv
import pingparsing as ping
from apscheduler.schedulers.background import BackgroundScheduler

class PingLogger:
	def __init__(self, config):
		self.results = []
		self.filename = f'ping_report_{time.strftime("%y%m%d_%H%M",time.localtime())}'
		self.config = config
		self.scheduler = BackgroundScheduler()
		self.parser = ping.PingParsing()
		self.transmitter = ping.PingTransmitter()
		self.printIntro()
		self.timeStart = time.localtime()

	def makePing(self):
		self.transmitter.destination = self.config['hostTarget']
		self.transmitter.count = self.config['packetCount']
		self.transmitter.timeout = self.config['timeout']

		now = time.strftime("%d.%m.%Y %H:%M")
		out = self.parser.parse(self.transmitter.ping()).as_dict()
		out['time'] = now
		return out

	def makeMeasurement(self):
		self.scheduler.add_job(self.job, 'interval', seconds = self.config['traceInterval'])
		self.scheduler.start()
		while True:
			time.sleep(1000)

	def printIntro(self):
		print('Starting packet loss measurement, press Ctrl+C to end measurement')
		print(f'Target: {self.config["hostTarget"]}')
		print(f'Interval between pings: {self.config["traceInterval"]}')
		print(' Lost |       Time       | Total packets')

	def job(self):
		result = self.makePing()
		self.writeTempLog(result)
		self.results.append(result)
		print ('%5i | %s | %-6i' % (result['packet_loss_count'], result['time'], sum(result["packet_transmit"] for result in self.results)))

	def endMeasurement(self):
		self.scheduler.shutdown()

	def makeResultFile(self):
		totalTransmit = sum(result["packet_transmit"] for result in self.results)
		totalReceived = sum(result["packet_receive"] for result in self.results)
		totalLost = sum(result["packet_loss_count"] for result in self.results)
		maxLost = {'lost': 0, 'time': None}
		for result in self.results:
			if result['packet_loss_count'] > maxLost['lost']:
				maxLost['lost'] = result['packet_loss_count']
				maxLost['time'] = result['time']

		rttAvg = [float(result['rtt_avg']) for result in self.results if result['rtt_avg'] != 'NaN']
		rttMin = min(float(result['rtt_min']) for result in self.results if result['rtt_min'] != 'NaN')
		rttMax = max(float(result['rtt_max']) for result in self.results if result['rtt_max'] != 'NaN')
		
		with open(self.filename + '.txt', 'w') as f:
			f.write(f'--- PING REPORT {time.strftime("%d.%m.%Y %H:%M",self.timeStart)} for target {self.config["hostTarget"]} ---\n\n')
			f.write(f'TOTAL PACKETS SENT: {totalTransmit}\n')
			f.write(f'TOTAL PACKETS RECEIVED: {totalReceived}\n')
			f.write(f'TOTAL PACKETS LOST: {totalLost}\n')
			f.write(f'LOSS RATE: {round(totalLost/totalTransmit*100,2)} %\n\n')
			f.write(f'{len(rttAvg)} total pings, min: {rttMin}, max: {rttMax}, avg: {round(sum(rttAvg)/len(rttAvg),3)}\n')

			f.write(f'There were {len(self.results)} runs.\n')
			f.write(f'The highest loss was {("at " + str(maxLost["time"])) if maxLost["time"] else "never"} with {maxLost["lost"]}/{self.config["packetCount"]} lost ({round(maxLost["lost"]/self.config["packetCount"]*100,2)}%)\n\n')

			f.write(f'-RUN LIST-\n')
			for i, result in enumerate(self.results):
				f.write(f'{i} - {result["time"]} - {result["packet_transmit"]} sent, {result["packet_receive"]} received, {result["packet_loss_count"]} lost. ')
				f.write(f'Ping: avg: {result["rtt_avg"]} - min: {result["rtt_min"]} - max: {result["rtt_max"]}\n')

	def makeResultCsv(self):
		with open(f'{self.filename}.csv', 'w') as f:
			writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
			writer.writeheader()
			writer.writerows(self.results)

	def writeTempLog(self, result):
		with open(f'temp_log_{str(datetime.date.today())}.txt', 'a') as tempFile:
			tempFile.write(f'{result["time"]} - {result["packet_transmit"]} sent, {result["packet_receive"]} received, {result["packet_transmit"] - result["packet_receive"]} lost\n')