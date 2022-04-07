class CommandResponse:
    def __init__(self, is_ok: bool, message: str = None) -> None:
        self.is_ok = is_ok
        self.message = message

    def ok(self) -> bool:
        return self.is_ok
