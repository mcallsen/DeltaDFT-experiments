# This is an adapted copy of the quantum espresso base workchain.

from copy import deepcopy
from aiida.orm import Code
from aiida.orm.data.base import Bool, Int, Str
from aiida.orm.data.folder import FolderData
from aiida.orm.data.remote import RemoteData
from aiida.orm.data.parameter import ParameterData
from aiida.orm.data.structure import StructureData
from aiida.orm.data.array.bands import BandsData
from aiida.orm.data.array.kpoints import KpointsData
from aiida.orm.data.singlefile import SinglefileData
from aiida.orm.utils import CalculationFactory
from aiida.common.extendeddicts import AttributeDict
from aiida.work.run import submit
from aiida.work.workchain import ToContext, if_, while_

# imports of common workchain utils. these might be independent of the actual code
# and probably could be part of aiida-workchain.

from aiida_quantumespresso.common.exceptions import UnexpectedCalculationFailure
from aiida_quantumespresso.common.workchain.utils import ErrorHandlerReport
from aiida_quantumespresso.common.workchain.utils import register_error_handler
from aiida_quantumespresso.common.workchain.base.restart import BaseRestartWorkChain

from aiida_vasp.utils.workchain import validate_calculation_and_interfaces
import aiida_vasp.interface.IBaseWorkchain as IBaseWorkchain


class VASPBaseWorkChain(BaseRestartWorkChain):

    """
    Base workchain to launch a VASP calculation
    """

    _verbose = True
    _error_handler_entry_point = 'aiida_quantumespresso.workflow_error_handlers.pw.base'


    def __init__(self, *args, **kwargs):
        super(VASPBaseWorkChain, self).__init__(*args, **kwargs)

        _plugin_name = self.inputs.code.get_input_plugin_name()
        _calculation_class = CalculationFactory( _plugin_name )

        validate_calculation_and_interfaces(self, IBaseWorkchain)

        self.defaults = set_defaults()


    @classmethod
    def define(cls, spec):
        super(VASPBaseWorkChain, cls).define(spec)
        spec.input('code', valid_type=Code)
        spec.input('structure', valid_type=StructureData)
        spec.input('kpoints', valid_type=KpointsData)
        spec.input('parameters', valid_type=ParameterData)
        spec.input_group('pseudos', required=False)
        spec.input('pseudo_family', valid_type=Str, required=False)
        spec.input('parent_folder', valid_type=RemoteData, required=False)
        spec.input('vdw_table', valid_type=SinglefileData, required=False)
        spec.input('settings', valid_type=ParameterData, required=False)
        spec.input('options', valid_type=ParameterData, required=False)
        spec.input('automatic_parallelization', valid_type=ParameterData, required=False)
        spec.outline(
            cls.setup,
            cls.validate_inputs,
            while_(cls.should_run_calculation)(
                cls.prepare_calculation,
                cls.run_calculation,
                cls.inspect_calculation,
            ),
            cls.results,
        )
        spec.output('output_band', valid_type=BandsData, required=False)
        spec.output('output_structure', valid_type=StructureData, required=False)
        spec.output('output_parameters', valid_type=ParameterData)
        spec.output('remote_folder', valid_type=RemoteData)
        spec.output('retrieved', valid_type=FolderData)


    def validate_inputs(self):
        """
        Define context dictionary 'inputs_raw' with the inputs for the PwCalculations as they were at the beginning
        of the workchain. Changes have to be made to a deep copy so this remains unchanged and we can always reset
        the inputs to their initial state. Inputs that are not required by the workchain will be given a default value
        if not specified or be validated otherwise.
        """
        self.ctx.inputs_raw = AttributeDict({
            'code': self.inputs.code,
            'structure': self.inputs.structure,
            'kpoints': self.inputs.kpoints,
            'parameters': self.inputs.parameters.get_dict()
        })

        # plugin specific information
        self.set_plugin_specific_input( self )

        # Assign a deepcopy to self.ctx.inputs which will be used by the BaseRestartWorkChain
        self.ctx.inputs = deepcopy(self.ctx.inputs_raw)


    def prepare_calculation(self):
        """
        Prepare the inputs for the next calculation
        """
        if self.ctx.restart_calc:
            self.set_restart_parameters(self)


    def _prepare_process_inputs(self, inputs):

        return super(VASPBaseWorkChain, self)._prepare_process_inputs(inputs)
