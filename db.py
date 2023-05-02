import mysql.connector as ms
import os

def load_init():
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
        `file` VARCHAR(200),
        `crop` VARCHAR(100) DEFAULT NULL,
        `featfile` VARCHAR(1) DEFAULT NULL,
        FOREIGN KEY (`crop`) REFERENCES `crop`(`set`) ON DELETE SET NULL
        );
    """)
    cursor.close()
    connection.close()

def insert_load(name,gender,age,weight,file_path,crop=None,featfile=None):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #check exist
    cursor.execute("SELECT * FROM `load` WHERE `name`='{:}';".format(name))
    if cursor.fetchone():
        return -1
    
    # filepath transform
    file_path = './'+os.path.relpath(file_path, start=os.curdir).replace('\\','/')

    #insert
    if crop:
        cursor.execute("INSERT INTO `load` (name,gender,age,weight,file,crop,featfile) VALUES ('{:}','{:}','{:}','{:}','{:}','{:}','{:}');".format(name,gender,age,weight,file_path,crop,featfile))
    else:
        cursor.execute("INSERT INTO `load` (name,gender,age,weight,file) VALUES ('{:}','{:}','{:}','{:}','{:}');".format(name,gender,age,weight,file_path))

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
    if name != original_name:
        cursor.execute("SELECT * FROM `load` WHERE `name`='{:}';".format(name))
        if cursor.fetchone():
            return -1
        
    # filepath transform
    file_path = './'+os.path.relpath(file_path, start=os.curdir)

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

def crop_init():
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
        CREATE TABLE IF NOT EXISTS `crop`(
        `set` VARCHAR(100) NOT NULL PRIMARY KEY,
        `x1` INT,
        `x2` INT,
        `y1` INT,
        `y2` INT
        );
    """)
    cursor.close()
    connection.close()

def insert_crop(setting,x1,x2,y1,y2):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #check exist
    cursor.execute("SELECT * FROM `crop` WHERE `set`='{:}';".format(setting))
    if cursor.fetchone():
        return -1
    #insert
    cursor.execute("INSERT INTO `crop` (`set`,`x1`,`x2`,`y1`,`y2`) VALUES ('{:}',{:},{:},{:},{:});".format(setting,x1,x2,y1,y2))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1

def load_crop(sel_set=None):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")
    #load
    if not sel_set:
        cursor.execute("SELECT * FROM `crop`;")
        ret = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM `crop` WHERE `set`='{:}';".format(sel_set))
        ret = cursor.fetchone()

    #close
    cursor.close()
    connection.close()
    return ret

def del_crop(sel_set):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    if type(sel_set) is not list:
        cursor.execute("DELETE FROM `crop` WHERE `set`='{:}';".format(sel_set))
    else:
        for sel in sel_set:
            cursor.execute("DELETE FROM `crop` WHERE `set`='{:}';".format(sel))

    #close
    cursor.close()
    connection.commit()
    connection.close()

def update_load_crop(name,crop):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #update
    cursor.execute("""
        UPDATE `load` 
        SET `crop`='{:}' 
        WHERE `name`='{:}';
    """.format(crop,name))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1

def update_load_feat(name):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #update
    cursor.execute("""
        UPDATE `load` 
        SET `featfile`='G' 
        WHERE `name`='{:}';
    """.format(name))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1


def model_init():
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
        CREATE TABLE IF NOT EXISTS `model`(
        `name` VARCHAR(100) NOT NULL PRIMARY KEY
        );
    """)
    cursor.close()
    connection.close()

def load_model(sel=None):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")
    #load
    if not sel:
        cursor.execute("SELECT * FROM `model`;")
        ret = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM `model` WHERE `name`='{:}';".format(sel))
        ret = cursor.fetchone()

    #close
    cursor.close()
    connection.close()
    return ret

def insert_model(name):
    #connect
    connection = ms.connect(host='localhost', port='3306', user='root', password='root')
    cursor = connection.cursor()
    cursor.execute("USE `micedb`;")

    #check exist
    cursor.execute("SELECT * FROM `model` WHERE `name`='{:}';".format(name))
    if cursor.fetchone():
        return -1
    #insert
    cursor.execute("INSERT INTO `model` (`name`) VALUES ('{:}');".format(name))

    #close
    cursor.close()
    connection.commit()
    connection.close()
    return 1