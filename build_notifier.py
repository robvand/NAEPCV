import sys
from ciscosparkapi import CiscoSparkAPI

SESSION_ROOM_ID= "Y2lzY29zcGFyazovL3VzL1JPT00vM2E4NjVlMDAtMzhiMi0xMWVhLTg1NWQtOTM2NGQwMDc3NmQ3"


class Build_Notifier:

    def __init__(self, token, branch, status, message=None):
        self.bot = CiscoSparkAPI(token)
        self.message = message if message else "Ping"
        self.branch = branch
        if status == "success":
            self.message = "&#x2705; - " + self.message
        else:
            self.message = "&#x274C; - " + self.message

    def send_notification(self):
        for room in self.bot.rooms.list():
            if room.type == 'group':
                if self.branch != "all" and room.id == SESSION_ROOM_ID:
                    continue
                try:
                    self.bot.messages.create(roomId=room.id, markdown=self.message)
                except Exception as e:
                    print(f"Exception was raised {e}")


if __name__ == '__main__':
    token, branch, status, *message = sys.argv[1:]
    message_str = " ".join(message)
    try:
        Build_Notifier(token, branch, status=status, message=message_str).send_notification()
    except Exception as e:
        print(f'Failed to send notifications: {e}')
