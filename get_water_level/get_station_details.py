import requests
import json
from datetime import date
from lxml import etree
from io import StringIO


def get_station_list(url, station_id):
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

        target_file = f'./water_station.html'
        with open(target_file, 'w') as f:
            f.write(content)

        return content

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return


if __name__ == '__main__':
    # Search terms
    station_id = "08MH001"
    # Endpoint
    station_detail_url = "https://wateroffice.ec.gc.ca/report/real_time_e.html"

    station_list_with_ids = get_station_list(
        station_detail_url, station_id)

    target_file = f'./water_station_list.json'
    with open(target_file, 'w') as f:
        f.write(json.dumps(station_list_with_ids))

    todays_date = date.today().strftime("%Y-%m-%d")
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
