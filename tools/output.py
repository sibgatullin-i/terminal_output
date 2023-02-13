from fileinput import filename
from types import SimpleNamespace
import os,pandas,json,datetime,time,requests,tabulate,winsound,sys
import eikon as terminal

# Displaying the parent directory of the script
script_rootFolder = os.path.dirname(__file__)
script_inputFolder = os.path.join(script_rootFolder,sys.argv[1])
script_parentFolder = os.path.join(script_rootFolder, "../")
output_csv = os.path.join(script_rootFolder,'output.csv')
lastprice_file = os.path.join(script_rootFolder,'lastprice')
settings_file = open ( (os.path.join(script_parentFolder, 'settings.json')), "r" )
settings = json.loads(settings_file.read(), object_hook=lambda d: SimpleNamespace(**d))

data = pandas.DataFrame()
instruments = []
fields = []

data_fields_wDate = ["DATE_NAME","BID_NAME","ASK_NAME","OPEN_NAME","CLOSE_NAME","HIGH_NAME","LOW_NAME","LAST_NAME"]
data_fields_output = ["QUOTE_SET","QUOTE_NAME","DATE_NAME","BID_NAME","ASK_NAME","OPEN_NAME","CLOSE_NAME","HIGH_NAME","LOW_NAME","LAST_NAME"]

print('Setting terminal API key...')
terminal.set_app_key(settings.terminalAppKey)

#reading input json objects to a dataframe data; instruments and fields are lists
print('Reading input objects from {}...'.format(script_inputFolder))
i = 0
for filename in os.listdir(script_inputFolder):
    if filename.endswith(".json"):
        with open(os.path.join(script_inputFolder, filename), 'r') as f:
            json_dict = json.loads(f.read())
            f.close()
            df = pandas.DataFrame(json_dict,index=[i])
            instruments.append(df.iloc[0]['FEED_ADDRESS'])
            for field in data_fields_wDate:
                fields.append(df.iloc[0][field])
            data = pandas.concat([data,df])
            i += 1

data.reset_index()

#removing duplicates with converting to set and back to list
instruments = list(set(instruments))
fields = list(set(fields))

#sending terminal Data API request saving to data_source DataFrame
print('Sending request to terminal...')
data_source,err = terminal.get_data(instruments,fields)
data_source.reset_index()

print('Filling data with values...')
for index in data.index:
    instr = data.at[index, 'FEED_ADDRESS']
    for fld in data_fields_wDate:
        fld_val = data.at[index,fld]
        val = data_source[data_source['Instrument'] == instr][fld_val].values[0]
        data.at[index,fld] = val

#update evaluation and removing technical row
#read and write values
priceNow = data[data.FEED_ADDRESS=='BTC='].BID_NAME.values[0]
file = open(lastprice_file,'r')
priceLast = float(file.read())
file.close()
file = open(lastprice_file,'w')
file.write(str(priceNow))
file.close()
#compare and save result, put '0' if price is the same
if priceLast != priceNow:
    priceUpdated = True
else:
    priceUpdated = False
    file = open(lastprice_file,'w')
    file.write('0')
    file.close()
#remove techincal row
data.drop(data.loc[data['FEED_ADDRESS'] == 'BTC='].index,inplace=True)


print('Proccessing Calypso modification...')
#multiply all values by MULT_COEF and to string, modify date field
for index in data.index:
    for fld in data_fields_wDate:
        if fld == 'DATE_NAME':
            if type(data.at[index,fld]) != pandas._libs.missing.NAType:
                data.at[index,fld] = datetime.datetime.strptime(data.at[index,fld],'%Y-%m-%d')
                data.at[index,fld] = datetime.datetime.strftime(data.at[index,fld], '%d/%m/%Y')
        else:
            if type(data.at[index,fld]) != pandas._libs.missing.NAType:
                data.at[index,fld] = round(data.at[index,fld] * data.at[index,'MULT_COEF'] , 10) #because something about floating point accuracy

#removing non-required fields
for col in data.columns:
    if col not in data_fields_output:
        data.drop(columns=col,inplace=True)

print('Adding Russian Wheat index...')
extraDateTo = datetime.date.today().strftime("%Y-%m-%d")
extraDateFrom = (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
instrument = settings.mdhruExtraInstrument1
extraRequestUri = '{0}/{1}/data/?field={2}&from={3}&to={4}'.format(settings.mdhruUri, instrument[0], instrument[1], extraDateFrom, extraDateTo)
extraResponse = requests.get(extraRequestUri, auth=(settings.mdhruUsername, settings.mdhruPassword))
extraObject = json.loads(extraResponse.text)
if len(extraObject) > 1:
    extraSortedData = sorted(extraObject, key=lambda x: x['time'], reverse=True)
    extraValue = extraSortedData[0]['value']
    extraDate = extraSortedData[0]['time']
    extraDate = datetime.datetime.fromisoformat(extraDate)
    extraDate = datetime.datetime.strftime(extraDate, '%d/%m/%Y')
    data.loc[len(data.index) + 1] = ['default', instrument[3], extraDate, extraValue, extraValue, extraValue, extraValue, extraValue, extraValue, extraValue]
    data.loc[len(data.index) + 1] = [instrument[2], instrument[3], extraDate, extraValue, extraValue, extraValue, extraValue, extraValue, extraValue, extraValue]

os.system('cls') #Windows only clear screen

#pretty print data
print(tabulate.tabulate(data,headers='keys',tablefmt='psql'))

print('Data updated {} | Last price {}, current price {}'.format(priceUpdated,priceLast,priceNow))

#save CSV
data.to_csv(output_csv,index=False,header=False)
print('CSV-file {} saved.'.format(output_csv))

winsound.Beep(1500, 1000) # just for fun
