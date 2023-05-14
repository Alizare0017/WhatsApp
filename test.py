with open('message.txt','r',encoding='utf-8') as f :
    
    my_string = ''.join(f.readlines())
    print(my_string)