import json
from PingLogger import PingLogger

def main():
	with open('config.json','r') as f:
		config = json.load(f)

	pingLogger = PingLogger(config)
	try:
		pingLogger.makeMeasurement()
	except KeyboardInterrupt:
		pingLogger.endMeasurement()
		pingLogger.makeResultFile()
		pingLogger.makeResultCsv()

if __name__ == '__main__':
	main()