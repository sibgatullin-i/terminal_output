import os,sys,pandas,json

if len(sys.argv) > 1:
    OBJECTSFILENAME = os.path.join(os.path.dirname(__file__),sys.argv[1])
else:
    print("No argument provided, using default objects.xlsx")
    OBJECTSFILENAME = os.path.join(os.path.dirname(__file__),"objects.xlsx")

#check for file
if os.path.exists(OBJECTSFILENAME):
    print("File found. Trying to read Excel data...")
else:
    print ("File not found")
    sys.exit(1)

#try to read Excel file
try:
    DATA = pandas.read_excel(OBJECTSFILENAME)
except:
    print ("Failed to read Excel file", OBJECTSFILENAME)
    sys.exit(1)

#create folder if not exists
TARGETFOLDER = os.path.join(os.path.dirname(__file__),'input')
if not os.path.exists(TARGETFOLDER):
    os.mkdir(TARGETFOLDER)
    
#delete all exisitng files in folder
for FILE in os.listdir(TARGETFOLDER):
    os.remove(os.path.join(TARGETFOLDER, FILE))

#create new files
for INDEX in DATA.index:
    FILENAME = DATA.at[INDEX,'QUOTE_SET'] + '_' + DATA.at[INDEX,'QUOTE_NAME'] + '.json'
    for CHAR in '<>:"/\|?* ':
        FILENAME = FILENAME.replace(CHAR, '')
    JSON = json.dumps(json.loads(DATA.loc[INDEX].to_json()),indent=4)
    FILE = open(os.path.join(TARGETFOLDER, FILENAME), 'w')
    FILE.write(JSON)
    FILE.close()
    print (os.path.join(TARGETFOLDER, FILENAME), " has been created")