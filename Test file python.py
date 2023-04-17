import pandas as p
solar_data_file = p.read_excel('IrradianceDataQuarter.xlsx', sheet_name=0)
solar_data_file = solar_data_file.set_index('DateTime')
load_profile = p.read_excel('Load_profile.xlsx',sheet_name=0)
load_profile = load_profile.set_index('Time')
invertor_data_file = p.read_excel('INV EXCEL.xlsx',sheet_name=0)
invertor_data_file = invertor_data_file.set_index('REFERENCE')
panel_file = p.read_excel('Solar_panel_data.xlsx',sheet_name=0)
panel_file = panel_file.set_index('PANELS')
test_file = p.read_excel('test.xlsx', sheet_name=0)
test_file = test_file.set_index('index')

def multiply(a,b):
    print(a)
    return a*b

test_file = test_file.apply(lambda x: multiply(x.index, x.name))
print(test_file)


