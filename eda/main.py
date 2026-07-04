import os
import pandas as pd

DATA_DIR = os.path.expanduser('~/Downloads')
df = pd.read_csv(os.path.join(DATA_DIR, 'TEP_FaultFree_Testing.csv'))
normal = df[df['faultNumber'] == 0]

variables = {
    'xmeas_1':  ('A Feed Flow',              'kscmh',  'A component flow into reactor'),
    'xmeas_2':  ('D Feed Flow',              'kg/hr',  'D component flow into reactor'),
    'xmeas_3':  ('E Feed Flow',              'kg/hr',  'E component flow into reactor'),
    'xmeas_4':  ('A/C Feed Flow',            'kscmh',  'Mixed A and C stream'),
    'xmeas_5':  ('Recycle Flow',             'kscmh',  'Recycle loop flow rate'),
    'xmeas_6':  ('Reactor Feed Rate',        'kscmh',  'Total flow entering reactor'),
    'xmeas_7':  ('Reactor Pressure',         'kPa',    'Process stability indicator'),
    'xmeas_8':  ('Reactor Level',            '%',      'Liquid level in reactor'),
    'xmeas_9':  ('Reactor Temperature',      'deg C',  'Key reaction state indicator'),
    'xmeas_10': ('Purge Rate',               'kscmh',  'Inert component removal'),
    'xmeas_11': ('Separator Temperature',    'deg C',  'Vapor-liquid separation efficiency'),
    'xmeas_12': ('Separator Level',          '%',      'Liquid level in separator'),
    'xmeas_13': ('Separator Pressure',       'kPa',    'Separator operating stability'),
    'xmeas_14': ('Separator Underflow',      'm3/hr',  'Flow from separator to stripper'),
    'xmeas_15': ('Stripper Level',           '%',      'Liquid level in stripper'),
    'xmeas_16': ('Stripper Pressure',        'kPa',    'Stripper operating condition'),
    'xmeas_17': ('Stripper Underflow',       'm3/hr',  'Final product flow'),
    'xmeas_18': ('Stripper Temperature',     'deg C',  'Product separation efficiency'),
    'xmeas_19': ('Stripper Steam Flow',      'kg/hr',  'Heat supply to stripper'),
    'xmeas_20': ('Compressor Work',          'kW',     'Recycle compressor energy'),
    'xmeas_21': ('Reactor CW Outlet Temp',   'deg C',  'Reactor cooling performance'),
    'xmeas_22': ('Separator CW Outlet Temp', 'deg C',  'Separator cooling performance'),
    'xmv_1':   ('D Feed Valve',             '%open',  'D feed flow control'),
    'xmv_2':   ('E Feed Valve',             '%open',  'E feed flow control'),
    'xmv_3':   ('A Feed Valve',             '%open',  'A feed flow control'),
    'xmv_4':   ('A/C Feed Valve',           '%open',  'A/C mixed feed control'),
    'xmv_5':   ('Compressor Recycle Valve', '%open',  'Recycle loop pressure control'),
    'xmv_6':   ('Purge Valve',              '%open',  'Inert purge control'),
    'xmv_7':   ('Separator Underflow Valve','%open',  'Separator level control'),
    'xmv_8':   ('Stripper Level Valve',     '%open',  'Stripper level control'),
    'xmv_9':   ('Stripper Steam Valve',     '%open',  'Stripper heat supply control'),
    'xmv_10':  ('Reactor CW Valve',         '%open',  'Reactor temperature control'),
    'xmv_11':  ('Separator CW Valve',       '%open',  'Separator temperature control'),
}

sensors = [col for col in df.columns if col.startswith('xmeas_') or col.startswith('xmv_')]
stats = normal[sensors].describe().round(3)

print(f"{'Variable':<12} {'Name':<26} {'Unit':<10} {'Mean':>8} {'Min':>8} {'Max':>8}  {'Description'}")
print("-" * 110)
for col, (name, unit, meaning) in variables.items():
    if col in stats.columns:
        mean = stats.loc['mean', col]
        mn   = stats.loc['min',  col]
        mx   = stats.loc['max',  col]
        print(f"{col:<12} {name:<26} {unit:<10} {mean:>8} {mn:>8} {mx:>8}  {meaning}")