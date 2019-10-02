import datetime


class MockEmployee():
    def __init__(self, id_gen):
        self.shift_date = []
        self.id = id_gen
        self.pattern_start_date = None
        self.non_pattern_dates = {}

    def add_shifts(self, start_date, block_length):
        shift_block = []
        current_date = start_date
        for i in range(block_length):
            shift_block.append(current_date)
            current_date = current_date + datetime.timedelta(days=1)
        self.shift_date.extend(shift_block)

    def add_day_shift(self, start_date):
        self.shift_date.append(start_date)

    def clear_schedule(self):
        self.shift_date = []


def id_generator():
    start_num = 0
    while True:
        yield start_num
        start_num += 1


def create_employee(num):
    id_gen = id_generator()
    return [MockEmployee(id_gen=next(id_gen)) for _ in range(num)]