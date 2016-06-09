from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from glob import glob
import os
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config



def read_file(filename):
    with open(filename, 'rb') as f:
        photo = f.read()
    return photo


def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)
        
        
def update_blob(id, filename):
    data = read_file(filename)
 
    query = "UPDATE Puzzles " \
            "SET icon = %s " \
            "WHERE puzzleid  = %s"
 
    args = (data, id)
 
    db_config = read_db_config()
 
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query, args)
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        conn.close()


def read_blob():
    query = "SELECT puzzleid, icon FROM Puzzles"
 
    # read database configuration
    db_config = read_db_config()
 
    try:
        conn = MySQLConnection(**db_config)
        cursor = conn.cursor()
        cursor.execute(query)
        for record in cursor:
            id, icon = record
            filename = str(id) + ".jpg"
            write_file(icon, filename)
 
    except Error as e:
        print(e)
 
    finally:
        cursor.close()
        conn.close()


#read_blob()

for filename in glob('*.jpg'):
    if 'updated' in filename:
        os.remove(filename)
        continue

for filename in glob('*.jpg'):
    img = Image.open(filename)
#    print(filename)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("MyriadPro-Bold.otf", 42)
    id = str(int(filename[:-4]))
#    print(int(id))
    if(int(filename[:-4]) < 10): id = "00" + id
    elif(int(filename[:-4]) < 100): id = "0" + id
    draw.text((17, 35), id, (255,0,0), font=font)#(255,255,255),font=font)
    updated_filename = id + '_updated.jpg'
    img.save(updated_filename)
    update_blob(id, updated_filename)