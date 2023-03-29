import mysql.connector as ms

def db_init():
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    #check db exist or create
    cursor.execute("SHOW DATABASES;")
    rec = cursor.fetchall()
    rec = [j for sub in rec for j in sub]
    if not 'micedb' in rec:
        cursor.execute("CREATE DATABASE `micedb`;")
    cursor.execute("USE `micedb`;")
    #table of files
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `load`(
        `name` VARCHAR(100) NOT NULL PRIMARY KEY,
        `gender` VARCHAR(10),
        `age` VARCHAR(10),
        `weight` VARCHAR(10),
        `file` VARCHAR(200)
        );
    """)
    cursor.close()
    connection.close()

def insert_load(name,gender,age,weight,file_path):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #check exist
    cursor.execute("SELECT * FROM `load` WHERE `name`='{:}';".format(name))
    if cursor.fetchone():
        return -1
    #insert
    cursor.execute("INSERT INTO `load` VALUES ('{:}','{:}','{:}','{:}','{:}');".format(name,gender,age,weight,file_path))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1

def load_load(sel_name=None):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")
    #load
    if not sel_name:
        cursor.execute("SELECT * FROM `load`;")
        ret = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM `load` WHERE `name`='{:}';".format(sel_name))
        ret = cursor.fetchone()

    #close
    cursor.close()
    connection.close()
    return ret

def del_load(sel_name):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    if type(sel_name) is not list:
        cursor.execute("DELETE FROM `load` WHERE `name`='{:}';".format(sel_name))
    else:
        for sel in sel_name:
            cursor.execute("DELETE FROM `load` WHERE `name`='{:}';".format(sel))

    #close
    cursor.close()
    connection.commit()
    connection.close()

def update_load(original_name,name,gender,age,weight,file_path):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #check exist
    cursor.execute("SELECT * FROM `load` WHERE `name`='{:}';".format(name))
    if cursor.fetchone():
        return -1
    #update
    cursor.execute("""
        UPDATE `load` 
        SET `name`='{:}', `gender`='{:}', `age`='{:}', `weight`='{:}', `file`='{:}' 
        WHERE `name`='{:}';
    """.format(name,gender,age,weight,file_path,original_name))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1