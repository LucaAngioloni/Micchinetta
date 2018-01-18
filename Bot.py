# MIT License

# Copyright (c) 2017 Luca Angioloni and Francesco Pegoraro

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from treetagger import TreeTagger

from collections import Counter
from Converter import Converter
import editdistance

class Bot():
    def __init__(self, products):
        self.username = ''
        self.prodlist = products
        #self.prodlist_itemoid = list(self.prodlist.keys())
        self.prodlist_itemoid = self.add_itemoid()
        self.request = Counter(self.prodlist.keys())
        self.request.subtract(self.request) # sottraggo se stesso cosi da avere un dict con keys = nome prodotti, e value=0

        self.tagger = TreeTagger(language='italian')
        self.converter = Converter()

        self.positive_predicates = ['volere']
        self.negative_predicates = ['rimuovere', 'togliere']
        self.predicates = self.positive_predicates + self.negative_predicates
        self.completings = ['ok']
        self.terminatings = ['fine']
        self.id_err = ['riconoscimento', 'identità', 'persona', 'utente', 'sono']


    def set_user_name(self, name):
        self.username = name
        print(self.username)

    def add_itemoid(self): 
        products = []
        for item in self.prodlist:
            for itemoid in item.split():
                products.append(itemoid)
        return products


    def check_id_error(self, userask):
        for word in userask.split():
            if word.lower() in self.id_err:
                return True
        return False

    def check_for_completings(self, userask):
        for word in userask.split():
            if word in self.completings:
                return True
        return False

    def check_for_terminatings(self, userask):
        for word in userask.split():
            if word in self.terminatings:
                return True
        return False

    def check_for_products(self, sentence):
        # torna True se la frase contiene prodotti o sinonimi di prodotti
        for prod in self.prodlist_itemoid:
            if prod in sentence:
                return True
        return False
        # for word in sentence.split():
        #     if word.lower() in self.prodlist_itemoid:
        #         return True
        # return False

    def check_itemoid(self, item):
        # una volta tree taggata una frase, per poterla sostituire con la versione semplificata,
        # bisogna controllare se esiste una versione semplificata della parola,
        # in caso negativo si aggiungono qui i casi speciali
        if item[2] == '<unknown>':
            if item[0] == 'coca-cole' or item[0] == 'cocacola' or item[0] == 'cocacole' or item[0] == 'Coca Cola':
                return 'coca-cola'
            else:
                return item[0]
        elif item[2]=='@card@':
            return item[0]
        elif '|' in item[2]:
            splitted = item[2].split('|')
            return splitted[0]
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
        # data una frase, controllo se ha gia esattamente un predicato, se si è ok e la ritorno
        # altrimenti tolgo tutti i predicati e imposto che ci sia "rimuovere"
        # Es. "voglio togliere un acqua" -> "rimuovere un acqua"
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
        for prod in self.prodlist:
            if prod in phrase:
                return prod
        return False
        # for word in phrase.split():
        #     if word.lower() in self.prodlist:
        #         return word.lower()
        # return False

    def get_amount(self, phrase):
        # data una frase, ritorna il primo digit trovato
        for word in phrase:
            if word.isdigit():
                return int(word)
        return None

    def get_all_products(self, phrase):
        # data una frase, ritorna una lista con tutti i prodotti conosciuti contenuti
        prod = []
        for item in self.prodlist:
            if item in phrase:
                prod.append(item)
        return prod

    def correct_no_amount(self, list_of_subphrase):
        # corregge casi come ['voglio acqua', 'coca-cola'] -> ['voglio 1 acqua', '1 coca-cola']
        new_list_subphrase = []
        for phrase in list_of_subphrase:
            if self.get_amount(phrase) is None:
                phrase = '1 '+ phrase
            new_list_subphrase.append(phrase)
        return new_list_subphrase

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
            elif item[0] in self.prodlist_itemoid:
                seq_phrase.append(item[0])
            elif res =='':
                seq_phrase.append(item[2])
            else:
                seq_phrase.append(res)

        # ricostruisco una frase convertendo numeri scritti in lettere in numeri
        parsed_phrase = ''
        for item in seq_phrase:    
            parsed_phrase += item + ' '

        print("parsed = " + parsed_phrase)
        # divido quando c'è una "e", pesumibilmente ogni sottofrase ha un significato diverso
        list_of_subphrase = parsed_phrase.split(' e ')
        print("list_of_subphrase = ")
        print(list_of_subphrase)
        list_of_subphrase = self.correct_no_amount(list_of_subphrase)
        print(list_of_subphrase)

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
                if self.request[prod] < 0:
                    self.request[prod] = 0

    def check_if_request_is_not_empty(self):
        for prod in self.request:
            if self.request[prod] > 0:
                return True
        return False

    def replace_itemoid(self, userask):
        word_list = userask.split()
        for word in word_list:
            if len(word)>2:
                for item in self.prodlist_itemoid:
                    if editdistance.eval(word, item)<3:
                        userask = userask.replace(word, item)
        return userask

    def replace_numbers(self, userask):
        converted_phrase = ''
        for item in userask.split():
            if item =='un' or item =='una':
                item = 'uno'
            if item != 'e' and item != 'biscotto':
                converted_phrase += self.converter.let2num(item) + ' '
            else:
                converted_phrase += item + ' '
        return converted_phrase


    def reply(self, userask):

        userask = userask.replace("'", " ").replace("alla", " ").replace("al", "").replace("ai", "").replace("di", "")

        userask = self.replace_numbers(userask)
        userask = self.replace_itemoid(userask)

        if userask.lower() == "impossibile capire" or userask.lower() == 'richieste speech-to-text terminate':
            reply = 'Scusa non ho capito. Ripeti perfavore.'
            print(reply)
            #call(["python3", "speak.py", reply])
            return False, reply, self.request
        elif self.check_for_terminatings(userask) or userask == "no":
            reply = 'Ciao' + str(self.username)
            return None, reply, self.request
        elif self.check_for_completings(userask):
            if self.check_if_request_is_not_empty():
                reply = 'Addebito richiesta effettuato. Ciao. ' + str(self.username)
                return True, reply, self.request
            else:
                reply = 'Ma ' + str(self.username) + ' ancora non mi hai chiesto nessun prodotto!'
                return False, reply, self.request
            
            # use API to complete request for the amount
        elif self.check_id_error(userask):
            reply = 'Mi dispiace molto non averti riconosciuto, riproviamo.'
            return None, reply, self.request
        elif self.check_for_products(userask):
            print("ok")
            self.update_request(userask)
            if sum(self.request.values()) == 0:
                reply = 'Non hai prodotti nel carrello, cosa ti serve?'
                return False, reply, self.request
            cost = 0
            missing = []
            ok = 0
            reply1 = ''
            for prod in self.request:
                if self.request[prod] > 0:
                    if int(self.prodlist[prod][1])>=self.request[prod]:
                        ok+=1
                        reply1 = reply1 + str(self.request[prod]) +' ' + prod + ', '
                        cost += float(self.prodlist[prod][0]) * self.request[prod]
                    else:
                        missing.append(prod)
                        self.request[prod] = int(self.prodlist[prod][1])
                        if self.request[prod] != 0:
                            ok+=1
                            reply1 = reply1 + str(self.request[prod]) +' ' + prod + ', '
                            cost += float(self.prodlist[prod][0]) * self.request[prod]
            cost = float("{0:.2f}".format(cost))
            print(cost)
            re = ''
            if ok >= len(missing):
                reply3 = 'al prezzo di ' + str(cost) + ' € ?'
                re = 'Quindi vuoi ' + reply1 + reply3
            reply2 = ''
            if len(missing)>1:
                reply2 += ' Mi dispiace ma '
                for el in missing:
                    reply2 += el + ', '
                reply2 += 'non sono disponibili nelle quantità richieste. Ho inserito le disponibili.'
            elif len(missing)==1:
                reply2 += ' Mi dispiace ma ' + missing[0] + ' non è disponibile nella quantità richiesta. Ho inserito la quantità disponibile.'

            reply = re + reply2
            if  sum(self.request.values()) != 0:
                reply += ' Dì ok per addebitare, o continua a modificare la richiesta.'
            else:
                reply += " Vuoi qualcos'altro ?"
            print(self.request)
            print(reply)
            return False, reply, self.request
        else:
            reply = 'Scusa non ho capito. Ripeti perfavore.'
            print(reply)
            return False, reply, self.request






