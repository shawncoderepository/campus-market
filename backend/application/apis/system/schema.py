from application.common.schema import SnakeCaseModel


class HealthRes(SnakeCaseModel):
    """健康检查响应数据。"""

    service_name: str
    service_status: str


class VersionRes(SnakeCaseModel):
    """版本信息响应数据。"""

    version: str
