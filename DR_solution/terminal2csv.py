import sys,os,json,pandas,datetime
from types import SimpleNamespace
import eikon as terminal

script_rootFolder = os.path.dirname(__file__)
script_parentFolder = os.path.join(script_rootFolder, "../")
inputFolder = os.path.join(script_rootFolder, 'inputJSON')
outputFolder = os.path.join(script_rootFolder, 'outputCSV')
settings_file = open ( (os.path.join(script_parentFolder, 'settings.json')), "r" )
settings = json.loads(settings_file.read(), object_hook=lambda d: SimpleNamespace(**d))

if len(sys.argv) > 1:
    inputDataFile = os.path.join(sys.argv[1])
    if not os.path.isfile(inputDataFile):
        print('file not found {}'.format(inputDataFile))
        print('See ya!')
        exit()
else:
    print('No JSON-file was passed as argument. Will proceed all files from {}'.format(inputFolder))
    answer = input('Are you sure? Y/N (default N):')
    if not (answer == 'Y' or answer == 'y'):
        print('See ya!')
        exit()

filesCount = 0
for inputDataFile in os.listdir(inputFolder):
    inputDataFile = os.path.join(inputFolder, inpuDataFile)
    if inputDataFile.endswith(".json") and os.path.isfile(inputDataFile):
        filesCount += 1
if filesCount == 0:
    print('No JSON-files found in {}'.format(inputFolder))
    print('See ya!')
    exit()

print('Setting terminal API key...')
terminal.set_app_key(settings.terminalAppKey)

for inputDataFile in os.listdir(inputFolder):
    if inputDataFile.endswith(".json") and os.path.isfile(inputDataFile):
        print('Reading {}...'.format(inputDataFile))
        inputDataFile = open(os.path.join(inputFolder, inputDataFile), 'r')
        inputData = json.loads(inputDataFile.read())
        inputDataFile.close()

        if len(inputData) < 6:
            print('Failed to import JSON')
            exit()

        fields = []
        instruments = inputData['RICs']

        for field in inputData['fields']:
            if field != 'RIC' and field in inputData.keys():
                fields.append(inputData[field])

        instruments = list(set(instruments))
        fields = list(set(fields))

        print('Sending request to terminal...')
        sourceData,err = terminal.get_data(instruments,fields)
        sourceData.reset_index()

        data = pandas.DataFrame(index = range(len(inputData['RICs'])), columns = inputData['fields'])

        for index in data.index:
            for column in data.columns:
                if column in inputData.keys():
                    data.at[index, column] = sourceData.at[index, inputData[column]]
            ### DATE modifications
            for column in inputData['dateColumnsMMDDYYYY']:
                if column in data.columns:
                    if type(data.at[index, column]) != pandas._libs.missing.NAType:
                        data.at[index, column] = datetime.datetime.strptime(data.at[index, column],'%Y-%m-%d')
                        data.at[index, column] = datetime.datetime.strftime(data.at[index, column], '%m/%d/%Y')
            for column in inputData['dateColumnsDDMMYYYY']:
                if column in data.columns:
                    if type(data.at[index, column]) != pandas._libs.missing.NAType:
                        data.at[index, column] = datetime.datetime.strptime(data.at[index, column],'%Y-%m-%d')
                        data.at[index, column] = datetime.datetime.strftime(data.at[index, column], '%d.%m.%Y')
            # / DATE modifications

            ### Adding time
            timeNow = datetime.datetime.today().strftime('%m/%d/%Y %H:%M:%S')
            for column in inputData['currentTimeColumn']:
                data.at[index, column] = timeNow
            # / Adding time

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
