import csv
import MySQLdb
import dbConfig

#print(dbConfig.MYSQL_USER, dbConfig.MYSQL_PASSWORD, dbConfig.MYSQL_HOST, dbConfig.MYSQL_DB)
TABLE_NAME = 'birdboxTable'


def tableExists(db, tableName):
    cursor = db.cursor()
    query = "SHOW TABLES LIKE '"+tableName+"';"
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result:
        print(tableName, " table already exists")
        return True
    else:
        print(tableName, " table does not exists")
        return False


def createDatabase(DB_NAME):
    print("Creating new schema")
    query = "CREATE DATABASE "+DB_NAME+";"
    print("Query: create db: ", query)

    db = MySQLdb.connect(dbConfig.MYSQL_HOST,
                         dbConfig.MYSQL_USER, dbConfig.MYSQL_PASSWORD)
    cursor = db.cursor()
    cursor.execute(query)
    cursor.close()
    return


def createTable(tableName, db, col_names, col_data_types):
    # print(col_names)
    # print(col_data_types)

    query_useDb = "USE birdbox;"
    query_createTable = "CREATE TABLE "+tableName+" ("

    i = 0
    queryParms = ''
    while i < len(col_names):
        #print(col_names[i]," ",col_data_types[i],",")
        if(col_names[i] not in ['COLUMN_NAMES', 'DATA_TYPES', 'IMPORT_INTO_DATABASE']):
            queryParms += col_names[i] + " " + col_data_types[i] + ", "

        i += 1

    # Remove last 2 characters
    query_createTable = query_createTable + queryParms[:-2] + ");"
    print("Query: select db:", query_useDb)
    print("Query: create table: ", query_createTable)

    cursor = db.cursor()
    cursor.execute(query_useDb)
    cursor.execute(query_createTable)
    cursor.close()
    return


def populateDataWithTable(db, table_name, col_names, dataRows):
    cursor = db.cursor()
    numberOfRecordsToCommit = 0
    for dataRow in dataRows:
        #print (dataRow)
        if(dataRow[1] == 'TRUE'):
            i = 0
            q1 = 'INSERT INTO '+table_name+' ('
            q2 = 'VALUES ('
            numberOfColumns = 0
            while i < len(col_names):
                if(col_names[i] not in ['COLUMN_NAMES',
                                        'DATA_TYPES',
                                        'IMPORT_INTO_DATABASE',
                                        'id',
                                        'last_updated',
                                        'last_invoked',
                                        'active']):

                    # Skip if no data
                    if (dataRow[i] == ''):
                        print("\n>>>>>> No data for ",
                              col_names[i], ". Skipping.")
                    else:
                        q1 += col_names[i] + ", "
                        q2 += '"'+dataRow[i]+'", '
                        numberOfColumns += 1

                i += 1

            if numberOfColumns > 0:
                query = q1[:-2]+") " + q2[:-2] + ");"
                print("\nQuery: ", query)
                try:
                    cursor.execute(query)
                except (MySQLdb.Error, MySQLdb.Warning) as e:
                    print("Error: ", e)
                    exit()

                numberOfRecordsToCommit += 1

        else:
            print("Skipping import of: ", dataRow)
            continue

    if numberOfRecordsToCommit > 0:
        db.commit()

    cursor.close()
    return

##########################################################################


def importCsv():
    CSV_FILE = 'BirdBox - birdbox_table.csv'

    col_names = ''
    col_data_types = ''
    dataRows = []
    with open(CSV_FILE, newline='') as csvfile:
        csvData = csv.reader(csvfile, delimiter=',', quotechar='"',
                             quoting=csv.QUOTE_ALL, skipinitialspace=True)
        for row in csvData:
            # print(row)
            # print(row[0])
            if(row[0] == 'COLUMN_NAMES'):
                col_names = row
            elif(row[0] == 'DATA_TYPES'):
                col_data_types = row
            elif(row[0] == 'DATA_ROW'):
                dataRows.append(row)
            else:
                pass

    # CONNECT TO DATABASE
    db = ''
    for attempt in range(2):
        try:
            db = MySQLdb.connect(dbConfig.MYSQL_HOST, dbConfig.MYSQL_USER,
                                 dbConfig.MYSQL_PASSWORD, dbConfig.MYSQL_DB)
        except MySQLdb._exceptions.OperationalError as err:
            print("Something went wrong: {}".format(err))
            print("Error code: ", err.args[0])
            print("Error: ", err.args[1])
            if(err.args[0] == 1049):
                print("Database schema does not exist. Attempting to create new schema")
                createDatabase(dbConfig.MYSQL_DB)
                #db = MySQLdb.connect("localhost", "user", "password", "birdbox")
                continue
        else:
            print("Connection to database established")
            break

    # DROP TABLE IF TABLE EXISTS
    if(tableExists(db, TABLE_NAME)):
        cursor = db.cursor()
        query = "DROP TABLE " + TABLE_NAME + ";"
        cursor.execute(query)
        cursor.close()

    # TABLE EXISTS
    createTable(TABLE_NAME, db, col_names, col_data_types)

    # POPULATE TABLE
    print("Number of data rows to inspect: ", len(dataRows))
    populateDataWithTable(db, TABLE_NAME, col_names, dataRows)

    db.close()
    exit()


if __name__ == "__main__":
    importCsv()
