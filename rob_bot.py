from email import message
from fbchat import Client
from fbchat.models import *
from fbchat import log
from random import randint

version = 3

username = "robbot8947"
password = "pythonbot123"

staging = True
if staging:
    thread_id = "5820049228023910"
else:
    thread_id = "4854566911328063"

# Subclass fbchat.Client and override required methods
class Heardler:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.scores = {}
    
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

        # add this check so that rob does not reply to commands he lists in his own patch notes
        if author_id != self.uid:
            log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

            protein = (message_object.text).lower() # cast message to lowercase so that all command checks aren't case sensitive
            auth = message_object.author
            message_author = user_dict[auth]
            uname = message_author.name
            first_name = uname.split(' ')[0]

            print(protein)

            loser = False

            heardle_scores = []
            # initial check if the message that has been sent is a heardle message
            if "#heardle" in protein:
                heardle_number = self.number_from_message(protein)

                heardle_scores.append([auth, protein])

                # iterate through scores in score list and report score
                for score_message in heardle_scores:
                    score = 7 - (score_message[1].count('⬛️') + score_message[1].count('🟥') + score_message[1].count('🟩'))

                # check score is valid and that score has not already been submitted for today
                if heardle_number not in message_author.scores.keys():
                    valid_score = False
                    if score <= 6 and score >= 0:
                        # i.e. valid score
                        valid_score = True
                        message_author.scores[heardle_number] = score
                        message_string = (f"{first_name} scored {score} for Heardle #{heardle_number}").upper()
                    else: # score is not valid
                        if score > 6:
                            message_string = (f"{first_name} probably cheated on Heardle #{heardle_number} today. score {score} is impossible, maximum score is 6").upper()
                        elif score < 0 :
                            message_string = (f"{first_name} probably didnt score {score} for Heardle #{heardle_number}, because score can't be negative").upper()
                else:
                    message_string = (f"{first_name} has already submitted a score for Heardle #{heardle_number}").upper()

                # check if player is a loser or not and score zeros                
                if score == 0:
                    loser = True         
        
                # set message to message decided in previous block, but transformed to uppercase
                message_object.text = message_string.upper()

                # send message set before
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)
                if not valid_score:
                    message_object.text = 'SOMETHING PROBABLY WENT WRONG, SCORE NOT RECORDED. MAYBE TRY AGAIN'
                    self.send(message_object, thread_id=thread_id, thread_type=thread_type)
                # i.e. if score is low
                elif loser:
                    message_object.text = insults[randint(0, len(insults)-1)]
                    loser = False
                    self.send(message_object, thread_id=thread_id, thread_type=thread_type)

            # logic tree for commands

            # if message isn't a heardle message, check to see if there is a command for rob in the message
            elif '/rob' in protein:
                
                # first command /rob here, reports whether rob is here and if he is asleep or not
                if 'status' in protein:
                    if self.awake:
                        message_object.text = 'RUNNING'
                    else:
                        message_object.text = 'ASLEEP'

                # second command /rob wake, will wake rob up if he is asleep
                elif 'wake' in protein:
                    self.awake = True
                    message_object.text = "AWAKE"

                # third command, /rob sleep, puts rob to sleep. rob will not 
                elif 'sleep' in protein:
                        message_object.text = "ZZZ"
                        self.awake = False
                
                # these commands depend on rob being awake
                elif self.awake:
                    # fourth command, /rob notes, rob will send patch notes for current version ot the chat
                    if 'notes' in protein:
                        message_object.text = notes
                    
                    # if none have triggered  
                    else:
                        message_object.text = 'NO COMMAND DETECTED\n' + commands
                else:
                    send_message = False

                if send_message:
                    self.send(message_object, thread_id=thread_id, thread_type=thread_type)

    def number_from_message(self, message):
        start_index = 10
        num_str = ""
        for char in message[start_index:]:
            if char.isnumeric():
                num_str += char
                print(char)
                print(num_str)
            else:
                break
        heardle_number = int(num_str)
        return heardle_number

insults = ["and they call me a bot".upper()]
wake_message = f"ROB_BOT V{version} BOOTING"
boot_complete = "BOOT COMPLETE"
commands = 'valid commands are: status, wake, sleep, notes'.upper()

client = HeardleBot(username, password)

thread_type = ThreadType.GROUP

# send wake message
client.send(Message(text=wake_message), thread_id=thread_id, thread_type=thread_type)

# open patch notes file for corresponding version and read them
file = open(f'patch_notes/patch_notes{version}.txt')
notes = file.read()

print(notes)

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

client.send(Message(text=boot_complete), thread_id=thread_id, thread_type=thread_type)
client.listen()
