import sys,os,json,pandas,datetime
from types import SimpleNamespace
import eikon as terminal

script_rootFolder = os.path.dirname(__file__)
script_parentFolder = os.path.join(script_rootFolder, "../")
inputFolder = os.path.join(script_rootFolder, 'inputJSON')
outputFolder = os.path.join(script_rootFolder, 'outputCSV')
settings_file = open ( (os.path.join(script_parentFolder, 'settings.json')), "r" )
settings = json.loads(settings_file.read(), object_hook=lambda d: SimpleNamespace(**d))

print('No JSON-file was passed as argument. Will proceed all files from {}'.format(inputFolder))
answer = input('Are you sure? Y/N (default N):')
if not (answer == 'Y' or answer == 'y'):
    print('See ya!')
    exit()

filesCount = 0
for inputDataFile in os.listdir(inputFolder):
    inputDataFile = os.path.join(inputFolder, inputDataFile)
    if inputDataFile.endswith(".json") and os.path.isfile(inputDataFile):
        filesCount += 1
if filesCount == 0:
    print('No JSON-files found in {}'.format(inputFolder))
    print('See ya!')
    exit()

print('Setting terminal API key...')
terminal.set_app_key(settings.terminalAppKey)

for inputDataFile in os.listdir(inputFolder):
    inputDataFile = os.path.join(inputFolder, inputDataFile)
    if inputDataFile.endswith(".json") and os.path.isfile(inputDataFile):
        print('Reading {}...'.format(inputDataFile))
        inputDataFile = open(os.path.join(inputFolder, inputDataFile), 'r')
        inputData = json.loads(inputDataFile.read())
        inputDataFile.close()

        if len(inputData) < 6:
            print('Failed to import JSON')
            exit()

        instruments = inputData['RICs']
        fields = []
        for field in inputData['fields']:
            if field != 'RIC' and field in inputData.keys():
                fields.append(inputData[field])

        instruments = list(set(instruments))
        fields = list(set(fields))

        print('Sending request to terminal...')
        sourceData,err = terminal.get_data(instruments,fields)
        sourceData.reset_index()
        
        print('Applying fields translation rules:')
        sourceData.rename(columns=inputData['fieldsTranslation'], inplace=True)
        print(sourceData)        

        data = pandas.DataFrame(index = range(len(inputData['RICs'])), columns = inputData['fields'])
        timeNow = datetime.datetime.today().strftime('%m/%d/%Y %H:%M:%S')
        for index in sourceData.index:
            for column in data.columns:
                if column in inputData['currentTimeColumns']:
                    data.at[index, column] = timeNow
                if column in inputData.keys() and type(sourceData.at[index, inputData[column]]) != pandas._libs.missing.NAType:
                    if column in inputData['dateColumnsMMDDYYYY']:
                        date = sourceData.at[index, inputData[column]]
                        date = datetime.datetime.strptime(date,'%Y-%m-%d')
                        date = datetime.datetime.strftime(date, '%m/%d/%Y')
                        data.at[index, column] = date
                    elif column in inputData['dateColumnsDDMMYYYY']:
                        date = sourceData.at[index, inputData[column]]
                        date = datetime.datetime.strptime(date,'%Y-%m-%d')
                        date = datetime.datetime.strftime(date, '%d.%m.%Y')
                        data.at[index, column] = date
                    else:
                        data.at[index, column] = sourceData.at[index, inputData[column]]
        data.dropna(subset=['RIC'], inplace=True)
        data.sort_values(by=['RIC'], inplace=True)

        print(data)

        print('<----------| CSV |---------->')
        print(data.to_csv(index = False))
        print('<----------| CSV |---------->')
        filename = inputData['fileName']
        if len(filename) < 1:
            print('No fileName in JSON')
            print("Save to file or Ctrl-C to exit")
            filename = input('Filename:')
            if len(filename) < 1:
                print('No filename given. Ясно.')
                exit()
        filename = os.path.join(outputFolder, filename)
        data.to_csv(filename, index = False)
        print('Saved to {}'.format(filename))
