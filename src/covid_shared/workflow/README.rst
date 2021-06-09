Jobmon Workflows for the IHME COVID-19 Pipeline
-----------------------------------------------

.. warning::

   These tools are only for internal use on the IHME cluster as jobmon
   is not yet open-source.

.. contents::

This subpackage provides wrappers around internal jobmon tooling for workflow
creation. The motivating use case are the pipeline stages in the
`SEIR package <https://github.com/ihmeuw/covid-model-seiir-pipeline>`_ where
stages are launched from a command line utility and parameterized with a
yaml-based model specification. These tools can be configured directly in
the python code, though it'll be a little awkward.

You can find the main jobmon documentation
`here <https://scicomp-docs.ihme.washington.edu/jobmon/current/index.html>`_.

Step 1 - Make a tool version
++++++++++++++++++++++++++++

When building a new tool that uses jobmon, you must first register it with the
jobmon databases.  To do this, open a python interpreter on the cluster
in an environment that has jobmon installed and do

.. code-block:: python

   from jobmon.client.api import Tool
   t = Tool.create_tool(name=MY_PACKAGE_NAME)
   t.create_new_tool_version()

This will return an integer value that you should write down.  We'll use it shortly.

.. note::

   `MY_PACKAGE_NAME` should be the name of the python package you are building.
   **Package names are underscore-separated.  They are what you would type if you
   were doing an `import MY_PACKAGE_NAME` in a python file**.

Step 2 - Update your package metadata
+++++++++++++++++++++++++++++++++++++

I'm presuming you're using the `src` package layout with the `__about__.py` convention
for package metadata. Your package should look like:

::

   ROOT/
       src/
           MY_PACKAGE_NAME/
               __about__.py
               __init__.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...

In your `__about__.py` file, you should add a new dunder-attribute called
`__jobmon_tool_version__` and set it equal to the integer value you got back from
making a new jobmon tool version in step 1. For example, the `__about__.py` file in
the SEIR pipeline looks like

.. code-block:: python

    __all__ = [
        "__title__",
        "__summary__",
        "__uri__",
        "__version__",
        "__jobmon_tool_version__",
        "__author__",
        "__email__",
        "__license__",
        "__copyright__",
    ]

    __title__ = "covid-model-seiir-pipeline"
    __summary__ = "Execution Pipeline for the IHME COVID-19 SEIIR Model."
    __uri__ = "https://github.com/ihmeuw/covid-model-seiir-pipeline"

    __version__ = "0.1.0"
    __jobmon_tool_version__ = 15

    __author__ = "The IHME Covid Modeling Team"
    __email__ = "uw_ihme_covid-eng@uw.edu"

    __license__ = "BSD 3-clause"
    __copyright__ = f"Copyright 2020 {__author__}"

If you want to use jobmon tool versioning for any performance tracking, you can
generate a new version when your pipeline stage has any significant changes. This
is not required, though.

.. note::

   Be sure your package `__init__.py` also has a `from .__about__ import *` in it.
   Otherwise none of th package attributes will be available in the package namespace.

Step 3 - Make a task
++++++++++++++++++++

To our package, we'll add a new file called `my_task.py`

::

   ROOT/
       src/
           MY_PACKAGE_NAME/
               __about__.py
               __init__.py
               my_task1.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...

Our task should have something like the following structure

.. code-block:: python

   import click
   from covid_shared import cli_tools
   from loguru import logger

   def my_task_main(output_version: str, draw: int):
       # Your business logic here
       ...

   @click.command()
   @click.option('output_version', type=click.STRING)
   @click.option('draw', type=click.INT)
   @cli_tools.add_verbose_and_with_debugger
   def my_task1(output_version: str, draw: int, verbose: int, with_debugger: bool):
       cli_tools.configure_logging_to_terminal(verbose)
       run_my_task = cli_tools.handle_exceptions(my_task_main, logger, with_debugger)
       run_my_task(output_version, draw)

For the remaining steps, we'll presume your workflow is made up of three distinct
kinds of tasks which you've written following the above template. So your package layout
looks like

::

   ROOT/
       src/
           MY_PACKAGE_NAME/
               __about__.py
               __init__.py
               my_task1.py
               my_task2.py
               my_task3.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...


Step 4 - Add the entry points to the setup.py
++++++++++++++++++++++++++++++++++++++++++++++

In order to make your commands runnable when you install the package, we need to
update the `setup.py` to include the entry points.

