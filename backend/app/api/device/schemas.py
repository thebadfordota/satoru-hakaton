from uuid import UUID

from pydantic import BaseModel


class ActivateDeviceResponseSchema(BaseModel):
    device_id: UUID
