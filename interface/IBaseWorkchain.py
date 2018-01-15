from aiida.common.extendeddicts import AttributeDict


def set_defaults():

    """
    Set default values for your calculation. These will be required e.g. by the
    error handlers for resetting parameters back to defaults in case that a 
    modification of the input parameters did not fix the actual problem.
    """

    defaults = AttributeDict( {} )

    return defaults
   

def prepare_plugin_specific_inputs( self ):

    """
    Set the plugin specific cards of the inputs dictionary which include parameters 
    corresponding to a restart calculation, vdW kernel tables and pseudopotentials.    
    """

    #Check whether this is a 'restart'-calculation and set the accoring input flags.
    if 'parent_folder' in self.inputs:
        self.set_restart_parameters(self)
    else:
        self.ctx.inputs_raw.parent_folder = None

    if 'settings' in self.inputs:
        self.ctx.inputs_raw.settings = self.inputs.settings.get_dict()
    else:
        self.ctx.inputs_raw.settings = {}

    if 'options' in self.inputs:
        self.ctx.inputs_raw._options = self.inputs.options.get_dict()
    else:
        self.ctx.inputs_raw._options = {}

    if 'vdw_table' in self.inputs:
        self.ctx.inputs_raw.vdw_table = self.inputs.vdw_table

    # Check whether valid input for the parallelisation has been provided in the
    # 'options' card of the inputs dictionary.
    if not any([key in self.inputs for key in ['options']]):
        self.abort_nowait('you have to specify the options input')
        return

    num_machines = self.ctx.inputs_raw['_options'].get('resources', {}).get('num_machines', None)
    max_wallclock_seconds = self.ctx.inputs_raw['_options'].get('max_wallclock_seconds', None)

    if num_machines is None or max_wallclock_seconds is None:
        self.abort_nowait("no automatic_parallelization requested, but the options do not specify both '{}' and '{}'"
        .format('num_machines', 'max_wallclock_seconds'))

    set_pseudopotential_input( self )


def set_restart_parameters( self ):

    """
    Set the input parameters required for a restart calculation.
    """

    self.ctx.inputs_raw.parent_folder = self.inputs.parent_folder


def set_pseudopotential_input( self ):

    """
    Set the required input cards for the pseudopotentials. If the calculation does not
    use pseudopotentials or any other kind of atomic dataset, just leave this method
    empty.
    """

    from aiida_vasp.utils.pseudopotential import validate_and_prepare_pseudos_inputs

    # Validate the inputs related to pseudopotentials
    structure = self.inputs.structure
    pseudos = self.inputs.get('pseudos', None)
    pseudo_family = self.inputs.get('pseudo_family', None)

    try:
        self.ctx.inputs_raw.paw = validate_and_prepare_pseudos_inputs(structure, pseudos, pseudo_family)
    except ValueError as exception:
        self.abort_nowait('{}'.format(exception))