.. code-block:: python

    import os

    from setuptools import setup, find_packages


    if __name__ == "__main__":
        base_dir = os.path.dirname(__file__)
        src_dir = os.path.join(base_dir, "src")

        about = {}
        with open(os.path.join(src_dir, YOUR_PACKAGE_NAME, "__about__.py")) as f:
            exec(f.read(), about)

        with open(os.path.join(base_dir, "README.rst")) as f:
            long_description = f.read()

        install_requirements = [
            ... your public dependencies ..
        ]

        test_requirements = [
            'pytest',
            'pytest-mock',
        ]

        internal_requirements = [
            .. your internal dependencies ..
        ]

        setup(
            name=about['__title__'],
            version=about['__version__'],

            description=about['__summary__'],
            long_description=long_description,
            license=about['__license__'],
            url=about["__uri__"],

            author=about["__author__"],
            author_email=about["__email__"],

            package_dir={'': 'src'},
            packages=find_packages(where='src'),
            include_package_data=True,

            install_requires=install_requirements,
            tests_require=test_requirements,
            extras_require={
                'test': test_requirements,
                'internal': internal_requirements,
                'dev': [test_requirements, internal_requirements]
            },

            # This is where we register your tasks.
            entry_points={'console_scripts': [
                'my_task1=MY_PACKAGE_NAME.my_task1:my_task1',
                'my_task2=MY_PACKAGE_NAME.my_task2:my_task2',
                'my_task3=MY_PACKAGE_NAME.my_task3:my_task3',
            ]},
            zip_safe=False,
        )

Step 5 - Add the task and workflow configuration
++++++++++++++++++++++++++++++++++++++++++++++++

Next we'll add another module to our package called `workflow.py`

::

   ROOT/
       src/
           YOUR_PACKAGE_NAME/
               __about__.py
               __init__.py
               my_task1.py
               my_task2.py
               my_task3.py
               workflow.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...

in which we'll use the tools defined in this subpackage.

.. code-block:: python

   import shutil
   from typing import NamedTuple

   from covid_shared import workflow

   import MY_PACKAGE_NAME


   class __MyTasks():
       """A container for string constants for the task names.

       You could skip this and use strings directly or use a dataclass or
       something.
       """
       my_task1: str = 'my_task1'
       my_task2: str = 'my_task2'
       my_task3: str = 'my_task3'


   MY_TASKS = __MyTasks()


   class MyTask1Specification(workflow.TaskSpecification):
       # There are only these three keys that need to be set.
       # The parent class is primary intended for validation and
       # serialization to and from dicts for easy parsing into yaml.
       default_max_runtime_seconds = 1000  # Maximum runtime of a task
       default_m_mem_free = '10G' # Maximum memory usage of a task
       default_num_cores = 1  # Number of processes the task uses.


   class MyTask2Specification(workflow.TaskSpecification):
       default_max_runtime_seconds = 5000
       default_m_mem_free = '2G'
       default_num_cores = 5


   class MyTask3Specification(workflow.TaskSpecification):
       default_max_runtime_seconds = 1500
       default_m_mem_free = '25G'
       default_num_cores = 20


   class MyWorkflowSpecification(workflow.WorkflowSpecification):
        # Only one thing needs to be set here, the mapping from task names
        # to their specification classes.  Again, the parent class here
        # is mainly about validation and serialization.
        tasks = {
            MY_TASKS.my_task1: MyTask1Specification,
            MY_TASKS.my_task2: MyTask2Specification,
            MY_TASKS.my_task3: MyTask3Specification,
        }


   # Next we need the actual templates
   class MyTask1Template(workflow.TaskTemplate):
       # Just need to set some class constants

       # Grab a reference to the jobmon tool that the template can use to make tasks.
       # See import at top of module
       tool = workflow.get_jobmon_tool(MY_PACKAGE_NAME)
       # These are the names of the arguments passed to your task.
       # task_args do not vary across tasks. You'd use them for something like
       # shared configuration or a common output directory.
       task_args = ['output_version']
       # node_args do vary between tasks. They are the args you're parallelizing by.
       node_args = ['draw']
       # This is the template for how the jobs submitted to the cluster
       # will be named.  I recommend you put your node args in this to make
       # e.g. querying qpid easier. Use double braces to produce a string
       # that can be appropriately interpolated when the task is actually made.
       task_name_template = f"{MY_TASKS.my_task1}_task_arg2_{{task_arg2}}"
       # This is the command as you would invoke it yourself in a qlogin,
       # parameterized by the task and node args.
       command_template = (
           # Resolve full path to executible. This will handle some environment compatibility issues.
           f'{shutil.which("my-task-1")} '
           '--task-arg1 {task_arg1} '
           '--task-arg2 {task_arg2} '
           '-vv'
       )


   class MyTask2Template(workflow.TaskTemplate):
       # Fill in same class constants
       ...


   class MyTask2Template(workflow.TaskTemplate):
       # Fill in same class constants
       ...


   class MyWorkflow(workflow.WorkflowTemplate):
       # Also need a reference here for making workflow objects.
       tool = workflow.utilities.get_jobmon_tool(covid_model_seiir_pipeline)
       # Template for how workflows will be named in the jobmon db.
       # Change the prefix to something descriptive, but leave the '-{version}'.
       workflow_name_template = 'my-workflow-{version}'
       # Here we link names to task templates instead of specifications.
       task_template_classes = {
            MY_TASKS.my_task1: MyTask1Template,
            MY_TASKS.my_task2: MyTask2Template,
            MY_TASKS.my_task3: MyTask3Template,
       }
       # Whether the workflow will stop when a single job fails. Generally,
       # set true if your tasks are mostly homogeneous (and therefore likely to
       # fail due to code errors) and false otherwise.
       fail_fast = False

       # The method name is fixed but the args in this method are whatever
       # you need them to be.
       def attach_tasks(self, location_ids: List[int], n_draws: int):
           # This method is totally bespoke per workflow and is where we
           # construct our task dag. For this example, we'll presume task 1
           # in our workflow is parallelized by draw, task 2 is a validation step
           # with no parallelization that happens after task 1, and task 3
           # is parallelized by location, but doesn't depend on either of the other
           # tasks.

           # unpack our templates
           task1_template = self.task_templates[MY_TASKS.my_task1]
           task2_template = self.task_templates[MY_TASKS.my_task2]
           task3_template = self.task_templates[MY_TASKS.my_task3]

           task2 = task2_template.get_task(
               output_version=self.version,
           )
           self.workflow.add_task(task2)
           for draw in range(n_draws):
               task1 = task1_template.get_task(
                   output_version=self.version,
                   draw=draw,
               )
               task1.add_downstream(task2)
               self.workflow.add_task(task1)

           for location_id in location_ids:
               task3 = task3_template.get_task(
                   output_version=self.version,
                   location_id=location_id,
               )
               self.workflow.add_task(task3)


