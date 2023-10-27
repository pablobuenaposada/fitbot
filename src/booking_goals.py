import yaml

from exceptions import InvalidBookingGoals


def transform_yaml_to_dict(booking_goals_yaml):
    try:
        data = yaml.safe_load(booking_goals_yaml)
        booking_goals_dict = {}
        day_mapping = {
            "monday": "0",
            "tuesday": "1",
            "wednesday": "2",
            "thursday": "3",
            "friday": "4",
            "saturday": "5",
            "sunday": "6",
        }

        for day, schedule in data.items():
            day_key = day.lower()
            if day_key in day_mapping:
                for time, name in schedule.items():
                    time = time.replace(":", "").replace(" ", "")
                    booking_goals_dict[day_mapping[day_key]] = {
                        "name": name,
                        "time": time,
                    }

    except Exception as e:
        raise InvalidBookingGoals(str(e))

    if not booking_goals_dict:
        raise InvalidBookingGoals("No valid booking goals provided")

    return booking_goals_dict
