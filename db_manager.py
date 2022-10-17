import sqlite3
from hashlib import md5


DATABASE_PATH = "./"

#######################################################
### :desc: create a database connection to the SQLite
###        database specified by db_file.
### :param db_file: database file
### :return: Connection object or None
#######################################################
def create_connection(db_file):
    conn = None
    db_file = DATABASE_PATH + "/" + db_file
    try:
        conn = sqlite3.connect(db_file)
        create_database(db_file, conn)
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn


#######################################################
### :desc: create a table from the create_table_sql 
###        statement.
### :param conn: Connection object
### :param create_table_sql: a CREATE TABLE statement
### :return: None
#######################################################
def create_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)


#######################################################
### :desc: create database and database file if it not
###        exists.
### :param DATABASE: file
### :param conn: Connection object
### :return: None
#######################################################
def create_database(DATABASE, conn = None):
    # PRIMARY_KEY: time;havg;pop,ep,26;...
    # TRAINING_START: 1647388800
    # TRAINING_END: 1652227080
    # MODEL_NAME: "vitor_lstm_10min"
    # FILENAME_HASH: MD5(MODEL_NAME+PRIMARY_KEY+BEGIN+END)

    models_table = """ CREATE TABLE IF NOT EXISTS model (
                                query_juice VARCHAR(128),
                                tc_schema varchar(30),
                                dimension VARCHAR(20),
                                inferior_limit INT,
                                superior_limit INT,
                                model_name varchar(32),
                                filename_md5 char(32),
                                filename_raw TEXT,

                                CONSTRAINT PK_model PRIMARY KEY (query_juice)
                            ); """


    close_at_end = False
    # create a database connection
    if conn is None:
        conn = create_connection(DATABASE)
        close_at_end = True

    # create tables
    if conn is not None:
        # create line table
        create_table(conn, models_table)

        if close_at_end: conn.close()
    else:
        print("Error! cannot create the database connection.")


###################################################################
#                                                                 #
#                         AUX FUNCTIONS                           #
#                                                                 #
###################################################################
# extract TC query juice
def decode_query(query):
    return


# md5 filename
def generate_filename(query_juice, model_name, inferior_limit, superior_limit):
    s = f"{query_juice};{model_name};{inferior_limit};{superior_limit}"
    return md5(s.encode("utf-8")).hexdigest()



###################################################################
#                                                                 #
#                         INSERT FUNCTIONS                        #
#                                                                 #
###################################################################
def insert_model(conn, query, inferior_limit, superior_limit, model_name):
    sql = ''' INSERT INTO model(query_juice, inferior_limit,
                superior_limit, model_name, filename_md5)
              VALUES(?, ?, ?, ?, ?) '''
    
    cur = conn.cursor()

    query_juice = decode_query(query)
    filename_md5 = generate_filename(query_juice, model_name,
                    inferior_limit, superior_limit)
    
    try:
        cur.execute(sql, (query_juice, inferior_limit,
                superior_limit, model_name, filename_md5))
        conn.commit()
    except sqlite3.IntegrityError as e:
        print("!!! ERROR: Query already exists in DATABASE!")
        print(f"\tQuery: {query}")
        return False
    
    return True

###################################################################
#                                                                 #
#                         QUERY FUNCTIONS                         #
#                                                                 #
###################################################################
def get_model_file(conn, query_juice):
    sql = ''' SELECT filename_md5 FROM model WHERE query_juice = ? '''
    cur = conn.cursor()
    cur.execute(sql, (query_juice, ))

    res = curr.fetchone()[0]
    
    return res




if __name__ == "__main__":
    create_database("models.db", None)

