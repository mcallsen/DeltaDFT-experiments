   
def validate_calculation_and_interfaces(workchain, interface):
    """
    Checks whether the plugin providing the calculation implments all the required
    methods defined in the interface and sets the corresponding attributes in the
    workchain.

    :param workchain: The instance of the workchain from which validate_interface
                      has been called.
    :param calculation: The Calculation class used in the workchain.
    :param interface: The interface which has to be implemented.
    """

    if workchain._calculation_class is None or not issubclass(workchain._calculation_class, JobCalculation):
        raise ValueError('no valid JobCalculation class defined for the _calculation_class attribute of {}'.format(workchain.__name__))

    try:
        get_helper_function = workchain._calculation_class.get_helper_function
    except:
        workchain.abort_nowait('The JobCalculation {} does not implement the interface required by aiida_workchain.interface.IJobCalculation'.format(_plugin_name))

    for method in dir(interface):

        methodName = method.__name__
        try:
            setattr(workchain, methodName, get_helperfunction( methodName ))
        except:
            workchain.abort_nowait('The interface {} provided by the plugin does not implement the interface required by aiida_workchain.interface.{}'.format(interface.__name__)) 
