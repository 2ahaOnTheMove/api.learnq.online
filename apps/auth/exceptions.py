from uuid import UUID


class AccountNotVerifiedError(Exception):
    def __init__(self, token: UUID):
        self.token = token
        super().__init__("Please verify your email address before logging in.")
