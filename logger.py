from datetime import datetime
import sqlite3
class Log:
    def __init__(self):
       pass

    def write_log(self, sessionID, log_message):
        self.file_object = open("conversationLogs/"+sessionID+".txt", 'a+')
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H:%M:%S")
        self.file_object.write(
            str(self.date) + "/" + str(self.current_time) + "\t\t" + log_message + "\n")
        self.file_object.close()
        self.insert_to_database(self.current_time,log_message)

    def insert_to_database(self, date, log_message):
        try:
            conn = sqlite3.connect('chat')
            curr = conn.cursor()
            curr.execute("""create table if not exists log_data(
                            date text,
                            log_message text
                            )""")
            query = """insert into log_data values('%s','%s')"""%(date,log_message)
            curr.execute(query)
            conn.commit()
            conn.close()
        except:
            pass
