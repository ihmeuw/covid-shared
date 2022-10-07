"""Primitives for construction jobmon workflows."""
import abc
import functools
from pathlib import Path
from typing import Dict, Type, TypeVar

from loguru import logger

from covid_shared import paths
from covid_shared.ihme_deps import Task, WorkflowRunStatus
from covid_shared.workflow.specification import TaskSpecification, WorkflowSpecification
from covid_shared.workflow.utilities import JobmonTool, get_cluster_name, make_log_dirs


class TaskTemplate(abc.ABC):
    """Factory class for a parameterized task.

    Subclasses are intended to inherit and provide string templates for the
    class variables ``task_name_template`` which will construct cluster
    job names from the task args and ``command_template`` which will
    resolve the task args into a job executable by bash.

    """

    task_name_template: str
    command_template: str
    node_args: list
    task_args: list
    tool: JobmonTool

    def __init__(self, name: str, task_specification: TaskSpecification):
        self.jobmon_template = self.tool.get_task_template(
            template_name=name,
            command_template=self.command_template,
            node_args=self.node_args,
            task_args=self.task_args,
        )
        self.params = task_specification.to_dict()

    def get_task(self, *_, **kwargs) -> Task:
        """Resolve job arguments into a bash executable task for jobmon."""
        task = self.jobmon_template.create_task(
            compute_resources=self.params,
            name=self.task_name_template.format(**kwargs),
            max_attempts=1,
            **kwargs,
        )
        return task


TTaskTemplate = TypeVar("TTaskTemplate", bound=TaskTemplate)


class WorkflowTemplate(abc.ABC):
    """Factory for building and running workflows from specifications.

    Subclasses are intended to inherit and provide a string template for the
    class variable ``workflow_name_template`` which takes an output version
    string and maps it to a unique workflow name, and a dictionary mapping
    task type names to concrete subclasses of the ``TaskTemplate`` base
    class as the ``task_template_classes`` class variable. This mapping
    is tightly coupled with the ``tasks`` mapping of the associated
    workflow specification (ie, they should have exactly the same keys).

    When instantiated, the ``WorkflowTemplate`` subclasses will
    produce a jobmon workflow from the provided workflow specification,
    set up output logging directories, and produce concrete templates for
    workflow tasks.

    Subclass implementers must provide an implementation of ``attach_tasks``
    which takes relevant model parameters as arguments and builds and attaches
    an appropriate task dag to the jobmon workflow.

    """

    tool: JobmonTool
    workflow_name_template: str = None
    task_template_classes: Dict[str, Type[TTaskTemplate]]
    fail_fast: bool = True

    def __init__(self, version: str, workflow_specification: WorkflowSpecification):
        self.version = version
        assert workflow_specification.tasks.keys() == self.task_template_classes.keys()
        self.task_templates = self.build_task_templates(
            workflow_specification.task_specifications
        )

        stdout, stderr = make_log_dirs(Path(version) / paths.LOG_DIR)

        cluster = get_cluster_name()

        resources = {
            "stdout": stdout,
            "stderr": stderr,
            "project": workflow_specification.project,
        }

        self.workflow = self.tool.create_workflow(
            name=self.workflow_name_template.format(version=version),
            default_cluster_name=cluster,
            default_compute_resources_set={
                cluster: resources,
            },
        )

        ##############
        # GROSS HACK #
        ##############
        # workflow.run no longer gives back a workflow status, which means
        # we can't get the workflow run id to log on a failure. This patches
        # one of the internal methods that generates a workflow run to hang
        # onto the workflow run id as an attribute of the workflow.
        old_create_workflow_run = self.workflow._create_workflow_run

        @functools.wraps(old_create_workflow_run)
        def _my_create_workflow_run(*args, **kwargs):
            # Call __func__ so we don't get two copies of self.
            client_wfr = old_create_workflow_run.__func__(*args, **kwargs)
            self.workflow.workflow_run_id = client_wfr.workflow_run_id
            return client_wfr

        self._monkey_patch_method(
            original_method=old_create_workflow_run,
            new_method=_my_create_workflow_run,
        )

    @staticmethod
    def _monkey_patch_method(original_method, new_method):
        # Invoke the descriptor protocol to bind the wrapped method to the
        # component instance.
        rebound_method = new_method.__get__(
            original_method.__self__,
            original_method.__self__.__class__,
        )
        # Then update the instance dictionary to reflect that the wrapped
        # method is bound to the original name.
        setattr(original_method.__self__, original_method.__name__, rebound_method)

    def build_task_templates(
        self, task_specifications: Dict[str, TaskSpecification]
    ) -> Dict[str, TaskTemplate]:
        """Parses task specifications into task templates."""
        task_templates = {}
        for task_name, task_specification in task_specifications.items():
            task_templates[task_name] = self.task_template_classes[task_name](
                task_name, task_specification
            )
        return task_templates

    @abc.abstractmethod
    def attach_tasks(self, *args, **kwargs) -> None:
        """Turn model arguments into jobmon workflow tasks."""
        pass

    def run(self) -> None:
        """Execute the constructed workflow."""
        try:
            r = self.workflow.run(
                fail_fast=self.fail_fast,
                seconds_until_timeout=60 * 60 * 24,
            )
        except RuntimeError:
            # fail_fast now induces a runtime error instead of returning an error
            # status, which is unexpected behavior.  Patch around this for now.
            r = WorkflowRunStatus.ERROR
        if r != WorkflowRunStatus.DONE:
            raise RuntimeError(
                f"Workflow failed with status {r}.\n"
                f"Workflow run id: {self.workflow.workflow_run_id}."
            )
