from django.core.management.base import BaseCommand

from distribution.gov_simulator import build_from_env, GovernmentGridSimulator


class Command(BaseCommand):
    help = 'Run government village-grid MQTT simulator (moved from Admin/virtual_meter_gov.py)'

    def add_arguments(self, parser):
        parser.add_argument('--broker', type=str, help='MQTT broker host')
        parser.add_argument('--port', type=int, help='MQTT broker port')
        parser.add_argument('--topic', type=str, help='MQTT topic to publish snapshot data')
        parser.add_argument('--houses', type=int, help='Number of houses to simulate')
        parser.add_argument('--interval', type=float, help='Publish interval in seconds')
        parser.add_argument('--csv-file', type=str, help='CSV file path for house templates')

    def handle(self, *args, **options):
        simulator = build_from_env()

        broker = options.get('broker')
        port = options.get('port')
        topic = options.get('topic')
        houses = options.get('houses')
        interval = options.get('interval')
        csv_file = options.get('csv_file')

        if any(value is not None for value in [broker, port, topic, houses, interval, csv_file]):
            simulator = GovernmentGridSimulator(
                broker=broker or simulator.broker,
                broker_port=port or simulator.broker_port,
                topic=topic or simulator.topic,
                num_houses=houses or simulator.num_houses,
                publish_interval_seconds=interval or simulator.publish_interval_seconds,
                csv_file=csv_file if csv_file is not None else simulator.csv_file,
            )

        self.stdout.write(self.style.NOTICE('Starting government grid simulator...'))
        self.stdout.write(f'Broker: {simulator.broker}:{simulator.broker_port}')
        self.stdout.write(f'Topic: {simulator.topic}')
        self.stdout.write(f'Houses: {simulator.num_houses}')
        self.stdout.write(f'Interval: {simulator.publish_interval_seconds}s')

        simulator.run_forever()
