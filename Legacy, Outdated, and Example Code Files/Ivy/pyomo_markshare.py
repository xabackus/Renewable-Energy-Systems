ERROR: No output file or format specified!

usage: pyomo convert [options] <model_or_config_file> [<data_files>]

positional arguments:
  model_or_config_file  A Python module that defines a Pyomo model, or a
                        configuration file that defines options for 'pyomo
                        convert' (in either YAML or JSON format)
  data_files            Pyomo data files that defined data used to initialize
                        the model (specified in the first argument)

options:
  -h, --help            show this help message and exit
  --generate-config-template TEMPLATE
                        Create a configuration template file in YAML or JSON
                        and exit.
  --output FILENAME     Output file name. This option is required unless the
                        file name is specified in a configuration file.
  --format FORMAT       Output format
  --namespace NAMESPACES
                        A namespace that is used to select data in Pyomo data
                        files.
  --model-name MODEL_NAME
                        The name of the model object that is created in the
                        specified Pyomo module
  --symbolic-solver-labels
                        When interfacing with the solver, use symbol names
                        derived from the model. For example,
                        "my_special_variable[1_2_3]" instead of "v1". Useful
                        for debugging. When using the ASL interface (--solver-
                        io=nl), generates corresponding .row (constraints) and
                        .col (variables) files. The ordering in these files
                        provides a mapping from ASL index to symbolic model
                        names.
  --file-determinism FILE_DETERMINISM
                        When interfacing with a solver using file based I/O,
                        set the effort level for ensuring the file creation
                        process is determistic. See the individual solver
                        interfaces for valid values and default level of file
                        determinism.
  --transform TRANSFORMATIONS
                        List of model transformations
  --preprocess PREPROCESS
                        Specify a Python module that gets immediately executed
                        (before the optimization model is setup).
  --logging LEVEL       Logging level: quiet, warning, info, verbose, debug
  --logfile FILE        Redirect output to the specified file.
  -c, --catch-errors    Trigger failures for exceptions to print the program
                        stack.
  --disable-gc          Disable the garbage collecter.
  -k, --keepfiles       Keep temporary files
  --path PATH           Give a path that is used to find the Pyomo python
                        files.
  --profile-count COUNT
                        Enable profiling of Python code. The value of this
                        option is the number of functions that are summarized.
  --report-timing       Report various timing statistics during model
                        construction.
  --tempdir TEMPDIR     Specify the directory where temporary files are
                        generated.

Description:

The 'pyomo convert' subcommand converts a Pyomo model into a specified
format.  The --output option is used to specify an output file.
If only the --format option is specified, then the output filename is
unknown.<format>.  The standard steps executed by this subcommand are:

  - Apply pre-solve operations (e.g. import Python packages)
  - Create the model
  - Apply model transformations

This subcommand can be executed with or without a configuration file.
For example:

  pyomo convert --output=model.lp model.py model.dat

This creates the file 'model.lp' with format 'lp'.

A yaml or json configuration file can also be used to specify conversion
options.  For example:

  pyomo convert config.yaml

No other command-line options are required!

A template configuration file can be generated with the
'--generate-config-template' option:

  pyomo convert --generate-config-template=template.yaml
  pyomo convert --generate-config-template=template.json

Note that yaml template files contain comments that describe the
configuration options.  Also, configuration files will generally support
more configuration options than are available with command-line options.
