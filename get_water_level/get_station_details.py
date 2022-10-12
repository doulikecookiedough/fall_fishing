import requests
import json
import asyncio
from datetime import date
from lxml import etree
from io import StringIO

# This retrieves the latest water level measurement


async def get_station_details(url, station_id):
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

        # water_station_html_example = f'./_ReferenceExamples/water_station.html'
        # with open(water_station_html_example, 'w') as f:
        #     f.write(content)

        # water_station_level_example = f'./_ReferenceExamples/water_level_{station_id}.json'
        # with open(water_station_level_example, 'w') as f:
        #     f.write(json.dumps(station_details_data))

        return station_details_data

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return

# This retrieves the water and discharge level data (to be displayed in a graph)


async def get_station_details_graph(url, station_id, date1, date2, param1, param2):
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

        # .content > bytes, .text > str
        # Decode bytes to string
        content = json.loads(res.content.decode("utf-8"))

        station_graph_data = []
        station_graph_data.append({
            'comment': "The discharge level is the volume of water moving down a stream or river per unit of time, commonly expressed in cubic feet per second or gallons per day.",
            'water_level': content['46']['provisional'],
            'discharge_level': content['47']['provisional']
        })

        # target_file = f'./_referenceExamples/water_station_{station_id}_graph.json'
        # with open(target_file, 'w') as f:
        #     f.write(json.dumps(station_graph_data))

        return station_graph_data

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return


async def main(station_detail_url, station_graph_url, station_id, start_date, end_date, water_level_primary_sensor_id, discharge_level_primary_sensor_derived_id):
    res = await asyncio.gather(get_station_details(
        station_detail_url, station_id), get_station_details_graph(
        station_graph_url, station_id, start_date, end_date, water_level_primary_sensor_id, discharge_level_primary_sensor_derived_id))

    return res

if __name__ == '__main__':
    # Search terms
    # These terms will be retrieved based on user input on a website at a later date
    station_id = "08MH001"
    start_date = "2022-09-20"
    end_date = date.today().strftime("%Y-%m-%d")
    water_level_primary_sensor_id = 46
    discharge_level_primary_sensor_derived_id = 47
    # Endpoint
    water_office_url = "https://wateroffice.ec.gc.ca"
    station_detail_url = f"{water_office_url}/report/real_time_e.html"
    station_graph_url = f"{water_office_url}/services/real_time_graph/json/inline"

    station_detail_request, station_graph_request = asyncio.run(main(
        station_detail_url, station_graph_url, station_id, start_date, end_date, water_level_primary_sensor_id, discharge_level_primary_sensor_derived_id))

    station_full_details = station_detail_request + station_graph_request

    target_file = f'./_ReferenceExamples/{station_id}_full_details.json'
    with open(target_file, 'w') as f:
        f.write(json.dumps(station_full_details))

    todays_date = end_date
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
