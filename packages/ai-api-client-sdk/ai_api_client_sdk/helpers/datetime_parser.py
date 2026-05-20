from datetime import datetime, timezone

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
DATETIME_FORMAT_FLOAT = '%Y-%m-%dT%H:%M:%S.%fZ'
DATETIME_FORMAT_36 = "%Y-%m-%dT%H:%M:%S+00:00"
DATETIME_FORMAT_FLOAT_TZ = '%Y-%m-%dT%H:%M:%S.%f+00:00'


def parse_datetime(datetime_str: str) -> datetime:
    try:
        parsed_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT_36)
    except ValueError as _:
        try:
            parsed_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT)
        except ValueError as _:
            try:
                parsed_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT_FLOAT)
            except ValueError as _:
                if len(datetime_str) > 32:
                    datetime_str = f'{datetime_str[:26]}{datetime_str[29:]}'
                parsed_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT_FLOAT_TZ)
    if not parsed_datetime.tzinfo:
        parsed_datetime = datetime(year=parsed_datetime.year, month=parsed_datetime.month, day=parsed_datetime.day,
                                   hour=parsed_datetime.hour, minute=parsed_datetime.minute,
                                   second=parsed_datetime.second, microsecond=parsed_datetime.microsecond,
                                   tzinfo=timezone.utc)
    return parsed_datetime
