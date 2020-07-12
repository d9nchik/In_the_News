from nntplib import NNTP

servername = 'nntp.aioe.org'
group = 'comp.lang.python.announce'
howMany = 10

server = NNTP(servername)
_, count, first, last, name = server.group(group)
start = last - howMany + 1

_, overviews = server.over((start, last))

for ID, over in overviews:
    subject = over['subject']
    _, info = server.body(ID)
    print(subject)
    print('-' * len(subject))
    for line in info.lines:
        print(line.decode('latin1'))
    print()

server.quit()
