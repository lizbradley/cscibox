import json

filename = "RAPiD-12-1K.Thornalley.2009.jsonld"
file = open(filename)
jstr = file.read()
file.close()
try:
    data = json.loads(jstr)
    print data
except Exception as e:
    message = str(e)
    print message
    paren = message.find("(")
    locstr = message[paren:]
    space = locstr.find(" ")
    paren = locstr.find(")")
    num = int(locstr[space:paren])
    print jstr[num-100:num]
    print "-----------"
    print jstr[num]
    print "-----------"
    print jstr[num+1:num+100]
    raise(e)
