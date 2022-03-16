from fbchat import Client
from fbchat.models import *
from fbchat import log
from random import randint

username = "robbot8947"
password = "pythonbot123"

# Subclass fbchat.Client and override required methods
class Heardler:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.scores = []
    
    def average_score(self):
        return sum(self.scores) / len(self.scores)

    def minimum_score(self):
        return min(self.scores)

    def maximum_score(self):
        return max(self.scores)

class HeardleBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        protein = message_object.text
        auth = message_object.author

        print(protein)
        loser = False
        if '/rob' in protein:
            message_object.text = "leave me alone man that shit isn't coded yet"
            self.send(message_object, thread_id=thread_id, thread_type=thread_type)


        heardle_scores = []
        if "#Heardle" in protein:
            heardle_number = self.number_from_message(protein)

            heardle_scores.append([auth, protein])

            uname = user_dict[auth].name

            for score_message in heardle_scores:
                score = score_message[1].count('🟩')
                if score > 5:
                    message_string = (f"{uname.split(' ')[0]} didn't score {score} for Heardle #{heardle_number} today, because that's impossible")
                if score == 0:
                    message_string = (f"{uname.split(' ')[0]} scored {score} for Heardle #{heardle_number} today")
                    loser = True
                else:
                    message_string = (f"{uname.split(' ')[0]} scored {score} for Heardle #{heardle_number} today")

            if "#Heardle" in message_object.text:
                message_object.text = message_string

                self.send(message_object, thread_id=thread_id, thread_type=thread_type)
                if loser:
                    message_object.text = insults[randint(0, len(insults)-1)]
                    self.send(message_object, thread_id=thread_id, thread_type=thread_type)
                    loser = False

    def number_from_message(self, message):
        start_index = 10
        num_str = ""
        for char in message[10:]:
            if char.isnumeric():
                num_str += char
                print(char)
                print(num_str)
            else:
                break
        heardle_number = int(num_str)
        return heardle_number


insults = ["and they call me a bot"]

client = HeardleBot(username, password)

thread_id = "4854566911328063"
thread_type = ThreadType.GROUP
client.send(Message(text="alive"), thread_id=thread_id, thread_type=thread_type)
    
threads = client.fetchThreadList()
print(threads)

for thread in threads:
    print(thread)
    print('\n')

group = threads[0]

user_dict = {}

for user_id in group.participants:
    user = client.fetchUserInfo(user_id)[user_id]
    # print(user)
    print("user's name: {}".format(user.name))
    
    user_dict[user_id] = Heardler(user_id, user.name)

print(user_dict)

client.listen()