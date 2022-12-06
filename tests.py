import datetime
from bot_package.crypto import assign_time


class TestTimeAssigment:
    y, m, d = 2020, 12, 5

    def test_every_24_hours(self):
        time = datetime.datetime(self.y, self.m, self.d, 8)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)

        assert assign_time(time, 1) == res_time

    def test_every_12_hours(self):
        time = datetime.datetime(self.y, self.m, self.d, 8)
        res_time = datetime.datetime(self.y, self.m, self.d, 12)
        assert assign_time(time, 2) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 13)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 2) == res_time

    def test_every_6_hours(self):
        time = datetime.datetime(self.y, self.m, self.d, 8)
        res_time = datetime.datetime(self.y, self.m, self.d, 12)
        assert assign_time(time, 3) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 19)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 3) == res_time

    def test_every_3_hours(self):
        time = datetime.datetime(self.y, self.m, self.d, 8)
        res_time = datetime.datetime(self.y, self.m, self.d, 9)
        assert assign_time(time, 4) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 22)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 4) == res_time

    def test_every_hour(self):
        time = datetime.datetime(self.y, self.m, self.d, 4)
        res_time = datetime.datetime(self.y, self.m, self.d, 5)
        assert assign_time(time, 5) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 23)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 5) == res_time

    def test_every_30_minutes(self):
        time = datetime.datetime(self.y, self.m, self.d, 4, 8)
        res_time = datetime.datetime(self.y, self.m, self.d, 4, 30)
        assert assign_time(time, 6) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 23, 32)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 6) == res_time

    def test_every_15_minutes(self):
        time = datetime.datetime(self.y, self.m, self.d, 4, 32)
        res_time = datetime.datetime(self.y, self.m, self.d, 4, 45)
        assert assign_time(time, 7) == res_time

        time = datetime.datetime(self.y, self.m, self.d, 23, 48)
        res_time = datetime.datetime(self.y, self.m, self.d+1, 0)
        assert assign_time(time, 7) == res_time







