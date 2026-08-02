import csv
for r in csv.DictReader(open('demo_feedback_processed.csv')):
    print(f'{r["customer_name"]:<15} {r["sentiment"]:<9} {r["summary"][:45]}')