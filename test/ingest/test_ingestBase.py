import csv

from app.ingestBase import Ingest

rest_args = ["street", "city", "state", "zip", "owner_id", "name", "rating", "price_category",
             "phone", "is_active", "picture"]

csv_row_data = ['Ap #462-9254 Enim Road', 'Phoenix', 'AZ', '85084', '1', 'My Restur', 5.0, 1, '407-455-4527', 1,
                'https://logo.com']

json_row_data = ['Ap #462-9254 Enim Road', 'Phoenix', 'AZ', '85084', 1, 'My Restur', 5.0, 1, '407-455-4527', 1,
                 'https://logo.com']

xml_row_data = ['Ap #462-9254 Enim Road', 'Phoenix', 'AZ', '85084', '1', 'My Restur', 3.6, 1, '407-455-4527', 1,
                'https://logo.com']
json_xml_row_data = ['Ap #462-9254 Enim Road', 'Phoenix', 'AZ', '85084', 1, 'My Restur', 5.0, 1, '407-455-4527', 1,
                     'https://logo.com']


def handle_data(ingest: Ingest, data: dict):
    return [
        data["street"], data["city"], data["state"], data["zip"], data["owner_id"], data["name"],
        float(data["rating"]), int(data["price_category"]), data["phone"], int(data["is_active"]), data["picture"]
    ]


def get_csv_rows(path: str):
    rows = []
    with open(path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            rows.append(row)
    return rows


def test_try_resolve_csv_headers():
    ingest = Ingest("./app/data/restaurants-ingest-test.csv", rest_args, None, None, None)

    header = get_csv_rows(ingest.path)[0]
    [is_default, mapping] = ingest.try_resolve_csv_headers(header)
    assert is_default is False

    target = ['city', 'street', 'state', 'zip', 'owner_id', 'name', 'rating', 'price_category', 'phone', 'is_active',
              'picture']
    for i in range(len(target)):
        assert target[i] == mapping[i]


def test_parse_row():
    ingest = Ingest("./app/data/restaurants-ingest-test.csv", rest_args, None, None, handle_data)

    [header, row, *rows] = get_csv_rows(ingest.path)
    [is_default, mapping] = ingest.try_resolve_csv_headers(header)

    parsed = ingest.parse_row(row, 1, mapping)
    print(parsed)

    for i in range(len(csv_row_data)):
        assert csv_row_data[i] == parsed[i]


def test_handle_json():
    ingest = Ingest("./app/data/restaurants-ingest-test.json", rest_args, None, None, handle_data)
    parsed = ingest.handle_json()[0]

    for i in range(len(json_row_data)):
        assert json_row_data[i] == parsed[i]


def test_handle_csv():
    ingest = Ingest("./app/data/restaurants-ingest-test.csv", rest_args, None, None, handle_data)
    parsed = ingest.handle_csv()[0]

    for i in range(len(csv_row_data)):
        assert csv_row_data[i] == parsed[i]


def test_handle_xml():
    ingest = Ingest("./app/data/restaurants-ingest-test.xml", rest_args, None, None, handle_data)
    parsed = ingest.handle_xml()[0]

    for i in range(len(xml_row_data)):
        assert xml_row_data[i] == parsed[i]
