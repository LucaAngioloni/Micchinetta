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
import re as regexp


class Bot():
    """
    Bot class that manages the dialog between the user and the system.
    Attributes:
        username                current users name
        prodlist                vending machine products data
        prodlist_itemoid        vending machine products data splitted by spaces for matching in check_for_products
        request                 Counter Dict object representing users bill
        tagger                  Object from TreeTagger Library
        converter               Instance of Converter class
        predicates              List of predicates that should be recognized from what user say
        positive_predicates     Sub-list of positive predicates
        negative_predicates     Sub-list of negative predicates
        completings             List of words that should end conversation positively
        terminatings            List of words that should remove items
        id_err                  List of key words that should trigger face recognition

    """
    
    def __init__(self, products):
        self.username = ''
        self.prodlist = products
        #self.prodlist_itemoid = list(self.prodlist.keys())
        self.prodlist_itemoid = self.add_itemoid()
        self.request = Counter(self.prodlist.keys())
        self.request.subtract(self.request) # sottraggo se stesso cosi da avere un dict con keys = nome prodotti, e value=0

        self.tagger = TreeTagger(language='italian')
        self.converter = Converter()

        self.positive_predicates = ['volere', 'aggiungere']
        self.negative_predicates = ['rimuovere', 'togliere', 'cancellare', 'eliminare']
        self.predicates = self.positive_predicates + self.negative_predicates
        self.completings = ['ok']
        self.terminatings = ['fine', 'tutto', 'termina', 'annulla', 'annullare']
        self.id_err = ['riconoscimento', 'identità', 'persona', 'utente', 'sono', 'faccia']


    def set_user_name(self, name):
        """
        Method to set the user name

        Args:
            name     the user name
        """
        self.username = name
        print(self.username)

    def add_itemoid(self):
        """
        Method to fill prodlist_itemoid

        """ 
        products = []
        for item in self.prodlist:
            for itemoid in item.split():
                products.append(itemoid)
        return products


    def check_id_error(self, userask):
        """
        Method to check if user said a word contained in id_err

        Args:
            userask     what the user said
        """
        for word in userask.split():
            if word.lower() in self.id_err:
                return True
        return False

    def check_for_completings(self, userask):
        """
        Method to check if the user said a word contained in completings

        Args:
            userask     what the user said
        """
        for word in userask.split():
            if word in self.completings:
                return True
        return False

    def check_for_terminatings(self, userask):
        """
        Method to check if the user said a word contained in terminatings

        Args:
            userask     what the user said
        """
        for word in userask.split():
            if word in self.terminatings:
                return True
        return False

    def check_for_products(self, sentence):
        """
        Method to check if the user said a word contained in prodlist_itemoid. 

        Args:
            userask     what the user said
        """
        for prod in self.prodlist_itemoid:
            if prod in sentence:
                return True
        return False


    def check_itemoid(self, item):
        """
        Once the phrase is POS-tagged, replace each word withe the simplified version of it (checking its existance).

        Args:
            item     the word from what user asked to be replaced
        """
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
        """
        Method to get predicate from a phrase

        Args:
            phrase     the phrase where to search for predicates
        """
        pred = []
        for i in self.predicates:
            if i in phrase:
                pred.append(i)
        return pred

    def contains_predicate(self, phrase):
        """
        Method to get the presence of predicate in a phrase

        Args:
            phrase     the phrase where to search for predicates
        """
        pred = self.get_predicates(phrase)
        if len(pred) == 0:
            return False
        else:
            return True

    def set_predicate(self, phrase):
        """
        Method to set a predicate in a phrase. If absent or more than one, force a negative_predicate. 
        Es. "voglio togliere un acqua" -> "rimuovere un acqua"

        Args:
            phrase     the phrase where to put the predicate
        """
        if len(self.get_predicates(phrase)) ==1:
            return phrase
        querywords = phrase.split()
        resultwords  = [word for word in querywords if word.lower() not in self.predicates]
        result = ' '.join(resultwords)
        result = 'rimuovere ' + result
        return result

    def set_request_kind(self, list_of_subphrase):
        """
        Given a list_of_subphrases, check if the first item in lisr_of_subphrases has a predicate, if no predicate is found in it,
        set a positive predicate. The we assign at each element with no predicate, the predicate of the previous element.

        Args:
            list_of_subphrases     the list containing phrases as elements
        """
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
        """
        Method to get a prod name from a phrase

        Args:
            phrase     a string
        """
        for prod in self.prodlist:
            if prod in phrase:
                return prod
        return False


    def get_amount(self, phrase):
        """
        Method to get the amount  from a phrase

        Args:
            phrase     a string
        """
        for word in phrase.split():
            if word.isdigit():
                return int(word)
        return None

    def get_all_products(self, phrase):
        """
        Method to get all the products from a phrase

        Args:
            phrase     a string
        """
        prod = []
        for item in self.prodlist:
            if item in phrase:
                prod.append(item)
        return prod

    def correct_no_amount(self, list_of_subphrase):
        """
        Method to correct no amount cases in list_of_subphrases

        Es. ['voglio acqua', 'coca-cola'] -> ['voglio 1 acqua', '1 coca-cola']

        Args:
            list_of_subphrases     the list containing phrases as elements
        """
        new_list_subphrase = []
        for phrase in list_of_subphrase:
            if self.get_amount(phrase) is None:
                phrase = '1 '+ phrase
            new_list_subphrase.append(phrase)
        return new_list_subphrase

    def correct_multiple_prod(self, list_of_subphrase):
        """
        Method to set the user name

        Args:
            name     the user name
        """
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


    def correct_ultra_no_amount(self, list_of_subphrase):
        """
        Method to correct another case of no_amount

        Args:
            list_of_subphrases     the list containing phrases as elements
        """
        new_list = []
        for phrase in list_of_subphrase:
            items = {}
            for item in self.prodlist:
                if item in phrase:
                    idx = phrase.find(item)
                    items[idx] = item
            if len(list(items.keys())) > 1:
                start_idx = 0
                keys = sorted(items.keys())
                for item_idx in keys:
                    idx = item_idx + len(items[item_idx])
                    new_list.append(phrase[start_idx:idx])
                    start_idx = idx
            else:
                new_list.append(phrase)
        return new_list


    def parse_input(self, usersaid):
        """
        Method to parse what user said

        Args:
            usersaid     what the user said
        """
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
        parsed_phrase = ' '.join(seq_phrase)


        print("parsed = " + parsed_phrase)
        # divido quando c'è una "e", pesumibilmente ogni sottofrase ha un significato diverso
        list_of_subphrase = parsed_phrase.split(' e ')
        print("list_of_subphrase = ")
        print(list_of_subphrase)

        list_of_subphrase = self.correct_no_amount(list_of_subphrase)
        print(list_of_subphrase)

        list_of_subphrase = self.correct_multiple_prod(list_of_subphrase)
        print(list_of_subphrase)

        list_of_subphrase = self.correct_ultra_no_amount(list_of_subphrase)
        print(list_of_subphrase)

        list_of_subphrase = self.correct_no_amount(list_of_subphrase)
        print(list_of_subphrase)

        corrected_subphrase = self.set_request_kind(list_of_subphrase)

        print(corrected_subphrase)
        return(corrected_subphrase)

    def update_request(self, userask):
        """
        parse the input and update request accordingly

        Args:
            userask     what the user asked
        """
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
        """
        Return True if the request dict is not empty.  

        """
        for prod in self.request:
            if self.request[prod] > 0:
                return True
        return False

    def replace_itemoid(self, userask):
        """
        Method to replace itemoid with preper item names using edit distance

        Args:
            userask     what the user asked
        """
        word_list = userask.split()
        for word in word_list:
            if len(word)>2:
                min_item = word
                min_dist = 1000
                for item in self.prodlist_itemoid:
                    dist = editdistance.eval(word, item)
                    if dist<3:
                        if dist < min_dist:
                            min_dist = dist
                            min_item = item
                userask = userask.replace(word, min_item)
        return userask

    def replace_numbers(self, userask):
        """
        Method to replace string number with digits

        Args:
            userask     what the user asked
        """
        converted_phrase = ''
        for item in userask.split():
            if item =='un' or item =='una':
                item = 'uno'
            if item != 'e':
                num = self.converter.let2num(item)
                if num.isdigit():
                    converted_phrase += num + ' '
                else:
                    converted_phrase += item + ' '
            else:
                converted_phrase += item + ' '
        return converted_phrase


    def reply(self, userask):
        """
        Method to reply to the user

        Args:
            userask     what the user asked
        """

        userask = userask.replace("'", " ").replace(" alla ", " ").replace(" al ", " ").replace(" ai ", " ").replace(" di ", " ").replace("coca cola", "coca-cola").replace("coca cole", "coca-cola")

        list_userask = regexp.split('(\d+)', userask)

        userask = ' '.join(list_userask)
        print(userask)

        userask = self.replace_numbers(userask)
        print(userask)
        userask = self.replace_itemoid(userask)
        print(userask)

        if userask.lower() == "impossibile capire" or userask.lower() == 'richieste speech-to-text terminate':
            reply = 'Scusa non ho capito. Ripeti perfavore.'
            print(reply)
            return False, reply, self.request
        elif self.check_for_terminatings(userask) or userask == "no":
            reply = 'Ciao ' + str(self.username)
            return None, reply, self.request
        elif self.check_for_completings(userask):
            if self.check_if_request_is_not_empty():
                reply = 'Addebito richiesta effettuato. Ciao ' + str(self.username)
                return True, reply, self.request
            else:
                reply = 'Ma ' + str(self.username) + ' ancora non mi hai chiesto nessun prodotto!'
                return False, reply, self.request
            
            # use API to complete request for the amount
        elif self.check_id_error(userask):
            reply = 'Mi dispiace molto non averti riconosciuto, riproviamo.'
            return None, reply, self.request
        elif self.check_for_products(userask):
            print("Prodotto rilevato, inizio parsing...")
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