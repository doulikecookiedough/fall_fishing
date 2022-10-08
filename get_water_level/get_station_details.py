import requests
import json
from datetime import date
from lxml import etree
from io import StringIO


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

        station_list = []
        station_rows = tree.xpath("//tbody/tr")
        for row in station_rows:
            station_cells = row.xpath("td")
            station_list.append(
                {
                    "id": station_cells[3].text,
                    "name": station_cells[1].xpath("label")[0].text,
                    "province": station_cells[2].text
                }
            )

        target_file = f'./_ReferenceExamples/water_station.html'
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

    # Retrieve the latest water level & historical graph data
    station_list_with_ids = get_station_details(
        station_detail_url, station_id)

    # target_file = f'./water_station_detail.json'
    # with open(target_file, 'w') as f:
    #     f.write(json.dumps(station_list_with_ids))

    todays_date = date.today().strftime("%Y-%m-%d")
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
