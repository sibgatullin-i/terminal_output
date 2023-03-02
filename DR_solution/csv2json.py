import sys,os,json

script_rootFolder = os.path.dirname(__file__)
script_parentFolder = os.path.join(script_rootFolder, "../")
inputFolder = os.path.join(script_rootFolder, 'inputCSV')
outputFolder = os.path.join(script_rootFolder, 'inputJSON')

jsonBlueprintString = '''
{
	"fileName":  "filename.csv",
    "RICs":  [
		"RIC1"
	],
    "fields":  [
		"Exchange ID"
	],
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
    "dateColumnsMMDDYYYY":  [
		"Trade Date",
		"Fixing Date",
		"Previous Day Trade Date",
		"Universal Day Trade Date"
	],
	"dateColumnsDDMMYYYY":  [
		"General Value1 Date",
		"General Value2 Date"
	],
    "currentTimeColumn":  [
		"Instrument Snap Time"
	]
}
'''

print(json.loads(jsonBlueprintString))