import requests
from datetime import date
from lxml import etree
from io import StringIO


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

        if res_status == 200:
            # .content > bytes, .text > str
            # Decode bytes to string
            content = res.content.decode("utf-8")

            parser = etree.HTMLParser()
            content_to_parse = StringIO(content)
            tree = etree.parse(content_to_parse, parser=parser)

            # Get list of station labels
            station_label_list = []
            station_data_labels = tree.xpath("//tbody/tr/td/label")
            for item in station_data_labels:
                element_value = item.text
                station_label_list.append(
                    {
                        "label": element_value
                    }
                )

            # Get list of station ids
            station_id_list = []
            station_data_ids = tree.xpath("//tbody/tr/td")
            for item in station_data_ids:
                element_value = str(item.text)
                station_status = any(char.isdigit() for char in element_value)
                if station_status:
                    station_id_list.append(
                        {
                            "id": element_value
                        }
                    )

            # Get list of station provinces
            station_province_list = []
            station_province_codes = tree.xpath("//tbody/tr/td")
            for item in station_province_codes:
                element_value = str(item.text)
                station_province_length = len(element_value)
                if station_province_length == 2 and element_value != "No":
                    station_province_list.append(
                        {
                            "code": element_value
                        }
                    )

            # Confirm that lists are the same length, return error if not
            station_label_list_length = len(station_label_list)
            station_id_list_length = len(station_id_list)
            station_province_list_length = len(station_province_list)
            station_list_mapped = []
            if station_label_list_length == station_id_list_length and station_id_list_length == station_province_list_length:
                # Join labels with ids, both already ordered based on xpath order
                for i in range(0, station_id_list_length):
                    station_list_mapped.append(
                        {
                            "id": station_id_list[i]['id'],
                            "name": station_label_list[i]['label'],
                            "province": station_province_list[i]['code']
                        }
                    )

            return station_list_mapped

        else:
            status_error_message = f"Status: {res_status}: There has been an error retrieving data from the endpoint. Review endpoint access."
            print(status_error_message)
            return

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
    print(f"Station ID List:\n{station_list_with_ids}")

    todays_date = date.today().strftime("%Y-%m-%d")
    disclaimer_info = f'Extracted from the Environment and Climate Change Canada Real-time Hydrometric Data web site (https://wateroffice.ec.gc.ca/mainmenu/real_time_data_index_e.html) on {todays_date}'
    print(disclaimer_info)
