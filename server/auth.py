from abc import ABC, abstractmethod
from enum import Enum

class AuthType(Enum):
    OTP = "otp"

# class AuthStrategy:
#     def __init__(self, auth_type: AuthType):
#         self.auth_type = auth_type

#     @abstractmethod
#     def validate(self, auth_value: str) -> bool:
#         raise NotImplementedError("This method should be overridden.")  

#     def supports(self, auth_type: str) -> bool:
#         return self.auth_type.value == auth_type
    
# class OTPAuthStrategy(AuthStrategy):
#     def __init__(self):
#         super().__init__(AuthType.OTP)

#     def validate(self, auth_value: str) -> bool:
#         # Implement OTP validation logic here
#         return True  # Placeholder implementation
    
# class Auth:
#     def __init__(self):
#         self.strategies = [
#             OTPAuthStrategy(),
#         ]

#     def get_strategy(self, auth_type: str) -> AuthStrategy:
#         for strategy in self.strategies:
#             if strategy.supports(auth_type):
#                 return strategy
#         raise ValueError(f"Unsupported auth type: {auth_type}")

    