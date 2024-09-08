from pydantic import BaseModel


class VerificationCodeRequestSchema(BaseModel):
    device_verification_code: str
