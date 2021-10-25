import pytest
import shutil

from pathlib import Path
from app.users.main import main
from test.users.common import TEST_DATA_DIR


def test_main_produce_random_called_with_correct_arguments(monkeypatch, test_kwargs):
    monkeypatch.setattr('app.users.producer.UsersProducer.produce_random', test_kwargs)

    main(['produce', '--all', '5'])
    assert test_kwargs.args == {'num_custs': 5, 'num_drivers': 5, 'num_admins': 5, 'num_emps': 5}

    main(['produce', '--custs', '1', '--drivers', '2', '--admins', '3', '--emps', '4'])
    assert test_kwargs.args == {'num_custs': 1, 'num_drivers':  2, 'num_admins': 3, 'num_emps': 4}


def test_main_convert_file_does_not_exist(capsys):
    with pytest.raises(SystemExit):
        main(['ingest', '--convert', 'nonexistent_file.csv', 'output.json'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output


def test_main_convert_called_with_correct_arguments(monkeypatch, test_kwargs):
    monkeypatch.setattr('app.users.producer.UsersProducer.convert_files', test_kwargs)
    Path(TEST_DATA_DIR).mkdir(parents=True, exist_ok=True)
    test_file = f"{TEST_DATA_DIR}/users-test.csv"
    with open(test_file, 'w') as f:
        pass

    main(['ingest', '--convert', test_file, 'output.json'])
    assert test_kwargs.args == {'in_file': test_file, 'out_file': 'output.json'}

    shutil.rmtree(TEST_DATA_DIR)


def test_main_ingest_files_do_not_exist(capsys):
    with pytest.raises(SystemExit):
        main(['ingest', '--csv', 'nonexistent_file.csv'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.csv does not exist.' in output

    with pytest.raises(SystemExit):
        main(['ingest', '--json', 'nonexistent_file.json'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.json does not exist.' in output

    with pytest.raises(SystemExit):
        main(['ingest', '--xml', 'nonexistent_file.xml'])

    output = capsys.readouterr().out
    assert 'nonexistent_file.xml does not exist.' in output
