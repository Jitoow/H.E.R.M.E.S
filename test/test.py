
while True : 

    prénom = input("Quel est ton prénom ?")
    if prénom == 'Jarvis' : 
        print("C'est moi !")
    elif prénom == 'stop' : 
        break
    else : 
        print('Bonjour ' + prénom)