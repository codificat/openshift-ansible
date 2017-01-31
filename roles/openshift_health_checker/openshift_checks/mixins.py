from openshift_checks import OpenShiftCheckException


class NotContainerized(object):
    """Mixin for checks that are only active when not in containerized mode."""

    @classmethod
    def is_active(cls, task_vars):
        return (
            super(NotContainerized, cls).is_active(task_vars)
            and not cls.is_containerized(task_vars)
        )

    @staticmethod
    def is_containerized(task_vars):
        try:
            return task_vars["openshift"]["common"]["is_containerized"]
        except (KeyError, TypeError):
            raise OpenShiftCheckException("'openshift.common.is_containerized' is undefined")
