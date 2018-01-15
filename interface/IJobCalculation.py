def get_helper_function( self, functionName ):

    """
    Return the function with functionName, which will be imported as a member
    of interface. The correct import path for the module containing all the
    helperfunctions has to be set here.
    """

    import aiida_vasp.interface.IBaseWorkchain as interface

    func = getattr(interface, functionName)

    return func
