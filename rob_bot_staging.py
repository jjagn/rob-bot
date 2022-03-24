from fbchat import Client
from fbchat.models import *
from fbchat import log
from random import randint
from pword import password
from collections import Counter

version = 4

username = "robbot8947"

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
        if len(self.scores.values()) > 0:
            return sum(self.scores.values()) / len(self.scores.values())
        else:
            return "no scores for player"

    def minimum_score(self):
        if len(self.scores.values()) > 0:
            return min(self.scores.values())
        else:
            return "no scores for player"

    def maximum_score(self):
        if len(self.scores.values()) > 0:
            return max(self.scores.values())
        else:
            return "no scores for player"

    def score_message(self):
        # returns a string with the leaderboard message showing score distribution for the player
        if len(self.scores.values()) > 0:
            score_list = self.scores.values()
            individual_scores = Counter(score_list)
            print_str = f"PLAYER {self.name.upper()} SCOREBOARD:\n"
            total = sum(individual_scores.values())
            print(f"total = {total}")
            possible_scores_list = [1,2,3,4,5,6]
            for score in possible_scores_list:
                print(f"score: {score}")
                try:
                    occurences = individual_scores[score]
                except:
                    occurences = 0
                print(f"occurences: {occurences}")

                multiplier = round(15*(occurences)/(total))

                print_str += f"{score}: "
                if occurences:
                    print_str += "■"*multiplier + (15-multiplier)*" " + f"({occurences})" + "\n"
                else:
                    print_str += "\n"
            
            return print_str
        else:
            return "no scores for player"

        

class HeardleBot(Client):
    awake = True
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.markAsDelivered(thread_id, message_object.uid)
        self.markAsRead(thread_id)
        self.process_message(author_id, message_object, thread_id, thread_type, False)

    def process_message(self, author_id, message_object, thread_id, thread_type, bootup_read=True):
        # add this check so that rob does not reply to commands he lists in his own patch notes
        if (author_id != self.uid) and (message.text != None) and message_object.author in user_dict.keys():
            # log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))

            protein = (message_object.text).lower() # cast message to lowercase so that all command checks aren't case sensitive
            auth = message_object.author
            message_author = user_dict[auth]
            uname = message_author.name
            first_name = uname.split(' ')[0]

            # print(protein)

            loser = False

            send_message = False

            # initial check if the message that has been sent is a heardle message
            if "#heardle" in protein:
                valid_score = False
                print(f"message: {protein}")
                heardle_number = self.number_from_message(protein)
                if heardle_number == None:
                    # leave function, invalid entry
                    return
                # calculate score. golf scoring
                score = (protein.count('⬛️') + protein.count('🟥') + protein.count('🟩'))

                # check score is valid and that score has not already been submitted for today
                if heardle_number not in message_author.scores.keys():
                    if score <= 6 and score >= 0:
                        # i.e. valid score
                        valid_score = True
                        message_author.scores[heardle_number] = score
                        message_string = (f"{first_name} scored {score} for Heardle #{heardle_number}").upper()
                        send_message = True
                    else: # score is not valid
                        if score > 6:
                            message_string = (f"{first_name} probably cheated on Heardle #{heardle_number} today. score {score} is impossible, maximum score is 6").upper()
                            send_message = True
                        elif score < 0 :
                            message_string = (f"{first_name} probably didnt score {score} for Heardle #{heardle_number}, because score can't be negative").upper()
                            send_message = True
                else:
                    message_string = (f"{first_name} has already submitted a score for Heardle #{heardle_number}").upper()
                    send_message = True

                # check if player is a loser or not and score zeros                
                if score == 0:
                    loser = True         
        
                # set message to message decided in previous block, but transformed to uppercase
                message_object.text = message_string.upper()
                send_message = True

                # send message set before unless it is the initial bootup read, in which case we 
                # don't want to spam the chat with messages
                if send_message and not bootup_read:
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
            elif '/rob' in protein and not bootup_read:
                
                # first command /rob here, reports whether rob is here and if he is asleep or not
                if 'status' in protein:
                    send_message = True
                    if self.awake:
                        message_object.text = 'RUNNING'
                    else:
                        message_object.text = 'ASLEEP'

                # second command /rob wake, will wake rob up if he is asleep
                elif 'wake' in protein:
                    self.awake = True
                    message_object.text = "AWAKE"
                    send_message = True

                # third command, /rob sleep, puts rob to sleep. rob will not 
                elif 'sleep' in protein:
                        message_object.text = "ZZZ"
                        self.awake = False
                        send_message = True
                
                elif 'leaderboard' in protein:
                    message_object.text = leaderboard(user_dict)
                    print('leaderboard')
                    send_message = True

                elif 'score' in protein:
                    message_object.text = message_author.score_message()
                    print('score')
                    send_message = True
                
                # these commands depend on rob being awake
                elif self.awake:
                    # fourth command, /rob notes, rob will send patch notes for current version ot the chat
                    if 'notes' in protein:
                        message_object.text = notes
                        send_message = True
                    
                    # if none have triggered  
                    else:
                        message_object.text = 'NO COMMAND DETECTED\n' + commands
                        print('no command detected')
                        send_message = True
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
                # print(char)
                # print(num_str)
            else:
                break
        try:
            heardle_number = int(num_str)
        except(ValueError):
            heardle_number = None
        return heardle_number

def leaderboard(users):
    # returns a string giving a leaderboard of all chat members ranked by average score
    scores = []
    for player in users.values():
        score = player.average_score()

        print(player.name)
        print(score)

        if type(score) == float:
            scores.append((player.name, score))

    sorted_by_score = sorted(scores, key=lambda tup: tup[1])

    print(sorted_by_score)

    print_str = "LEADERBOARD: \n"
    i = 1
    for item in sorted_by_score:
        name = item[0]
        score = item[1]
        print_str += f"{i}. " + name.upper() + " "*(25-len(name)) +  "{:.2f}".format(score) + "\n"
        i += 1

    print(print_str)

    return(print_str)



insults = ["and they call me a bot".upper()]
wake_message = f"ROB_BOT V{version} BOOTING"
boot_complete = "BOOT COMPLETE"
commands = 'valid commands are: status, wake, sleep, notes'.upper()

client = HeardleBot(username, password)

thread_type = ThreadType.GROUP

# open patch notes file for corresponding version and read them
file = open(f'patch_notes/patch_notes{version}.txt')
notes = file.read()
file.close()

# print(notes)

print('fetching threads:')
threads = client.fetchThreadList()
# print(threads)

for thread in threads:
    # print(thread)
    if thread.uid == thread_id:
        group = thread
        print('thread found')
    print('\n')

user_dict = {}

for user_id in group.participants:
    # loop through users in thread and create a heardler object for each
    user = client.fetchUserInfo(user_id)[user_id]
    print(user)
    print("user's name: {}".format(user.name))
    
    user_dict[user_id] = Heardler(user_id, user.name)

# print(user_dict)

# fetch messages from the thread
messages = client.fetchThreadMessages(thread_id, limit = 10000)
# Since the message come in reversed order, reverse them
messages.reverse()

print(f"messages retrieved: {len(messages)}")
for message in messages:
    client.process_message(message.uid, message, thread_id, thread_type)
    #print('processed message successfully')

client.send(Message(text=boot_complete), thread_id=thread_id, thread_type=thread_type)
client.listen()
