import sys
import os

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()

from ansible.plugins.action import ActionBase

# Augment sys.path so that we can import checks from a directory relative to
# this callback plugin.
sys.path.insert(1, os.path.dirname(os.path.dirname(__file__)))

from openshift_checks import OpenShiftCheck, OpenShiftCheckException


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
