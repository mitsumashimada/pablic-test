import glob
import ast
import sys
import os

def chatReplayConverter(filepath):
   print(filepath)
   filename = os.path.basename(filepath)
   dirname = os.path.dirname(filepath)
   target_id = filename.split('.')[0]
   if dirname != "":
       output_path = dirname + "/" + target_id + ".tsv"
   else:
       output_path = target_id + ".tsv"

   if glob.glob(output_path):
       print("Exists")
       return

   count = 1
   result = ""
   with open(filepath, 'r', encoding='utf8') as f:
       lines = f.readlines()
       for line in lines:
           sys.stdout.write('\rProcessing line %d' % (count))
           if 'liveChatTickerPaidMessageItemRenderer' in line:
               continue
           if 'liveChatTextMessageRenderer' not in line and 'liveChatPaidMessageRenderer' not in line:
               continue
           ql = line
           frac = target_id
           #frac += (", #Chat No.%05d " % count)
           frac += f'\t{count}'
           info = ast.literal_eval(ql)

           # Case Normal Chat
           if 'liveChatTextMessageRenderer' in line:
               info = info['replayChatItemAction']['actions'][0]['addChatItemAction']['item']['liveChatTextMessageRenderer']
               content = ""
               if 'simpleText' in info['message']:
                   content = info['message']['simpleText']
               elif 'runs' in info['message']:
                   for fragment in info['message']['runs']:
                       if 'text' in fragment:
                           content += fragment['text']
               else:
                   print("no text")
                   continue
               authorName = info['authorName']['simpleText']
               time = info['timestampText']['simpleText']
               #frac += ", type: NORMALCHAT, user: \"" + authorName + "\", time: " + time + ", amount: 0, \"" + content + "\"\n"
               frac += f'\tNORMALCHAT\t{authorName}\t{time}\t0\t{content}\n'

           # Case Super Chat
           if 'liveChatPaidMessageRenderer' in line:
               info = info['replayChatItemAction']['actions'][0]['addChatItemAction']['item']['liveChatPaidMessageRenderer']
               content = ""
               if 'message' in info:
                   if 'simpleText' in info['message']:
                       content = info['message']['simpleText']
                   elif 'runs' in info['message']:
                       for fragment in info['message']['runs']:
                           if 'text' in fragment:
                               content += fragment['text']
                   else:
                       print("no text")
                       continue

               if 'authorName' in info:
                   authorName = info['authorName']['simpleText']
               else:
                   authorName = "%anonymous%"
               time = info['timestampText']['simpleText']
               purchaseAmout = info['purchaseAmountText']['simpleText']
               #frac += ", type: SUPERCHAT, user: \"" + authorName + "\", time: " + time + ", amount: " + purchaseAmout + ", \"" + content + "\"\n"
               frac += f'\tSUPERCHAT\t{authorName}\t{time}\t{purchaseAmout}\t{content}\n'
           result += frac
           count += 1

   sys.stdout.write('\nDone!\n')
   try:
       with open(output_path, 'w', encoding='utf8') as f:
           f.write(result)
   except:
       print("Cannot convert json file")

file = sys.argv[1]
chatReplayConverter(file)
