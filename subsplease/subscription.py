from subsplease.utils import Program
from subsplease.db import LocalShow
from subsplease.display import display_subs


class SubscriptionService:
    def __init__(self, program: Program):
        self.program = program

    def get_subs(self) -> list[LocalShow]:
        return [x for x in self.program.current.values() if x.tracking]

    def show_subs(self):
        display_subs(self.get_subs())
