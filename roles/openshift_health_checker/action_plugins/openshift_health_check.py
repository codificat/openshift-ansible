from abc import ABCMeta, abstractmethod, abstractproperty

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)

        if task_vars is None:
            task_vars = {}

        if "openshift" not in task_vars:
            result["failed"] = True
            result["msg"] = "'openshift' is undefined, did 'openshift_facts' run?"
            return result

        try:
            known_checks = self.load_known_checks(task_vars)
        except OpenShiftCheckException as e:
            result["failed"] = True
            result["msg"] = e.message
            return result

        args = self._task.args
        requested_checks = set(args.get("checks", []))

        unknown_checks = requested_checks - set(known_checks)
        if unknown_checks:
            result["failed"] = True
            result["msg"] = (
                "One or more checks are unknown: {}. "
                "Make sure there is no typo in the playbook and no files are missing."
            ).format(", ".join(unknown_checks))
            return result

        result["checks"] = check_results = {}

        for check_name in requested_checks & set(known_checks):
            display.banner("CHECK [{} : {}]".format(check_name, task_vars["ansible_host"]))
            check = known_checks[check_name]

            if check.is_active(task_vars):
                try:
                    r = check.run(tmp, task_vars)
                except OpenShiftCheckException as e:
                    r = {}
                    r["failed"] = True
                    r["msg"] = e.message
            else:
                r = {"skipped": True}

            check_results[check_name] = r

            if r.get("failed", False):
                result["failed"] = True
                result["msg"] = "One or more checks failed"

        return result

    def load_known_checks(self, task_vars):
        known_checks = {}

        known_check_classes = set(cls for cls in OpenShiftCheck.subclasses())

        for cls in known_check_classes:
            check_name = cls.name
            if check_name in known_checks:
                other_cls = known_checks[check_name].__class__
                raise OpenShiftCheckException(
                    "non-unique check name '{}' in: '{}.{}' and '{}.{}'".format(
                        check_name,
                        cls.__module__, cls.__name__,
                        other_cls.__module__, other_cls.__name__))
            known_checks[check_name] = cls(module_executor=self._execute_module)

        return known_checks


class OpenShiftCheckException(Exception):
    pass


class OpenShiftCheck(object):
    """A base class for defining checks for an OpenShift cluster environment."""

    __metaclass__ = ABCMeta

    def __init__(self, module_executor):
        self.module_executor = module_executor

    @abstractproperty
    def name(self):
        """The name of this check, usually derived from the class name."""
        return "openshift_check"

    @classmethod
    def is_active(cls, task_vars):
        """Returns true if this check applies to the ansible-playbook run."""
        return True

    @abstractmethod
    def run(self, tmp, task_vars):
        """Executes a check, normally implemented as a module."""
        return {}

    @classmethod
    def subclasses(cls):
        """Returns a generator of subclasses of this class and its subclasses."""
        for subclass in cls.__subclasses__():
            yield subclass
            for subclass in subclass.subclasses():
                yield subclass


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


class PackageAvailability(NotContainerized, OpenShiftCheck):
    """Check that required RPM packages are available."""

    name = "package_availability"

    def run(self, tmp, task_vars):
        try:
            rpm_prefix = task_vars["openshift"]["common"]["service_type"]
        except (KeyError, TypeError):
            raise OpenShiftCheckException("'openshift.common.service_type' is undefined")

        group_names = task_vars.get("group_names", [])

        packages = set()

        if "masters" in group_names:
            packages.update(self.master_packages(rpm_prefix))
        if "nodes" in group_names:
            packages.update(self.node_packages(rpm_prefix))

        args = {"packages": sorted(set(packages))}
        return self.module_executor("check_yum_update", args, tmp, task_vars)

    @staticmethod
    def master_packages(rpm_prefix):
        return [
            "{rpm_prefix}".format(rpm_prefix=rpm_prefix),
            "{rpm_prefix}-clients".format(rpm_prefix=rpm_prefix),
            "{rpm_prefix}-master".format(rpm_prefix=rpm_prefix),
            "bash-completion",
            "cockpit-bridge",
            "cockpit-docker",
            "cockpit-kubernetes",
            "cockpit-shell",
            "cockpit-ws",
            "etcd",
            "httpd-tools",
        ]

    @staticmethod
    def node_packages(rpm_prefix):
        return [
            "{rpm_prefix}".format(rpm_prefix=rpm_prefix),
            "{rpm_prefix}-node".format(rpm_prefix=rpm_prefix),
            "{rpm_prefix}-sdn-ovs".format(rpm_prefix=rpm_prefix),
            "bind",
            "ceph-common",
            "dnsmasq",
            "docker",
            "firewalld",
            "flannel",
            "glusterfs-fuse",
            "iptables-services",
            "iptables",
            "iscsi-initiator-utils",
            "libselinux-python",
            "nfs-utils",
            "ntp",
            "openssl",
            "pyparted",
            "python-httplib2",
            "PyYAML",
            "yum-utils",
        ]


class PackageUpdate(NotContainerized, OpenShiftCheck):
    """Check that there are no conflicts in RPM packages."""

    name = "package_update"

    def run(self, tmp, task_vars):
        args = {"packages": []}
        return self.module_executor("check_yum_update", args, tmp, task_vars)


class PackageVersion(NotContainerized, OpenShiftCheck):
    """Check that available RPM packages match the required versions."""

    name = "package_version"

    @classmethod
    def is_active(cls, task_vars):
        return (
            super(PackageVersion, cls).is_active(task_vars)
            and task_vars.get("deployment_type") == "openshift-enterprise"
        )

    def run(self, tmp, task_vars):
        try:
            openshift_release = task_vars["openshift_release"]
        except (KeyError, TypeError):
            raise OpenShiftCheckException("'openshift_release' is undefined")

        args = {"version": openshift_release}
        return self.module_executor("aos_version", args, tmp, task_vars)
