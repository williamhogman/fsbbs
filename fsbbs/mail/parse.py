
class MessageParser(object):
    """ Class for parsing messages as they come in over the wire"""

    def __init__(self):
        self.reset()

    def reset(self):
        """ Resets the parser to its initial state"""
        self.lines = list()
        self.headers =  dict()
        self._in_body = False

    def _add_header(self,header):
        name,val = self._parse_header(header)
        self.headers[name] = val


    def _parse_from(self,hdr):
        hdr = hdr.strip()
        print(hdr)
        start = hdr.find("<")
        if start != -1:
            rel = hdr[start+1:]
            stop = rel.find(">")
            if stop != -1:
                return rel[:stop].strip()
            else:
                return hdr
        else:
            return hdr
            
            
    def _parse_header(self,header):
        separator = header.find(":")
        name = header[:separator]
        value = header[separator+1:].lstrip()
        # headers are not case-sensitive, but servers usually correct it
        if name.lower() == "from": 
            return (name,self._parse_from(value))
            
        return (name,value)

    def feed(self,line):
        """ feeds a line into the message parser"""
        # empty line not in body
        if not self._in_body and not line:
            self._in_body = True
        elif self._in_body:
            self.lines.append(line)
        else:
            self._add_header(line)

    def get(self): 
        """ Gets the headers and body of the message being parsed """
        return (self.headers,self.lines)

    def get_and_reset(self):
        """ gets the data and resets the parser to its initial state"""
        rtn = self.get()
        self.reset()
        return rtn

class ParsedMessage(object):
    """ A message that is parsed using a message parser. message_parsed is called """
    def __init__(self):
        self.parser = MessageParser()

    def lineReceived(self,line):
        self.parser.feed(line)
        
    def eomReceived(self):
        return self.message_parsed(self.parser.get_and_reset())

    def connectionLost(self):
        self.parser.reset()

    def message_parsed(self,msg):
        """ Override this in your subclass to get the message when it has been parsed"""
        pass
