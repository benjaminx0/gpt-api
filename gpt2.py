import openai
import os
from termcolor import colored

key = "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"

openai.api_key = key


model_engine = "gpt-3.5-turbo"
engine_name = "-T"

doStream = True
allmemory = []
default = [{"role":"system", "content" : "You are an AI chatbot able to help with many tasks"}]
allmemory.append(default)

prevmem = []
alwaysAdd = True #alwaysAdd = False
prevans = ""
token = 2048
randomness = 0.3
currentslot = 0
totalslots = 0
titles = {}

enginecmds = colored("""\
/engine view
/engine ada (A)           (The cheapest and fastest engine, but less powerful)
/engine babbage (B)       (Faster than Curie and less cost)
/engine curie (C)         (Less powerful than Davinci, but less cost and much faster)
/engine davinci (D)       (The most powerful of the GPT-3 engines, good at most tasks)
/engine code (DC)         (The most powerful codex engine, optimized for coding & words->code)
/engine turbo (T)         (The ChatGPT engine, optimized for dialogue)
/tokens [number]          (<2048 recommended) (Amount of tokens requested (1k tokens ~= 750 words))
/temperature [number]     (<1 recommended) (Creativity/randomness in model)
/system [string]          (System instructions for Turbo model (gpt-3.5-turbo))

""","red")

streamcmds = colored("""
/stream true              (Enable streaming (one word at a time) responses)
/stream false             (Print entire completion at once) (Does not improve speed)
""","cyan")

memorycmds = colored("""
/memory add               (Add a single prompt-response pair to the memory)
/memory alwaysAdd         (Add prompts and responses to memory by default) (Default choice)
/memory neverAdd          (Don't add prompts and responses to memory by default)
/memory new               (Create a new memory slot) (Effectively creates new conversation)
/memory slot [number]     (Switch memory slots) (Use /memory printAll to view the index for slots)
/memory print             (Print the contents of the current memory) (Shows indexes to use for deletion)
/memory printAll          (Print the entire contents of memory) (Shows indexes for slot switching or deletion)
/memory clear             (Clear the current memory slot)
/memory clearAll          (Clear every memory slot)
/memory del [index]       (Delete an element of memory in the current slot) (View indexes with /memory print)
/memory del [start]-[end] (Delete multiple elements of memory, from the starting element (inclusive) to the ending one (exclusive))
/memory delSlot [index]   (Delete an entire slot of memory)
/memory rename [string]   (Rename the current memory slot)
/memory regenerate        (Generate a new title for the current slot of memory)

/memory condense (BETA)   (Condenses the memory, allowing for context to be retained longer)
""","yellow")

misccmds = colored("""
/help                     (Shows this list of commands)
/clear                    (Clears the screen)
/quit                     (Quits the program completely) (This erases all memory)
""","magenta")

tips = colored("\nYou can also replace engine name with its corresponding letter. Higher letters (A > B) are less powerful but have better cost (T is on par with D, and DC is slightly less than D)","green")

