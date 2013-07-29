import urllib2
import re
import sqlite3
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def main():
	dbconn = sqlite3.connect("apples.db")
	db = dbconn.cursor()

	db.execute("CREATE TABLE IF NOT EXISTS green_apples (word, synonyms)")
	db.execute("CREATE TABLE IF NOT EXISTS red_apples (word, flavour)")
	db.execute("DELETE FROM green_apples")
	db.execute("DELETE FROM red_apples")

	green_cards_regex = re.compile("<li><b>([^<]+)</b> - \(([^\n]+)\)", re.S | re.I | re.U)
	red_cards_regex = re.compile("<li><b>([^<]+)</b> - ([^\n]+)", re.S | re.I | re.U)

	html = urllib2.urlopen("http://www.com-www.com/applestoapples/applestoapples-partyset-green-2004.html").read()
	matches = green_cards_regex.finditer(html)
	for match in matches:
		# print "Word: {word}; Flavour: {flavour}".format(word=match.group(1), flavour=match.group(2))
		db.execute("INSERT INTO green_apples (word, synonyms) VALUES (?, ?)", (match.group(1), match.group(2)))

	html = urllib2.urlopen("http://www.com-www.com/applestoapples/applestoapples-partyset-red-2004.html").read()
	matches = red_cards_regex.finditer(html)
	for match in matches:
		# print "{word} - {flavour}".format(word=match.group(1), flavour=strip_tags(match.group(2)))
		db.execute("INSERT INTO red_apples (word, flavour) VALUES (?, ?)", (match.group(1), strip_tags(match.group(2))))

	dbconn.commit()
	dbconn.close()

if __name__ == '__main__':
	main()