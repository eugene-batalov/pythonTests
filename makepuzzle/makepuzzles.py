from PIL import Image, ImageDraw, ImageFont
import random
import io
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
import pandas
from os.path import isfile

def complexities(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('select longsideelements, shortsideelements from Complexity')
        c = [r for r in cursor]
    except Error as e:
        print(e)
    finally:
        cursor.close()
    return c

def select_pic_id(conn, filename):
    try:
        cursor = conn.cursor()
        cursor.execute('select pictureid from Pictures where filename = %s', (filename,))
        picId =  cursor.fetchone()
    except Error as e:
        print(e)
    finally:
        cursor.close()
    return picId[0]
    
def create_puzzle(im, c):
    w, h = im.size
    dx = int(w/c[0])
    dy = int(h/c[1])
    pieces = []
    for i in range(0,c[0]*dx,dx):
        for j in range(0,c[1]*dy,dy):
#            print("crop: ",(i, j, i+dx, j+dy))
            pieces.append(im.crop((i, j, i+dx, j+dy)))
    random.shuffle(pieces)
    random.shuffle(pieces)
    new_im = Image.new('RGB', (c[0]*dx,c[1]*dy))
    index = 0
    for i in range(0,c[0]*dx,dx):
        for j in range(0,c[1]*dy,dy):
            new_im.paste(pieces[index], (i , j))
            index+=1
    return new_im

def select_puzzle_by_picId(conn, picId):
    try:
        cursor = conn.cursor()
        cursor.execute('select puzzleid from Puzzles where picture = %s', (picId, ))
        puzzleId =  cursor.fetchone()
    except Error as e:
        print(e)
    finally:
        cursor.close()
    return puzzleId[0]

def insert_icon(conn, picId, puzzleBlob):
    img = Image.open(io.BytesIO(puzzleBlob))
    img = img.resize((100, 100), Image.ANTIALIAS)
    puzzleId = select_puzzle_by_picId(conn, picId)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("MyriadPro-Bold.otf", 42)
    id = str(puzzleId)
    if( int(puzzleId) < 10): id = "00" + id
    elif(int(puzzleId) < 100): id = "0" + id
    draw.text((17, 35), id, (255,0,0), font=font)#(255,255,255),font=font)
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format='JPEG')
    try:
        cursor = conn.cursor()
        cursor.execute('update Puzzles set icon = %s where puzzleid = %s', (imgByteArr.getvalue(), puzzleId))
        conn.commit()
    except Error as e:
        print(e)
    finally:
        cursor.close()

def defGroupZone(fileName):
    if fileName.startswith("Беспл"):
        return (0, 1)
    if fileName.startswith("Природа"):
        return (3, 2)
    if fileName.startswith("Город"):
        return (1, 2)
    if fileName.startswith("Транспорт"):
        return (4, 2)
    if fileName.startswith("Искусство"):
        return (2, 2)
    if fileName.startswith("Турнир"):
        return (6, 3)
    
def insert_puzzle(conn, picId, puzzleBlob, complexityId, question, answer, fileName):
    try:
        (group, zone) = defGroupZone(fileName)
        cursor = conn.cursor()
        cursor.execute('insert into Puzzles (puzzledata, picture, groupid, zone, complexity, task, answer) values (%s, %s, %s, %s, %s, %s, %s)', 
                       (puzzleBlob, picId, str(group), str(zone), str(complexityId), question, answer))
        conn.commit()
        insert_icon(conn, picId, puzzleBlob)
    except Error as e:
        print(e)
    finally:
        cursor.close()
        
def insert_picture_puzzle(conn, dirName, fileName, complexity, complexityId, question, answer):
    try:
        cursor = conn.cursor()
        with open(dirName+fileName+'.jpg', 'rb') as f:
            picture = f.read()
        cursor.execute('insert into Pictures (filename, picturedata) values(%s, %s)', (fileName, picture))
        conn.commit()
        picId = select_pic_id(conn, fileName)
#        print('id:', picId)
        imgByteArr = io.BytesIO()
        puzzle = create_puzzle(Image.open(io.BytesIO(picture)), complexity)
        puzzle.save(imgByteArr, format='JPEG')
        insert_puzzle(conn, picId, imgByteArr.getvalue(), complexityId, question, answer, fileName)
    except Error as e:
        print(e)
    finally:
        cursor.close()
        
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Точка входа
dirName = 'Пазлы_20160526\\'
data = pandas.read_excel('questions.xlsx', converters={'Текст ответа':int}).drop('№', 1).dropna()
#print([data['Текст ответа'][i] for i in data.index[-3:]])
db_config = read_db_config()
conn = MySQLConnection(**db_config)
cursor = conn.cursor()
complexity = complexities(conn)
#print('c[1]: ', c[1][0])
for i in data.index[:]:
    try:
        fileName = data['Имя файла'][i]
        cursor.execute('select pictureid from Pictures where filename = %s', (fileName,))
        if cursor.fetchone():
            print(fileName, 'skipped already in DB')
            continue
        level = i % 4
        complexityId = level + 1
        if(isfile(dirName+fileName+'.jpg')):
            print(fileName, 'processing')
            insert_picture_puzzle(conn, dirName, fileName, complexity[level], complexityId, data['Текст вопроса'][i], data['Текст ответа'][i])
        else:
            print(fileName, 'skipped no such file in dir:', dirName)
    except Error as e:
        print(e)

cursor.close()
conn.close()