import re
from typing import List, Union

__all__ = ("validate_config_params",)


def validate_config_params(project_id: str, report_id: Union[str, None]) -> List[str]:
    errors = []

    project_pattern = re.compile(r"[a-z][a-z0-9-]{2,39}")
    if project_pattern.match(project_id) is None:
        errors.append(f"Invalid project_id: {project_id!r} does not match pattern "
                      f"{project_pattern.pattern!r}")

    report_pattern = re.compile(r".{1,40}")
    if (report_id is not None) and (report_pattern.match(report_id) is None):
        errors.append(f"Invalid report_id: {report_id!r} does not match pattern "
                      f"{report_pattern.pattern!r}")

    return errors
