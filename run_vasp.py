from aiida.work.run import run
from aiida.orm import CalculationFactory, Code
from aiida.orm.data.base import Str
from aiida.orm.data.array.kpoints import KpointsData
from aiida.orm.data.parameter import ParameterData
from aiida.workflows.user.VASPBaseWorkchain import VASPBaseWorkChain

VaspCalculation = CalculationFactory('vasp.vasp')

options = {
	'resources': {
		'num_machines': 1,
		'tot_num_mpiprocs': 1,
	},
	'max_wallclock_seconds': 1800,
}

kpoints = KpointsData()
kpoints.set_kpoints_mesh([1, 1, 1])

inputs = {
	'code': Code.get_from_string('VASP.5.4.4@Raichu'),
	'structure': load_node(888),
	'kpoints': kpoints,
	'parameters': ParameterData(dict={}),
	'settings': ParameterData(dict={}),
	'pseudo_family': Str('vasp-pbe'),
}

process = VaspCalculation.process()
running = run(VASPBaseWorkChain, **inputs)
