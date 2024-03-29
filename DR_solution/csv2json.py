import sys,os,json,pandas

script_rootFolder = os.path.dirname(__file__)
script_parentFolder = os.path.join(script_rootFolder, "../")
inputFolder = os.path.join(script_rootFolder, 'inputCSV')
outputFolder = os.path.join(script_rootFolder, 'inputJSON')

jsonBlueprintString = '''
{
	"fileName":  "filename.csv",
	"RICs":  [],
	"fields":  [],
	"Bid Price": "CF_BID",
	"Primary Activity": "PRIMACT_1",
	"Last Price": "CF_LAST",
	"General Value1": "GEN_VAL1",
	"Ask Price": "CF_ASK",
	"Open Price": "OPEN_PRC",
	"Percent Change": "PCTCHNG",
	"Mid Price": "MID_1",
	"Official Close Price": "OFF_CLOSE",
	"Official Ask": "CF_ASK",
	"Close Price": "CF_CLOSE",
	"Close Mid Price": "MID_CLOSE",
	"High Price": "CF_HIGH",
	"Primary Activity 2": "PRIMACT_2",
	"Low Price": "CF_LOW",
	"VWAP Price": "TR.TSVWAP",
	"Fixing Date": "FIX_DATE",
	"Trade Date": "CF_DATE",
	"Bid Yield": "BID_YIELD",
	"General Value1 Date": "GV1_DATE",
	"General Value2 Date": "GV2_DATE",
	"General Value2": "GEN_VAL1",
	"Previous Close Price": "HST_CLOSE",
	"Previous Close Date": "HSCLSDATE",
  	"Universal Close Price": "HST_CLOSE",
	"Universal Close Price Date": "HSTCLSDATE",
	"Previous Day Trade Date": "HSTCLSDATE",
	"Exchange Description": "CF_EXCHNG",
	"Currency Code": "CF_CURR",
	"Volume": "CF_VOL",
  	"RIC":  "Instrument",
 	"dateColumnsMMDDYYYY": [
		"Trade Date",
		"Fixing Date",
		"Previous Day Trade Date",
		"Previous Close Date",
		"Universal Day Trade Date",
		"Universal Close Price Date"
	],
	"dateColumnsDDMMYYYY": [
		"General Value1 Date",
		"General Value2 Date"
	],
    	"currentTimeColumns": [
		"Instrument Snap Time"
	],
	"fieldsTranslation": {
		"returned field name": "requested field name",
		"VWAP": "TR.TSVWAP"
	}
}
'''

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

for filename in os.listdir(outputFolder):
  file = os.path.join(outputFolder, filename)
  if filename.endswith('.json'):
    print('Deleting {}'.format(file))
    os.remove(file)

for filename in os.listdir(inputFolder):
  if filename.endswith('.csv') and os.path.isfile(file):
    jsonBlueprint = json.loads(jsonBlueprintString)
    file = os.path.join(inputFolder, filename)
    print('Reading {}'.format(file))
    csvData = pandas.read_csv(file)
    newFilename = filename[0:-3] + 'json'
    newFile = os.path.join(outputFolder, newFilename)
    for RIC in csvData['RIC']:
      jsonBlueprint['RICs'].append(RIC)
    for field in csvData.columns:
      jsonBlueprint['fields'].append(field)
    jsonBlueprint['fileName'] = filename
    with open(newFile, 'w') as outfile:
      json.dump(jsonBlueprint, outfile, indent = 2, ensure_ascii = True)
    print('JSON-file saved: {}'.format(newFile))
    del csvData, RIC, field, jsonBlueprint, newFile, newFilename
