import requests
import json
from datetime import date
from lxml import etree
from io import StringIO
from multiprocessing import Process


def get_station_details(url, station_id):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'content-type': 'application/json'
        }
        params = {
            'stn': station_id
        }
        cookies = {
            'disclaimer': "agree"
        }
        res = requests.get(url, params=params,
                           cookies=cookies, headers=headers)
        res_status = res.status_code

        if res_status != 200:
            status_error_message = f"Status: {res_status}: There has been an error retrieving data from the endpoint. Review endpoint access."
            print(status_error_message)
            return

        # .content > bytes, .text > str
        # Decode bytes to string
        content = res.content.decode("utf-8")

        parser = etree.HTMLParser()
        content_to_parse = StringIO(content)
        tree = etree.parse(content_to_parse, parser=parser)

        station_details_data = []
        latest_water_measurement_statement = ""
        station_paragraphs = tree.xpath("//p")
        for row in station_paragraphs:
            if row.text != None and "latest water level" in row.text:
                latest_water_measurement_statement = row.text
                station_details_data.append(
                    {"latest_water_statement": latest_water_measurement_statement})
            else:
                latest_water_measurement_statement = "Water level unavailable at this time. Please try again later."
                # To do: Send email alert

        target_file = f'./_ReferenceExamples/water_station.html'
        with open(target_file, 'w') as f:
            f.write(content)

        return station_details_data

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return


def get_station_details_graph(url, station_id, date1, date2, param1, param2):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'content-type': 'application/json'
        }
        params = {
            'station': station_id,
            'start_date': date1,
            'end_date': date2,
            'param1': param1,
            'param2': param2
        }
        cookies = {
            'disclaimer': "agree"
        }

        res = requests.get(url, params=params,
                           cookies=cookies, headers=headers)

        print(res.url)

        # .content > bytes, .text > str
        # Decode bytes to string
        content = res.content.decode("utf-8")

        target_file = f'./_ReferenceExamples/water_station_graph_example.html'
        with open(target_file, 'w') as f:
            f.write(content)

        return "Done"

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return


if __name__ == '__main__':
    # Search terms
    station_id = "08MH001"
    start_date = "2022-09-20"
    end_date = date.today().strftime("%Y-%m-%d")
    water_level_primary_sensor_id = 46
    discharge_level_primary_sensor_derived_id = 47
    # Endpoint
    water_office_url = "https://wateroffice.ec.gc.ca"
    station_detail_url = f"{water_office_url}/report/real_time_e.html"
    station_graph_url = f"{water_office_url}/services/real_time_graph/json/inline?"

    # Retrieve the latest water level & historical graph data
    station_detail_request = get_station_details(
        station_detail_url, station_id)

    # Retrieve water level historical graph data
    station_graph_request = get_station_details_graph(
        station_graph_url, station_id, start_date, end_date, water_level_primary_sensor_id, discharge_level_primary_sensor_derived_id)

    target_file = f'./water_station_{station_id}.json'
    with open(target_file, 'w') as f:
        f.write(json.dumps(station_detail_request))

    todays_date = end_date
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