Step 6 - Write your application main
++++++++++++++++++++++++++++++++++++

Next we'll write the application main to build the workflow.  We'll just put it in
`main.py`.

::

   ROOT/
       src/
           YOUR_PACKAGE_NAME/
               __about__.py
               __init__.py
               main.py
               my_task1.py
               my_task2.py
               my_task3.py
               workflow.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...


.. code-block:: python

   from covid_shared import cli_tools, ihme_deps
   from loguru import logger

   from MY_PACKAGE_NAME.workflow import MyWorkflowSpecification, MyWorkflow

   def run_my_workflow(app_metadata: cli_tools.Metadata,
                       output_version: str,
                       n_draws: int,
                       location_set_version_id: int):
      logger.info(f'Starting my worklfow {output_version}')

      # This is a very good spot to do any precondition checking if you can.
      # Much better to fail here where you can produce intelligible errors.

      hierarchy = ihme_deps.load_location_hierarchy(location_set_version_id)
      location_ids = hierarchy[hierarchy.most_detailed == 1].location_id.unique().tolist()

      # We might build this from a configuration file in a more complicated
      # application to allow overrides of the defaults. Here, we've written
      # our parameterization in code.
      my_workflow_specification = MyWorkflowSpecification()
      my_workflow = MyWorkflow(
          version=output_version,
          workflow_specification=my_workflow_specification,
      )
      my_workflow.attach_tasks(
          n_draws=n_draws,
          location_ids=location_ids,
      )
      my_workflow.run()


Step 7 - Write your CLI
+++++++++++++++++++++++

Finally, we wrap the application main in a command line utility using the standard
tooling.  We'll stick this in `cli.py`.

::

   ROOT/
       src/
           YOUR_PACKAGE_NAME/
               __about__.py
               __init__.py
               cli.py
               main.py
               my_task1.py
               my_task2.py
               my_task3.py
               workflow.py
               ...your modules and subpackages..
       tests/
           ...
       setup.py
       ...your package metadata files...

.. code-block:: python

   import click
   from covid_shared import cli_tools, paths
   from loguru import logger

   from MY_PACKAGE_NAME.main import run_my_workflow


   @click.command()
   @cli_tools.pass_run_metadata()
   @click.option('--location-set-version-id', type=click.INT)
   @click.option('--n_draws', type=click.INT)
   @cli_tools.add_output_options(paths.MY_OUTPUT_ROOT)
   @cli_tools.add_verbose_and_with_debugger
   def my_main_entry_point(run_metadata: cli_tools.RunMetadata,
                           location_set_version_id: int,
                           n_draws: int,
                           output_root: str, mark_best: bool, production_tag: str,
                           verbose: int, with_debugger):
       cli_tools.configure_logging_to_terminal(verbose)

       output_root = Path(output_root).resolve()
       cli_tools.setup_directory_structure(output_root, with_production=True)
       run_directory = cli_tools.make_run_directory(output_root)

       run_metadata['output_root'] = str(run_directory)

       main = cli_tools.monitor_application(run_my_workflow, logger, with_debugger)
       app_metadata, _ = main(run_directory, location_set_version_id, n_draws)

       cli_tools.finish_application(run_metadata, app_metadata, run_directory,
                                    mark_best, production_tag)


We'll also need to update our `setup.py` to include the new entry point:

.. code-block:: python

    import os

    from setuptools import setup, find_packages


    if __name__ == "__main__":
        ...

        setup(
            ...
            entry_points={'console_scripts': [
                'my_task1=MY_PACKAGE_NAME.my_task1:my_task1',
                'my_task2=MY_PACKAGE_NAME.my_task2:my_task2',
                'my_task3=MY_PACKAGE_NAME.my_task3:my_task3',
                'my_cli=MY_PACKAGE_NAME.cli:my_main_entry_point',
            ]},
            ...
        )


