from dataclasses import dataclass


@dataclass
class Appointment(object):
    tag: str
    uhrzeit: str

    def pretty_print_one_line(self):
        return f"am {self.tag} um {self.uhrzeit}\n"

    def same_day(self, otherApp):
        return self.day == otherApp.day
