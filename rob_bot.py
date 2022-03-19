from fbchat import Client
from fbchat.models import *
from fbchat import log
from random import randint

version = 2

username = "robbot8947"
password = "pythonbot123"

staging = False
if staging:
    thread_id = "5820049228023910"
else:
    thread_id = "4854566911328063"

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
    awake = True
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)

        log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

        protein = (message_object.text).lower()
        auth = message_object.author
        uname = user_dict[auth].name
        first_name = uname.split(' ')[0]

        print(protein)

        loser = False

        if self.awake:
            if '/rob' in protein.lower():
                message_object.text = "leave me alone man that shit isn't coded yet"
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)
            
            if 'goodnight rob' in protein.lower:
                message_object.text = "zzz"
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)
                self.awake = False

            if ' rob' in protein.lower():
                message_object.text = f"hey {first_name.lower()}"
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

            if 'thanks rob' in protein.lower():
                message_object.text = "welcome g"
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

            if 'patch notes please rob' in protein.lower():
                message_object.text = notes
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

        if 'wake up rob' in protein.lower():
            self.awake = True
            message_object.text = "sup"
            self.send(message_object, thread_id=thread_id, thread_type=thread_type)

        if 'are you here rob' in protein:
            if self.awake:
                message_object.text = 'yeah'
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)
            else:
                message_object.text = 'zzz'
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

        heardle_scores = []
        if "#Heardle" in protein:
            heardle_number = self.number_from_message(protein)

            heardle_scores.append([auth, protein])

            for score_message in heardle_scores:
                score = 7 - (score_message[1].count('⬛️') + score_message[1].count('🟥') + score_message[1].count('🟩'))
                if score > 6:
                    message_string = (f"{first_name} didn't score {score} for Heardle #{heardle_number} today, because that's impossible")
                if score == 0:
                    message_string = (f"{first_name} scored {score} for Heardle #{heardle_number} today")
                    loser = True
                else:
                    message_string = (f"{first_name} scored {score} for Heardle #{heardle_number} today")

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
wakes = ['alive', 'sup', 'back sorry', 'hey guys']
patch_notes = "patch notes for beta version 0.0 -won't respond if you just say a word with rob in it\n"

client = HeardleBot(username, password)

thread_type = ThreadType.GROUP
wake_text = wakes[randint(0, len(wakes)-1)]
client.send(Message(text=wake_text), thread_id=thread_id, thread_type=thread_type)

# open patch notes file for corresponding version and read them
file = open(f'patch_notes/patch_notes{version}.txt')
notes = file.read()

print(notes)

# send patch notes to chat
client.send(Message(text=notes), thread_id=thread_id, thread_type=thread_type)

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