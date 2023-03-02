import sys,os,json,pandas

script_rootFolder = os.path.dirname(__file__)
script_parentFolder = os.path.join(script_rootFolder, "../")
inputFolder = os.path.join(script_rootFolder, 'inputCSV')
outputFolder = os.path.join(script_rootFolder, 'inputJSON')

jsonBlueprintString = '''
{
	"fileName":  "filename.csv",
  "RICs":  ["RIC1"],
  "fields":  ["Exchange ID"],
	"Bid Price": "CF_BID",
	"Primary Activity": "PRIMACT_1",
	"Last Price": "CF_LAST",
	"General Value1": "GEN_VAL1",
	"Ask Price": "CF_ASK",
	"Open Price": "OPEN_PRC",
	"Percent Change": "PCTCHNG",
	"Mid Price": "MID_PRICE",
	"Official Close Price": "OFF_CLOSE",
	"Official Ask": "CF_ASK",
	"Close Price": "CF_CLOSE",
	"High Price": "CF_HIGH",
	"Primary Activity 2": "PRIMACT_2",
	"Low Price": "CF_LOW",
	"VWAP Price": "VWAP",
	"Fixing Date": "FIX_DATE",
	"Trade Date": "CF_DATE",
	"Bid Yield": "BID_YIELD",
	"General Value1 Date": "GV_DATE1",
	"General Value2 Date": "GV_DATE2",
	"General Value2": "GEN_VAL1",
	"Previous Close Price": "HST_CLOSE",
	"Previous Day Trade Date": "HSTCLSDATE",
	"Exchange Description": "CF_EXCHNG",
	"Currency Code": "CF_CURR",
	"Volume": "CF_VOL",
  "RIC":  "Instrument",
  "dateColumnsMMDDYYYY": [
		"Trade Date",
		"Fixing Date",
		"Previous Day Trade Date",
		"Universal Day Trade Date"
	],
	"dateColumnsDDMMYYYY": [
		"General Value1 Date",
		"General Value2 Date"
	],
    "currentTimeColumn": ["Instrument Snap Time"]
}
'''

jsonBlueprint = json.loads(jsonBlueprintString)

for filename in os.listdir(outputFolder):
  file = os.path.join(outputFolder, filename)
  if filename.endswith('.json'):
    print('Deleting {}'.format(file))
    os.remove(file)

print('Reading all CSV-files from {}'.format(inputFolder))
files = []
for filename in os.listdir(inputFolder):
  file = os.path.join(inputFolder, filename)
  if filename.endswith('.csv') and os.path.isfile(file):
    files.append(file)

if len(files) == 0:
  print('No CSV-files found in {}'.format(inputFolder))
  print('See ya!')
  exit()
print('Found files: {}'.format(len(files)))

for filename in os.listdir(inputFolder):
  file = os.path.join(inputFolder, filename)
  print('Reading {}'.format(file))
  csvData = pandas.read_csv(file)
  newFilename = filename[-20:] + '.json'
  print(newFilename)
  for RIC in csvData['RIC']:
    jsonBlueprint['RICs'].append(RIC)
  for field in csvData.columns:
    jsonBlueprint['fields'].append(field)

print(json.dumps(jsonBlueprint, ensure_ascii = True, indent = 2))