from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SegmentType = Literal["LU", "P"]
PowerType = Literal["constant", "lighting"]
Manufacturer = Literal["Hikvision", "Dahua"]
SpectoVoltage = Literal["24V", "220V"]


class DirectionLanes(BaseModel):
    lanes: int = Field(ge=1, le=12, description="Количество полос на направление")


class RadarConfig(BaseModel):
    enabled: bool = False
    directions: list[DirectionLanes] = Field(default_factory=list)


class HrCameraConfig(BaseModel):
    enabled: bool = True
    directions: list[DirectionLanes] = Field(default_factory=lambda: [DirectionLanes(lanes=2)])


class SpectoConfig(BaseModel):
    enabled: bool = False
    quantity: int = Field(default=0, ge=0)
    voltage: SpectoVoltage | None = None


class LvmConfig(BaseModel):
    enabled: bool = True


class ApkConfiguration(BaseModel):
    label: str = ""
    segment: SegmentType
    power_type: PowerType
    apk_count: int = Field(ge=1, le=10000)
    specto_a: SpectoConfig = Field(default_factory=SpectoConfig)
    specto_b: SpectoConfig = Field(default_factory=SpectoConfig)
    radar: RadarConfig = Field(default_factory=RadarConfig)
    hr_camera: HrCameraConfig = Field(default_factory=HrCameraConfig)
    lvm: LvmConfig = Field(default_factory=LvmConfig)

    @model_validator(mode="after")
    def validate_specto_b_for_p(self) -> "ApkConfiguration":
        if (
            self.segment == "P"
            and self.specto_b.enabled
            and self.specto_b.quantity not in (0, 1, 2)
        ):
            raise ValueError("Specto B для перекрёстка: количество должно быть 1 или 2")
        return self


class ProjectRequest(BaseModel):
    name: str = "Новый проект"
    apk_version: str = "4.0"
    manufacturer: Manufacturer = "Hikvision"
    configurations: list[ApkConfiguration] = Field(min_length=1)


class ProjectSummary(BaseModel):
    name: str
    apk_version: str
    manufacturer: str
    configurations: list[dict]
    line_items: list[dict]
    consolidated: list[dict]
    total_cost_kzt: float | None
    missing_prices: int
