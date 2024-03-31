from flask import Flask, render_template, request
from urllib.parse import unquote  # Import unquote from urllib.parse
import boto3
from calendar import monthrange
from datetime import datetime

app = Flask(__name__)

def get_cost_and_usage(account_id: str, region: str, start: str, end: str) -> dict:
    bclient = boto3.client('ce', region_name=region)

    response = bclient.get_dimension_values(
        TimePeriod={'Start': start, 'End': end},
        Dimension='SERVICE'
    )

    print("Response from AWS Cost Explorer API:", response)

    services = {}
    dimension_values = response.get('DimensionValues', [])
    for value in dimension_values:
        if 'Value' in value:
            service_name = value['Value']
            services[service_name] = 0

    for service in services:
        data = bclient.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {
                    'Type': 'DIMENSION',
                    'Key': 'SERVICE'
                }
            ]
        )
        for result in data['ResultsByTime']:
            for group in result['Groups']:
                service = group['Keys'][0]
                amount = group['Metrics']['UnblendedCost']['Amount']
                services[service] += float(amount)

    return {'response': response, 'services': services}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        account_id = request.form['account_id']
        region = request.form['region']
        start = request.form['start']
        end = request.form['end']

        if not start or not end:
            ldom = monthrange(datetime.today().year, datetime.today().month)[1]
            start = datetime.today().replace(day=1).strftime('%Y-%m-%d')
            end = datetime.today().replace(day=ldom).strftime('%Y-%m-%d')

        result = get_cost_and_usage(account_id, region, start, end)
        return render_template('result.html', result=result)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
