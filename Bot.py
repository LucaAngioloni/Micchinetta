from treetagger import TreeTagger

from collections import Counter
from Converter import Converter

from subprocess import call




# engine = pyttsx3.init()
# voices = engine.getProperty('voices')
# engine.setProperty('voice', voices[1].id)

# engine.say('Riccardo Celli coglione, cosa farai quando avrai finito gli esami?')
# engine.runAndWait()

# 
# 

class Bot():
    def __init__(self, products):
        self.username = ''
        self.prodlist = products
        self.prodlist_itemoid = list(self.prodlist.keys())
        self.add_itemoid()
        self.request = Counter(self.prodlist.keys())
        self.request.subtract(self.request) # sottraggo se stesso cosi da avere un dict con keys = nome prodotti, e value=0

        self.tagger = TreeTagger(language='italian')
        self.converter = Converter()

        self.positive_predicates = ['volere']
        self.negative_predicates = ['rimuovere', 'togliere']
        self.predicates = self.positive_predicates + self.negative_predicates
        self.completings = ['ok']

    def set_user_name(self, name):
        self.username = name
        print(self.username)

    def add_itemoid(self): # aggiungere qui sinonimi e plurali di prodotti
        self.prodlist_itemoid.extend(['coca-cole', 'acque', 'Coca Cola'])

    def check_fore_completings(self, userask):
        for word in userask.split():
            if word.lower() in self.completings:
                return True
        return False

    def check_for_products(self, sentence):
        # torna True se la frase contiene prodotti o sinonimi di prodotti
        for word in sentence.split():
            if word.lower() in self.prodlist_itemoid:
                return True
        return False

    def check_itemoid(self, item):
        # una volta tree taggata una frase, per poterla sostituire con la versione semplificata,
        # bisogna controllare se esiste una versione semplificata della parola,
        # in caso negativo si aggiungono qui i casi speciali
        if item[2] == '<unknown>':
            if item[0] == 'coca-cole' or 'cocacola' or 'cocacole' or 'Coca Cola':
                return 'coca-cola'
            else:
                return item[0]
        else:
            if item[0] == 'arachidi':
                return 'arachidi'
            else:
                return ''

    def get_predicates(self, phrase):
        # restiruisce la lista di predicati presenti in una frase
        pred = []
        for i in self.predicates:
            if i in phrase:
                pred.append(i)
        return pred

    def contains_predicate(self, phrase):
        # torna True se una frase è provvista di predicato
        pred = self.get_predicates(phrase)
        if len(pred) == 0:
            return False
        else:
            return True

    def set_predicate(self, phrase):
        if len(self.get_predicates(phrase)) ==1:
            return phrase
        querywords = phrase.split()
        resultwords  = [word for word in querywords if word.lower() not in self.predicates]
        result = ' '.join(resultwords)
        result = 'rimuovere ' + result
        return result

    def set_request_kind(self, list_of_subphrase):
        # data una lista di sottofrasi, assegna alla prima il predicato 'volere' se sprovvista di predicato, 
        # e poi assegna alle sottofrasi sprovviste, il predicato di quella immediatamente precedente 
        if self.contains_predicate(list_of_subphrase[0]) == False:
            list_of_subphrase[0] = 'volere ' + list_of_subphrase[0]
        else:
            list_of_subphrase[0] = self.set_predicate(list_of_subphrase[0])

        for i, phrase in enumerate(list_of_subphrase[1:len(list_of_subphrase)], start=1):
            if self.contains_predicate(phrase) == False:
                pr = " ".join(str(x) for x in self.get_predicates(list_of_subphrase[i-1]))
                list_of_subphrase[i] = pr + ' '+ list_of_subphrase[i]
            else:
                list_of_subphrase[i] = self.set_predicate(list_of_subphrase[i])
        return list_of_subphrase


    def get_prod(self, phrase):
        # data una frase, ritorna il primo prodotto conosciuto trovato
        for word in phrase.split():
            if word.lower() in self.prodlist:
                return word.lower()
        return False

    def get_amount(self, phrase):
        # data una frase, ritorna il primo digit trovato
        for word in phrase:
            if word.isdigit():
                return int(word)

    def get_all_products(self, phrase):
        # data una frase, ritorna una lista con tutti i prodotti conosciuti contenuti
        prod = []
        for word in phrase.split():
            if word in self.prodlist:
                prod.append(word)
        return prod

    def correct_no_amount(self, list_of_subphrase):
        # corregge casi come ['voglio acqua', 'coca-cola'] -> ['voglio 1 acqua', '1 coca-cola']
        print("TODO")


    def correct_multiple_prod(self, list_of_subphrase):
        # corregge casi come ['voglio 1 acqua 1 coca-cola'] -> ['voglio 1 acqua', '1 coca-cola']
        new_list = []
        final_list = []
        for phrase in list_of_subphrase:
            in_list = []
            count = 0
            splitted_phrase = phrase.split()
            splitted_phrase.extend('1')
            for idx, word in enumerate(splitted_phrase):
                if word.isdigit():
                    count+=1
                    if count>1:
                        length = sum(len(x) for x in in_list)
                        in_list.append(phrase.split()[length:idx])
            new_list.extend(in_list)
        for element in new_list:
            sub_phrase = ' '.join(element)
            final_list.append(sub_phrase)
        return final_list


    def parse_input(self, usersaid):
        p = self.tagger.tag(usersaid)
        # faccio una lista degli elementi parsati per semplificare la frase
        seq_phrase = []
        for item in p:
            res = self.check_itemoid(item)
            if item[2] == 'un' or item[2] == 'una':
                seq_phrase.append('uno')
            elif res =='':
                seq_phrase.append(item[2])
            else:
                seq_phrase.append(res)

        # ricostruisco una frase convertendo numeri scritti in lettere in numeri
        parsed_phrase = ''
        for item in seq_phrase:
            if item is not 'e':
                parsed_phrase += self.converter.let2num(item) + ' '
            else:
                parsed_phrase += item + ' '

        print("parsed = " + parsed_phrase)
        # divido quando c'è una "e", pesumibilmente ogni sottofrase ha un significato diverso
        list_of_subphrase = parsed_phrase.split(' e ')
        print("list_of_subphrase = ")
        print(list_of_subphrase)
        #list_of_subphrase = self.correct_no_amount(list_of_subphrase)
        list_of_subphrase = self.correct_multiple_prod(list_of_subphrase)
        print(list_of_subphrase)

        corrected_subphrase = self.set_request_kind(list_of_subphrase)

        print(corrected_subphrase)
        return(corrected_subphrase)

    def update_request(self, userask):
        list_of_subphrases = self.parse_input(userask)
        for phrase in list_of_subphrases:
            pred = self.get_predicates(phrase)
            amount = self.get_amount(phrase)
            prod = self.get_prod(phrase)
            if pred[0] in self.positive_predicates and prod in self.prodlist:
                self.request[prod]+=amount
            elif pred[0] in self.negative_predicates and prod in self.prodlist:
                self.request[prod]-=amount


    def sayhi(self): 
        greetings = "Ciao "+str(self.username)+" cosa ti serve?"
        print(greetings)
        call(["python3", "speak.py", greetings])

    def reply(self, userask):

        if self.check_fore_completings(userask):
            reply = 'Addebito richiesta effettuato. Ciao ' + str(self.username)
            call(["python3", "speak.py", reply])
            return True,reply, self.request
            # use API to complete request for the amount
        if self.check_for_products(userask):
            print("ok")
            self.update_request(userask)
            reply = 'Quindi vuoi '
            cost = 0
            for prod in self.request:
                if self.request[prod] > 0:
                    reply = reply + str(self.request[prod]) +' ' + prod + ' '
                    cost += self.prodlist[prod] * self.request[prod]
            cost = float("{0:.2f}".format(cost))
            print(cost)
            reply = reply + 'al prezzo di ' + str(cost) + ' € ?' + ' Dì ok per addebitare, o continua a modificare la richiesta'
            #self.say(reply)
            call(["python3", "speak.py", reply])
            print(self.request)
            print(reply)
            return False, reply, self.request





