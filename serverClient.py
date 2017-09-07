import os
import select
import socket
import sys
import threading
import globalVars as glob

def messageKeyboard(messageData):
    start=messageData.find('{')+1
    
    end=messageData.find('}')-1
    
    keyS=messageData.find(',')+1
    keyE=start-1
    key=messageData[keyS:keyE]
    
#     print('key'+messageData[keyS:keyE])
#     print('other'+messageData[start:end])
    
    other=messageData[start:end]
    ind=other.find('la')
    other=other.split(',')
    
    tempI=other[2].find(':')
    
    alt=other[2][tempI:tempI+3]
    
    if alt.find('T')>=0:
        alt=True
    else:
        alt=False

    if key.find('tab')>=0:
        tab=True
    else:
        tab=False
        
    
    if key.find('space')>=0:
        space=True
    else:
        space=False
    
#     print(alt,tab,space)
    return [alt,tab,space]
    
    #TODO
    #Implement the way to capture left alt, tab and space
    #While alt+ tab sounds like a great idea it is not
    #it requires the sychronizaiton of both hands
    #it should be either alt or tab
    #implement this as events I can tell to mainKSI how to interpret
    #meaning mode 4 could be alt is toggle
    # mode 5 tab is toggle
    
    

def messageDecypher(messageData):
        mess=messageData.split(',')
        for i in range(len(mess)):
            if mess[i]=='':
                mess.pop(i)
    
        data=[[0,0] for i in range(4)]
    
        for i in mess:
    
            if i.find('wii')>=0:
                wiiID=i
    
    
            if i.find('|')>=0:
                ind=int(i[int(i.find('|')-1)])
                indx=i.find('x')
                indy=i.find('y')
                data[ind][0]=float(i[indx+1:indy])
                data[ind][1]=float(i[indy+1:])
        
        return wiiID,data




class Client(threading.Thread):
    
    
    
    def __init__(self):
        print('Started client comm')
        
        
        self.host = 'localhost'
        self.port = 50020
        
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host,self.port))
            self.server.listen(60)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)
            
        (client,address)=self.server.accept()
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.size = 2048
        self.data=[]
#         vals.wiimoteNum = vals.wiimoteNum + 1

    def run(self):
        
        running = 1
        while running:
            data = self.client.recv(self.size)                
            if data:
#                 print(data)
#                 try:
                if data.find('mflt')>=0:
                    print('got something from the mflt client')
                    print(data)
                    #The next section sends the mouse state
                    #for now I just inhabilitated it
                    self.client.send(str(glob.fingersOn))
                    print(glob.fingersOn)
                elif data.find('click')>=0:
                    print "click cliked"
#                         vals.newClick_flg = 1 
                elif data.find('switch')>=0:
                    print "switch switched"
#                         vals.mouse_flg = not vals.mouse_flg
                elif data.find('wii')>=0:
                    self.wiiID,self.data=messageDecypher(data)
                elif data.find('key')>=0:
#                         print('got keylog')
#                     print(data)
                    glob.keystatus=messageKeyboard(data)
#                 except:
#                 print "User quit."
#                 return
                
                
                if data.find('wii')>=0:
                    if self.wiiID.find('1')>=0:
                        glob.coords[0]=self.data
                    else:
                        glob.coords[1]=self.data
                
            else:
#                 self.client.close()
#                 global kill
#                 kill=True
                running = 0