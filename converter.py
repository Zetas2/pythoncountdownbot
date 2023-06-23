# Handeling the database
import sqlite3

"""Yup... All this does is to add a column to a database. 
Dont mind it... It wont be used more than for me to convert 
old databases to new ones with more features"""

# conn_info_db = sqlite3.connect("Countdowns.db")
# conn_info_db.execute("""ALTER TABLE Countdowns ADD COLUMN countdownname varchar(50);""")


"""
All this below was to move the countdowns for premium users from one database to another
"""
"""
conn_premium_db = sqlite3.connect("premiumGuilds.db")
cursor = conn_premium_db.execute(
    "SELECT guildid FROM Premium"
)
allids = []
for row in cursor:
    if str(row[0]) not in allids:
        allids.append(str(row[0]))
allids.sort()
print(allids)
"""

conn_premium_countdowns_db = sqlite3.connect("PremiumCountdowns.db")
# conn_premium_countdowns_db.execute(
#    """CREATE TABLE IF NOT EXISTS PremiumCountdowns (timestamp int,msgid int,channelid int,guildid int,roleid int,startedby int,times int,length int,imagelink varchar(255),messagestart varchar(255),messageend varchar(255),messagecompleted varchar(255),number int, countdownname varchar(50));"""
# )
cursor = conn_premium_countdowns_db.execute(
    "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,number,countdownname FROM PremiumCountdowns WHERE guildid in ('1026639365503459329', '1040842883885965423', '1078358047082156122', '1106937341152591902', '1119672797430558751', '719541990580289557', '832785220184571934', '837389954631204935', '849629393600381008', '893576552904806431', '898302095558598696', '936584263086772254', '946567581060464710', '988768713891250198');",
)

for row in cursor:
    print(row)

conn_countdowns_db = sqlite3.connect("Countdowns.db")
cursor = conn_countdowns_db.execute(
    "SELECT timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,number,countdownname FROM Countdowns WHERE guildid in ('1026639365503459329', '1040842883885965423', '1078358047082156122', '1106937341152591902', '1119672797430558751', '719541990580289557', '832785220184571934', '837389954631204935', '849629393600381008', '893576552904806431', '898302095558598696', '936584263086772254', '946567581060464710', '988768713891250198');",
)
print(
    "--------------------------------------------------------------------------------------------------------------"
)
allpremium = []
for row in cursor:
    allpremium.append(row)
#    print(row)

for row in allpremium:
    print(row)


# for row in cursor:
#    countdownname = str(row[13])
#    number = str(row[12])
#    message_completed = str(row[11])
#    message_end = str(row[10])
#    message_start = str(row[9])
#    image_link = str(row[8])
#    length = int(row[7])
#    times = int(row[6])
#    started_by = int(row[5])
#    role_id = int(row[4])
#    guild_id = int(row[3])
#    channel_id = int(row[2])
#    msg_id = int(row[1])
#    timestamp = int(row[0])
#
#    conn_premium_countdowns_db.execute(
#        "INSERT INTO PremiumCountdowns (timestamp,msgid,channelid,guildid,roleid,startedby,times,length,imagelink,messagestart,messageend,messagecompleted,number,countdownname) VALUES (:timestamp,:msgid,:channelid,:guildid,:mention,:startedby,:times,:length,:imagelink,:messagestart,:messageend,:messagecompleted,:number,:countdownname);",
#        {
#            "timestamp": int(timestamp),
#            "msgid": int(msg_id),
#            "channelid": int(channel_id),
#            "guildid": int(guild_id),
#            "mention": int(role_id),
#            "startedby": int(started_by),
#            "times": int(times),
#            "length": int(length),
#            "imagelink": str(image_link),
#            "messagestart": str(message_start),
#            "messageend": str(message_end),
#            "messagecompleted": str(message_completed),
#            "number": (int(1)),
#            "countdownname": str(countdownname),
#        },
#    )
#    conn_premium_countdowns_db.commit()