os.system("clear")
prompt = input(colored("You > ","green"))
prevprompt = ""
while prompt != "/quit":
    #print(currentslot)
    if prompt == "/help":
        print(enginecmds
            + streamcmds
            + memorycmds
            + misccmds
            + tips)
    elif prompt.startswith("/system"):
        newinstructions = prompt[7:].strip()
        allmemory[currentslot][0]["content"] = (newinstructions if newinstructions != "" else " ")
        
    elif prompt == "/memory add":
        if prevprompt.strip() != "":
            allmemory[currentslot].append({"role": "user", "content":prevprompt})
            allmemory[currentslot].append({"role":"assistant","content":prevans}) #prevprompt & prevans
            print(colored("Appended to memory","yellow"))
        else:
            print(colored("Nothing to append!","yellow"))

    elif prompt == "/memory clear":
        allmemory[currentslot] = [{"role":"system", "content" : allmemory[currentslot][0]["content"]}]
        print(colored("Memory cleared","yellow"))

    elif prompt == "/memory alwaysAdd":
        alwaysAdd = True
        print(colored("Always append to memory","yellow"))

    elif prompt == "/memory neverAdd":
        alwaysAdd = False
        print(colored("Never automatically append to memory","yellow"))

    elif prompt == "/memory print":
        index = 0
        for i in allmemory[currentslot]:
            if i["role"] != "system":
                char = ("Q" if i["role"] == "user" else "A")
                print(str(index)+" "+colored(char+": "+i["content"],"yellow"))
                index+=1
        print()
    #elif prompt == "/memory autoDel":
        #autoDel = True
    
    elif prompt == "/memory condense":
        print(colored("Warning: This makes memory only compatible with non-turbo models!\nPress [Y] if you want to continue","red"))
        if input(colored(">","red")) == "y":
            memorystr = ""
            for i in allmemory[currentslot]:
                memorystr += i+"\n"
            
            completion = openai.Completion.create(
                engine="text-davinci-003",
                prompt="Summarize this string, with one sentence about each paragraph.\n"+memorystr,
                n=1,
                stop=None,
                max_tokens=token,
                temperature=0.3,
            )
            prevmem = []
            for i in allmemory[currentslot]:
                prevmem.append(i)
                
            newmem = completion.choices[0].text.strip()
            if newmem.strip() != "":
                allmemory[currentslot] = [newmem]
                print(colored("Condensing complete","yellow"))
            else:
                print(colored("Error occured during condensing","red"))
    
    elif prompt == "/memory new":
        currentslot = totalslots + 1
        totalslots += 1
        allmemory.append([{"role":"system", "content" : "You are an AI chatbot able to help with many tasks"}])
        prevmem = []
        print(colored("New slot created!","yellow"))
        
    elif prompt.startswith("/memory slot"):
        #c = input(colored("WARNING: Make sure to save memory with /memory new before switching slots, otherwise current slot will not be saved. Press [Y] to continue and anything else to cancel\n>","red"))
        #if c.lower() == "y":
        try:
            currentslot = int(prompt[12:].strip())
            prevmem = []
            for i in allmemory[currentslot]:
                prevmem.append(i)
                
            print(colored("Memory changed to "+prompt[12:].strip(),"yellow"))
        except:
            print(colored("Error occured when retrieving memory!","red"))
        
    
    elif prompt == "/memory printAll":
        print()
        index = 0
        for i in allmemory:
            if index == currentslot:
                try:
                    print(colored("Slot "+str(index)+" "+titles[index],"green"))
                except:
                    print(colored("Slot "+str(index),"green"))
            else:
                try:
                    print(colored("Slot "+str(index)+" "+titles[index]))
                except:
                    print(colored("Slot "+str(index),"green"))
                    
            index += 1
            for j in i:
                print(colored(j,"yellow"))
            print()
        print()
    
    elif prompt == "/memory clearAll":
        allmemory = []
        titles = {}
        allmemory.append([{"role":"system", "content" : "You are an AI chatbot able to help with many tasks"}])
        currentslot = 0
        print(colored("All memory cleared","yellow"))
    
    elif prompt == "/memory undo":
        allmemory[currentslot] = prevmem
        
      
    elif prompt.startswith("/memory delSlot"):
        try:
            index = int(prompt[15:])
            if len(allmemory) == 1:
                print(colored("Cannot delete all slots\nTry clearing memory instead","red"))
            else:
                allmemory.remove(allmemory[index])
                if index == currentslot:
                    currentslot = 0
                elif index > currentslot:
                    currentslot = currentslot
                else: #index < currentslot
                    currentslot -= 1
                    
                totalslots -= 1
                print(colored("Deletion complete","yellow"))
            titles.pop(index)
            
        except:
            print(colored("Error occured","red"))
            
    elif prompt.startswith("/memory del"):
        try:
            prevmem = []
            for i in allmemory[currentslot]:
                prevmem.append(i)
                
            if "-" not in prompt:
                index = int(prompt[11:]) + 1
                
                #print(prevmem)
                allmemory[currentslot].remove(allmemory[currentslot][index])
                #print(prevmem)
            else:
                promptstr = prompt[11:]
                promptstr = promptstr.split("-")
                
                start = int(promptstr[0])
                end = int(promptstr[1])
                if start > end or end > len(allmemory[currentslot])+1:
                    assert False
                delamount = end-start
                
                for i in range(0,delamount):
                    allmemory[currentslot].remove(allmemory[currentslot][start+1])
                
        except:
            print(colored("Error occured","red"))
            
    elif prompt == "/memory regenerate":
        tempmem = []
        for i in allmemory[currentslot]:
            tempmem.append(i)
        tempmem.append({"role":"user","content":"create a title for the conversation so far"})
        try:
            newtitle = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=tempmem,
                temperature=0.3,
            )
            titles[currentslot] = newtitle['choices'][0]['message']['content'].strip()
            print(colored("Title set to "+titles[currentslot],"blue"))
        except:
            print(colored("Failed to generate new title","red"))
                
    elif prompt.startswith("/memory rename"):
        newname = prompt[14:].strip()
        if input(colored("Changing the name of the current slot to '"+newname+"', press [Y] to confirm and continue\n>","red")).lower() == "y":
            titles[currentslot] = newname
            print(colored("Name changed successfully!","yellow"))

    elif prompt.startswith("/tokens"):
        try:
            token = int(prompt[7:].strip())
            
        except:
            token = 2048
            print(colored("Error occured","red"))
    
    elif prompt.startswith("/temperature"):
        try:
            randomness = float(prompt[12:].strip())
            #print(randomness)
        except:
            print(colored("Error occured","red"))
    
    elif prompt == "/clear":
        os.system("clear")

    elif prompt == "/engine view":
        print(colored(model_engine,"cyan"))
    
    elif prompt == "/engine ada" or prompt.lower() == "/engine a":
        model_engine = "text-ada-001"
        engine_name = "-A"
        print(colored("Set to text-ada-001 (A)","red"))

    elif prompt == "/engine babbage" or prompt.lower() == "/engine b":
        model_engine = "text-babbage-001"
        engine_name = "-B"
        print(colored("Set to text-babbage-001 (B)","red"))

    elif prompt == "/engine curie" or prompt.lower() == "/engine c":
        model_engine = "text-curie-001"
        engine_name = "-C"
        print(colored("Set to text-curie-001 (C)","red"))

    elif prompt == "/engine davinci" or prompt.lower() == "/engine d":
        model_engine = "text-davinci-003"
        engine_name = "-D"
        print(colored("Set to text-davinci-003 (D)","red"))
    
    elif prompt == "/engine code" or prompt.lower() == "/engine dc":
        model_engine = "code-davinci-002"
        engine_name = "-DC"
        print(colored("Set to code-davinci-002 (DC)", "red"))
        
    elif prompt == "/engine turbo" or prompt.lower() == "/engine t":
        model_engine = "gpt-3.5-turbo"
        engine_name = "-T"
        print(colored("Set to gpt-3.5-turbo (T)","red"))

        
    elif prompt == "/stream true":
        doStream = True
        print(colored("Stream = True","cyan"))

    elif prompt == "/stream false":
        doStream = False
        print(colored("Stream = False","cyan"))

    else:
        try:
            prevprompt = prompt
            
            
            print(colored("GPT"+engine_name+" > ","blue"),end="",flush=True)
            if model_engine != "gpt-3.5-turbo":
                tempprompt = ""
                for i in allmemory[currentslot]:
                    tempprompt += i["role"] + ":" + i["content"] + "\n"
                    
                completion = openai.Completion.create(
                    engine=model_engine,
                    prompt=tempprompt+"\n"+prompt,
                    n=1,
                    stop=None,
                    max_tokens=token,
                    temperature=randomness,
                    stream=doStream,
                )
                if doStream:
                    temp = ""
                    index = 0
                    for event in completion:
                        if index > 1 or event['choices'][0]['text'] != "\n":
                            print(colored(event['choices'][0]['text'],"cyan"),end="",flush=True)
                    
                        index += 1
                        temp += event['choices'][0]['text']
                
                    prevans = temp.strip()

                else:
                    print(colored(completion.choices[0].text.strip(),"cyan"),end="")
                    prevans = completion.choices[0].text.strip()
                    
            else:
                allmemory[currentslot].append({"role":"user","content":prompt})
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=allmemory[currentslot],
                    temperature=randomness,
                    stream=doStream,
                )
                if doStream:
                    temp = ""
                    for event in completion:
                        try:
                            print(colored(event['choices'][0]['delta']['content'],"cyan"),end="",flush=True)
                            temp += event['choices'][0]['delta']['content']
                        except:
                            pass
                                                    
                    prevans = temp
                    
                else:
                    print(colored(completion['choices'][0]['message']['content'].strip(),"cyan"),end="")
                    prevans = completion['choices'][0]['message']['content'].strip()

    
            print()
            
            if alwaysAdd and model_engine != "gpt-3.5-turbo":
                allmemory[currentslot].append({"role" : "user", "content": prevprompt}) #prevprompt & prevans
            allmemory[currentslot].append({"role" : "assistant", "content" : prevans})

            if currentslot not in titles:
                tempmem = []
                for i in allmemory[currentslot]:
                    tempmem.append(i)
                tempmem.append({"role":"user","content":"create a title for the conversation so far"})
                
                newtitle = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=tempmem,
                    temperature=0.3,
                )
                titles[currentslot] = newtitle['choices'][0]['message']['content'].strip()
                print(colored("Title set to "+titles[currentslot]+" (changeable with /memory rename)","blue"))
                
            
            if not alwaysAdd:
                allmemory[currentslot].remove(allmemory[currentslot][len(allmemory[currentslot])-1])
                allmemory[currentslot].remove(allmemory[currentslot][len(allmemory[currentslot])-1])
        
            
        
        except:
            try:
                if allmemory[currentslot][-1]["content"] == prompt:
                    allmemory[currentslot].remove(allmemory[currentslot][-1])
            except:
                pass
                
            print(colored("Error occured when generating completion!","red"))
    prompt = input(colored("You > ","green"))
