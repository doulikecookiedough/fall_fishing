import requests
import json
from datetime import date
from lxml import etree
from io import StringIO


# This function accepts an URL, query_type (ex. region) and region (ex. PYR)
# These values can be found by reviewing the values found in https://wateroffice.ec.gc.ca/search/
def get_station_list(url, query_type, region):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'content-type': 'application/json'
        }
        params = {
            'search_type': query_type,
            'region': region
        }
        res = requests.get(url, params=params, headers=headers)
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
        # station_labels = tree.xpath("//tbody/tr/td/label")
        # station_label_count = 0
        for row in station_rows:
            station_cells = row.xpath("td")
            station_list.append(
                {
                    "id": station_cells[3].text,
                    "name": station_cells[1].xpath("label")[0].text,
                    "province": station_cells[2].text
                }
            )
            # station_label_count = station_label_count + 1

        # Station list should look like [... , {"id": "08MH001", "name": "CHILLIWACK RIVER AT VEDDER CROSSING", "province": "BC"} , ...]
        return station_list

    except Exception as e:
        exception_message = f"Exception: {e}"
        print(exception_message)
        return


if __name__ == '__main__':
    # Search terms
    search_type = "region"
    region = "PYR"
    # Endpoint
    water_office_begin_url = "https://wateroffice.ec.gc.ca/search/real_time_results_e.html"

    station_list_with_ids = get_station_list(
        water_office_begin_url, search_type, region)

    target_file = f'./water_station_list.json'
    with open(target_file, 'w') as f:
        f.write(json.dumps(station_list_with_ids))

    todays_date = date.today().strftime("%Y-%m-%d")
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
