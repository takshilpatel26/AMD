"""
Management command to populate sample distribution network data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random

from distribution.models import (
    Company, District, Village, Transformer, House
)
from distribution.simulator import simulator


class Command(BaseCommand):
    help = 'Populate sample distribution network data (Company, Districts, Villages, Transformers, Houses)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-readings',
            action='store_true',
            help='Also generate sample readings after creating infrastructure',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Number of hours of historical readings to generate (default: 24)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Creating distribution network sample data...'))
        
        # Create Company
        company, created = Company.objects.get_or_create(
            code='TORRENT',
            defaults={
                'name': 'Torrent Power Limited',
                'address': 'Torrent House, Off Ashram Road, Ahmedabad - 380009, Gujarat',
                'contact_email': 'customercare@torrentpower.com',
                'contact_phone': '+91-79-26500500',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Created company: {company.name}'))
        else:
            self.stdout.write(f'  Company already exists: {company.name}')

        # Create Districts
        districts_data = [
            {'name': 'Anand', 'code': 'ANAND', 'state': 'Gujarat', 'capacity': 50000},
            {'name': 'Kheda', 'code': 'KHEDA', 'state': 'Gujarat', 'capacity': 45000},
            {'name': 'Vadodara', 'code': 'VADODARA', 'state': 'Gujarat', 'capacity': 75000},
        ]

        districts = []
        for d_data in districts_data:
            district, created = District.objects.get_or_create(
                company=company,
                code=d_data['code'],
                defaults={
                    'name': d_data['name'],
                    'state': d_data['state'],
                    'total_capacity_kva': d_data['capacity'],
                }
            )
            districts.append(district)
            if created:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Created district: {district.name}'))

        # Villages per district
        villages_data = {
            'ANAND': [
                {'name': 'Borsad', 'code': 'BOR', 'pop': 5000, 'hh': 1200},
                {'name': 'Petlad', 'code': 'PET', 'pop': 4500, 'hh': 1000},
                {'name': 'Anklav', 'code': 'ANK', 'pop': 3000, 'hh': 700},
                {'name': 'Sojitra', 'code': 'SOJ', 'pop': 2500, 'hh': 600},
            ],
            'KHEDA': [
                {'name': 'Nadiad', 'code': 'NAD', 'pop': 6000, 'hh': 1400},
                {'name': 'Kapadvanj', 'code': 'KAP', 'pop': 4000, 'hh': 900},
                {'name': 'Mahudha', 'code': 'MAH', 'pop': 3500, 'hh': 800},
            ],
            'VADODARA': [
                {'name': 'Padra', 'code': 'PAD', 'pop': 5500, 'hh': 1300},
                {'name': 'Dabhoi', 'code': 'DAB', 'pop': 4200, 'hh': 950},
                {'name': 'Karjan', 'code': 'KAR', 'pop': 3800, 'hh': 850},
                {'name': 'Savli', 'code': 'SAV', 'pop': 3200, 'hh': 750},
            ],
        }

        all_villages = []
        for district in districts:
            v_list = villages_data.get(district.code, [])
            for v_data in v_list:
                village, created = Village.objects.get_or_create(
                    district=district,
                    code=v_data['code'],
                    defaults={
                        'name': v_data['name'],
                        'pincode': f'38{random.randint(1000, 9999)}',
                        'population': v_data['pop'],
                        'total_households': v_data['hh'],
                        'gps_latitude': 22.0 + random.uniform(0, 1),
                        'gps_longitude': 72.0 + random.uniform(0, 1),
                    }
                )
                all_villages.append(village)
                if created:
                    self.stdout.write(f'    ✓ Created village: {village.name}')

        # Create Transformers (4-6 per village)
        transformer_types = ['distribution', 'pole_mounted', 'pad_mounted']
        capacities = [25, 63, 100, 250]  # KVA options
        
        all_transformers = []
        for village in all_villages:
            num_transformers = random.randint(4, 6)
            for t_num in range(1, num_transformers + 1):
                t_id = f"TRF-{village.district.code}-{village.code}-{t_num:02d}"
                
                transformer, created = Transformer.objects.get_or_create(
                    transformer_id=t_id,
                    defaults={
                        'village': village,
                        'name': f'{village.name} Transformer {t_num}',
                        'transformer_type': random.choice(transformer_types),
                        'capacity_kva': random.choice(capacities),
                        'input_voltage': 11000,
                        'output_voltage': 230,
                        'efficiency_rating': random.uniform(96, 99),
                        'max_houses': 10,
                        'installation_date': date.today() - timedelta(days=random.randint(365, 3650)),
                        'last_maintenance_date': date.today() - timedelta(days=random.randint(30, 180)),
                        'gps_latitude': float(village.gps_latitude or 22.0) + random.uniform(-0.01, 0.01),
                        'gps_longitude': float(village.gps_longitude or 72.0) + random.uniform(-0.01, 0.01),
                        'status': random.choices(
                            ['active', 'active', 'active', 'active', 'maintenance', 'faulty'],
                            weights=[60, 20, 10, 5, 3, 2]
                        )[0],
                    }
                )
                all_transformers.append(transformer)
                if created:
                    self.stdout.write(f'      ✓ Created transformer: {t_id}')

        # Create Houses (8-10 per transformer)
        connection_types = ['residential', 'residential', 'residential', 'agricultural', 'commercial']
        
        first_names = ['Ramesh', 'Suresh', 'Mahesh', 'Priya', 'Anita', 'Sunita', 'Vijay', 'Sanjay', 
                       'Rajesh', 'Dinesh', 'Geeta', 'Seema', 'Kavita', 'Amit', 'Arun']
        last_names = ['Patel', 'Shah', 'Desai', 'Mehta', 'Joshi', 'Trivedi', 'Parikh', 'Modi',
                      'Panchal', 'Thakkar', 'Bhatt', 'Dave', 'Pandya', 'Raval', 'Soni']

        house_count = 0
        for transformer in all_transformers:
            num_houses = random.randint(8, 10)
            village = transformer.village
            
            for h_num in range(1, num_houses + 1):
                consumer_id = f"CON-{village.district.code}-{village.code}-{transformer.transformer_id.split('-')[-1]}-{h_num:03d}"
                
                house, created = House.objects.get_or_create(
                    consumer_id=consumer_id,
                    defaults={
                        'transformer': transformer,
                        'consumer_name': f'{random.choice(first_names)} {random.choice(last_names)}',
                        'address': f'House {h_num}, Near {transformer.name}, {village.name}',
                        'phone_number': f'+91{random.randint(7000000000, 9999999999)}',
                        'connection_type': random.choice(connection_types),
                        'connected_load_kw': random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 5.0]),
                        'meter_number': f'MTR{random.randint(100000, 999999)}',
                        'connection_date': date.today() - timedelta(days=random.randint(180, 2000)),
                        'connection_status': 'active',
                        'gps_latitude': float(transformer.gps_latitude or 22.0) + random.uniform(-0.005, 0.005),
                        'gps_longitude': float(transformer.gps_longitude or 72.0) + random.uniform(-0.005, 0.005),
                    }
                )
                if created:
                    house_count += 1

        self.stdout.write(self.style.SUCCESS(f'\n✓ Created {house_count} houses'))

        # Summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('DISTRIBUTION NETWORK SUMMARY'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Company: {company.name}')
        self.stdout.write(f'Districts: {District.objects.filter(company=company).count()}')
        self.stdout.write(f'Villages: {Village.objects.count()}')
        self.stdout.write(f'Transformers: {Transformer.objects.count()}')
        self.stdout.write(f'Houses: {House.objects.count()}')

        # Generate readings if requested
        if options['with_readings']:
            self.stdout.write(self.style.NOTICE(f'\nGenerating {options["hours"]} hours of readings...'))
            
            houses = House.objects.filter(is_active=True, connection_status='active')
            readings = simulator.simulate_historical_data(hours=options['hours'], houses=houses)
            
            anomalies = sum(1 for r in readings if r.is_anomaly)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Generated {len(readings)} readings'))
            self.stdout.write(self.style.WARNING(f'⚠ {anomalies} anomalies detected (alerts created)'))

        self.stdout.write(self.style.SUCCESS('\n✅ Sample data population complete!'))
